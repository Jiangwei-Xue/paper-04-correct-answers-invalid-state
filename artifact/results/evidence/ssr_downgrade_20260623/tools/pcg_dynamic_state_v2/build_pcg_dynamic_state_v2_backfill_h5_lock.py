#!/usr/bin/env python3
"""Build an H5-style lock for the 2026-06-23 targeted missing-row backfill."""

from __future__ import annotations

import csv
import hashlib
import json
import platform
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKFILL_ID = "pcg_dynamic_state_v2_targeted_missing_rows_backfill_20260623"
BACKFILL_RESULT_DIR = PROJECT_ROOT / "results" / BACKFILL_ID
CORE_LOCK_DIR = PROJECT_ROOT / "data" / "pcg_dynamic_state_v2" / "h5_release_lock_20260623"
OUT_DIR = PROJECT_ROOT / "data" / "pcg_dynamic_state_v2" / "h5_targeted_backfill_lock_20260623"
REDACTION_MAP = PROJECT_ROOT / "REDACTION_MAP.json"


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def sha256_json(value: Any) -> str:
    return sha256_bytes(canonical_json(value).encode("utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_redactions() -> dict[str, dict[str, Any]]:
    if not REDACTION_MAP.exists():
        return {}
    data = json.loads(REDACTION_MAP.read_text(encoding="utf-8"))
    return {item["path"]: item for item in data.get("redactions", [])}


REDACTIONS = load_redactions()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


def mtime_ns(path: Path) -> str:
    return str(path.stat().st_mtime_ns)


def artifact_row(
    artifact_id: str,
    artifact_type: str,
    path: Path,
    *,
    produced_by_run: str | None = None,
    consumed_by_runs: list[str] | None = None,
    notes: str = "",
) -> dict[str, Any]:
    redaction = REDACTIONS.get(rel(path))
    declared_sha = redaction.get("original_sha256") if redaction else file_sha256(path)
    return {
        "artifact_id": artifact_id,
        "artifact_type": artifact_type,
        "path": rel(path),
        "sha256": declared_sha,
        "canonical_sha256": None,
        "size_bytes": path.stat().st_size,
        "mtime_utc": mtime_ns(path),
        "created_utc": None,
        "git_commit": None,
        "produced_by_run": produced_by_run,
        "consumed_by_runs": consumed_by_runs or [],
        "parent_artifact_hashes": [],
        "child_artifact_hashes": [],
        "notes": notes,
    }


def key_for(row: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        str(row.get("task_id")),
        str(row.get("method")),
        str(row.get("budget", row.get("state_budget"))),
        str(row.get("run_id", row.get("run_index"))),
    )


def environment_lock(requirements: Path) -> dict[str, Any]:
    req_sha = file_sha256(requirements) if requirements.exists() else None
    system = platform.system() or "UnknownOS"
    machine = platform.machine() or "unknown-arch"
    lock_without_hash = {
        "schema_version": "pcg_dynamic_state_v2.backfill_h5_environment_lock.v1",
        "python_executable_name": Path(sys.executable).name,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
        "platform": f"{system}-{machine}",
        "machine": machine,
        "processor": None,
        "requirements_path": rel(requirements) if requirements.exists() else None,
        "requirements_sha256": req_sha,
        "secret_files_read": False,
        "model_api_called_by_lock_builder": False,
        "note": "Environment lock records local verifier environment. It is not a container image hash.",
    }
    return {**lock_without_hash, "environment_lock_sha256": sha256_json(lock_without_hash)}


def existing_core_lock_hash() -> str | None:
    summary = CORE_LOCK_DIR / "H5_LOCK_SUMMARY.json"
    return file_sha256(summary) if summary.exists() else None


def path_from_row(row: dict[str, Any], key: str) -> Path | None:
    value = row.get(key)
    if not value:
        return None
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    controlled_path = BACKFILL_RESULT_DIR / "BACKFILL_CONTROLLED_ROWS.jsonl"
    scores_path = BACKFILL_RESULT_DIR / "BACKFILL_SCORES.jsonl"
    scores_csv_path = BACKFILL_RESULT_DIR / "BACKFILL_SCORES.csv"
    required_backfill_files = [
        BACKFILL_RESULT_DIR / "BACKFILL_AUDIT.json",
        BACKFILL_RESULT_DIR / "BACKFILL_AUDIT.md",
        controlled_path,
        BACKFILL_RESULT_DIR / "BACKFILL_HASH_MANIFEST.jsonl",
        scores_path,
        scores_csv_path,
        BACKFILL_RESULT_DIR / "MISSINGNESS_SENSITIVITY_AUDIT.md",
        PROJECT_ROOT / "tools" / "pcg_dynamic_state_v2" / "backfill_pcg_dynamic_state_v2_missing_rows_20260623.py",
        Path(__file__),
        PROJECT_ROOT / "tools" / "pcg_dynamic_state_v2" / "verify_pcg_dynamic_state_v2_backfill_h5_lock.py",
    ]

    failures: list[dict[str, Any]] = []
    for path in required_backfill_files:
        if not path.exists():
            failures.append({"missing_required_file": rel(path)})

    if failures:
        print(json.dumps({"passed": False, "failures": failures}, ensure_ascii=False, indent=2))
        return 1

    env = environment_lock(PROJECT_ROOT / "requirements.txt")
    write_json(OUT_DIR / "ENVIRONMENT_LOCK.json", env)

    controlled_rows = read_jsonl(controlled_path)
    score_by_key = {key_for(row): row for row in read_jsonl(scores_path)}
    core_summary_sha = existing_core_lock_hash()

    artifact_rows: list[dict[str, Any]] = [
        artifact_row("environment_lock", "environment", OUT_DIR / "ENVIRONMENT_LOCK.json"),
    ]
    for path in required_backfill_files:
        artifact_rows.append(artifact_row(f"backfill::{rel(path)}", "manifest" if path.suffix in {".jsonl", ".json", ".md"} else "code", path, produced_by_run=BACKFILL_ID))

    if (CORE_LOCK_DIR / "H5_LOCK_SUMMARY.json").exists():
        artifact_rows.append(
            artifact_row(
                "parent_core_h5_lock_summary",
                "manifest",
                CORE_LOCK_DIR / "H5_LOCK_SUMMARY.json",
                notes="Parent core PCG v2 H5 lock summary. This addendum does not rewrite the parent lock.",
            )
        )

    seen_parent_files: set[Path] = set()
    row_manifest: list[dict[str, Any]] = []
    scores_with_hashes: list[dict[str, Any]] = []

    for row in controlled_rows:
        score_row = score_by_key.get(key_for(row))
        raw_path = path_from_row(row, "private_raw_ref")
        raw_exists = bool(raw_path and raw_path.exists())
        raw_byte_sha = file_sha256(raw_path) if raw_exists and raw_path else None

        config_path = path_from_row(row, "original_config_path")
        runner_path = path_from_row(row, "original_runner_path")
        scorer_path = path_from_row(row, "original_scorer_path")
        parent_paths = [
            ("config", config_path),
            ("runner", runner_path),
            ("scorer", scorer_path),
            ("raw_private_output", raw_path),
        ]
        for artifact_type, path in parent_paths:
            if path and path.exists() and path not in seen_parent_files:
                artifact_rows.append(
                    artifact_row(
                        f"{row.get('backfill_packet_id')}::{rel(path)}",
                        artifact_type,
                        path,
                        consumed_by_runs=[BACKFILL_ID] if artifact_type != "raw_private_output" else [],
                        produced_by_run=BACKFILL_ID if artifact_type == "raw_private_output" else None,
                    )
                )
                seen_parent_files.add(path)

        config_sha = file_sha256(config_path) if config_path and config_path.exists() else None
        runner_sha = file_sha256(runner_path) if runner_path and runner_path.exists() else None
        scorer_sha = file_sha256(scorer_path) if scorer_path and scorer_path.exists() else None
        score_row_sha = sha256_json(score_row) if score_row else None
        controlled_row_sha = sha256_json(row)

        missing = []
        for field in [
            "global_artifact_id",
            "config_sha256",
            "runner_sha256",
            "task_manifest_sha256",
            "scorer_oracle_sha256",
            "prompt_hash",
            "request_hash",
            "raw_response_sha256",
            "parsed_output_sha256",
            "metric_record_sha256",
            "manifest_entry_hash",
            "h5_chain_hash",
            "backfill_row_sha256",
            "backfill_runner_sha256",
        ]:
            if not row.get(field):
                missing.append(field)
        if not raw_exists:
            missing.append("raw_private_file_byte_hash")
        if not score_row:
            missing.append("score_row_join")
        if not config_sha:
            missing.append("config_file_byte_hash")
        if not runner_sha:
            missing.append("runner_file_byte_hash")
        if not scorer_sha:
            missing.append("scorer_file_byte_hash")

        parents = {
            "parent_core_h5_lock_summary_sha256": core_summary_sha,
            "dataset_hash": row.get("task_manifest_sha256"),
            "oracle_hash": row.get("scorer_oracle_sha256"),
            "prompt_hash": row.get("prompt_hash"),
            "request_hash": row.get("request_hash"),
            "config_hash_existing": row.get("config_sha256"),
            "config_file_byte_sha256": config_sha,
            "runner_hash_existing": row.get("runner_sha256"),
            "runner_file_byte_sha256": runner_sha,
            "scorer_file_byte_sha256": scorer_sha,
            "environment_lock_sha256": env["environment_lock_sha256"],
            "raw_response_canonical_sha256_existing": row.get("raw_response_sha256"),
            "raw_private_file_byte_sha256": raw_byte_sha,
            "parsed_output_sha256": row.get("parsed_output_sha256"),
            "metric_record_sha256": row.get("metric_record_sha256"),
            "score_row_canonical_sha256": score_row_sha,
            "controlled_row_canonical_sha256": controlled_row_sha,
            "backfill_row_sha256": row.get("backfill_row_sha256"),
            "backfill_runner_sha256": row.get("backfill_runner_sha256"),
        }
        release_row_without_hash = {
            "schema_version": "pcg_dynamic_state_v2.targeted_backfill_row_h5_lock.v1",
            "backfill_id": row.get("backfill_id", BACKFILL_ID),
            "packet_id": row.get("backfill_packet_id"),
            "packet_role": row.get("backfill_role"),
            "original_experiment_id": row.get("original_experiment_id"),
            "global_artifact_id": row.get("global_artifact_id"),
            "task_id": row.get("task_id"),
            "method": row.get("method"),
            "budget": row.get("budget", row.get("state_budget")),
            "run_id": row.get("run_id", row.get("run_index")),
            "provider": row.get("provider"),
            "requested_model": row.get("requested_model"),
            "selected_model_or_returned_model": row.get("selected_model_or_returned_model"),
            "gate_status": row.get("gate_status"),
            "gate_reason": row.get("gate_reason"),
            "answer_success": row.get("answer_success"),
            "state_governance_success": row.get("state_governance_success"),
            "reliable_composite_success": row.get("reliable_composite_success"),
            "existing_h5_chain_hash": row.get("h5_chain_hash"),
            "existing_manifest_entry_hash": row.get("manifest_entry_hash"),
            "effective_parser_sha256": scorer_sha,
            "effective_eval_harness_sha256": scorer_sha,
            "raw_private_ref": row.get("private_raw_ref"),
            "raw_private_file_present": raw_exists,
            "score_row_joined": score_row is not None,
            "config_file_hash_matches_row": config_sha == row.get("config_sha256"),
            "runner_file_hash_matches_row": runner_sha == row.get("runner_sha256"),
            "scorer_file_hash_present": scorer_sha is not None,
            "backfill_runner_hash_matches_row": file_sha256(required_backfill_files[7]) == row.get("backfill_runner_sha256"),
            "missing_core_fields": missing,
            "parent_hashes": parents,
        }
        release_row = {
            **release_row_without_hash,
            "release_row_h5_sha256": sha256_json(release_row_without_hash),
            "h5_status": "H5_PRIVATE_RAW_LOCK" if not missing else "H4_INCOMPLETE",
            "public_review_status": "anonymous_review_hash_locked_private_raw_not_public",
        }
        row_manifest.append(release_row)

        scores_with_hashes.append(
            {
                "backfill_id": BACKFILL_ID,
                "packet_id": release_row["packet_id"],
                "global_artifact_id": release_row["global_artifact_id"],
                "task_id": release_row["task_id"],
                "method": release_row["method"],
                "budget": release_row["budget"],
                "run_id": release_row["run_id"],
                "provider": release_row["provider"],
                "model": row.get("model", row.get("requested_model")),
                "answer_success": release_row["answer_success"],
                "state_governance_success": release_row["state_governance_success"],
                "reliable_composite_success": release_row["reliable_composite_success"],
                "release_row_h5_sha256": release_row["release_row_h5_sha256"],
                "h5_status": release_row["h5_status"],
            }
        )

    write_jsonl(OUT_DIR / "ROW_H5_MANIFEST.jsonl", row_manifest)
    artifact_rows.append(artifact_row("row_h5_manifest", "manifest", OUT_DIR / "ROW_H5_MANIFEST.jsonl"))

    scores_with_hashes_path = OUT_DIR / "backfill_scores_with_h5_hashes.csv"
    with scores_with_hashes_path.open("w", encoding="utf-8", newline="") as handle:
        if scores_with_hashes:
            writer = csv.DictWriter(handle, fieldnames=list(scores_with_hashes[0].keys()))
            writer.writeheader()
            writer.writerows(scores_with_hashes)
    artifact_rows.append(artifact_row("backfill_scores_with_h5_hashes", "metric", scores_with_hashes_path))

    write_jsonl(OUT_DIR / "ARTIFACT_HASH_MANIFEST.jsonl", artifact_rows)

    summary_without_hash = {
        "schema_version": "pcg_dynamic_state_v2.targeted_backfill_h5_lock_summary.v1",
        "lock_id": "pcg_dynamic_state_v2_targeted_missing_rows_backfill_h5_lock_20260623",
        "backfill_id": BACKFILL_ID,
        "scope": "Two targeted DeepSeek backfill rows that closed backend_or_empty_output gaps in the core PCG v2 downgrade evidence.",
        "row_count": len(row_manifest),
        "h5_private_raw_lock_rows": sum(1 for row in row_manifest if row["h5_status"] == "H5_PRIVATE_RAW_LOCK"),
        "h4_incomplete_rows": sum(1 for row in row_manifest if row["h5_status"] != "H5_PRIVATE_RAW_LOCK"),
        "artifact_manifest_path": rel(OUT_DIR / "ARTIFACT_HASH_MANIFEST.jsonl"),
        "row_manifest_path": rel(OUT_DIR / "ROW_H5_MANIFEST.jsonl"),
        "scores_with_hashes_path": rel(scores_with_hashes_path),
        "environment_lock_path": rel(OUT_DIR / "ENVIRONMENT_LOCK.json"),
        "environment_lock_sha256": env["environment_lock_sha256"],
        "parent_core_h5_lock_summary_sha256": core_summary_sha,
        "model_api_called_by_lock_builder": False,
        "model_api_called_by_backfill": True,
        "secret_files_read_by_lock_builder": False,
        "public_release_status": "ANON_REVIEW_READY_AS_HASH_LOCK_WITH_PRIVATE_RAW_REFS; raw release policy still required for public artifact release.",
        "failures": failures,
    }
    summary = {**summary_without_hash, "summary_sha256": sha256_json(summary_without_hash)}
    write_json(OUT_DIR / "H5_LOCK_SUMMARY.json", summary)

    artifact_rows.append(artifact_row("h5_lock_summary", "manifest", OUT_DIR / "H5_LOCK_SUMMARY.json"))
    write_jsonl(OUT_DIR / "ARTIFACT_HASH_MANIFEST.jsonl", artifact_rows)

    print(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2))
    return 1 if failures or summary["h4_incomplete_rows"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
