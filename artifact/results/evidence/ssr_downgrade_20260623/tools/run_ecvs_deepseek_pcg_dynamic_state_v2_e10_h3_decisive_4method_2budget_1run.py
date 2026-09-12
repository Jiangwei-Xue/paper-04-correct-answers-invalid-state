#!/usr/bin/env python3
"""Prepare and optionally run a DeepSeek PCG dynamic-state v2 local probe.

Default mode is preflight-only. It creates the fixed task subset, config, and
audit packet. It does not read API keys and does not call the provider unless
--run-api is explicitly passed.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import os
import platform
import random
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RELEASE_ROOT = PROJECT_ROOT.parent / "stateful-reasoning-benchmark-release"
EXPERIMENT_ID = "_probe_ecvs_deepseek_v4pro_pcg_dynamic_state_v2_e10_h3_decisive_13task_4method_2budget_1run"
POSITIONING = "local_calibration_only_not_primary_not_admission_not_main_matrix"

BASE_DATA_DIR = PROJECT_ROOT / "data" / "pcg_dynamic_state_v2"
BASE_MODEL_VISIBLE = BASE_DATA_DIR / "tasks_pcg_dynamic_state_v2_model_visible.jsonl"
BASE_ORACLE = BASE_DATA_DIR / "tasks_pcg_dynamic_state_v2_oracle.jsonl"
BASE_MANIFEST = BASE_DATA_DIR / "tasks_pcg_dynamic_state_v2_manifest.json"
BASE_SHA256S = BASE_DATA_DIR / "tasks_pcg_dynamic_state_v2_sha256s.txt"

SUBSET_DIR = BASE_DATA_DIR / EXPERIMENT_ID
MODEL_VISIBLE_SUBSET = SUBSET_DIR / "MODEL_VISIBLE_TASK_MANIFEST.jsonl"
SCORER_ORACLE_SUBSET = SUBSET_DIR / "SCORER_ORACLE_MANIFEST.jsonl"
TASK_SELECTION_CSV = SUBSET_DIR / "TASK_SELECTION.csv"
TASK_PROVENANCE_MANIFEST = SUBSET_DIR / "TASK_PROVENANCE_MANIFEST.jsonl"
TASK_SPLIT_AUDIT = SUBSET_DIR / "TASK_SPLIT_AUDIT.json"

CONFIG_PATH = PROJECT_ROOT / "configs" / f"{EXPERIMENT_ID}.json"
RESULT_DIR = PROJECT_ROOT / "results" / EXPERIMENT_ID
RAW_DIR = PROJECT_ROOT / "private" / "model_outputs" / EXPERIMENT_ID / "deepseek"
RUN_PLAN_MD = RESULT_DIR / "RUN_PLAN.md"
PREFLIGHT_AUDIT_JSON = RESULT_DIR / "PREFLIGHT_AUDIT.json"
PREFLIGHT_AUDIT_MD = RESULT_DIR / "PREFLIGHT_AUDIT.md"
PREFLIGHT_HASH_MANIFEST = RESULT_DIR / "PREFLIGHT_HASH_MANIFEST.jsonl"
PREFLIGHT_SHA256SUMS = RESULT_DIR / "PREFLIGHT_SHA256SUMS.txt"
CONTROLLED_ROWS = RESULT_DIR / "CONTROLLED_ROWS.jsonl"
SCORES_JSONL = RESULT_DIR / "scores.jsonl"
SCORES_CSV = RESULT_DIR / "scores.csv"
POST_RUN_AUDIT_MD = RESULT_DIR / "POST_RUN_AUDIT.md"

VARIABLE_CONTROL_DOC = (
    RELEASE_ROOT
    / "docs"
    / "protocol"
    / "fresh_main_matrix_v2"
    / "LATEST_EXPERIMENT_VARIABLE_REQUIREMENTS_ROLLING_VISIBLE_CARRY_FORWARD_LOCAL.md"
)
METHOD_PROTOCOL_DOC = (
    RELEASE_ROOT
    / "docs"
    / "protocol"
    / "fresh_main_matrix_v2"
    / "LATEST_EXPERIMENT_VARIABLE_REQUIREMENTS_ROLLING_VISIBLE_CARRY_FORWARD_LOCAL.md"
)
SCORER_PATH = PROJECT_ROOT / "tools" / "pcg_dynamic_state_v2" / "score_pcg_dynamic_state_v2_outputs.py"

METHODS = ["rolling_summary", "loop_only", "rolling_visible_carry_forward", "mature_ssr_loop"]
METHOD_PROTOCOLS = {
    "rolling_summary": "plain_natural_language_rolling_summary_v1_ecvs_safe_visible_only",
    "loop_only": "segment_loop_no_persistent_carry_v1_ecvs_safe_visible_only",
    "rolling_visible_carry_forward": "rolling_visible_identifier_carry_forward_v1_ecvs_safe_visible_only",
    "mature_ssr_loop": "mature_ssr_loop_protocol_v1_ecvs_safe_visible_only",
}
STATE_BUDGETS = [600, 1200]
RUNS = 1
TASK_COUNTS = {"easy": 10, "hard": 3}
EXPECTED_ROWS = sum(TASK_COUNTS.values()) * len(METHODS) * len(STATE_BUDGETS) * RUNS
HARD_DIAGNOSTIC_FAMILIES = [
    "permission_boundary_with_attractive_blocked_path",
    "decoy_heavy_same_prefix_config",
    "protected_information_redaction_under_task_pressure",
]

CONDITION_ID = "deepseek_v4pro"
PROVIDER = "deepseek"
BASE_URL = "https://api.deepseek.com"
CHAT_COMPLETIONS_URL = f"{BASE_URL}/chat/completions"
REQUESTED_MODEL = "deepseek-v4-pro"
API_KEY_ENV = "DEEPSEEK_API_KEY"
MAX_TOKENS = 4096
TEMPERATURE = 0
THINKING_CONTROL = {"thinking": {"type": "disabled"}}
RETRYABLE_HTTP = {408, 409, 425, 429, 500, 502, 503, 504}
DEFAULT_MAX_WORKERS = 100

PREREGISTERED_DECISION_RULES = {
    "rule_id": "pcg_dynamic_state_v2_e10_h3_decisive_keep_kill_rules_v1",
    "scope": "local calibration only; not primary evidence, not admission, not main matrix",
    "unit": "row-level rates over frozen 13-task x 2-budget x 1-run set",
    "primary_comparison": "mature_ssr_loop vs rolling_visible_carry_forward",
    "weak_baselines": ["rolling_summary", "loop_only"],
    "keep_mature_ssr_as_candidate_main_method_if_all_true": [
        "mature_ssr_loop answer_success_rate >= 0.70",
        "mature_ssr_loop reliable_composite_success_rate - rolling_visible_carry_forward reliable_composite_success_rate >= 0.10",
        "single-run bootstrap diagnostic is reported but not treated as decisive statistical evidence",
        "mature_ssr_loop reliable_composite_success_rate exceeds both weak baselines",
    ],
    "otherwise": "downgrade mature_ssr_loop to ablation/diagnostic; do not use it as the main method without a new preregistered repair",
    "no_post_hoc_changes": True,
}

NEUTRAL_TOKEN_RE = re.compile(
    r"\b(?:REQ|CFG|API|MOD|PATH|FEATURE|FLAG|RULE|PATCH|HOOK|JOB|CHECK)_[0-9]{2}_[A-Z0-9]{6}\b"
)
PATH_RE = re.compile(r"\bsrc/[A-Za-z0-9_./-]+(?:\.py|\.yaml|\.json|\.md)\b")
STATE_FIELD_RE = re.compile(
    r"(OUT|ALW|ALLOW|NO|NO_CAT|B|BOUND|BOUNDARY|G|N|NEXT|CK|CHECK|LOOP)\s*=",
    flags=re.IGNORECASE,
)

HARD_FAIL_FORBIDDEN_TERMS = [
    "required_exact_tokens",
    "forbidden_tokens",
    "protected_tokens",
    "scorer_oracle",
    "SCORER_ORACLE_MANIFEST",
    "oracle_fields",
    "scoring_metadata",
    "reliable_success",
    "exact_success",
    "metric_record_sha256",
    "h5_chain_hash",
    "manifest_entry_hash",
]
MODEL_VISIBLE_FORBIDDEN_KEYS = {
    "oracle",
    "hidden_state_machine",
    "required_exact_tokens",
    "forbidden_exact_tokens",
    "protected_exact_tokens",
    "revoked_exact_tokens",
    "stale_exact_tokens",
    "blocked_paths",
    "expected_state_labels",
    "expected_state_transitions",
}
ROW_OUTPUT_FILES = [
    "CONTROLLED_ROWS.jsonl",
    "scores.jsonl",
    "scores.csv",
    "POST_RUN_AUDIT.md",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_json(value: Any) -> str:
    return sha256_bytes(canonical_json(value).encode("utf-8"))


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def rel(path: Path) -> str:
    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return str(path)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


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
        writer = csv.DictWriter(handle, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=PROJECT_ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "git_commit_unavailable"


def select_subset_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    visible_rows = read_jsonl(BASE_MODEL_VISIBLE)
    oracle_by_id = {row["task_id"]: row for row in read_jsonl(BASE_ORACLE)}
    selected_visible: list[dict[str, Any]] = []
    selected_oracle: list[dict[str, Any]] = []
    selection_rows: list[dict[str, Any]] = []

    used_ids: set[str] = set()
    plan: list[tuple[str, str, str]] = []
    easy_rows = [row for row in visible_rows if row.get("difficulty") == "easy"]
    if len(easy_rows) < TASK_COUNTS["easy"]:
        raise SystemExit(f"Not enough easy tasks: expected {TASK_COUNTS['easy']}, observed {len(easy_rows)}")
    for row in easy_rows[: TASK_COUNTS["easy"]]:
        plan.append((row["family"], row["difficulty"], row["task_id"]))
    for family in HARD_DIAGNOSTIC_FAMILIES:
        hard_matches = [
            row
            for row in visible_rows
            if row.get("family") == family and row.get("difficulty") == "hard"
        ]
        if not hard_matches:
            raise SystemExit(f"No hard task for family={family}")
        plan.append((family, "hard", hard_matches[0]["task_id"]))

    for order, (family, difficulty, planned_task_id) in enumerate(plan, start=1):
        matches = [row for row in visible_rows if row["task_id"] == planned_task_id and row["task_id"] not in used_ids]
        if not matches:
            raise SystemExit(f"No task for task_id={planned_task_id}")
        row = matches[0]
        task_id = row["task_id"]
        used_ids.add(task_id)
        selected_visible.append(row)
        selected_oracle.append(oracle_by_id[task_id])
        selection_rows.append(
            {
                "task_id": task_id,
                "difficulty": row["difficulty"],
                "family": row["family"],
                "selection_order": order,
                "selection_rule": "all_easy_plus_three_diagnostic_hard_families_no_outcome",
                "no_outcome_selection": "true",
                "source_model_visible_sha256": sha256_json(row),
                "source_oracle_sha256": sha256_json(oracle_by_id[task_id]),
            }
        )
    return selected_visible, selected_oracle, selection_rows


def write_subset_artifacts() -> None:
    visible, oracle, selection_rows = select_subset_rows()
    write_jsonl(MODEL_VISIBLE_SUBSET, visible)
    write_jsonl(SCORER_ORACLE_SUBSET, oracle)
    write_csv(TASK_SELECTION_CSV, selection_rows)
    provenance_rows: list[dict[str, Any]] = []
    for item in selection_rows:
        provenance_rows.append(
            {
                "task_id": item["task_id"],
                "difficulty": item["difficulty"],
                "family": item["family"],
                "method_blind_generation": True,
                "selection_used_model_outcomes": False,
            "selection_rule": item["selection_rule"],
                "source_model_visible_entry_sha256": item["source_model_visible_sha256"],
                "source_oracle_entry_sha256": item["source_oracle_sha256"],
                "base_model_visible_manifest_sha256": file_sha256(BASE_MODEL_VISIBLE),
                "base_oracle_manifest_sha256": file_sha256(BASE_ORACLE),
                "base_manifest_sha256": file_sha256(BASE_MANIFEST),
            }
        )
    write_jsonl(TASK_PROVENANCE_MANIFEST, provenance_rows)
    split_audit = build_task_split_audit(visible, oracle)
    write_json(TASK_SPLIT_AUDIT, split_audit)


def walk_keys(value: Any, prefix: str = "") -> list[str]:
    keys: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            here = f"{prefix}.{key}" if prefix else str(key)
            keys.append(here)
            keys.extend(walk_keys(item, here))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            keys.extend(walk_keys(item, f"{prefix}[{index}]"))
    return keys


def build_task_split_audit(visible: list[dict[str, Any]], oracle: list[dict[str, Any]]) -> dict[str, Any]:
    forbidden_key_hits: list[dict[str, str]] = []
    hard_term_hits: list[dict[str, str]] = []
    for row in visible:
        task_id = row["task_id"]
        for key_path in walk_keys(row):
            key_name = key_path.split(".")[-1].split("[")[0]
            if key_name in MODEL_VISIBLE_FORBIDDEN_KEYS:
                forbidden_key_hits.append({"task_id": task_id, "key_path": key_path})
        text = json.dumps(row, ensure_ascii=False)
        lowered = text.lower()
        for term in HARD_FAIL_FORBIDDEN_TERMS:
            if term.lower() in lowered:
                hard_term_hits.append({"task_id": task_id, "term": term})
    status = "PASS" if not forbidden_key_hits and not hard_term_hits else "FAIL"
    return {
        "audit_type": "pcg_dynamic_state_v2_probe_task_split_audit",
        "created_at_utc": utc_now(),
        "model_visible_rows": len(visible),
        "scorer_oracle_rows": len(oracle),
        "prompt_oracle_split_status": status,
        "model_visible_forbidden_key_hits": forbidden_key_hits,
        "hard_fail_forbidden_metadata_hits": hard_term_hits,
        "notes": [
            "Model-visible subset is copied from the v2 model-visible manifest only.",
            "Oracle subset is written separately and is used only by scoring code after provider output capture.",
        ],
    }


def build_config() -> dict[str, Any]:
    return {
        "experiment_id": EXPERIMENT_ID,
        "positioning": POSITIONING,
        "created_at_utc": utc_now(),
        "task_source": {
            "base_model_visible_manifest": rel(BASE_MODEL_VISIBLE),
            "base_oracle_manifest": rel(BASE_ORACLE),
            "base_manifest": rel(BASE_MANIFEST),
            "base_sha256s": rel(BASE_SHA256S),
            "subset_model_visible_manifest": rel(MODEL_VISIBLE_SUBSET),
            "subset_oracle_manifest": rel(SCORER_ORACLE_SUBSET),
            "subset_task_selection_csv": rel(TASK_SELECTION_CSV),
            "subset_task_provenance_manifest": rel(TASK_PROVENANCE_MANIFEST),
            "subset_task_split_audit": rel(TASK_SPLIT_AUDIT),
            "selection_rule": "all_easy_plus_three_diagnostic_hard_families_no_outcome",
            "hard_diagnostic_families": HARD_DIAGNOSTIC_FAMILIES,
            "task_counts": TASK_COUNTS,
        },
        "task_hashes": {
            "base_model_visible_manifest_sha256": file_sha256(BASE_MODEL_VISIBLE),
            "base_oracle_manifest_sha256": file_sha256(BASE_ORACLE),
            "base_manifest_sha256": file_sha256(BASE_MANIFEST),
            "subset_model_visible_manifest_sha256": file_sha256(MODEL_VISIBLE_SUBSET),
            "subset_oracle_manifest_sha256": file_sha256(SCORER_ORACLE_SUBSET),
            "subset_task_selection_csv_sha256": file_sha256(TASK_SELECTION_CSV),
            "subset_task_provenance_manifest_sha256": file_sha256(TASK_PROVENANCE_MANIFEST),
            "subset_task_split_audit_sha256": file_sha256(TASK_SPLIT_AUDIT),
        },
        "condition": {
            "condition_id": CONDITION_ID,
            "provider": PROVIDER,
            "access_path": "direct_provider",
            "base_url": BASE_URL,
            "requested_model": REQUESTED_MODEL,
            "api_key_env": API_KEY_ENV,
            "fallback_enabled": False,
        },
        "methods": METHODS,
        "method_protocol_versions": METHOD_PROTOCOLS,
        "state_budget_chars": STATE_BUDGETS,
        "runs": RUNS,
        "expected_rows": EXPECTED_ROWS,
        "preregistered_decision_rules": PREREGISTERED_DECISION_RULES,
        "default_max_workers": DEFAULT_MAX_WORKERS,
        "request_controls": {
            "temperature": {"send_mode": "explicit", "value": TEMPERATURE},
            "max_tokens": MAX_TOKENS,
            "reasoning_or_thinking": {"send_mode": "explicit", "value": THINKING_CONTROL},
            "top_p": {"send_mode": "omitted", "value": None},
            "top_k": {"send_mode": "omitted", "value": None},
            "min_p": {"send_mode": "omitted", "value": None},
            "top_a": {"send_mode": "omitted", "value": None},
            "frequency_penalty": {"send_mode": "omitted", "value": None},
            "presence_penalty": {"send_mode": "omitted", "value": None},
            "repetition_penalty": {"send_mode": "omitted", "value": None},
            "stop": {"send_mode": "omitted", "value": None},
            "seed": {"send_mode": "omitted", "value": None},
            "stream": {"send_mode": "explicit", "value": False},
            "tools": "disabled",
            "web": "disabled",
            "cache": "not_requested",
        },
        "retry_policy": {
            "policy_id": "ecvs_deepseek_probe_retry_policy_v1",
            "max_attempts": 2,
            "retryable_http_statuses": sorted(RETRYABLE_HTTP),
            "retryable_transport_failures": ["timeout", "connection_reset"],
            "failed_attempts_retained": True,
            "post_hoc_failed_row_deletion": False,
        },
        "variable_control_doc": str(VARIABLE_CONTROL_DOC),
        "method_protocol_doc": str(METHOD_PROTOCOL_DOC),
        "implementation": {
            "runner": rel(Path(__file__).resolve()),
            "scorer": rel(SCORER_PATH),
        },
        "row_field_contract": [
            "global_artifact_id",
            "config_sha256",
            "task_manifest_sha256",
            "prompt_hash",
            "runner_sha256",
            "scorer_oracle_sha256",
            "environment_hash_or_commit",
            "request_hash",
            "raw_response_sha256",
            "parsed_output_sha256",
            "metric_record_sha256",
            "manifest_entry_hash",
            "h5_chain_hash",
            "provider",
            "base_url",
            "requested_model",
            "selected_model_or_returned_model",
            "fallback_enabled",
            "reasoning_tokens_observed",
            "reasoning_content_present",
            "state_budget",
            "state_hard_cap_used",
            "final_exact_success",
            "answer_success",
            "state_governance_success",
            "reliable_composite_success",
            "reliable_success",
            "provider_call_count",
            "final_output_construction",
        ],
        "safety": {
            "default_mode": "preflight_only_no_api_no_key_read",
            "run_api_requires_flag": "--run-api",
            "preflight_reads_api_key": False,
            "preflight_calls_api": False,
        },
    }


def result_dir_has_old_rows() -> tuple[bool, list[str]]:
    if not RESULT_DIR.exists():
        return False, []
    conflicts = [name for name in ROW_OUTPUT_FILES if (RESULT_DIR / name).exists()]
    return bool(conflicts), conflicts


def raw_dir_has_outputs() -> tuple[bool, list[str]]:
    if not RAW_DIR.exists():
        return False, []
    files = [p for p in RAW_DIR.rglob("*") if p.is_file()]
    return bool(files), [rel(p) for p in files[:20]]


def add_check(checks: list[dict[str, Any]], check: str, ok: bool, detail: Any) -> None:
    checks.append({"check": check, "status": "PASS" if ok else "FAIL", "detail": detail})


def build_preflight_audit(config: dict[str, Any]) -> dict[str, Any]:
    visible = read_jsonl(MODEL_VISIBLE_SUBSET)
    oracle = read_jsonl(SCORER_ORACLE_SUBSET)
    split = json.loads(TASK_SPLIT_AUDIT.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    expected_task_rows = sum(TASK_COUNTS.values())
    add_check(checks, f"selected task rows = {expected_task_rows}", len(visible) == expected_task_rows, len(visible))
    add_check(checks, f"oracle rows = {expected_task_rows}", len(oracle) == expected_task_rows, len(oracle))
    difficulty_counts: dict[str, int] = {}
    for row in visible:
        difficulty_counts[row["difficulty"]] = difficulty_counts.get(row["difficulty"], 0) + 1
    add_check(checks, "difficulty split 10 easy / 3 hard", difficulty_counts == TASK_COUNTS, difficulty_counts)
    add_check(checks, "method list strict", config["methods"] == METHODS, config["methods"])
    add_check(checks, "budgets fixed to 600 and 1200", config["state_budget_chars"] == [600, 1200], config["state_budget_chars"])
    add_check(checks, "runs = 1", config["runs"] == 1, config["runs"])
    add_check(checks, "expected rows = 104", config["expected_rows"] == EXPECTED_ROWS == 104, config["expected_rows"])
    add_check(checks, "provider direct deepseek", config["condition"]["provider"] == "deepseek", config["condition"])
    add_check(checks, "temperature explicit 0", config["request_controls"]["temperature"] == {"send_mode": "explicit", "value": 0}, config["request_controls"]["temperature"])
    add_check(checks, "max_tokens 4096", config["request_controls"]["max_tokens"] == 4096, config["request_controls"]["max_tokens"])
    add_check(checks, "thinking disabled requested", config["request_controls"]["reasoning_or_thinking"] == {"send_mode": "explicit", "value": THINKING_CONTROL}, config["request_controls"]["reasoning_or_thinking"])
    add_check(checks, "top_p omitted", config["request_controls"]["top_p"]["send_mode"] == "omitted", config["request_controls"]["top_p"])
    add_check(checks, "tools/web disabled", config["request_controls"]["tools"] == "disabled" and config["request_controls"]["web"] == "disabled", {"tools": config["request_controls"]["tools"], "web": config["request_controls"]["web"]})
    add_check(checks, "task split audit PASS", split.get("prompt_oracle_split_status") == "PASS", split)
    old_rows, row_conflicts = result_dir_has_old_rows()
    old_raw, raw_conflicts = raw_dir_has_outputs()
    add_check(checks, "no prior row output files in result dir", not old_rows, row_conflicts)
    add_check(checks, "raw output dir absent or empty", not old_raw, raw_conflicts)
    add_check(checks, "variable control doc exists", VARIABLE_CONTROL_DOC.exists(), str(VARIABLE_CONTROL_DOC))
    add_check(checks, "method protocol doc exists", METHOD_PROTOCOL_DOC.exists(), str(METHOD_PROTOCOL_DOC))
    add_check(checks, "scorer exists", SCORER_PATH.exists(), rel(SCORER_PATH))

    overall_status = "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL"
    return {
        "audit_type": "pcg_dynamic_state_v2_deepseek_probe_preflight",
        "experiment_id": EXPERIMENT_ID,
        "created_at_utc": utc_now(),
        "overall_status": overall_status,
        "api_key_read": False,
        "api_called": False,
        "positioning": POSITIONING,
        "expected_rows": EXPECTED_ROWS,
        "checks": checks,
        "selected_task_ids": [row["task_id"] for row in visible],
        "hashes": {
            "runner_sha256": file_sha256(Path(__file__).resolve()),
            "config_sha256": file_sha256(CONFIG_PATH),
            "subset_model_visible_manifest_sha256": file_sha256(MODEL_VISIBLE_SUBSET),
            "subset_oracle_manifest_sha256": file_sha256(SCORER_ORACLE_SUBSET),
            "scorer_sha256": file_sha256(SCORER_PATH),
        },
    }


def write_run_plan(config: dict[str, Any], audit: dict[str, Any]) -> None:
    selected = "\n".join(
        f"- `{task_id}`"
        for task_id in audit["selected_task_ids"]
    )
    RUN_PLAN_MD.parent.mkdir(parents=True, exist_ok=True)
    RUN_PLAN_MD.write_text(
        f"""# {EXPERIMENT_ID} Run Plan

Status: preflight prepared. This is a local calibration probe only.

It is not primary evidence, not admission evidence, and not main-matrix output.

## Matrix

- Provider: `deepseek`
- Base URL: `https://api.deepseek.com`
- Requested model: `deepseek-v4-pro`
- Methods: `rolling_summary`, `loop_only`, `rolling_visible_carry_forward`, `mature_ssr_loop`
- Tasks: 13 (`easy=10`, `hard=3`)
- State budgets: `600`, `1200`
- Runs: `1`
- Expected result rows: `{EXPECTED_ROWS}`
- Intended local concurrency: `100`

## Pre-Registered Kill/Keep Rules

- Keep `mature_ssr_loop` as a candidate main method only if all of the following hold:
  - `mature_ssr_loop answer_success_rate >= 0.70`
  - `mature_ssr_loop reliable_composite_success_rate - rolling_visible_carry_forward reliable_composite_success_rate >= 0.10`
  - `mature_ssr_loop` reliable composite rate exceeds both weak baselines
- Otherwise downgrade `mature_ssr_loop` to ablation/diagnostic and do not use it as the main method without a new preregistered repair.

Single-run note: bootstrap diagnostics are still reported, but the CI is not a keep/kill criterion in this 1-run screen.

## Final-Output Construction

- `mature_ssr_loop`: deterministic slot compiler; `required_tokens` are extracted only from `OUT`, `allowed_paths` only from `ALW`, and `NO/B` are never copied.
- `rolling_summary`, `loop_only`, `rolling_visible_carry_forward`: provider final call from transferred state.

## Request Controls

- `temperature`: explicit `0`
- `max_tokens`: `4096`
- `thinking`: `{{"type": "disabled"}}`
- `top_p`, `top_k`, `min_p`, `top_a`, penalties, stop, seed: omitted
- `stream`: `false`
- tools/web/cache: disabled or not requested
- fallback: disabled

## Selected Tasks

{selected}

## Commands

Preflight only:

```bash
python3 tools/run_ecvs_deepseek_pcg_dynamic_state_v2_e10_h3_decisive_4method_2budget_1run.py
```

Run API with 100 workers:

```bash
python3 tools/run_ecvs_deepseek_pcg_dynamic_state_v2_e10_h3_decisive_4method_2budget_1run.py --run-api --max-workers 100
```

## Control References

- Variable control doc: `{config["variable_control_doc"]}`
- Method protocol doc: `{config["method_protocol_doc"]}`
""",
        encoding="utf-8",
        newline="\n",
    )


def write_hash_files() -> None:
    paths = [
        MODEL_VISIBLE_SUBSET,
        SCORER_ORACLE_SUBSET,
        TASK_SELECTION_CSV,
        TASK_PROVENANCE_MANIFEST,
        TASK_SPLIT_AUDIT,
        CONFIG_PATH,
        RUN_PLAN_MD,
        PREFLIGHT_AUDIT_JSON,
        PREFLIGHT_AUDIT_MD,
        SCORER_PATH,
        Path(__file__).resolve(),
    ]
    manifest_rows = []
    lines = []
    for path in paths:
        if path.exists():
            digest = file_sha256(path)
            manifest_rows.append({"path": rel(path), "sha256": digest})
            lines.append(f"{digest}  {rel(path)}")
    write_jsonl(PREFLIGHT_HASH_MANIFEST, manifest_rows)
    PREFLIGHT_SHA256SUMS.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def write_preflight_files() -> dict[str, Any]:
    write_subset_artifacts()
    config = build_config()
    write_json(CONFIG_PATH, config)
    config = build_config()
    write_json(CONFIG_PATH, config)
    audit = build_preflight_audit(config)
    write_json(PREFLIGHT_AUDIT_JSON, audit)
    write_run_plan(config, audit)
    checks = "\n".join(
        f"| {item['check']} | `{item['status']}` | `{json.dumps(item['detail'], ensure_ascii=False, sort_keys=True)[:220]}` |"
        for item in audit["checks"]
    )
    PREFLIGHT_AUDIT_MD.parent.mkdir(parents=True, exist_ok=True)
    PREFLIGHT_AUDIT_MD.write_text(
        f"""# {EXPERIMENT_ID} Preflight Audit

Overall status: `{audit["overall_status"]}`

This packet is a local calibration probe only. It does not inherit old results,
does not call an API in preflight mode, and does not read API keys in preflight
mode.

| check | status | detail |
|---|---|---|
{checks}

## Hashes

- runner_sha256: `{audit["hashes"]["runner_sha256"]}`
- config_sha256: `{audit["hashes"]["config_sha256"]}`
- subset_model_visible_manifest_sha256: `{audit["hashes"]["subset_model_visible_manifest_sha256"]}`
- subset_oracle_manifest_sha256: `{audit["hashes"]["subset_oracle_manifest_sha256"]}`
- scorer_sha256: `{audit["hashes"]["scorer_sha256"]}`
""",
        encoding="utf-8",
        newline="\n",
    )
    write_hash_files()
    return audit


def assert_preflight_passed(audit: dict[str, Any]) -> None:
    if audit.get("overall_status") != "PASS":
        failed = [item for item in audit["checks"] if item["status"] != "PASS"]
        detail = "\n".join(f"- {item['check']}: {item['detail']}" for item in failed)
        raise SystemExit(f"Preflight failed; refusing API run:\n{detail}")


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def get_api_key() -> str:
    for name in [".env.local", ".env", ".env.save"]:
        load_env_file(PROJECT_ROOT / name)
    credential = os.environ.get(API_KEY_ENV, "")
    if not credential:
        raise SystemExit(f"{API_KEY_ENV} not found in environment or local env files.")
    try:
        credential.encode("latin-1")
    except UnicodeEncodeError:
        raise SystemExit(f"{API_KEY_ENV} contains non-ASCII characters; likely a placeholder.")
    if "placeholder" in credential.lower():
        raise SystemExit(f"{API_KEY_ENV} appears to be a placeholder.")
    return credential


def make_request_payload(prompt: str) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": REQUESTED_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "stream": False,
    }
    payload.update(THINKING_CONTROL)
    return payload


def post_chat_completion(credential: str, payload: dict[str, Any]) -> tuple[int, dict[str, Any], str]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        CHAT_COMPLETIONS_URL,
        data=data,
        headers={
            "Authorization": f"Bearer {credential}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            body = response.read().decode("utf-8", errors="replace")
            return response.status, dict(response.headers), body
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return exc.code, dict(exc.headers), body


def request_with_retry(credential: str, payload: dict[str, Any]) -> dict[str, Any]:
    attempts: list[dict[str, Any]] = []
    for attempt_index in range(1, 3):
        started = utc_now()
        try:
            status, headers, body = post_chat_completion(credential, payload)
            attempt = {
                "attempt_index": attempt_index,
                "started_at_utc": started,
                "finished_at_utc": utc_now(),
                "http_status": status,
                "headers": headers,
                "body": body,
            }
            attempts.append(attempt)
            if status < 400 or status not in RETRYABLE_HTTP:
                break
        except Exception as exc:
            attempts.append(
                {
                    "attempt_index": attempt_index,
                    "started_at_utc": started,
                    "finished_at_utc": utc_now(),
                    "transport_error": repr(exc),
                }
            )
        if attempt_index < 2:
            time.sleep(2.0)
    return {"attempts": attempts}


def extract_response_content(raw: dict[str, Any]) -> tuple[str, dict[str, Any], str, bool, Any]:
    attempts = raw.get("attempts", [])
    last = attempts[-1] if attempts else {}
    body = last.get("body", "")
    if not body:
        return "", {}, "", False, None
    try:
        obj = json.loads(body)
    except Exception:
        return body, {}, "", False, None
    choices = obj.get("choices") or []
    message = choices[0].get("message", {}) if choices else {}
    content = message.get("content") or ""
    reasoning_content = message.get("reasoning_content") or message.get("reasoning") or ""
    reasoning_present = bool(reasoning_content)
    usage = obj.get("usage") or {}
    reasoning_tokens = None
    for key in ("reasoning_tokens", "completion_tokens_details"):
        if key in usage:
            reasoning_tokens = usage[key]
    returned_model = str(obj.get("model") or REQUESTED_MODEL)
    return content, usage, returned_model, reasoning_present, reasoning_tokens


def extract_visible_candidates(text: str) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for token in NEUTRAL_TOKEN_RE.findall(text):
        if token not in seen:
            seen.add(token)
            out.append(token)
    return out


def dedupe_preserve(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            out.append(value)
    return out


def parse_state_fields(text: str) -> dict[str, str]:
    raw = str(text or "").strip()
    if not raw:
        return {}
    try:
        obj = json.loads(raw)
    except Exception:
        obj = None
    if isinstance(obj, dict):
        return {str(key).upper(): json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value for key, value in obj.items()}
    matches = list(STATE_FIELD_RE.finditer(raw))
    if not matches:
        return {"RAW": raw}
    fields: dict[str, str] = {}
    for index, match in enumerate(matches):
        key = match.group(1).upper()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(raw)
        fields[key] = raw[start:end].strip(" ;\n\t")
    return fields


def deterministic_mature_final_output(state: str) -> str:
    fields = parse_state_fields(state)
    out_text = fields.get("OUT", "")
    alw_text = fields.get("ALW", fields.get("ALLOW", ""))
    required_tokens = dedupe_preserve(NEUTRAL_TOKEN_RE.findall(out_text))
    allowed_paths = dedupe_preserve(PATH_RE.findall(alw_text))
    payload = {
        "final_answer": {
            "required_tokens": required_tokens,
            "allowed_paths": allowed_paths,
            "state_labels": {},
            "state_transitions": [],
            "boundary_checks": {
                "construction": "deterministic_from_mature_ssr_slots",
                "source_for_required_tokens": "OUT",
                "source_for_allowed_paths": "ALW",
                "no_NO_or_B_material_copied": True,
            },
        }
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def fit_state(text: str, budget: int) -> tuple[str, bool, int, int]:
    before = len(text)
    if before <= budget:
        return text, False, before, len(text)
    return text[:budget], True, before, budget


def build_update_prompt(method: str, task: dict[str, Any], segment: dict[str, Any], state: str, budget: int, visible_text_so_far: str) -> str:
    if method == "rolling_summary":
        method_block = """You are maintaining a plain natural-language rolling summary for later solving.
Use only the current model-visible segment and prior transferred summary.
Do not use hidden answers, labels, oracle fields, scoring metadata, or required/forbidden/protected token arrays.
Do not use typed state fields, deterministic visible-token carry, SSR fields, or special slot labels.
Keep only information you judge useful for the final answer; remove obsolete or excluded material when you can infer it from visible text."""
        schema = '{"SUMMARY":"..."}'
    elif method == "loop_only":
        method_block = """You are processing the current model-visible segment only.
Do not preserve prior segment details except what is explicitly present in this current segment.
Do not use hidden answers, labels, oracle fields, scoring metadata, or required/forbidden/protected token arrays.
Do not use typed state fields, deterministic visible-token carry, SSR fields, or special slot labels."""
        schema = '{"CURRENT_SEGMENT_NOTES":"..."}'
    elif method == "rolling_visible_carry_forward":
        method_block = """You are maintaining a compact visible-only rolling state.
Use only the current model-visible segment and prior transferred state.
Do not use hidden answers, labels, oracle fields, scoring metadata, or required/forbidden/protected token arrays.
Write ordinary compact notes. Do not use SSR fields OUT/ALW/NO/B/G/N/CK/LOOP."""
        schema = '{"NOTE":"...", "BOUNDARY":"..."}'
    else:
        method_block = """You are maintaining a compact structured state for later solving.
Use only the current model-visible segment and prior transferred state.
Do not use hidden answers, labels, oracle fields, scoring metadata, or required/forbidden/protected token arrays.
Use compact fields OUT, ALW, NO, B, G, N, CK, LOOP. NO and B should use generic categories and visible evidence only."""
        schema = '{"OUT":"...", "ALW":"...", "NO":"...", "B":"...", "G":"...", "N":"...", "CK":"...", "LOOP":"..."}'
    return f"""{method_block}

Task id: {task["task_id"]}
Difficulty: {task["difficulty"]}
Family: {task["family"]}
State budget after deterministic fitting: {budget} characters

Prior transferred state:
{state or "[empty]"}

Current segment {segment["segment_id"]}/{len(task["segments"])} ({segment["role"]}):
{segment["text"]}

Return JSON only in this schema:
{schema}
"""


def compile_state(method: str, raw_state: str, visible_text_so_far: str, budget: int) -> tuple[str, dict[str, Any]]:
    candidates = extract_visible_candidates(visible_text_so_far)
    if method == "rolling_summary":
        rendered = raw_state.strip()
        protocol = METHOD_PROTOCOLS[method]
    elif method == "loop_only":
        rendered = raw_state.strip()
        protocol = METHOD_PROTOCOLS[method]
    elif method == "rolling_visible_carry_forward":
        rendered = f"VISIBLE_KEEP={','.join(candidates)}\nNOTE={raw_state.strip()}"
        protocol = METHOD_PROTOCOLS[method]
    else:
        rendered = raw_state.strip()
        if "OUT" not in rendered:
            rendered = f"OUT={','.join(candidates)}\nALW=visible allowed scope only\nNO=excluded or unsafe categories only\nB=no forbidden/protected/revoked/stale/blocked/archive-only/rollback-only output\nG=solve final active allowed set\nN=continue\nCK=check state labels\nLOOP=boundary-risk check"
        protocol = METHOD_PROTOCOLS[method]
    fitted, hard_cap, before, after = fit_state(rendered, budget)
    audit = {
        "method_protocol_version": protocol,
        "visible_identifier_candidates_count": len(candidates),
        "visible_identifier_candidates_sha256": sha256_json(candidates),
        "compiler_input_visible_text_sha256": sha256_bytes(visible_text_so_far.encode("utf-8")),
        "compiler_input_raw_state_sha256": sha256_bytes(raw_state.encode("utf-8")),
        "compiler_output_state_sha256": sha256_bytes(fitted.encode("utf-8")),
        "state_chars_before_budget": before,
        "state_chars_after_budget": after,
        "state_budget": budget,
        "state_budget_fit_success": len(fitted) <= budget,
        "state_hard_cap_used": hard_cap,
        "compiler_forbidden_source_check": "visible_only_no_oracle",
    }
    return fitted, audit


def build_final_prompt(method: str, task: dict[str, Any], state: str) -> str:
    if method == "mature_ssr_loop":
        method_specific = """Mature SSR slot-transfer rule:
- Treat OUT as the only source for final_answer.required_tokens.
- Treat ALW as the only source for final_answer.allowed_paths.
- Extract neutral task tokens only from OUT, and path-like strings only from ALW.
- Never copy anything from NO, B, G, N, CK, LOOP, notes, boundaries, or exclusion fields into required_tokens or allowed_paths.
- If OUT or ALW is empty, return an empty list for that field rather than guessing from NO/B or the original task."""
    elif method == "rolling_visible_carry_forward":
        method_specific = """Visible-carry rule:
- VISIBLE_KEEP is an output-bearing carried field. If it contains excluded candidates, that is a state-governance failure.
- Use NOTE/BOUNDARY only to decide which VISIBLE_KEEP items are safe for final_answer.required_tokens."""
    elif method == "rolling_summary":
        method_specific = """Rolling-summary rule:
- Use only the transferred natural-language summary.
- Do not infer from hidden oracle fields or scorer metadata.
- Output only items the summary supports as currently active/allowed."""
    else:
        method_specific = """Loop-only rule:
- Use only the final transferred current-segment notes.
- Do not reconstruct prior state unless it is present in those notes.
- Output only items the notes support as currently active/allowed."""
    return f"""Use only the transferred state below and the output schema instruction.
Do not use hidden answers, oracle fields, scoring metadata, or any external context.
State-governance rule: output-bearing transferred-state fields such as OUT, ALW, VISIBLE_KEEP, ACTIVE, REQUIRED, or equivalent keep/output fields may only support active or allowed material in the final answer. Excluded candidates may be named only in state_labels, state_transitions, boundary_checks, NO/EXCLUDED fields, or explicit exclusion notes.
{method_specific}

Task id: {task["task_id"]}
Method: {method}

Transferred state:
{state}

Output schema instruction:
{task["final_instruction"]}

Return JSON only.
"""


def method_summary(rows: list[dict[str, Any]], method: str) -> dict[str, Any]:
    method_rows = [row for row in rows if row["method"] == method]

    def count(key: str) -> int:
        return sum(1 for row in method_rows if row.get(key))

    n = len(method_rows)
    return {
        "rows": n,
        "final_exact_success": count("final_exact_success"),
        "final_exact_success_rate": count("final_exact_success") / n if n else 0.0,
        "answer_success": count("answer_success"),
        "answer_success_rate": count("answer_success") / n if n else 0.0,
        "state_governance_success": count("state_governance_success"),
        "state_governance_success_rate": count("state_governance_success") / n if n else 0.0,
        "reliable_composite_success": count("reliable_composite_success"),
        "reliable_composite_success_rate": count("reliable_composite_success") / n if n else 0.0,
        "reliable_success": count("reliable_success"),
        "reliable_success_rate": count("reliable_success") / n if n else 0.0,
        "avg_output_tokens": round(sum(int(row.get("output_tokens") or 0) for row in method_rows) / n, 3) if n else 0.0,
        "avg_provider_call_count": round(sum(int(row.get("provider_call_count") or 0) for row in method_rows) / n, 3) if n else 0.0,
        "state_hard_cap_rows": sum(1 for row in method_rows if row.get("state_hard_cap_used")),
    }


def bootstrap_diff_ci(rows: list[dict[str, Any]], left_method: str, right_method: str, metric: str, samples: int = 5000) -> dict[str, Any]:
    by_key: dict[tuple[str, int, int], dict[str, dict[str, Any]]] = {}
    for row in rows:
        key = (str(row["task_id"]), int(row["state_budget"]), int(row["run_id"]))
        by_key.setdefault(key, {})[str(row["method"])] = row
    diffs: list[float] = []
    for method_rows in by_key.values():
        if left_method in method_rows and right_method in method_rows:
            left = 1.0 if method_rows[left_method].get(metric) else 0.0
            right = 1.0 if method_rows[right_method].get(metric) else 0.0
            diffs.append(left - right)
    if not diffs:
        return {"metric": metric, "paired_units": 0, "point_diff": 0.0, "ci_lower": 0.0, "ci_upper": 0.0}
    rng = random.Random(20260620)
    means: list[float] = []
    for _ in range(samples):
        sample = [diffs[rng.randrange(len(diffs))] for _ in diffs]
        means.append(sum(sample) / len(sample))
    means.sort()
    lower = means[int(0.025 * (len(means) - 1))]
    upper = means[int(0.975 * (len(means) - 1))]
    return {
        "metric": metric,
        "paired_units": len(diffs),
        "point_diff": sum(diffs) / len(diffs),
        "ci_lower": lower,
        "ci_upper": upper,
        "left_method": left_method,
        "right_method": right_method,
        "bootstrap_samples": samples,
        "bootstrap_seed": 20260620,
    }


def preregistered_decision(rows: list[dict[str, Any]], summaries: dict[str, dict[str, Any]]) -> dict[str, Any]:
    diff = bootstrap_diff_ci(rows, "mature_ssr_loop", "rolling_visible_carry_forward", "reliable_composite_success")
    mature = summaries["mature_ssr_loop"]
    visible = summaries["rolling_visible_carry_forward"]
    weak_best = max(
        summaries["rolling_summary"]["reliable_composite_success_rate"],
        summaries["loop_only"]["reliable_composite_success_rate"],
    )
    criteria = {
        "mature_answer_success_rate_at_least_0_70": mature["answer_success_rate"] >= 0.70,
        "mature_reliable_advantage_at_least_0_10_over_visible": (
            mature["reliable_composite_success_rate"] - visible["reliable_composite_success_rate"]
        )
        >= 0.10,
        "mature_reliable_exceeds_weak_baselines": mature["reliable_composite_success_rate"] > weak_best,
    }
    keep = all(criteria.values())
    return {
        "decision": "KEEP_MATURE_SSR_AS_CANDIDATE_MAIN_METHOD" if keep else "DOWNGRADE_MATURE_SSR_TO_ABLATION_DIAGNOSTIC",
        "criteria": criteria,
        "bootstrap_reliable_composite_diff": diff,
        "rules": PREREGISTERED_DECISION_RULES,
    }


def run_one_row(task: dict[str, Any], oracle: dict[str, Any], method: str, budget: int, run_id: int, credential: str, config_sha256: str, runner_sha256: str, scorer_sha256: str) -> dict[str, Any]:
    visible_text_so_far = ""
    state = ""
    call_records: list[dict[str, Any]] = []
    compiler_audits: list[dict[str, Any]] = []
    backend_error = False
    gate_status = "measured"
    gate_reason = "ok"
    returned_model = REQUESTED_MODEL
    reasoning_present_any = False
    reasoning_tokens_observed: Any = "provider_not_exposed"
    input_tokens = 0
    output_tokens = 0

    for segment in task["segments"]:
        visible_text_so_far += "\n" + segment["text"]
        prompt_state = "" if method == "loop_only" else state
        prompt = build_update_prompt(method, task, segment, prompt_state, budget, visible_text_so_far)
        payload = make_request_payload(prompt)
        request_hash = sha256_json(payload)
        raw = request_with_retry(credential, payload)
        content, usage, returned_model, reasoning_present, reasoning_tokens = extract_response_content(raw)
        reasoning_present_any = reasoning_present_any or reasoning_present
        if reasoning_tokens is not None:
            reasoning_tokens_observed = reasoning_tokens
        input_tokens += int(usage.get("prompt_tokens", 0) or usage.get("input_tokens", 0) or 0)
        output_tokens += int(usage.get("completion_tokens", 0) or usage.get("output_tokens", 0) or 0)
        raw_hash = sha256_json(raw)
        call_records.append(
            {
                "call_type": "state_update",
                "segment_id": segment["segment_id"],
                "prompt_hash": sha256_bytes(prompt.encode("utf-8")),
                "request_hash": request_hash,
                "raw_response_sha256": raw_hash,
                "usage": usage,
                "returned_model": returned_model,
            }
        )
        state, compiler_audit = compile_state(method, content, visible_text_so_far, budget)
        compiler_audits.append(compiler_audit)
        if not content:
            backend_error = True

    final_prompt = build_final_prompt(method, task, state)
    final_payload = make_request_payload(final_prompt)
    final_output_construction = "provider_final_call"
    if method == "mature_ssr_loop":
        final_output = deterministic_mature_final_output(state)
        final_payload = {
            "construction": "deterministic_mature_ssr_slot_compiler",
            "state_sha256": sha256_bytes(state.encode("utf-8")),
            "rules": ["required_tokens_from_OUT", "allowed_paths_from_ALW", "NO_B_never_copied"],
        }
        final_raw = {
            "attempts": [
                {
                    "attempt_index": 0,
                    "started_at_utc": utc_now(),
                    "finished_at_utc": utc_now(),
                    "synthetic_final_construction": True,
                    "body": json.dumps(
                        {
                            "model": "deterministic_mature_ssr_slot_compiler",
                            "choices": [{"message": {"content": final_output}}],
                            "usage": {"prompt_tokens": 0, "completion_tokens": 0},
                        },
                        ensure_ascii=False,
                    ),
                }
            ]
        }
        final_usage = {"prompt_tokens": 0, "completion_tokens": 0}
        final_output_construction = "deterministic_mature_ssr_slot_compiler"
    else:
        final_raw = request_with_retry(credential, final_payload)
        final_output, final_usage, returned_model, reasoning_present, reasoning_tokens = extract_response_content(final_raw)
        reasoning_present_any = reasoning_present_any or reasoning_present
        if reasoning_tokens is not None:
            reasoning_tokens_observed = reasoning_tokens
    final_request_hash = sha256_json(final_payload)
    input_tokens += int(final_usage.get("prompt_tokens", 0) or final_usage.get("input_tokens", 0) or 0)
    output_tokens += int(final_usage.get("completion_tokens", 0) or final_usage.get("output_tokens", 0) or 0)
    if not final_output:
        backend_error = True
    if backend_error:
        gate_status = "rerun_required"
        gate_reason = "backend_or_empty_output"
    if reasoning_present_any:
        gate_status = "excluded"
        gate_reason = "reasoning_content_present"

    parsed_output = {"final_output": final_output, "final_state": state}
    parsed_output_sha256 = sha256_json(parsed_output)
    raw_response_sha256 = sha256_json({"state_calls": call_records, "final_raw": final_raw})
    scorer = load_module(SCORER_PATH, "pcg_dynamic_state_v2_scorer")
    metric = scorer.score_task(
        oracle,
        {
            "task_id": task["task_id"],
            "method": method,
            "model": REQUESTED_MODEL,
            "budget": budget,
            "run_id": run_id,
            "final_output": final_output,
            "final_state": state,
        },
    )
    metric_record_sha256 = sha256_json(metric)
    prompt_hash = sha256_json({"state_update_prompts": [item["prompt_hash"] for item in call_records], "final_prompt": final_prompt})
    global_artifact_id = f"{EXPERIMENT_ID}::{task['task_id']}::{method}::budget{budget}::run{run_id}"
    manifest_entry = {
        "global_artifact_id": global_artifact_id,
        "task_id": task["task_id"],
        "method": method,
        "budget": budget,
        "run_id": run_id,
        "config_sha256": config_sha256,
        "task_manifest_sha256": file_sha256(MODEL_VISIBLE_SUBSET),
        "prompt_hash": prompt_hash,
        "runner_sha256": runner_sha256,
        "scorer_oracle_sha256": file_sha256(SCORER_ORACLE_SUBSET),
        "environment_hash_or_commit": git_commit(),
        "request_hash": final_request_hash,
        "raw_response_sha256": raw_response_sha256,
        "parsed_output_sha256": parsed_output_sha256,
        "metric_record_sha256": metric_record_sha256,
    }
    manifest_entry_hash = sha256_json(manifest_entry)
    h5_chain_hash = sha256_json({**manifest_entry, "manifest_entry_hash": manifest_entry_hash})
    private_raw_ref = RAW_DIR / f"{method}__{task['task_id']}__run_{run_id}__budget_{budget}.jsonl"
    write_jsonl(private_raw_ref, [{"global_artifact_id": global_artifact_id, "state_calls": call_records, "final_raw": final_raw}])
    row = {
        **manifest_entry,
        "manifest_entry_hash": manifest_entry_hash,
        "h5_chain_hash": h5_chain_hash,
        "experiment_id": EXPERIMENT_ID,
        "condition_id": CONDITION_ID,
        "provider": PROVIDER,
        "base_url": BASE_URL,
        "requested_model": REQUESTED_MODEL,
        "selected_model_or_returned_model": returned_model,
        "fallback_enabled": False,
        "temperature_send_mode": "explicit",
        "temperature_value": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "reasoning_disable_mode": "thinking.type=disabled",
        "reasoning_tokens_observed": reasoning_tokens_observed,
        "reasoning_content_present": reasoning_present_any,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "call_count": len(call_records) + 1,
        "provider_call_count": len(call_records) + (0 if method == "mature_ssr_loop" else 1),
        "final_output_construction": final_output_construction,
        "state_budget": budget,
        "state_hard_cap_used": any(item["state_hard_cap_used"] for item in compiler_audits),
        "backend_error": backend_error,
        "gate_status": gate_status,
        "gate_reason": gate_reason,
        "final_output": final_output,
        "final_state": state,
        "private_raw_ref": rel(private_raw_ref),
        "compiler_audits": compiler_audits,
        **metric,
    }
    return row


def run_api(max_workers: int) -> None:
    audit = json.loads(PREFLIGHT_AUDIT_JSON.read_text(encoding="utf-8"))
    assert_preflight_passed(audit)
    credential = get_api_key()
    visible = read_jsonl(MODEL_VISIBLE_SUBSET)
    oracle_by_id = {row["task_id"]: row for row in read_jsonl(SCORER_ORACLE_SUBSET)}
    config_sha256 = file_sha256(CONFIG_PATH)
    runner_sha256 = file_sha256(Path(__file__).resolve())
    scorer_sha256 = file_sha256(SCORER_PATH)
    work_items = [
        (task, oracle_by_id[task["task_id"]], method, budget, run_id)
        for task in visible
        for method in METHODS
        for budget in STATE_BUDGETS
        for run_id in range(1, RUNS + 1)
    ]
    rows: list[dict[str, Any]] = []
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [
            pool.submit(run_one_row, task, oracle, method, budget, run_id, credential, config_sha256, runner_sha256, scorer_sha256)
            for task, oracle, method, budget, run_id in work_items
        ]
        for future in as_completed(futures):
            rows.append(future.result())
            print(f"completed {len(rows)}/{len(work_items)}", flush=True)
    rows.sort(key=lambda r: (r["task_id"], r["method"], int(r["state_budget"]), int(r["run_id"])))
    write_jsonl(CONTROLLED_ROWS, rows)
    score_rows = [{k: v for k, v in row.items() if k in {
        "task_id", "method", "model", "budget", "run_id", "required_token_recall",
        "required_token_missing_count", "missing_required_tokens", "forbidden_token_leakage",
        "forbidden_token_hits", "protected_token_leakage", "protected_token_hits",
        "revoked_token_leakage", "revoked_token_hits", "stale_token_leakage",
        "stale_token_hits", "blocked_path_leakage", "blocked_path_hits",
        "boundary_violation", "state_label_accuracy", "state_transition_accuracy",
        "final_exact_success", "answer_success", "state_governance_success",
        "reliable_composite_success", "reliable_success", "state_required_token_present",
        "state_required_token_negated", "state_internal_conflict",
        "output_bearing_state_conflict", "exclusion_field_conflict",
        "state_forbidden_token_present", "state_forbidden_token_negated",
        "mechanical_carry_failure_mode_detected", "state_budget",
        "provider_call_count", "final_output_construction"
    }} for row in rows]
    write_jsonl(SCORES_JSONL, score_rows)
    write_csv(SCORES_CSV, score_rows)
    summary_by_method = {method: method_summary(rows, method) for method in METHODS}
    decision = preregistered_decision(rows, summary_by_method)
    write_hash_files()
    summary_lines = "\n".join(
        "| `{method}` | {rows} | {final_exact_success} | {final_exact_success_rate:.3f} | {answer_success} | {answer_success_rate:.3f} | {state_governance_success} | {state_governance_success_rate:.3f} | {reliable_composite_success} | {reliable_composite_success_rate:.3f} | {avg_output_tokens:.3f} | {avg_provider_call_count:.3f} | {state_hard_cap_rows} |".format(
            method=method,
            **stats,
        )
        for method, stats in summary_by_method.items()
    )
    criteria_lines = "\n".join(
        f"- `{name}`: `{value}`" for name, value in decision["criteria"].items()
    )
    diff = decision["bootstrap_reliable_composite_diff"]
    POST_RUN_AUDIT_MD.write_text(
        "# Post-Run Audit\n\n"
        f"Experiment: `{EXPERIMENT_ID}`\n\n"
        f"Rows: `{len(rows)}` / expected `{EXPECTED_ROWS}`\n\n"
        f"Reasoning content present rows: `{sum(1 for row in rows if row.get('reasoning_content_present'))}`\n\n"
        f"Backend/rerun rows: `{sum(1 for row in rows if row.get('backend_error'))}`\n\n"
        "## Success By Method\n\n"
        "| method | rows | final_exact | final_exact_rate | answer | answer_rate | state_gov | state_gov_rate | reliable_composite | reliable_rate | avg_output_tokens | avg_provider_calls | state_hard_cap_rows |\n"
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n"
        + summary_lines
        + "\n\n## Pre-Registered Decision\n\n"
        f"Decision: `{decision['decision']}`\n\n"
        f"Bootstrap reliable composite diff (`mature_ssr_loop - rolling_visible_carry_forward`): point `{diff['point_diff']:.3f}`, 95% CI `[{diff['ci_lower']:.3f}, {diff['ci_upper']:.3f}]`, paired units `{diff['paired_units']}`.\n\n"
        "Criteria:\n\n"
        + criteria_lines
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({"rows": len(rows), "summary_by_method": summary_by_method, "decision": decision}, ensure_ascii=False, indent=2))


def verify_sha256s() -> bool:
    ok = True
    if not PREFLIGHT_SHA256SUMS.exists():
        return False
    for line in PREFLIGHT_SHA256SUMS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, path_text = line.split("  ", 1)
        path = PROJECT_ROOT / path_text
        if not path.exists() or file_sha256(path) != expected:
            ok = False
    return ok


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-api", action="store_true", help="Actually call DeepSeek. Default is preflight-only.")
    parser.add_argument("--max-workers", type=int, default=DEFAULT_MAX_WORKERS)
    args = parser.parse_args()

    audit = write_preflight_files()
    print(json.dumps({
        "experiment_id": EXPERIMENT_ID,
        "preflight_status": audit["overall_status"],
        "expected_rows": EXPECTED_ROWS,
        "selected_tasks": audit["selected_task_ids"],
        "config": rel(CONFIG_PATH),
        "run_plan": rel(RUN_PLAN_MD),
        "preflight_sha256sums_ok": verify_sha256s(),
    }, ensure_ascii=False, indent=2))
    if args.run_api:
        run_api(max_workers=args.max_workers)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
