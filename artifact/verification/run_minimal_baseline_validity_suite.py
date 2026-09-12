#!/usr/bin/env python3
"""Generate and verify a deterministic minimal baseline validity suite.

The suite is a diagnostic scale reference for the PCG dynamic-state v2 primary
matrix. It does not call model APIs. It reuses the frozen 7,200-row primary
manifest, generates local policy outputs, runs the strict deterministic scorer,
and writes an H5-style hash manifest that links source manifests, generated
outputs, and metrics.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import platform
import random
import re
import shutil
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2]
DEFAULT_OUTPUT_DIR = ROOT / "artifact" / "results" / "baselines" / "minimal_validity_suite_20260706"
DEFAULT_BUILD_DIR = ROOT / ".verification_build" / "minimal_baseline_validity_suite"
ROW_MANIFEST = (
    ROOT
    / "artifact"
    / "protocol"
    / "main_matrix"
    / "configs"
    / "pcg_dynamic_state_v2_confirmatory_40task_5model_6method_2budget_3run_20260625.rows.jsonl"
)
VISIBLE_TASK_MANIFEST = (
    ROOT
    / "artifact"
    / "results"
    / "evidence"
    / "ssr_downgrade_20260623"
    / "data"
    / "pcg_dynamic_state_v2"
    / "main_matrix_v1"
    / "MODEL_VISIBLE_TASK_MANIFEST.jsonl"
)
ORACLE_MANIFEST = (
    ROOT
    / "artifact"
    / "results"
    / "evidence"
    / "ssr_downgrade_20260623"
    / "data"
    / "pcg_dynamic_state_v2"
    / "main_matrix_v1"
    / "SCORER_ORACLE_MANIFEST.jsonl"
)
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

POLICIES = [
    {
        "policy_id": "random_visible_v1",
        "policy_kind": "visible_only",
        "description": "Randomly samples visible candidate tokens and visible paths.",
        "oracle_access_for_generation": False,
    },
    {
        "policy_id": "copy_initial_visible_v1",
        "policy_kind": "visible_only",
        "description": "Copies the initially active token set and initially allowed paths.",
        "oracle_access_for_generation": False,
    },
    {
        "policy_id": "carry_all_visible_v1",
        "policy_kind": "visible_only",
        "description": "Carries every visible candidate token and path.",
        "oracle_access_for_generation": False,
    },
    {
        "policy_id": "rule_visible_transition_v1",
        "policy_kind": "visible_only",
        "description": "Applies simple visible-text status rules to active and excluded candidates.",
        "oracle_access_for_generation": False,
    },
    {
        "policy_id": "oracle_ceiling_control_v1",
        "policy_kind": "oracle_upper_control",
        "description": "Uses the scorer oracle to confirm the deterministic scorer ceiling.",
        "oracle_access_for_generation": True,
    },
]

TOKEN_RE = re.compile(r"\b(?:REQ|CFG|API|MOD|PATH|FEATURE|FLAG|RULE|PATCH|HOOK|JOB|CHECK)_[0-9]{2}_[A-Z0-9]{6}\b")
PATH_RE = re.compile(r"\bsrc/[A-Za-z0-9_./-]+(?:\.py|\.yaml|\.json|\.md)\b")
INITIAL_ACTIVE_RE = re.compile(r"Initial active tokens:\s*([^\.]+)\.", re.I)
INITIAL_ALLOWED_RE = re.compile(r"Allowed path candidates currently include\s+([^\.]+?\.(?:py|yaml|json|md))", re.I)

def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_json(value: Any) -> str:
    return sha256_text(canonical_json(value))


def file_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            row["_line_number"] = line_number
            row["_line_sha256"] = sha256_text(line.rstrip("\n"))
            rows.append(row)
    return rows


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(canonical_json(row) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    keys: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                keys.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            out.append(value)
    return out


def visible_text(task: dict[str, Any]) -> str:
    return "\n".join(str(segment.get("text", "")) for segment in task.get("segments", []))


def visible_tokens(task: dict[str, Any]) -> list[str]:
    return unique(TOKEN_RE.findall(visible_text(task)))


def visible_paths(task: dict[str, Any]) -> list[str]:
    return unique(PATH_RE.findall(visible_text(task)))


def parse_initial_active(task: dict[str, Any]) -> list[str]:
    match = INITIAL_ACTIVE_RE.search(visible_text(task))
    if not match:
        return []
    return unique(TOKEN_RE.findall(match.group(1)))


def parse_initial_allowed_paths(task: dict[str, Any]) -> list[str]:
    return unique(match.group(1) for match in INITIAL_ALLOWED_RE.finditer(visible_text(task)))


def visible_status_map(task: dict[str, Any]) -> dict[str, str]:
    text = visible_text(task)
    status = {token: "candidate" for token in visible_tokens(task)}
    for token in parse_initial_active(task):
        status[token] = "active"
    for token in list(status):
        contexts = " ".join(sentence for sentence in re.split(r"(?<=[.])\s+", text) if token in sentence)
        low = contexts.lower()
        if "revoked" in low:
            status[token] = "revoked"
        elif "stale" in low or "superseded" in low or "deprecated" in low:
            status[token] = "stale"
        elif "forbidden" in low:
            status[token] = "forbidden"
        elif "protected" in low or "private" in low:
            status[token] = "protected"
        elif "archive log re-mentions" in low or "historical fix" in low:
            status[token] = "revoked"
        elif "error trace re-mentions" in low:
            status[token] = "forbidden"
        elif "rollback-only" in low or "rollback only" in low:
            status[token] = "rollback_only"
        elif "archive-only" in low or "archive only" in low:
            status[token] = "archive_only"
        elif "decoy" in low:
            status[token] = "decoy"
        elif "blocked" in low:
            status[token] = "blocked"
        if re.search(rf"{re.escape(token)}\s+(?:is|becomes|became)\s+(?:now\s+)?active\b", contexts, flags=re.I):
            status[token] = "active"
    return status


def state_labels_from_status(status: dict[str, str]) -> dict[str, str]:
    mapping = {
        "active": "active",
        "candidate": "decoy",
        "revoked": "revoked",
        "stale": "stale",
        "forbidden": "forbidden",
        "protected": "protected",
        "rollback_only": "rollback_only",
        "archive_only": "archive_only",
        "decoy": "decoy",
        "blocked": "blocked",
    }
    return {token: mapping.get(label, "decoy") for token, label in status.items()}


def answer_payload(required_tokens: list[str], allowed_paths: list[str], state_labels: dict[str, str] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "final_answer": {
            "required_tokens": required_tokens,
            "allowed_paths": allowed_paths,
            "boundary_checks": {
                "baseline_policy_generated": True,
            },
        }
    }
    if state_labels:
        payload["final_answer"]["state_labels"] = state_labels
    return payload


def state_surface(required_tokens: list[str], allowed_paths: list[str], excluded_tokens: list[str] | None = None) -> str:
    surface: dict[str, Any] = {
        "ACTIVE": required_tokens,
        "ALW": allowed_paths,
    }
    if excluded_tokens is not None:
        surface["NO"] = excluded_tokens
    return json.dumps(surface, ensure_ascii=False, sort_keys=True)


def random_policy(task: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    tokens = visible_tokens(task)
    paths = visible_paths(task)
    k = len(parse_initial_active(task)) or min(2, len(tokens))
    seed = int(hashlib.sha256(f"random_visible_v1|{row['row_id']}|20260706".encode("utf-8")).hexdigest()[:16], 16)
    rng = random.Random(seed)
    sampled_tokens = sorted(rng.sample(tokens, k=min(k, len(tokens)))) if tokens else []
    sampled_paths = sorted(rng.sample(paths, k=1)) if paths else []
    return {
        "final_output": answer_payload(sampled_tokens, sampled_paths),
        "final_state": state_surface(sampled_tokens, sampled_paths),
        "policy_trace": {
            "seed": seed,
            "visible_token_count": len(tokens),
            "visible_path_count": len(paths),
            "sampled_token_count": len(sampled_tokens),
        },
    }


def copy_initial_policy(task: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    tokens = parse_initial_active(task)
    paths = parse_initial_allowed_paths(task)
    return {
        "final_output": answer_payload(tokens, paths),
        "final_state": state_surface(tokens, paths),
        "policy_trace": {
            "initial_active_count": len(tokens),
            "initial_allowed_path_count": len(paths),
        },
    }


def carry_all_visible_policy(task: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    tokens = visible_tokens(task)
    paths = visible_paths(task)
    return {
        "final_output": answer_payload(tokens, paths),
        "final_state": json.dumps({"CARRY_ALL": tokens + paths}, ensure_ascii=False, sort_keys=True),
        "policy_trace": {
            "visible_token_count": len(tokens),
            "visible_path_count": len(paths),
        },
    }


def rule_visible_transition_policy(task: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    status = visible_status_map(task)
    active = [token for token, label in status.items() if label == "active"]
    excluded = [token for token, label in status.items() if label != "active"]
    paths = parse_initial_allowed_paths(task)
    return {
        "final_output": answer_payload(active, paths),
        "final_state": state_surface(active, paths, excluded),
        "policy_trace": {
            "state_labels_suppressed_for_answer_surface": True,
            "visible_status_labels": state_labels_from_status(status),
            "visible_status_counts": dict(sorted(counts(status.values()).items())),
            "active_count": len(active),
            "excluded_count": len(excluded),
            "initial_allowed_path_count": len(paths),
        },
    }


def oracle_ceiling_policy(task: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    oracle = task["oracle"]
    required = list(oracle["required_exact_tokens"])
    allowed_paths = list(oracle["allowed_paths"])
    excluded = list(oracle["final_excluded_set"])
    return {
        "final_output": answer_payload(required, allowed_paths, dict(oracle["expected_state_labels"])),
        "final_state": state_surface(required, allowed_paths, excluded),
        "policy_trace": {
            "oracle_required_count": len(required),
            "oracle_excluded_count": len(excluded),
            "oracle_allowed_path_count": len(allowed_paths),
        },
    }


def counts(values: Any) -> dict[str, int]:
    result: dict[str, int] = defaultdict(int)
    for value in values:
        result[str(value)] += 1
    return dict(result)


POLICY_FUNCTIONS = {
    "random_visible_v1": random_policy,
    "copy_initial_visible_v1": copy_initial_policy,
    "carry_all_visible_v1": carry_all_visible_policy,
    "rule_visible_transition_v1": rule_visible_transition_policy,
    "oracle_ceiling_control_v1": oracle_ceiling_policy,
}


def build_config(run_started_at_utc: str) -> dict[str, Any]:
    return {
        "schema_version": "pcg_dynamic_state_v2.minimal_baseline_validity_suite.config.v1",
        "suite_id": "minimal_baseline_validity_suite_20260706",
        "run_started_at_utc": run_started_at_utc,
        "api_calls_performed": 0,
        "live_model_sanity_condition": {
            "enabled": False,
            "required_model_if_enabled": "deepseek-v4-pro",
            "provider": "deepseek",
        },
        "basis": {
            "primary_row_manifest": rel(ROW_MANIFEST),
            "visible_task_manifest": rel(VISIBLE_TASK_MANIFEST),
            "oracle_manifest": rel(ORACLE_MANIFEST),
            "scorer": rel(SCORER_PATH),
            "rows": 7200,
        },
        "policies": POLICIES,
        "analysis_boundary": (
            "Diagnostic scale reference only. The visible-only policies do not "
            "call an LLM or read the scorer oracle during generation. The "
            "oracle ceiling control is not a model baseline."
        ),
    }


def environment_record() -> dict[str, Any]:
    system = platform.system() or "UnknownOS"
    machine = platform.machine() or "unknown-arch"
    return {
        "schema_version": "pcg_dynamic_state_v2.minimal_baseline_environment.v1",
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
        "platform": f"{system}-{machine}",
        "implementation": platform.python_implementation(),
        "api_calls_performed": 0,
    }


def build_output_row(
    policy: dict[str, Any],
    generated: dict[str, Any],
    source_row: dict[str, Any],
    visible_task: dict[str, Any],
    oracle_task: dict[str, Any],
    run_started_at_utc: str,
    hashes: dict[str, str],
    config_hash: str,
    env_hash: str,
) -> dict[str, Any]:
    output_payload = {
        "final_output": generated["final_output"],
        "final_state": generated["final_state"],
    }
    output_hash = sha256_json(output_payload)
    row_source_clean = {key: value for key, value in source_row.items() if not key.startswith("_")}
    run_input_hash = sha256_json(
        {
            "baseline_policy_id": policy["policy_id"],
            "source_primary_row_sha256": source_row["_line_sha256"],
            "visible_task_sha256": sha256_json(visible_task),
            "oracle_entry_sha256": sha256_json(oracle_task),
            "config_hash": config_hash,
            "environment_hash": env_hash,
            "scorer_hash": hashes["scorer"],
            "script_hash": hashes["script"],
        }
    )
    return {
        "schema_version": "pcg_dynamic_state_v2.minimal_baseline_output_row.v1",
        "suite_id": "minimal_baseline_validity_suite_20260706",
        "baseline_row_id": f"{source_row['row_id']}::{policy['policy_id']}",
        "baseline_policy_id": policy["policy_id"],
        "baseline_policy_kind": policy["policy_kind"],
        "baseline_policy_description": policy["description"],
        "oracle_access_for_generation": bool(policy["oracle_access_for_generation"]),
        "api_calls_performed": 0,
        "created_at_utc": run_started_at_utc,
        "source_primary_row_id": source_row["row_id"],
        "source_global_artifact_id": source_row["global_artifact_id"],
        "source_logical_request_hash": source_row["logical_request_hash"],
        "source_model_condition_id": source_row["model_condition_id"],
        "source_method": source_row["method"],
        "source_budget": int(source_row["budget"]),
        "source_run_id": int(source_row["run_id"]),
        "task_id": source_row["task_id"],
        "task_family": source_row["task_family"],
        "task_difficulty": source_row["task_difficulty"],
        "row_manifest_entry_sha256": source_row["_line_sha256"],
        "row_source_sha256": sha256_json(row_source_clean),
        "task_manifest_entry_sha256": source_row["task_manifest_entry_sha256"],
        "visible_task_sha256": sha256_json(visible_task),
        "oracle_entry_sha256": source_row["oracle_entry_sha256"],
        "oracle_record_sha256": sha256_json(oracle_task),
        "row_manifest_file_sha256": hashes["row_manifest"],
        "visible_task_manifest_file_sha256": hashes["visible_manifest"],
        "oracle_manifest_file_sha256": hashes["oracle_manifest"],
        "scorer_sha256": hashes["scorer"],
        "generator_script_sha256": hashes["script"],
        "baseline_config_sha256": config_hash,
        "environment_record_sha256": env_hash,
        "run_input_hash": run_input_hash,
        "final_output": generated["final_output"],
        "final_state": generated["final_state"],
        "policy_trace": generated["policy_trace"],
        "baseline_output_sha256": output_hash,
    }


def build_score_row(output_row: dict[str, Any], scorer: Any, oracle_task: dict[str, Any]) -> dict[str, Any]:
    metric = scorer.score_task(
        oracle_task,
        {
            "task_id": output_row["task_id"],
            "method": output_row["baseline_policy_id"],
            "model": "local_deterministic_policy",
            "budget": output_row["source_budget"],
            "run_id": output_row["source_run_id"],
            "final_output": output_row["final_output"],
            "final_state": output_row["final_state"],
        },
    )
    metric_hash = sha256_json(metric)
    score_payload = {
        **metric,
        "schema_version": "pcg_dynamic_state_v2.minimal_baseline_score_row.v1",
        "suite_id": output_row["suite_id"],
        "baseline_row_id": output_row["baseline_row_id"],
        "baseline_policy_id": output_row["baseline_policy_id"],
        "baseline_policy_kind": output_row["baseline_policy_kind"],
        "oracle_access_for_generation": output_row["oracle_access_for_generation"],
        "api_calls_performed": 0,
        "created_at_utc": output_row["created_at_utc"],
        "source_primary_row_id": output_row["source_primary_row_id"],
        "source_global_artifact_id": output_row["source_global_artifact_id"],
        "source_logical_request_hash": output_row["source_logical_request_hash"],
        "source_model_condition_id": output_row["source_model_condition_id"],
        "source_method": output_row["source_method"],
        "source_budget": output_row["source_budget"],
        "source_run_id": output_row["source_run_id"],
        "task_family": output_row["task_family"],
        "task_difficulty": output_row["task_difficulty"],
        "row_manifest_entry_sha256": output_row["row_manifest_entry_sha256"],
        "visible_task_sha256": output_row["visible_task_sha256"],
        "oracle_record_sha256": output_row["oracle_record_sha256"],
        "run_input_hash": output_row["run_input_hash"],
        "baseline_output_sha256": output_row["baseline_output_sha256"],
        "metric_record_sha256": metric_hash,
        "score_record_sha256": sha256_json(
            {
                "metric": metric,
                "baseline_output_sha256": output_row["baseline_output_sha256"],
                "run_input_hash": output_row["run_input_hash"],
            }
        ),
    }
    return score_payload


def aggregate(rows: list[dict[str, Any]], keys: list[str]) -> list[dict[str, Any]]:
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[tuple(row[key] for key in keys)].append(row)
    out: list[dict[str, Any]] = []
    for group_key, group_rows in sorted(grouped.items(), key=lambda item: tuple(str(part) for part in item[0])):
        n = len(group_rows)
        answer = sum(bool(row["answer_success"]) for row in group_rows)
        governance = sum(bool(row["state_governance_success"]) for row in group_rows)
        co_success = sum(bool(row["reliable_composite_success"]) for row in group_rows)
        record = {key: value for key, value in zip(keys, group_key)}
        record.update(
            {
                "n": n,
                "answer_success_count": answer,
                "answer_success_rate": round(answer / n, 6) if n else 0.0,
                "state_governance_success_count": governance,
                "state_governance_success_rate": round(governance / n, 6) if n else 0.0,
                "co_success_count": co_success,
                "co_success_rate": round(co_success / n, 6) if n else 0.0,
            }
        )
        out.append(record)
    return out


def manifest_row(
    path: Path,
    artifact_id: str,
    artifact_type: str,
    created_utc: str,
    parent_hashes: list[str],
    produced_by_run: str | None,
    notes: str,
) -> dict[str, Any]:
    stat = path.stat()
    mtime = datetime.fromtimestamp(stat.st_mtime, timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    digest = file_sha256(path)
    return {
        "artifact_id": artifact_id,
        "artifact_type": artifact_type,
        "path": rel(path),
        "sha256": digest,
        "canonical_sha256": digest if path.suffix in {".json", ".jsonl", ".csv", ".md"} else None,
        "size_bytes": stat.st_size,
        "mtime_utc": mtime,
        "created_utc": created_utc,
        "git_commit": None,
        "produced_by_run": produced_by_run,
        "consumed_by_runs": ["minimal_baseline_validity_suite_20260706"],
        "parent_artifact_hashes": parent_hashes,
        "child_artifact_hashes": [],
        "notes": notes,
    }


def current_git_commit() -> str | None:
    head = ROOT / ".git" / "HEAD"
    if not head.exists():
        return None
    text = head.read_text(encoding="utf-8").strip()
    if text.startswith("ref: "):
        ref_path = ROOT / ".git" / text.split(" ", 1)[1]
        if ref_path.exists():
            return ref_path.read_text(encoding="utf-8").strip()
    return text if text else None


def write_hash_manifest(out_dir: Path, created_utc: str, source_hashes: dict[str, str], output_files: dict[str, Path]) -> None:
    rows = [
        manifest_row(ROW_MANIFEST, "primary_row_manifest", "dataset", created_utc, [], None, "Frozen 7,200-row primary manifest."),
        manifest_row(VISIBLE_TASK_MANIFEST, "visible_task_manifest", "dataset", created_utc, [], None, "Model-visible task manifest."),
        manifest_row(ORACLE_MANIFEST, "scorer_oracle_manifest", "dataset", created_utc, [], None, "Scorer-only oracle manifest."),
        manifest_row(SCORER_PATH, "strict_main_matrix_scorer", "eval_harness", created_utc, [], None, "Strict deterministic scorer."),
        manifest_row(SCRIPT_PATH, "minimal_baseline_generator", "eval_harness", created_utc, [], None, "Baseline generator and verifier."),
    ]
    parent_hashes = [
        source_hashes["row_manifest"],
        source_hashes["visible_manifest"],
        source_hashes["oracle_manifest"],
        source_hashes["scorer"],
        source_hashes["script"],
    ]
    for artifact_id, path in output_files.items():
        artifact_type = {
            "baseline_config": "config",
            "environment": "environment",
            "baseline_outputs": "raw_output",
            "baseline_scores": "metric",
            "baseline_scores_csv": "metric",
            "summary": "metric",
            "summary_by_policy": "metric",
            "summary_by_policy_family_difficulty": "metric",
            "interlock_report": "manifest",
        }.get(artifact_id, "manifest")
        rows.append(
            manifest_row(
                path,
                artifact_id,
                artifact_type,
                created_utc,
                parent_hashes,
                "minimal_baseline_validity_suite_20260706",
                "Generated by the deterministic minimal baseline validity suite.",
            )
        )
    manifest_path = out_dir / "HASH_MANIFEST.jsonl"
    write_jsonl(manifest_path, rows)


def write_report(out_dir: Path, summary: dict[str, Any], source_hashes: dict[str, str]) -> None:
    by_policy = summary["by_policy"]
    lines = [
        "# Minimal Baseline Validity Suite Interlock Report",
        "",
        "## Summary",
        "",
        f"- suite_id: `{summary['suite_id']}`",
        f"- generated_at_utc: `{summary['generated_at_utc']}`",
        f"- source_rows: `{summary['source_rows']}`",
        f"- baseline_score_rows: `{summary['baseline_score_rows']}`",
        "- api_calls_performed: `0`",
        "- evidence_level: `E5` for the deterministic saved-output baseline chain",
        "",
        "## Baseline Rates",
        "",
        "| policy | kind | n | answer | governance | co-success |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    kind_by_policy = {policy["policy_id"]: policy["policy_kind"] for policy in POLICIES}
    for row in by_policy:
        lines.append(
            "| {policy} | {kind} | {n} | {a:.2%} | {g:.2%} | {r:.2%} |".format(
                policy=row["baseline_policy_id"],
                kind=kind_by_policy[row["baseline_policy_id"]],
                n=row["n"],
                a=row["answer_success_rate"],
                g=row["state_governance_success_rate"],
                r=row["co_success_rate"],
            )
        )
    lines.extend(
        [
            "",
            "## Chain",
            "",
            "- row_manifest_sha256: `" + source_hashes["row_manifest"] + "`",
            "- visible_task_manifest_sha256: `" + source_hashes["visible_manifest"] + "`",
            "- oracle_manifest_sha256: `" + source_hashes["oracle_manifest"] + "`",
            "- scorer_sha256: `" + source_hashes["scorer"] + "`",
            "- generator_script_sha256: `" + source_hashes["script"] + "`",
            "",
            "Each output row stores the source primary row hash, visible-task hash, oracle-entry hash used by the scorer, run-input hash, generated output hash, metric hash, and score-record hash.",
            "",
            "## Boundary",
            "",
            "The visible-only baselines are local deterministic policies. They do not call a model and do not read the oracle while generating answers. The oracle ceiling control is included only to confirm that the scorer can produce the expected upper bound.",
            "",
        ]
    )
    (out_dir / "BASELINE_INTERLOCK_REPORT.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")


def run_suite(out_dir: Path, run_started_at_utc: str) -> dict[str, Any]:
    scorer = load_module(SCORER_PATH, "pcg_dynamic_state_v2_strict_scorer")
    rows = read_jsonl(ROW_MANIFEST)
    visible_by_id = {row["task_id"]: {key: value for key, value in row.items() if not key.startswith("_")} for row in read_jsonl(VISIBLE_TASK_MANIFEST)}
    oracle_by_id = {row["task_id"]: {key: value for key, value in row.items() if not key.startswith("_")} for row in read_jsonl(ORACLE_MANIFEST)}

    source_hashes = {
        "row_manifest": file_sha256(ROW_MANIFEST),
        "visible_manifest": file_sha256(VISIBLE_TASK_MANIFEST),
        "oracle_manifest": file_sha256(ORACLE_MANIFEST),
        "scorer": file_sha256(SCORER_PATH),
        "script": file_sha256(SCRIPT_PATH),
    }
    config = build_config(run_started_at_utc)
    environment = environment_record()
    config_hash = sha256_json(config)
    env_hash = sha256_json(environment)

    output_rows: list[dict[str, Any]] = []
    score_rows: list[dict[str, Any]] = []
    for row in rows:
        task_id = row["task_id"]
        visible_task = visible_by_id[task_id]
        oracle_task = oracle_by_id[task_id]
        for policy in POLICIES:
            generated = POLICY_FUNCTIONS[policy["policy_id"]](oracle_task if policy["oracle_access_for_generation"] else visible_task, row)
            output_row = build_output_row(
                policy=policy,
                generated=generated,
                source_row=row,
                visible_task=visible_task,
                oracle_task=oracle_task,
                run_started_at_utc=run_started_at_utc,
                hashes=source_hashes,
                config_hash=config_hash,
                env_hash=env_hash,
            )
            score_row = build_score_row(output_row, scorer, oracle_task)
            output_rows.append(output_row)
            score_rows.append(score_row)

    by_policy = aggregate(score_rows, ["baseline_policy_id"])
    by_policy_family_difficulty = aggregate(score_rows, ["baseline_policy_id", "task_family", "task_difficulty"])
    summary = {
        "schema_version": "pcg_dynamic_state_v2.minimal_baseline_summary.v1",
        "suite_id": "minimal_baseline_validity_suite_20260706",
        "generated_at_utc": run_started_at_utc,
        "api_calls_performed": 0,
        "source_rows": len(rows),
        "policy_count": len(POLICIES),
        "baseline_output_rows": len(output_rows),
        "baseline_score_rows": len(score_rows),
        "source_hashes": source_hashes,
        "baseline_config_sha256": config_hash,
        "environment_record_sha256": env_hash,
        "by_policy": by_policy,
    }

    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "baseline_config": out_dir / "baseline_config.json",
        "environment": out_dir / "environment.json",
        "baseline_outputs": out_dir / "baseline_outputs.jsonl",
        "baseline_scores": out_dir / "baseline_scores.jsonl",
        "baseline_scores_csv": out_dir / "baseline_scores.csv",
        "summary": out_dir / "baseline_summary.json",
        "summary_by_policy": out_dir / "baseline_summary_by_policy.csv",
        "summary_by_policy_family_difficulty": out_dir / "baseline_summary_by_policy_family_difficulty.csv",
        "interlock_report": out_dir / "BASELINE_INTERLOCK_REPORT.md",
    }
    write_json(files["baseline_config"], config)
    write_json(files["environment"], environment)
    write_jsonl(files["baseline_outputs"], output_rows)
    write_jsonl(files["baseline_scores"], score_rows)
    write_csv(files["baseline_scores_csv"], score_rows)
    write_json(files["summary"], summary)
    write_csv(files["summary_by_policy"], by_policy)
    write_csv(files["summary_by_policy_family_difficulty"], by_policy_family_difficulty)
    write_report(out_dir, summary, source_hashes)
    write_hash_manifest(out_dir, run_started_at_utc, source_hashes, files)
    return summary


def normalized_jsonl(path: Path) -> list[dict[str, Any]]:
    volatile = {"created_at_utc", "generated_at_utc", "run_started_at_utc", "mtime_utc", "git_commit"}
    rows = []
    for row in read_jsonl(path):
        rows.append({key: value for key, value in row.items() if key not in volatile and not key.startswith("_")})
    return rows


def normalized_json(path: Path) -> Any:
    volatile = {"created_at_utc", "generated_at_utc", "run_started_at_utc", "git_commit"}

    def clean(value: Any) -> Any:
        if isinstance(value, dict):
            return {key: clean(item) for key, item in value.items() if key not in volatile}
        if isinstance(value, list):
            return [clean(item) for item in value]
        return value

    return clean(json.loads(path.read_text(encoding="utf-8")))


def compare_files(expected_dir: Path, observed_dir: Path) -> list[str]:
    failures: list[str] = []
    jsonl_files = ["baseline_outputs.jsonl", "baseline_scores.jsonl"]
    json_files = ["baseline_config.json", "environment.json", "baseline_summary.json"]
    exact_files = [
        "BASELINE_INTERLOCK_REPORT.md",
        "baseline_summary_by_policy.csv",
        "baseline_summary_by_policy_family_difficulty.csv",
    ]

    for name in jsonl_files:
        expected_path = expected_dir / name
        if not expected_path.exists():
            continue
        if normalized_jsonl(expected_path) != normalized_jsonl(observed_dir / name):
            failures.append(f"{name} differs after volatile fields are ignored")
    for name in json_files:
        if normalized_json(expected_dir / name) != normalized_json(observed_dir / name):
            failures.append(f"{name} differs after volatile fields are ignored")
    for name in exact_files:
        if (expected_dir / name).read_text(encoding="utf-8") != (observed_dir / name).read_text(encoding="utf-8"):
            failures.append(f"{name} differs")
    if normalized_manifest(expected_dir / "HASH_MANIFEST.jsonl") != normalized_manifest(observed_dir / "HASH_MANIFEST.jsonl"):
        failures.append("HASH_MANIFEST.jsonl differs after volatile fields and build paths are ignored")
    return failures


def normalized_manifest(path: Path) -> list[dict[str, Any]]:
    keep = {
        "artifact_id",
        "artifact_type",
        "sha256",
        "canonical_sha256",
        "produced_by_run",
        "consumed_by_runs",
        "parent_artifact_hashes",
        "child_artifact_hashes",
        "notes",
    }
    rows = []
    for row in read_jsonl(path):
        rows.append({key: row.get(key) for key in sorted(keep)})
    return sorted(rows, key=lambda item: str(item.get("artifact_id")))


def check_suite() -> dict[str, Any]:
    if not DEFAULT_OUTPUT_DIR.exists():
        raise SystemExit(f"missing baseline output directory: {DEFAULT_OUTPUT_DIR}")
    expected_summary = json.loads((DEFAULT_OUTPUT_DIR / "baseline_summary.json").read_text(encoding="utf-8"))
    summary = run_suite(DEFAULT_BUILD_DIR, expected_summary["generated_at_utc"])
    failures = compare_files(DEFAULT_OUTPUT_DIR, DEFAULT_BUILD_DIR)
    compact_missing = sorted(
        name
        for name in ["baseline_outputs.jsonl", "baseline_scores.jsonl", "baseline_scores.csv"]
        if not (DEFAULT_OUTPUT_DIR / name).exists()
    )
    result = {
        "passed": not failures,
        "suite_id": "minimal_baseline_validity_suite_20260706",
        "source_rows": summary["source_rows"],
        "baseline_score_rows_recomputed": summary["baseline_score_rows"],
        "policy_count": summary["policy_count"],
        "api_calls_performed": 0,
        "archive_compact_mode": bool(compact_missing),
        "compact_files_recomputed": compact_missing,
        "failure_count": len(failures),
        "failures": failures[:20],
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="Generate checked-in baseline suite outputs.")
    parser.add_argument("--check", action="store_true", help="Recompute and compare against checked-in outputs.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    if args.write == args.check:
        parser.error("use exactly one of --write or --check")

    if args.write:
        summary = run_suite(args.output_dir, utc_now())
        print(json.dumps({"passed": True, **summary}, ensure_ascii=False, sort_keys=True))
        return 0

    result = check_suite()
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
