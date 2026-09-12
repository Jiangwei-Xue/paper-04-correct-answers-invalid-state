#!/usr/bin/env python3
"""Replay the primary main matrix from saved VCR cassettes.

This verifier does not call model APIs. It rebuilds primary score rows from the
saved cassette raw responses, reruns the deterministic scorer, writes
recomputed score JSONL/CSV files under `.verification_build/`, and compares the
claim-bearing fields with the checked-in score files.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import shutil
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2]
VERIFY_DIR = ROOT / "artifact" / "verification"
RECORD_ROOT = ROOT / "artifact" / "results" / "main_matrix" / "record_mode_20260627"
SCORER_PATH = (
    ROOT
    / "artifact"
    / "results"
    / "evidence"
    / "ssr_downgrade_20260623"
    / "tools"
    / "pcg_dynamic_state_v2"
    / "score_pcg_dynamic_state_v2_main_matrix.py"
)
DEFAULT_OUTPUT_DIR = ROOT / ".verification_build" / "main_matrix_replay"

PRIMARY_SLICES = [
    (
        "deepseek_v4pro",
        RECORD_ROOT
        / "ALL_MODEL_DIRECT_CLEAN_V2_FROM_ZERO_20260628"
        / "deepseek_v4pro"
        / "confirmatory",
    ),
    (
        "qwen37max",
        RECORD_ROOT
        / "ALL_MODEL_DIRECT_CLEAN_V2_FROM_ZERO_20260628"
        / "qwen37max"
        / "confirmatory",
    ),
    (
        "kimi_k26",
        RECORD_ROOT
        / "ALL_MODEL_DIRECT_CLEAN_V2_FROM_ZERO_20260628"
        / "kimi_k26"
        / "confirmatory",
    ),
    (
        "openrouter_claude48",
        RECORD_ROOT
        / "OPENROUTER_GPT_CLAUDE_CLEAN_V2_FROM_ZERO_20260627"
        / "openrouter_claude48"
        / "confirmatory",
    ),
    (
        "openrouter_gpt55",
        RECORD_ROOT
        / "OPENROUTER_GPT_CLAUDE_CLEAN_V2_FROM_ZERO_20260627"
        / "openrouter_gpt55"
        / "confirmatory",
    ),
]

SKIP_COMPARE_FIELDS = {
    "record_mode_created_at_utc",
}


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


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            clean = {key: value for key, value in row.items() if not key.startswith("_")}
            handle.write(canonical_json(clean) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    keys: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key.startswith("_"):
                continue
            if key not in seen:
                seen.add(key)
                keys.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows([{k: v for k, v in row.items() if not k.startswith("_")} for row in rows])


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def file_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def clean_internal(row: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in row.items() if not key.startswith("_")}


def expected_model_for(row: dict[str, Any], endpoints: dict[str, dict[str, Any]]) -> str:
    endpoint = endpoints.get(row["model_condition_id"], {})
    return endpoint.get("expected_exact_model_string") or endpoint.get("requested_model") or row["requested_model"]


def final_output_construction(row: dict[str, Any], raw_response: dict[str, Any]) -> str:
    if row.get("method") == "mature_ssr_loop":
        return "deterministic_mature_ssr_slot_compiler"
    final_raw = raw_response.get("final_raw")
    if isinstance(final_raw, dict):
        attempts = final_raw.get("attempts") or []
        if any(isinstance(item, dict) and item.get("synthetic_final_construction") for item in attempts):
            return "deterministic_mature_ssr_slot_compiler"
    return "provider_final_call"


def build_score_row(
    row: dict[str, Any],
    cassette_entry: dict[str, Any],
    oracle: dict[str, Any],
    scorer: Any,
    smoke: Any,
    endpoints: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    raw_response = cassette_entry.get("raw_response")
    if not isinstance(raw_response, dict):
        raw_response = {}
    provider_metadata = cassette_entry.get("provider_metadata") or {}
    final_output = raw_response.get("final_output", "")
    final_state = raw_response.get("final_state", "")
    compiler_audits = raw_response.get("compiler_audits") or []

    score_error = None
    try:
        metric = scorer.score_task(
            oracle,
            {
                "task_id": row["task_id"],
                "method": row["method"],
                "model": row["requested_model"],
                "budget": int(row["budget"]),
                "run_id": row["run_id"],
                "final_output": final_output,
                "final_state": final_state,
            },
        )
        score_row_emitted = True
    except Exception as exc:
        metric = {}
        score_error = f"{type(exc).__name__}: {exc}"
        score_row_emitted = False

    expected_model = expected_model_for(row, endpoints)
    returned_model = provider_metadata.get("returned_model", row["requested_model"])
    returned_model_match = returned_model == expected_model
    backend_error = bool(provider_metadata.get("backend_error")) or not returned_model_match
    raw_sha = sha256_json(raw_response)

    return {
        **metric,
        "schema_version": "pcg_dynamic_state_v2.main_matrix_score_row.v1",
        "experiment_id": row["experiment_id"],
        "row_id": row["row_id"],
        "global_artifact_id": row["global_artifact_id"],
        "logical_request_hash": row["logical_request_hash"],
        "task_id": row["task_id"],
        "model_condition_id": row["model_condition_id"],
        "provider": row["provider"],
        "requested_model": row["requested_model"],
        "selected_model_or_returned_model": returned_model,
        "expected_model_string": expected_model,
        "returned_model_match": returned_model_match,
        "method": row["method"],
        "budget": int(row["budget"]),
        "run_id": row["run_id"],
        "matrix_role": row["matrix_role"],
        "primary_analysis_eligible": bool(row["primary_analysis_eligible"]),
        "record_mode_role": "confirmatory",
        "final_json_parse_success": smoke.json_parse_success(str(final_output or "")),
        "score_row_emitted": score_row_emitted,
        "backend_error": backend_error,
        "reasoning_content_present": bool(provider_metadata.get("reasoning_content_present")),
        "reasoning_tokens_observed": provider_metadata.get("reasoning_tokens_observed"),
        "finish_reason": provider_metadata.get("finish_reason", cassette_entry.get("finish_reason")),
        "http_status": provider_metadata.get("http_status"),
        "score_error": score_error,
        "raw_response_sha256": raw_sha,
        "parsed_output_sha256": sha256_json({"final_output": final_output, "final_state": final_state}),
        "metric_record_sha256": sha256_json(metric),
        "provider_call_count": len(raw_response.get("state_calls") or [])
        + (0 if row.get("method") == "mature_ssr_loop" else 1),
        "final_attempt_count": provider_metadata.get("final_attempt_count"),
        "retry_policy_id": provider_metadata.get("retry_policy_id"),
        "retry_policy_sha256": provider_metadata.get("retry_policy_sha256"),
        "openrouter_runtime_hardening_applied": (
            isinstance(provider_metadata.get("openrouter_runtime_hardening"), dict)
            and provider_metadata["openrouter_runtime_hardening"].get("applied") is True
        ),
        "final_output_construction": final_output_construction(row, raw_response),
        "state_hard_cap_used": any(
            isinstance(item, dict) and item.get("state_hard_cap_used") for item in compiler_audits
        ),
        "local_transport_path_failure_detected": bool(
            provider_metadata.get("local_transport_path_failure_detected")
        ),
    }


def compare_rows(expected: dict[str, Any], observed: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    expected_clean = clean_internal(expected)
    observed_clean = clean_internal(observed)
    keys = (set(expected_clean) | set(observed_clean)) - SKIP_COMPARE_FIELDS
    for key in sorted(keys):
        if expected_clean.get(key) != observed_clean.get(key):
            failures.append(
                f"{expected_clean.get('row_id', '<unknown>')} field {key}: "
                f"expected={expected_clean.get(key)!r} observed={observed_clean.get(key)!r}"
            )
            if len(failures) >= 50:
                break
    return failures


def replay_slice(
    model_condition: str,
    slice_dir: Path,
    output_root: Path,
    scorer: Any,
    smoke: Any,
    endpoints: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    config_path = slice_dir / f"{model_condition}_confirmatory.config.json"
    rows_path = slice_dir / f"{model_condition}_confirmatory.rows.jsonl"
    cassette_path = slice_dir / f"{model_condition}_confirmatory.cassette.jsonl"
    expected_scores_path = slice_dir / "scores.confirmatory.jsonl"
    expected_scores_csv = slice_dir / "scores.confirmatory.csv"

    config = read_json(config_path)
    rows = read_jsonl(rows_path)
    cassette_rows = read_jsonl(cassette_path)
    expected_scores = read_jsonl(expected_scores_path)
    oracle_by_id = smoke.task_maps()[1]

    failures: list[str] = []
    if len(rows) != int(config["matrix_shape"]["expected_rows"]):
        failures.append(f"{model_condition}: row count does not match config expected_rows")

    cassette_by_hash: dict[str, dict[str, Any]] = {}
    for entry in cassette_rows:
        request_hash = entry.get("logical_request_hash")
        if not request_hash:
            failures.append(f"{model_condition}: cassette line {entry.get('_line_number')} lacks logical_request_hash")
            continue
        if request_hash in cassette_by_hash:
            failures.append(f"{model_condition}: duplicate cassette hash {request_hash}")
            continue
        raw_response = entry.get("raw_response")
        observed_raw_hash = sha256_json(raw_response)
        if observed_raw_hash != entry.get("raw_response_sha256"):
            failures.append(f"{model_condition}: raw_response_sha256 mismatch for {request_hash}")
        cassette_by_hash[request_hash] = entry

    expected_by_hash = {row["logical_request_hash"]: row for row in expected_scores}
    recomputed: list[dict[str, Any]] = []
    for row in sorted(rows, key=lambda item: item["row_id"]):
        request_hash = row["logical_request_hash"]
        cassette_entry = cassette_by_hash.get(request_hash)
        expected = expected_by_hash.get(request_hash)
        if cassette_entry is None:
            failures.append(f"{model_condition}: cassette cache miss for {request_hash}")
            continue
        if expected is None:
            failures.append(f"{model_condition}: expected score missing for {request_hash}")
            continue
        oracle = oracle_by_id[row["task_id"]]
        observed = build_score_row(row, cassette_entry, oracle, scorer, smoke, endpoints)
        recomputed.append(observed)
        failures.extend(compare_rows(expected, observed))

    out_dir = output_root / model_condition / "confirmatory"
    write_jsonl(out_dir / "scores.confirmatory.jsonl", recomputed)
    write_csv(out_dir / "scores.confirmatory.csv", recomputed)

    return {
        "model_condition_id": model_condition,
        "slice_dir": rel(slice_dir),
        "config": rel(config_path),
        "row_manifest": {"path": rel(rows_path), "sha256": file_sha256(rows_path), "rows": len(rows)},
        "cassette": {"path": rel(cassette_path), "sha256": file_sha256(cassette_path), "rows": len(cassette_rows)},
        "expected_scores": {
            "jsonl": rel(expected_scores_path),
            "csv": rel(expected_scores_csv),
            "jsonl_sha256": file_sha256(expected_scores_path),
            "csv_sha256": file_sha256(expected_scores_csv),
            "rows": len(expected_scores),
        },
        "recomputed_scores": {
            "jsonl": rel(out_dir / "scores.confirmatory.jsonl"),
            "csv": rel(out_dir / "scores.confirmatory.csv"),
            "rows": len(recomputed),
        },
        "failure_count": len(failures),
        "failures": failures[:50],
        "api_calls_performed": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--keep-output", action="store_true")
    args = parser.parse_args()

    output_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    if output_dir.exists() and not args.keep_output:
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    smoke = load_module(VERIFY_DIR / "run_model_admission_smoke.py", "run_model_admission_smoke_replay")
    scorer = load_module(SCORER_PATH, "pcg_dynamic_state_v2_main_matrix_scorer_replay")
    endpoints = smoke.endpoint_by_condition()

    slice_results = [
        replay_slice(model_condition, slice_dir, output_dir, scorer, smoke, endpoints)
        for model_condition, slice_dir in PRIMARY_SLICES
    ]
    total_rows = sum(result["recomputed_scores"]["rows"] for result in slice_results)
    total_cassette_rows = sum(result["cassette"]["rows"] for result in slice_results)
    failures = [failure for result in slice_results for failure in result["failures"]]
    summary = {
        "schema_version": "pcg_dynamic_state_v2.main_matrix_cassette_replay.v1",
        "mode": "offline_saved_cassette_score_replay",
        "passed": total_rows == 7200 and total_cassette_rows == 7200 and not failures,
        "api_calls_performed": 0,
        "primary_rows_expected": 7200,
        "primary_rows_recomputed": total_rows,
        "cassette_entries_checked": total_cassette_rows,
        "slice_count": len(slice_results),
        "scorer": {"path": rel(SCORER_PATH), "sha256": file_sha256(SCORER_PATH)},
        "output_dir": rel(output_dir),
        "failure_count": len(failures),
        "failures": failures[:50],
        "slices": slice_results,
        "claim_boundary": (
            "Verifies saved cassette outputs, deterministic scorer, checked-in score rows, "
            "and primary 7,200-row score CSV closure without live provider calls."
        ),
    }
    write_json(output_dir / "main_matrix_cassette_replay_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
