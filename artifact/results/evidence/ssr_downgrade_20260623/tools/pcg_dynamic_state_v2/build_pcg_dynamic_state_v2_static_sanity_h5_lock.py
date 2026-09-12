#!/usr/bin/env python3
"""Build an H5-style lock for the canonical static-sanity gate packet."""

from __future__ import annotations

import csv
import hashlib
import json
import platform
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT_ID = "pcg_dynamic_state_v2_static_sanity_deepseek_1task_4method_budget600_1run_20260623"
RESULT_DIR = PROJECT_ROOT / "results" / EXPERIMENT_ID
DATA_DIR = PROJECT_ROOT / "data" / "pcg_dynamic_state_v2" / EXPERIMENT_ID
OUT_DIR = PROJECT_ROOT / "data" / "pcg_dynamic_state_v2" / "h5_static_sanity_lock_20260623"
REDACTION_MAP = PROJECT_ROOT / "REDACTION_MAP.json"

CONFIG_PATH = PROJECT_ROOT / "configs" / f"{EXPERIMENT_ID}.json"
RUNNER_PATH = PROJECT_ROOT / "tools" / "run_deepseek_pcg_dynamic_state_v2_static_sanity_20260623.py"
RANDOM10_RUNNER = PROJECT_ROOT / "tools" / "run_deepseek_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622.py"
BASE_RUNNER = PROJECT_ROOT / "tools" / "run_ecvs_deepseek_pcg_dynamic_state_v2_e10_h3_decisive_4method_2budget_1run.py"
SCORER_PATH = PROJECT_ROOT / "tools" / "pcg_dynamic_state_v2" / "score_pcg_dynamic_state_v2_main_matrix.py"
VERIFY_PATH = PROJECT_ROOT / "tools" / "pcg_dynamic_state_v2" / "verify_pcg_dynamic_state_v2_static_sanity_h5_lock.py"


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


def artifact_row(artifact_id: str, artifact_type: str, path: Path, *, produced_by_run: str | None = None, consumed_by_runs: list[str] | None = None, notes: str = "") -> dict[str, Any]:
    redaction = REDACTIONS.get(rel(path))
    declared_sha = redaction.get("original_sha256") if redaction else file_sha256(path)
    return {
        "artifact_id": artifact_id,
        "artifact_type": artifact_type,
        "path": rel(path),
        "sha256": declared_sha,
        "canonical_sha256": None,
        "size_bytes": path.stat().st_size,
        "mtime_utc": str(path.stat().st_mtime_ns),
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
    material = {
        "schema_version": "pcg_dynamic_state_v2.static_sanity_h5_environment_lock.v1",
        "python_executable_name": Path(sys.executable).name,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
        "platform": f"{system}-{machine}",
        "machine": machine,
        "processor": None,
        "requirements_path": rel(requirements) if requirements.exists() else None,
        "requirements_sha256": req_sha,
        "secret_files_read": False,
        "model_api_called_by_lock_builder": False,
    }
    return {**material, "environment_lock_sha256": sha256_json(material)}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    controlled_path = RESULT_DIR / "CONTROLLED_ROWS.jsonl"
    scores_path = RESULT_DIR / "scores.jsonl"
    scores_csv_path = RESULT_DIR / "scores.csv"
    required = [
        DATA_DIR / "MODEL_VISIBLE_TASK_MANIFEST.jsonl",
        DATA_DIR / "SCORER_ORACLE_MANIFEST.jsonl",
        DATA_DIR / "TASK_PROVENANCE_MANIFEST.jsonl",
        DATA_DIR / "TASK_SELECTION.csv",
        DATA_DIR / "TASK_SPLIT_AUDIT.json",
        CONFIG_PATH,
        RESULT_DIR / "RUN_PLAN.md",
        RESULT_DIR / "PREFLIGHT_AUDIT.json",
        RESULT_DIR / "PREFLIGHT_AUDIT.md",
        RESULT_DIR / "PREFLIGHT_HASH_MANIFEST.jsonl",
        controlled_path,
        scores_path,
        scores_csv_path,
        RESULT_DIR / "POST_RUN_AUDIT.md",
        RESULT_DIR / "STATIC_SANITY_GATE_REPORT.md",
        RESULT_DIR / "STATIC_SANITY_SUMMARY.json",
        RUNNER_PATH,
        RANDOM10_RUNNER,
        BASE_RUNNER,
        SCORER_PATH,
        Path(__file__),
        VERIFY_PATH,
    ]
    failures = [{"missing_required_file": rel(path)} for path in required if not path.exists()]
    if failures:
        print(json.dumps({"passed": False, "failures": failures}, ensure_ascii=False, indent=2))
        return 1

    env = environment_lock(PROJECT_ROOT / "requirements.txt")
    write_json(OUT_DIR / "ENVIRONMENT_LOCK.json", env)

    artifact_rows = [artifact_row("environment_lock", "environment", OUT_DIR / "ENVIRONMENT_LOCK.json")]
    for path in required:
        artifact_type = "code" if "/tools/" in "/" + rel(path) else "manifest"
        if path in {controlled_path, scores_path, scores_csv_path, RESULT_DIR / "POST_RUN_AUDIT.md", RESULT_DIR / "STATIC_SANITY_GATE_REPORT.md", RESULT_DIR / "STATIC_SANITY_SUMMARY.json"}:
            artifact_type = "metric" if path.name.startswith("score") or path.name == "STATIC_SANITY_SUMMARY.json" else "run_log"
        artifact_rows.append(artifact_row(f"static_sanity::{rel(path)}", artifact_type, path, produced_by_run=EXPERIMENT_ID if artifact_type in {"metric", "run_log", "manifest"} else None))

    controlled_rows = read_jsonl(controlled_path)
    score_by_key = {key_for(row): row for row in read_jsonl(scores_path)}
    row_manifest: list[dict[str, Any]] = []
    scores_with_hashes: list[dict[str, Any]] = []
    seen_raw: set[Path] = set()

    config_sha = file_sha256(CONFIG_PATH)
    runner_sha = file_sha256(RUNNER_PATH)
    random_runner_sha = file_sha256(RANDOM10_RUNNER)
    base_runner_sha = file_sha256(BASE_RUNNER)
    scorer_sha = file_sha256(SCORER_PATH)
    visible_sha = file_sha256(DATA_DIR / "MODEL_VISIBLE_TASK_MANIFEST.jsonl")
    oracle_sha = file_sha256(DATA_DIR / "SCORER_ORACLE_MANIFEST.jsonl")

    for row in controlled_rows:
        score_row = score_by_key.get(key_for(row))
        raw_ref = row.get("private_raw_ref")
        raw_path = PROJECT_ROOT / raw_ref if raw_ref else None
        raw_exists = bool(raw_path and raw_path.exists())
        raw_sha = file_sha256(raw_path) if raw_path and raw_exists else None
        if raw_path and raw_exists and raw_path not in seen_raw:
            artifact_rows.append(artifact_row(f"static_sanity_raw::{rel(raw_path)}", "raw_output", raw_path, produced_by_run=EXPERIMENT_ID))
            seen_raw.add(raw_path)

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
        ]:
            if not row.get(field):
                missing.append(field)
        if not raw_exists:
            missing.append("raw_private_file_byte_hash")
        if not score_row:
            missing.append("score_row_join")

        parents = {
            "dataset_hash": row.get("task_manifest_sha256"),
            "dataset_file_byte_sha256": visible_sha,
            "oracle_hash": row.get("scorer_oracle_sha256"),
            "oracle_file_byte_sha256": oracle_sha,
            "prompt_hash": row.get("prompt_hash"),
            "request_hash": row.get("request_hash"),
            "config_hash_existing": row.get("config_sha256"),
            "config_file_byte_sha256": config_sha,
            "runner_hash_existing": row.get("runner_sha256"),
            "runner_file_byte_sha256": runner_sha,
            "random10_runner_file_byte_sha256": random_runner_sha,
            "base_runner_file_byte_sha256": base_runner_sha,
            "scorer_file_byte_sha256": scorer_sha,
            "environment_lock_sha256": env["environment_lock_sha256"],
            "raw_response_canonical_sha256_existing": row.get("raw_response_sha256"),
            "raw_private_file_byte_sha256": raw_sha,
            "parsed_output_sha256": row.get("parsed_output_sha256"),
            "metric_record_sha256": row.get("metric_record_sha256"),
            "score_row_canonical_sha256": sha256_json(score_row) if score_row else None,
            "controlled_row_canonical_sha256": sha256_json(row),
        }
        release_without_hash = {
            "schema_version": "pcg_dynamic_state_v2.static_sanity_row_h5_lock.v1",
            "experiment_id": EXPERIMENT_ID,
            "packet_role": "canonical_static_sanity_gate",
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
            "raw_private_ref": raw_ref,
            "raw_private_file_present": raw_exists,
            "score_row_joined": score_row is not None,
            "config_file_hash_matches_row": config_sha == row.get("config_sha256"),
            "runner_file_hash_matches_row": runner_sha == row.get("runner_sha256"),
            "task_manifest_hash_matches_row": visible_sha == row.get("task_manifest_sha256"),
            "oracle_hash_matches_row": oracle_sha == row.get("scorer_oracle_sha256"),
            "effective_eval_harness_sha256": scorer_sha,
            "missing_core_fields": missing,
            "parent_hashes": parents,
        }
        release_row = {
            **release_without_hash,
            "release_row_h5_sha256": sha256_json(release_without_hash),
            "h5_status": "H5_PRIVATE_RAW_LOCK" if not missing else "H4_INCOMPLETE",
            "public_review_status": "anonymous_review_hash_locked_private_raw_not_public",
        }
        row_manifest.append(release_row)
        scores_with_hashes.append(
            {
                "experiment_id": EXPERIMENT_ID,
                "global_artifact_id": row.get("global_artifact_id"),
                "task_id": row.get("task_id"),
                "method": row.get("method"),
                "budget": row.get("budget", row.get("state_budget")),
                "run_id": row.get("run_id", row.get("run_index")),
                "answer_success": row.get("answer_success"),
                "state_governance_success": row.get("state_governance_success"),
                "reliable_composite_success": row.get("reliable_composite_success"),
                "release_row_h5_sha256": release_row["release_row_h5_sha256"],
                "h5_status": release_row["h5_status"],
            }
        )

    write_jsonl(OUT_DIR / "ROW_H5_MANIFEST.jsonl", row_manifest)
    artifact_rows.append(artifact_row("row_h5_manifest", "manifest", OUT_DIR / "ROW_H5_MANIFEST.jsonl"))

    scores_with_hashes_path = OUT_DIR / "static_sanity_scores_with_h5_hashes.csv"
    with scores_with_hashes_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(scores_with_hashes[0].keys()))
        writer.writeheader()
        writer.writerows(scores_with_hashes)
    artifact_rows.append(artifact_row("static_sanity_scores_with_h5_hashes", "metric", scores_with_hashes_path))

    write_jsonl(OUT_DIR / "ARTIFACT_HASH_MANIFEST.jsonl", artifact_rows)
    summary_without_hash = {
        "schema_version": "pcg_dynamic_state_v2.static_sanity_h5_lock_summary.v1",
        "lock_id": "pcg_dynamic_state_v2_static_sanity_h5_lock_20260623",
        "experiment_id": EXPERIMENT_ID,
        "scope": "Canonical one-task static-sanity gate for the 2026-06-22 PCG v2 mature_ssr_loop runner.",
        "row_count": len(row_manifest),
        "h5_private_raw_lock_rows": sum(1 for row in row_manifest if row["h5_status"] == "H5_PRIVATE_RAW_LOCK"),
        "h4_incomplete_rows": sum(1 for row in row_manifest if row["h5_status"] != "H5_PRIVATE_RAW_LOCK"),
        "artifact_manifest_path": rel(OUT_DIR / "ARTIFACT_HASH_MANIFEST.jsonl"),
        "row_manifest_path": rel(OUT_DIR / "ROW_H5_MANIFEST.jsonl"),
        "scores_with_hashes_path": rel(scores_with_hashes_path),
        "environment_lock_path": rel(OUT_DIR / "ENVIRONMENT_LOCK.json"),
        "environment_lock_sha256": env["environment_lock_sha256"],
        "model_api_called_by_lock_builder": False,
        "model_api_called_by_static_sanity_runner": True,
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
