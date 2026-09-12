#!/usr/bin/env python3
"""Offline-first main-matrix runner contract.

The submission artifact must be reproducible without provider credentials.  This
script therefore treats the cassette as the boundary between live provider calls
and scoring.  Replay never calls the network.  Record mode imports provider
responses only from an explicit adapter/source JSONL and rewrites them as a
hash-checked cassette.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_json(value: Any) -> str:
    return sha256_bytes(canonical_json(value).encode("utf-8"))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            row["_line_number"] = line_number
            rows.append(row)
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            clean = {key: value for key, value in row.items() if key != "_line_number"}
            handle.write(canonical_json(clean) + "\n")


def resolve(path: str | Path) -> Path:
    path = Path(path)
    return path if path.is_absolute() else ROOT / path


def load_config(config_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    config = read_json(config_path)
    rows_path = resolve(config["row_manifest"]["path"])
    rows = read_jsonl(rows_path)
    return config, rows


def raw_payload_hash(entry: dict[str, Any]) -> str:
    if "raw_response" in entry:
        return sha256_json(entry["raw_response"])
    if "raw_response_text" in entry:
        return sha256_bytes(str(entry["raw_response_text"]).encode("utf-8"))
    if "raw_provider_response" in entry:
        return sha256_json(entry["raw_provider_response"])
    raise ValueError("cassette entry has no raw_response, raw_response_text, or raw_provider_response")


def normalize_record_source_entry(entry: dict[str, Any], row_by_hash: dict[str, dict[str, Any]]) -> dict[str, Any]:
    request_hash = (
        entry.get("logical_request_hash")
        or entry.get("request_hash")
        or entry.get("row_request_hash")
    )
    if not request_hash:
        raise ValueError(f"record source line {entry.get('_line_number')} lacks logical_request_hash")
    if request_hash not in row_by_hash:
        raise ValueError(f"record source line {entry.get('_line_number')} has unknown request hash {request_hash}")

    row = row_by_hash[request_hash]
    raw_hash = entry.get("raw_response_sha256") or raw_payload_hash(entry)
    normalized = {
        "schema_version": "pcg_dynamic_state_v2.main_matrix_cassette.v1",
        "logical_request_hash": request_hash,
        "row_id": row["row_id"],
        "global_artifact_id": row["global_artifact_id"],
        "task_id": row["task_id"],
        "model_condition_id": row["model_condition_id"],
        "provider": row["provider"],
        "requested_model": row["requested_model"],
        "method": row["method"],
        "budget": row["budget"],
        "run_id": row["run_id"],
        "raw_response": entry.get("raw_response", entry.get("raw_provider_response", entry.get("raw_response_text"))),
        "raw_response_sha256": raw_hash,
        "provider_metadata": entry.get("provider_metadata", {}),
        "usage": entry.get("usage", {}),
        "finish_reason": entry.get("finish_reason"),
        "record_metadata": {
            "source_line_number": entry.get("_line_number"),
            "source_row_id": entry.get("row_id"),
            "source_global_artifact_id": entry.get("global_artifact_id"),
        },
    }
    observed_hash = raw_payload_hash(normalized)
    if observed_hash != raw_hash:
        raise ValueError(
            f"raw hash mismatch for {request_hash}: declared {raw_hash}, observed {observed_hash}"
        )
    return normalized


def build_cassette_index(cassette_rows: list[dict[str, Any]]) -> tuple[dict[str, dict[str, Any]], list[str]]:
    index: dict[str, dict[str, Any]] = {}
    failures: list[str] = []
    for entry in cassette_rows:
        request_hash = entry.get("logical_request_hash")
        if not request_hash:
            failures.append(f"line {entry.get('_line_number')} missing logical_request_hash")
            continue
        if request_hash in index:
            failures.append(f"duplicate cassette hash {request_hash}")
            continue
        try:
            observed = raw_payload_hash(entry)
        except Exception as exc:
            failures.append(f"{request_hash}: {exc}")
            continue
        declared = entry.get("raw_response_sha256")
        if declared != observed:
            failures.append(f"{request_hash}: raw_response_sha256 mismatch declared={declared} observed={observed}")
            continue
        index[request_hash] = entry
    return index, failures


def audit(config_path: Path, cassette_path: Path | None) -> int:
    config, rows = load_config(config_path)
    failures: list[str] = []
    expected = int(config["matrix_shape"]["expected_rows"])
    if len(rows) != expected:
        failures.append(f"row manifest count {len(rows)} != expected {expected}")
    seen_rows = set()
    seen_hashes = set()
    for row in rows:
        row_id = row.get("row_id")
        request_hash = row.get("logical_request_hash")
        if row_id in seen_rows:
            failures.append(f"duplicate row_id {row_id}")
        seen_rows.add(row_id)
        if request_hash in seen_hashes:
            failures.append(f"duplicate logical_request_hash {request_hash}")
        seen_hashes.add(request_hash)
    cassette_count = 0
    cache_miss_count = 0
    if cassette_path:
        cassette_rows = read_jsonl(cassette_path)
        cassette_index, cassette_failures = build_cassette_index(cassette_rows)
        failures.extend(cassette_failures)
        cassette_count = len(cassette_index)
        row_hashes = {row["logical_request_hash"] for row in rows}
        cache_miss_count = len(row_hashes - set(cassette_index))
        extra = set(cassette_index) - row_hashes
        if extra:
            failures.append(f"cassette contains {len(extra)} hashes outside config")
    summary = {
        "mode": "audit",
        "config": str(config_path),
        "expected_rows": expected,
        "rows_checked": len(rows),
        "cassette_entries_checked": cassette_count,
        "cache_miss_count": cache_miss_count,
        "failure_count": len(failures),
        "failures": failures[:50],
        "api_calls_performed": 0,
    }
    print(canonical_json(summary))
    return 0 if not failures else 1


def record(config_path: Path, source_path: Path, cassette_path: Path) -> int:
    _, rows = load_config(config_path)
    row_by_hash = {row["logical_request_hash"]: row for row in rows}
    source_rows = read_jsonl(source_path)
    cassette_rows: list[dict[str, Any]] = []
    failures: list[str] = []
    for entry in source_rows:
        try:
            cassette_rows.append(normalize_record_source_entry(entry, row_by_hash))
        except Exception as exc:
            failures.append(str(exc))
    if failures:
        print(canonical_json({"mode": "record", "failure_count": len(failures), "failures": failures[:50]}))
        return 1
    write_jsonl(cassette_path, cassette_rows)
    print(
        canonical_json(
            {
                "mode": "record",
                "source_rows": len(source_rows),
                "cassette_entries_written": len(cassette_rows),
                "cassette": str(cassette_path),
                "api_calls_performed": 0,
                "note": "record mode imported explicit provider-adapter output; it did not call a provider itself",
            }
        )
    )
    return 0


def replay(config_path: Path, cassette_path: Path, out_path: Path) -> int:
    config, rows = load_config(config_path)
    cassette_rows = read_jsonl(cassette_path)
    cassette_index, failures = build_cassette_index(cassette_rows)
    output_rows: list[dict[str, Any]] = []
    missing: list[str] = []
    for row in rows:
        request_hash = row["logical_request_hash"]
        entry = cassette_index.get(request_hash)
        if entry is None:
            missing.append(request_hash)
            continue
        output_rows.append(
            {
                "schema_version": "pcg_dynamic_state_v2.main_matrix_replay_output.v1",
                "experiment_id": config["experiment_id"],
                "row_id": row["row_id"],
                "global_artifact_id": row["global_artifact_id"],
                "logical_request_hash": request_hash,
                "task_id": row["task_id"],
                "model_condition_id": row["model_condition_id"],
                "provider": row["provider"],
                "requested_model": row["requested_model"],
                "method": row["method"],
                "budget": row["budget"],
                "run_id": row["run_id"],
                "raw_response": entry.get("raw_response"),
                "raw_response_sha256": entry.get("raw_response_sha256"),
                "provider_metadata": entry.get("provider_metadata", {}),
                "usage": entry.get("usage", {}),
                "finish_reason": entry.get("finish_reason"),
                "api_calls_performed": 0,
            }
        )
    if missing:
        failures.append(f"cache miss for {len(missing)} configured rows")
    if failures:
        print(
            canonical_json(
                {
                    "mode": "replay",
                    "failure_count": len(failures),
                    "cache_miss_count": len(missing),
                    "missing_hashes_sample": missing[:20],
                    "api_calls_performed": 0,
                }
            )
        )
        return 1
    write_jsonl(out_path, output_rows)
    print(
        canonical_json(
            {
                "mode": "replay",
                "rows_replayed": len(output_rows),
                "output": str(out_path),
                "api_calls_performed": 0,
            }
        )
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["record", "replay", "audit"], required=True)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--cassette", type=Path)
    parser.add_argument("--record-source-jsonl", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    config_path = resolve(args.config)
    if args.mode == "audit":
        return audit(config_path, resolve(args.cassette) if args.cassette else None)
    if args.mode == "record":
        if not args.record_source_jsonl or not args.cassette:
            raise SystemExit("record requires --record-source-jsonl and --cassette")
        return record(config_path, resolve(args.record_source_jsonl), resolve(args.cassette))
    if args.mode == "replay":
        if not args.cassette or not args.out:
            raise SystemExit("replay requires --cassette and --out")
        return replay(config_path, resolve(args.cassette), resolve(args.out))
    raise AssertionError(args.mode)


if __name__ == "__main__":
    raise SystemExit(main())
