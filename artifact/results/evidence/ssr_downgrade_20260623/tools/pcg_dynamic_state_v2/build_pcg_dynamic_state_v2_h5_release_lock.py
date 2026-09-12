#!/usr/bin/env python3
"""Build an H5-style release lock for core PCG dynamic-state v2 evidence.

This script does not call model APIs and does not read secret files. It hashes
existing controlled rows, score rows, configs, runners, scorer code, task
manifests, and private raw-output files referenced by result rows.
"""

from __future__ import annotations

import csv
import hashlib
import json
import platform
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = PROJECT_ROOT / "data" / "pcg_dynamic_state_v2" / "h5_release_lock_20260623"
REDACTION_MAP = PROJECT_ROOT / "REDACTION_MAP.json"

CORE_PACKETS = [
    {
        "packet_id": "deepseek_decisive_104",
        "role": "method_triage_decisive_probe",
        "result_dir": PROJECT_ROOT
        / "results"
        / "_probe_ecvs_deepseek_v4pro_pcg_dynamic_state_v2_e10_h3_decisive_13task_4method_2budget_1run",
        "config": PROJECT_ROOT
        / "configs"
        / "_probe_ecvs_deepseek_v4pro_pcg_dynamic_state_v2_e10_h3_decisive_13task_4method_2budget_1run.json",
        "runner": PROJECT_ROOT / "tools" / "run_ecvs_deepseek_pcg_dynamic_state_v2_e10_h3_decisive_4method_2budget_1run.py",
        "scorer": PROJECT_ROOT / "tools" / "pcg_dynamic_state_v2" / "score_pcg_dynamic_state_v2_outputs.py",
    },
    {
        "packet_id": "deepseek_random10_rerun100",
        "role": "direct_provider_random10_probe",
        "result_dir": PROJECT_ROOT
        / "results"
        / "_probe_deepseek_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_rerun100",
        "config": PROJECT_ROOT
        / "configs"
        / "_probe_deepseek_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_rerun100.json",
        "runner": PROJECT_ROOT / "tools" / "run_deepseek_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622.py",
        "scorer": PROJECT_ROOT / "tools" / "pcg_dynamic_state_v2" / "score_pcg_dynamic_state_v2_main_matrix.py",
    },
    {
        "packet_id": "qwen_random10",
        "role": "direct_provider_random10_probe",
        "result_dir": PROJECT_ROOT
        / "results"
        / "_probe_qwen37max_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_50workers",
        "config": PROJECT_ROOT
        / "configs"
        / "_probe_qwen37max_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_50workers.json",
        "runner": PROJECT_ROOT / "tools" / "run_qwen37max_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622.py",
        "scorer": PROJECT_ROOT / "tools" / "pcg_dynamic_state_v2" / "score_pcg_dynamic_state_v2_main_matrix.py",
    },
    {
        "packet_id": "kimi_random10",
        "role": "direct_provider_random10_probe",
        "result_dir": PROJECT_ROOT
        / "results"
        / "_probe_kimi_k26_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_50workers",
        "config": PROJECT_ROOT
        / "configs"
        / "_probe_kimi_k26_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_50workers.json",
        "runner": PROJECT_ROOT / "tools" / "run_kimi_k26_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622.py",
        "scorer": PROJECT_ROOT / "tools" / "pcg_dynamic_state_v2" / "score_pcg_dynamic_state_v2_main_matrix.py",
    },
]

COMMON_ARTIFACTS = [
    PROJECT_ROOT / "data" / "pcg_dynamic_state_v2" / "main_matrix_v1" / "MODEL_VISIBLE_TASK_MANIFEST.jsonl",
    PROJECT_ROOT / "data" / "pcg_dynamic_state_v2" / "main_matrix_v1" / "SCORER_ORACLE_MANIFEST.jsonl",
    PROJECT_ROOT / "data" / "pcg_dynamic_state_v2" / "main_matrix_v1" / "TASK_PROVENANCE_MANIFEST.jsonl",
    PROJECT_ROOT / "tools" / "pcg_dynamic_state_v2" / "score_pcg_dynamic_state_v2_outputs.py",
    PROJECT_ROOT / "tools" / "pcg_dynamic_state_v2" / "score_pcg_dynamic_state_v2_main_matrix.py",
    Path(__file__),
    PROJECT_ROOT / "tools" / "pcg_dynamic_state_v2" / "verify_pcg_dynamic_state_v2_h5_release_lock.py",
]


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


def mtime_utc(path: Path) -> str:
    return path.stat().st_mtime_ns.__str__()


def artifact_row(
    artifact_id: str,
    artifact_type: str,
    path: Path,
    *,
    produced_by_run: str | None = None,
    consumed_by_runs: list[str] | None = None,
    parent_artifact_hashes: list[str] | None = None,
    child_artifact_hashes: list[str] | None = None,
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
        "mtime_utc": mtime_utc(path),
        "created_utc": None,
        "git_commit": None,
        "produced_by_run": produced_by_run,
        "consumed_by_runs": consumed_by_runs or [],
        "parent_artifact_hashes": parent_artifact_hashes or [],
        "child_artifact_hashes": child_artifact_hashes or [],
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
        "schema_version": "pcg_dynamic_state_v2.h5_environment_lock.v1",
        "python_executable_name": Path(sys.executable).name,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
        "platform": f"{system}-{machine}",
        "machine": machine,
        "processor": None,
        "requirements_path": rel(requirements) if requirements.exists() else None,
        "requirements_sha256": req_sha,
        "secret_files_read": False,
        "model_api_called": False,
        "note": "Environment lock records local verifier environment. It is not a container image hash.",
    }
    return {**lock_without_hash, "environment_lock_sha256": sha256_json(lock_without_hash)}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    env = environment_lock(PROJECT_ROOT / "requirements.txt")

    artifact_rows: list[dict[str, Any]] = []
    row_manifest: list[dict[str, Any]] = []
    scores_with_hashes: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    write_json(OUT_DIR / "ENVIRONMENT_LOCK.json", env)
    artifact_rows.append(
        artifact_row(
            "environment_lock",
            "environment",
            OUT_DIR / "ENVIRONMENT_LOCK.json",
            notes="Local environment lock for H5 verifier; no secrets read.",
        )
    )

    common_seen: set[Path] = set()
    for path in COMMON_ARTIFACTS:
        if path.exists() and path not in common_seen:
            artifact_rows.append(artifact_row(f"common::{rel(path)}", "code" if "tools/" in rel(path) else "dataset", path))
            common_seen.add(path)

    for packet in CORE_PACKETS:
        result_dir = packet["result_dir"]
        controlled_path = result_dir / "CONTROLLED_ROWS.jsonl"
        scores_path = result_dir / "scores.jsonl"
        scores_csv_path = result_dir / "scores.csv"
        preflight_manifest_path = result_dir / "PREFLIGHT_HASH_MANIFEST.jsonl"
        post_run_audit_path = result_dir / "POST_RUN_AUDIT.md"

        required_paths = [
            controlled_path,
            scores_path,
            scores_csv_path,
            preflight_manifest_path,
            post_run_audit_path,
            packet["config"],
            packet["runner"],
            packet["scorer"],
        ]
        for path in required_paths:
            if not path.exists():
                failures.append({"packet_id": packet["packet_id"], "missing_required_file": rel(path)})
                continue

        packet_run_id = result_dir.name
        for path, artifact_type in [
            (controlled_path, "run_log"),
            (scores_path, "metric"),
            (scores_csv_path, "metric"),
            (preflight_manifest_path, "manifest"),
            (post_run_audit_path, "run_log"),
            (packet["config"], "config"),
            (packet["runner"], "code"),
            (packet["scorer"], "eval_harness"),
        ]:
            if path.exists():
                artifact_rows.append(
                    artifact_row(
                        f"{packet['packet_id']}::{rel(path)}",
                        artifact_type,
                        path,
                        produced_by_run=packet_run_id if artifact_type in {"run_log", "metric", "manifest"} else None,
                        consumed_by_runs=[packet_run_id] if artifact_type in {"config", "code", "eval_harness"} else [],
                    )
                )

        if not controlled_path.exists() or not scores_path.exists():
            continue

        controlled_rows = read_jsonl(controlled_path)
        score_by_key = {key_for(row): row for row in read_jsonl(scores_path)}
        config_file_sha = file_sha256(packet["config"]) if packet["config"].exists() else None
        runner_file_sha = file_sha256(packet["runner"]) if packet["runner"].exists() else None
        scorer_file_sha = file_sha256(packet["scorer"]) if packet["scorer"].exists() else None

        for row in controlled_rows:
            score_row = score_by_key.get(key_for(row))
            raw_ref = row.get("private_raw_ref")
            raw_path = PROJECT_ROOT / raw_ref if raw_ref else None
            raw_exists = bool(raw_path and raw_path.exists())
            raw_byte_sha = file_sha256(raw_path) if raw_exists and raw_path else None
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
            ]:
                if not row.get(field):
                    missing.append(field)
            if not raw_exists:
                missing.append("raw_private_file_byte_hash")
            if not score_row:
                missing.append("score_row_join")

            parents = {
                "dataset_hash": row.get("task_manifest_sha256"),
                "oracle_hash": row.get("scorer_oracle_sha256"),
                "prompt_hash": row.get("prompt_hash"),
                "request_hash": row.get("request_hash"),
                "config_hash_existing": row.get("config_sha256"),
                "config_file_byte_sha256": config_file_sha,
                "runner_hash_existing": row.get("runner_sha256"),
                "runner_file_byte_sha256": runner_file_sha,
                "scorer_file_byte_sha256": scorer_file_sha,
                "environment_lock_sha256": env["environment_lock_sha256"],
                "raw_response_canonical_sha256_existing": row.get("raw_response_sha256"),
                "raw_private_file_byte_sha256": raw_byte_sha,
                "parsed_output_sha256": row.get("parsed_output_sha256"),
                "metric_record_sha256": row.get("metric_record_sha256"),
                "score_row_canonical_sha256": score_row_sha,
                "controlled_row_canonical_sha256": controlled_row_sha,
            }
            release_row_without_hash = {
                "schema_version": "pcg_dynamic_state_v2.row_h5_lock.v1",
                "packet_id": packet["packet_id"],
                "packet_role": packet["role"],
                "global_artifact_id": row.get("global_artifact_id"),
                "experiment_id": row.get("experiment_id", packet_run_id),
                "task_id": row.get("task_id"),
                "method": row.get("method"),
                "budget": row.get("budget", row.get("state_budget")),
                "run_id": row.get("run_id", row.get("run_index")),
                "provider": row.get("provider"),
                "requested_model": row.get("requested_model"),
                "selected_model_or_returned_model": row.get("selected_model_or_returned_model"),
                "gate_status": row.get("gate_status"),
                "gate_reason": row.get("gate_reason"),
                "existing_h5_chain_hash": row.get("h5_chain_hash"),
                "existing_manifest_entry_hash": row.get("manifest_entry_hash"),
                "effective_parser_sha256": scorer_file_sha,
                "effective_eval_harness_sha256": scorer_file_sha,
                "raw_private_ref": raw_ref,
                "raw_private_file_present": raw_exists,
                "score_row_joined": score_row is not None,
                "config_file_hash_matches_row": config_file_sha == row.get("config_sha256"),
                "runner_file_hash_matches_row": runner_file_sha == row.get("runner_sha256"),
                "missing_core_fields": missing,
                "parent_hashes": parents,
            }
            release_row = {
                **release_row_without_hash,
                "release_row_h5_sha256": sha256_json(release_row_without_hash),
                "h5_status": "H5_PRIVATE_RAW_LOCK" if not missing else "H4_INCOMPLETE",
                "public_review_status": "needs_public_raw_or_raw_commitment_policy",
            }
            row_manifest.append(release_row)

            scores_with_hashes.append(
                {
                    "packet_id": packet["packet_id"],
                    "global_artifact_id": row.get("global_artifact_id"),
                    "task_id": row.get("task_id"),
                    "method": row.get("method"),
                    "budget": row.get("budget", row.get("state_budget")),
                    "run_id": row.get("run_id", row.get("run_index")),
                    "provider": row.get("provider"),
                    "model": row.get("model", row.get("requested_model")),
                    "answer_success": row.get("answer_success"),
                    "state_governance_success": row.get("state_governance_success"),
                    "reliable_composite_success": row.get("reliable_composite_success"),
                    "existing_h5_chain_hash": row.get("h5_chain_hash"),
                    "release_row_h5_sha256": release_row["release_row_h5_sha256"],
                    "h5_status": release_row["h5_status"],
                }
            )

    write_jsonl(OUT_DIR / "ROW_H5_MANIFEST.jsonl", row_manifest)
    artifact_rows.append(
        artifact_row("row_h5_manifest", "manifest", OUT_DIR / "ROW_H5_MANIFEST.jsonl", notes="Per-row H5 release lock manifest.")
    )

    scores_csv = OUT_DIR / "scores_with_h5_hashes.csv"
    with scores_csv.open("w", encoding="utf-8", newline="") as handle:
        if scores_with_hashes:
            writer = csv.DictWriter(handle, fieldnames=list(scores_with_hashes[0].keys()))
            writer.writeheader()
            writer.writerows(scores_with_hashes)
    artifact_rows.append(artifact_row("scores_with_h5_hashes", "metric", scores_csv))

    write_jsonl(OUT_DIR / "ARTIFACT_HASH_MANIFEST.jsonl", artifact_rows)

    summary_without_hash = {
        "schema_version": "pcg_dynamic_state_v2.h5_release_lock_summary.v1",
        "lock_id": "pcg_dynamic_state_v2_core_ssr_downgrade_h5_lock_20260623",
        "scope": "Core non-Claude/GPT SSR-downgrade evidence: DeepSeek decisive, DeepSeek random10, Qwen random10, Kimi random10.",
        "row_count": len(row_manifest),
        "h5_private_raw_lock_rows": sum(1 for row in row_manifest if row["h5_status"] == "H5_PRIVATE_RAW_LOCK"),
        "h4_incomplete_rows": sum(1 for row in row_manifest if row["h5_status"] != "H5_PRIVATE_RAW_LOCK"),
        "artifact_manifest_path": rel(OUT_DIR / "ARTIFACT_HASH_MANIFEST.jsonl"),
        "row_manifest_path": rel(OUT_DIR / "ROW_H5_MANIFEST.jsonl"),
        "scores_with_hashes_path": rel(scores_csv),
        "environment_lock_path": rel(OUT_DIR / "ENVIRONMENT_LOCK.json"),
        "environment_lock_sha256": env["environment_lock_sha256"],
        "model_api_called": False,
        "secret_files_read": False,
        "public_release_status": "NOT_PUBLIC_READY_UNTIL_RAW_POLICY_AND_ANONYMIZED_RELEASE_REPO",
        "failures": failures,
    }
    summary = {**summary_without_hash, "summary_sha256": sha256_json(summary_without_hash)}
    write_json(OUT_DIR / "H5_LOCK_SUMMARY.json", summary)

    # Re-hash manifests after summary is written and include the summary itself.
    artifact_rows.append(artifact_row("h5_lock_summary", "manifest", OUT_DIR / "H5_LOCK_SUMMARY.json"))
    write_jsonl(OUT_DIR / "ARTIFACT_HASH_MANIFEST.jsonl", artifact_rows)

    print(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2))
    return 1 if failures or summary["h4_incomplete_rows"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
