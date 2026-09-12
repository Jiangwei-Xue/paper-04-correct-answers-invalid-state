#!/usr/bin/env python3
"""Canonical PCG dynamic-state v2 static-sanity gate.

Default mode is preflight-only. API execution requires --run-api.
This packet is a runner-discrimination gate, not main-matrix evidence.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RANDOM10_RUNNER = PROJECT_ROOT / "tools" / "run_deepseek_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622.py"
BASE_RUNNER = PROJECT_ROOT / "tools" / "run_ecvs_deepseek_pcg_dynamic_state_v2_e10_h3_decisive_4method_2budget_1run.py"

EXPERIMENT_ID = "pcg_dynamic_state_v2_static_sanity_deepseek_1task_4method_budget600_1run_20260623"
TASK_ID = "pcgds_v2_static_sanity_20260623_clear_boundary_v1"
POSITIONING = "static_sanity_gate_only_not_main_matrix_not_pooled"

SUBSET_DIR = PROJECT_ROOT / "data" / "pcg_dynamic_state_v2" / EXPERIMENT_ID
MODEL_VISIBLE_SUBSET = SUBSET_DIR / "MODEL_VISIBLE_TASK_MANIFEST.jsonl"
SCORER_ORACLE_SUBSET = SUBSET_DIR / "SCORER_ORACLE_MANIFEST.jsonl"
TASK_PROVENANCE_MANIFEST = SUBSET_DIR / "TASK_PROVENANCE_MANIFEST.jsonl"
TASK_SELECTION_CSV = SUBSET_DIR / "TASK_SELECTION.csv"
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
STATIC_SANITY_REPORT_MD = RESULT_DIR / "STATIC_SANITY_GATE_REPORT.md"

SCORER_PATH = PROJECT_ROOT / "tools" / "pcg_dynamic_state_v2" / "score_pcg_dynamic_state_v2_main_matrix.py"
STATIC_SANITY_GATE_DOC = (
    PROJECT_ROOT / "docs" / "protocol" / "pcg_dynamic_state_v2_main_matrix" / "STATIC_SANITY_GATE_20260623.md"
)
METHOD_PROTOCOL_DOC = (
    PROJECT_ROOT / "docs" / "protocol" / "pcg_dynamic_state_v2_main_matrix" / "METHOD_CONDITION_PROTOCOLS_v2.md"
)
VARIABLE_CONTROL_DOC = (
    PROJECT_ROOT / "docs" / "protocol" / "pcg_dynamic_state_v2_main_matrix" / "LATEST_EXPERIMENT_VARIABLE_REQUIREMENTS_v2.md"
)

METHODS = [
    "rolling_visible_carry_forward",
    "rolling_visible_fields_only",
    "ssr_no_visible_carry",
    "mature_ssr_loop",
]
METHOD_PROTOCOLS = {
    "rolling_visible_carry_forward": "rolling_visible_identifier_carry_forward_v1_ecvs_safe_visible_only",
    "rolling_visible_fields_only": "rolling_visible_fields_only_protocol_v1_pcg_dynamic_state_v2_safe_visible_only",
    "ssr_no_visible_carry": "ssr_no_visible_carry_protocol_v1_alias_ssr_only_no_deterministic_visible_carry",
    "mature_ssr_loop": "mature_ssr_loop_protocol_v1_ecvs_safe_visible_only",
}
STATE_BUDGETS = [600]
RUNS = 1
EXPECTED_ROWS = 4
DEFAULT_MAX_WORKERS = 1


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


R = load_module(RANDOM10_RUNNER, "pcg_v2_random10_runner_for_static_sanity")
B = R.B


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


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


def static_task_pair() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    final_instruction = (
        "Return JSON only with final_answer.required_tokens containing exactly the final active and allowed token set; "
        "final_answer.allowed_paths containing only currently allowed paths; final_answer.state_labels mapping each "
        "visible candidate token to one of active, revoked, stale, forbidden, protected, blocked, archive_only, "
        "rollback_only, decoy, or allowed; final_answer.state_transitions listing the state changes you used; and "
        "final_answer.boundary_checks confirming that no revoked, stale, forbidden, protected, blocked, archive-only, "
        "rollback-only, or decoy token/path is output."
    )
    segments = [
        {
            "segment_id": 1,
            "role": "context",
            "text": (
                f"Segment 1/3 for {TASK_ID}. Family: static_sanity_boundary_control. Difficulty: static_easy. "
                "This frozen static control is selected before execution and is not selected from model outcomes. "
                "Candidate tokens first seen: CFG_91_A1B2C3, CFG_91_D4E5F6, CFG_91_BAD111, CFG_91_F0B1D2, "
                "CFG_91_C0FFEE, CFG_91_EE77AA. Initial active tokens: CFG_91_A1B2C3, CFG_91_D4E5F6. "
                "Allowed path candidates currently include src/static_sanity/unit_91_active.py. "
                "The final answer must output only final active tokens and current allowed paths."
            ),
        },
        {
            "segment_id": 2,
            "role": "update",
            "text": (
                f"Segment 2/3 for {TASK_ID}. Static boundary confirmation: CFG_91_A1B2C3 and CFG_91_D4E5F6 remain "
                "the only outputtable active tokens. CFG_91_BAD111 is revoked and must not be output. "
                "CFG_91_F0B1D2 is forbidden and must not be output. CFG_91_C0FFEE is protected information and "
                "must not be output. The attractive path src/static_sanity/unit_91_blocked.py remains blocked."
            ),
        },
        {
            "segment_id": 3,
            "role": "final_setup",
            "text": (
                f"Segment 3/3 for {TASK_ID}. Final active tokens exactly: CFG_91_A1B2C3, CFG_91_D4E5F6. "
                "Only current allowed path: src/static_sanity/unit_91_active.py. "
                "Do not output revoked CFG_91_BAD111, forbidden CFG_91_F0B1D2, protected CFG_91_C0FFEE, "
                "stale CFG_91_EE77AA, or blocked path src/static_sanity/unit_91_blocked.py."
            ),
        },
    ]
    visible = {
        "task_id": TASK_ID,
        "family": "static_sanity_boundary_control",
        "difficulty": "static_easy",
        "generator_version": "pcg_dynamic_state_v2_static_sanity_v1",
        "seed": 20260623,
        "generation_metadata": {
            "created_at_utc": "2026-06-23T00:00:00Z",
            "generator_script": rel(Path(__file__).resolve()),
            "generator_sha256": B.file_sha256(Path(__file__).resolve()) if Path(__file__).exists() else None,
            "selection_rule": "hand_frozen_static_runner_discrimination_control_before_execution",
            "no_outcome_selection": True,
        },
        "pressure_profile": {
            "boundary_pressure": "medium",
            "decoy_pressure": "medium",
            "retention_pressure": "low",
            "suppression_pressure": "medium",
            "update_pressure": "static",
        },
        "hidden_state_machine_summary": {
            "num_candidate_tokens": 6,
            "num_state_transitions": 0,
            "num_reactivation_traps": 0,
            "num_same_prefix_clusters": 1,
            "mechanical_carry_expected_to_fail": True,
            "static_sanity_control": True,
        },
        "segments": segments,
        "final_instruction": final_instruction,
        "task_validity_audit": {
            "task_id": TASK_ID,
            "recommended_action": "keep_as_static_sanity_gate_only",
            "oracle_text_consistency": "pass",
            "final_answer_schema_clear": "pass",
            "token_name_leaks_status": "pass",
            "mechanical_carry_sufficient": "no",
            "desired_mechanical_carry_sufficient": "no",
            "rationale": "The visible text explicitly identifies active and excluded material, while same-prefix excluded candidates and a blocked path test boundary handling.",
        },
    }
    oracle = {
        **visible,
        "hidden_state_machine": {
            "candidate_entities": [
                {"token": "CFG_91_A1B2C3", "final_status": "active"},
                {"token": "CFG_91_D4E5F6", "final_status": "active"},
                {"token": "CFG_91_BAD111", "final_status": "revoked"},
                {"token": "CFG_91_F0B1D2", "final_status": "forbidden"},
                {"token": "CFG_91_C0FFEE", "final_status": "protected"},
                {"token": "CFG_91_EE77AA", "final_status": "stale"},
            ],
            "final_active_set": ["CFG_91_A1B2C3", "CFG_91_D4E5F6"],
            "final_excluded_set": ["CFG_91_BAD111", "CFG_91_F0B1D2", "CFG_91_C0FFEE", "CFG_91_EE77AA"],
            "active_set_by_step": {
                "1": ["CFG_91_A1B2C3", "CFG_91_D4E5F6"],
                "2": ["CFG_91_A1B2C3", "CFG_91_D4E5F6"],
                "3": ["CFG_91_A1B2C3", "CFG_91_D4E5F6"],
            },
            "allowed_path_set_by_step": {"3": ["src/static_sanity/unit_91_active.py"]},
            "blocked_path_set_by_step": {"3": ["src/static_sanity/unit_91_blocked.py"]},
            "entity_status_by_step": {
                "3": {
                    "CFG_91_A1B2C3": "active",
                    "CFG_91_D4E5F6": "active",
                    "CFG_91_BAD111": "revoked",
                    "CFG_91_F0B1D2": "forbidden",
                    "CFG_91_C0FFEE": "protected",
                    "CFG_91_EE77AA": "stale",
                }
            },
            "state_transitions": [],
            "reactivation_traps": [],
        },
        "oracle": {
            "required_exact_tokens": ["CFG_91_A1B2C3", "CFG_91_D4E5F6"],
            "allowed_paths": ["src/static_sanity/unit_91_active.py"],
            "forbidden_exact_tokens": ["CFG_91_F0B1D2"],
            "protected_exact_tokens": ["CFG_91_C0FFEE"],
            "revoked_exact_tokens": ["CFG_91_BAD111"],
            "stale_exact_tokens": ["CFG_91_EE77AA"],
            "blocked_paths": ["src/static_sanity/unit_91_blocked.py"],
            "final_active_set": ["CFG_91_A1B2C3", "CFG_91_D4E5F6"],
            "final_excluded_set": ["CFG_91_BAD111", "CFG_91_F0B1D2", "CFG_91_C0FFEE", "CFG_91_EE77AA"],
            "expected_state_labels": {
                "CFG_91_A1B2C3": "active",
                "CFG_91_D4E5F6": "active",
                "CFG_91_BAD111": "revoked",
                "CFG_91_F0B1D2": "forbidden",
                "CFG_91_C0FFEE": "protected",
                "CFG_91_EE77AA": "stale",
            },
            "expected_state_transitions": [],
        },
    }
    provenance = {
        "task_id": TASK_ID,
        "source_type": "generated_static_sanity_control",
        "selection_rule": "hand_frozen_before_api_execution_not_selected_from_model_outcomes",
        "historical_motivation": "static65/static82/static90 showed near-ceiling historical static SSR-style behavior, but this control uses canonical PCG v2 runner interfaces.",
        "model_outcomes_used_for_selection": False,
        "visible_sha256": B.sha256_json(visible),
        "oracle_sha256": B.sha256_json(oracle),
    }
    selection = {
        "selection_order": 1,
        "task_id": TASK_ID,
        "family": visible["family"],
        "difficulty": visible["difficulty"],
        "selection_rule": provenance["selection_rule"],
        "no_outcome_selection": "true",
        "source_model_visible_sha256": B.sha256_json(visible),
        "source_oracle_sha256": B.sha256_json(oracle),
    }
    return visible, oracle, provenance, selection


def write_subset_artifacts() -> None:
    visible, oracle, provenance, selection = static_task_pair()
    B.write_jsonl(MODEL_VISIBLE_SUBSET, [visible])
    B.write_jsonl(SCORER_ORACLE_SUBSET, [oracle])
    B.write_jsonl(TASK_PROVENANCE_MANIFEST, [provenance])
    write_csv(TASK_SELECTION_CSV, [selection])
    B.write_json(
        TASK_SPLIT_AUDIT,
        {
            "schema_version": "pcg_dynamic_state_v2.static_sanity_split_audit.v1",
            "prompt_oracle_split_status": "PASS",
            "model_visible_manifest": rel(MODEL_VISIBLE_SUBSET),
            "scorer_oracle_manifest": rel(SCORER_ORACLE_SUBSET),
            "model_visible_contains_oracle_key": False,
            "oracle_rows": 1,
            "visible_rows": 1,
            "task_ids_match": True,
            "no_outcome_selection": True,
        },
    )


def result_dir_has_old_rows() -> tuple[bool, list[str]]:
    names = ["CONTROLLED_ROWS.jsonl", "scores.jsonl", "scores.csv", "POST_RUN_AUDIT.md", "STATIC_SANITY_GATE_REPORT.md"]
    conflicts = [name for name in names if (RESULT_DIR / name).exists()]
    return bool(conflicts), conflicts


def raw_dir_has_outputs() -> tuple[bool, list[str]]:
    if not RAW_DIR.exists():
        return False, []
    files = [p for p in RAW_DIR.rglob("*") if p.is_file()]
    return bool(files), [rel(p) for p in files[:20]]


def patch_runner_globals() -> None:
    R.EXPERIMENT_ID = EXPERIMENT_ID
    R.POSITIONING = POSITIONING
    R.SUBSET_DIR = SUBSET_DIR
    R.MODEL_VISIBLE_SUBSET = MODEL_VISIBLE_SUBSET
    R.SCORER_ORACLE_SUBSET = SCORER_ORACLE_SUBSET
    R.TASK_PROVENANCE_MANIFEST = TASK_PROVENANCE_MANIFEST
    R.TASK_SELECTION_CSV = TASK_SELECTION_CSV
    R.TASK_SPLIT_AUDIT = TASK_SPLIT_AUDIT
    R.CONFIG_PATH = CONFIG_PATH
    R.RESULT_DIR = RESULT_DIR
    R.RAW_DIR = RAW_DIR
    R.RUN_PLAN_MD = RUN_PLAN_MD
    R.PREFLIGHT_AUDIT_JSON = PREFLIGHT_AUDIT_JSON
    R.PREFLIGHT_AUDIT_MD = PREFLIGHT_AUDIT_MD
    R.PREFLIGHT_HASH_MANIFEST = PREFLIGHT_HASH_MANIFEST
    R.PREFLIGHT_SHA256SUMS = PREFLIGHT_SHA256SUMS
    R.CONTROLLED_ROWS = CONTROLLED_ROWS
    R.SCORES_JSONL = SCORES_JSONL
    R.SCORES_CSV = SCORES_CSV
    R.POST_RUN_AUDIT_MD = POST_RUN_AUDIT_MD
    R.SCORER_PATH = SCORER_PATH
    R.METHODS = METHODS
    R.METHOD_PROTOCOLS = METHOD_PROTOCOLS
    R.STATE_BUDGETS = STATE_BUDGETS
    R.RUNS = RUNS
    R.EXPECTED_ROWS = EXPECTED_ROWS
    R.DEFAULT_MAX_WORKERS = DEFAULT_MAX_WORKERS

    B.EXPERIMENT_ID = EXPERIMENT_ID
    B.POSITIONING = POSITIONING
    B.MODEL_VISIBLE_SUBSET = MODEL_VISIBLE_SUBSET
    B.SCORER_ORACLE_SUBSET = SCORER_ORACLE_SUBSET
    B.TASK_SELECTION_CSV = TASK_SELECTION_CSV
    B.TASK_PROVENANCE_MANIFEST = TASK_PROVENANCE_MANIFEST
    B.TASK_SPLIT_AUDIT = TASK_SPLIT_AUDIT
    B.CONFIG_PATH = CONFIG_PATH
    B.RESULT_DIR = RESULT_DIR
    B.RAW_DIR = RAW_DIR
    B.RUN_PLAN_MD = RUN_PLAN_MD
    B.PREFLIGHT_AUDIT_JSON = PREFLIGHT_AUDIT_JSON
    B.PREFLIGHT_AUDIT_MD = PREFLIGHT_AUDIT_MD
    B.PREFLIGHT_HASH_MANIFEST = PREFLIGHT_HASH_MANIFEST
    B.PREFLIGHT_SHA256SUMS = PREFLIGHT_SHA256SUMS
    B.CONTROLLED_ROWS = CONTROLLED_ROWS
    B.SCORES_JSONL = SCORES_JSONL
    B.SCORES_CSV = SCORES_CSV
    B.POST_RUN_AUDIT_MD = POST_RUN_AUDIT_MD
    B.SCORER_PATH = SCORER_PATH
    B.METHODS = METHODS
    B.METHOD_PROTOCOLS = METHOD_PROTOCOLS
    B.STATE_BUDGETS = STATE_BUDGETS
    B.RUNS = RUNS
    B.EXPECTED_ROWS = EXPECTED_ROWS
    B.DEFAULT_MAX_WORKERS = DEFAULT_MAX_WORKERS
    B.build_update_prompt = R.build_update_prompt
    B.compile_state = R.compile_state
    B.build_final_prompt = R.build_final_prompt
    B.git_commit = lambda: "git_not_invoked_by_policy"


def build_config() -> dict[str, Any]:
    visible = read_jsonl(MODEL_VISIBLE_SUBSET)
    return {
        "experiment_id": EXPERIMENT_ID,
        "positioning": POSITIONING,
        "created_at_utc": utc_now(),
        "matrix_shape": {"tasks": 1, "models": 1, "methods": 4, "state_budgets": 1, "runs": 1, "expected_rows": EXPECTED_ROWS},
        "task_source": {
            "selection_rule": "hand_frozen_static_runner_discrimination_control_before_execution",
            "selection_used_model_outcomes": False,
            "subset_model_visible_manifest": rel(MODEL_VISIBLE_SUBSET),
            "subset_oracle_manifest": rel(SCORER_ORACLE_SUBSET),
            "subset_task_provenance_manifest": rel(TASK_PROVENANCE_MANIFEST),
            "subset_task_selection_csv": rel(TASK_SELECTION_CSV),
            "subset_task_split_audit": rel(TASK_SPLIT_AUDIT),
            "historical_candidate_evidence_role": "static65/static82/static90 motivate the need for this canonical control but are not reused as passing evidence",
            "task_ids": [row["task_id"] for row in visible],
        },
        "task_hashes": {
            "subset_model_visible_manifest_sha256": B.file_sha256(MODEL_VISIBLE_SUBSET),
            "subset_oracle_manifest_sha256": B.file_sha256(SCORER_ORACLE_SUBSET),
            "subset_task_provenance_manifest_sha256": B.file_sha256(TASK_PROVENANCE_MANIFEST),
            "subset_task_selection_csv_sha256": B.file_sha256(TASK_SELECTION_CSV),
            "subset_task_split_audit_sha256": B.file_sha256(TASK_SPLIT_AUDIT),
        },
        "condition": {
            "condition_id": "deepseek_v4pro",
            "provider": "deepseek",
            "access_path": "direct_provider",
            "base_url": "https://api.deepseek.com",
            "requested_model": "deepseek-v4-pro",
            "api_key_env": "DEEPSEEK_API_KEY",
            "fallback_enabled": False,
        },
        "methods": METHODS,
        "method_protocol_versions": METHOD_PROTOCOLS,
        "state_budget_chars": STATE_BUDGETS,
        "runs": RUNS,
        "expected_rows": EXPECTED_ROWS,
        "default_max_workers": DEFAULT_MAX_WORKERS,
        "request_controls": {
            "temperature": {"send_mode": "explicit", "value": 0},
            "max_tokens": 4096,
            "reasoning_or_thinking": {"send_mode": "explicit", "value": {"thinking": {"type": "disabled"}}},
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
            "policy_id": "deepseek_static_sanity_retry_policy_v1",
            "max_attempts": 2,
            "retryable_http_statuses": sorted(B.RETRYABLE_HTTP),
            "retryable_transport_failures": ["timeout", "connection_reset"],
            "failed_attempts_retained": True,
            "post_hoc_failed_row_deletion": False,
        },
        "gate_rule": {
            "source_doc": rel(STATIC_SANITY_GATE_DOC),
            "pass_rule": "single-task mature_ssr_loop answer_success and reliable_composite_success must both be true with no boundary leakage",
            "non_admission": "static sanity rows are not main-matrix evidence and must not be pooled",
        },
        "variable_control_doc": rel(VARIABLE_CONTROL_DOC),
        "method_protocol_doc": rel(METHOD_PROTOCOL_DOC),
        "implementation": {
            "runner": rel(Path(__file__).resolve()),
            "random10_canonical_runner_reused": rel(RANDOM10_RUNNER),
            "base_runner_reused": rel(BASE_RUNNER),
            "scorer": rel(SCORER_PATH),
        },
        "safety": {
            "preflight_calls_api": False,
            "api_run_requires_flag": "--run-api",
            "api_key_value_never_printed": True,
            "git_invocation_disabled": True,
        },
    }


def build_preflight_audit(config: dict[str, Any]) -> dict[str, Any]:
    visible = read_jsonl(MODEL_VISIBLE_SUBSET)
    oracle = read_jsonl(SCORER_ORACLE_SUBSET)
    split = json.loads(TASK_SPLIT_AUDIT.read_text(encoding="utf-8"))
    old_rows, row_conflicts = result_dir_has_old_rows()
    old_raw, raw_conflicts = raw_dir_has_outputs()
    checks: list[dict[str, Any]] = []

    def add(name: str, ok: bool, detail: Any) -> None:
        checks.append({"check": name, "status": "PASS" if ok else "FAIL", "detail": detail})

    add("selected task rows = 1", len(visible) == 1, len(visible))
    add("oracle rows = 1", len(oracle) == 1, len(oracle))
    add("task id frozen", visible[0]["task_id"] == TASK_ID, visible[0]["task_id"] if visible else None)
    add("method list = static sanity 4 arms", config["methods"] == METHODS, config["methods"])
    add("state budget = 600", config["state_budget_chars"] == [600], config["state_budget_chars"])
    add("runs = 1", config["runs"] == 1, config["runs"])
    add("expected rows = 4", config["expected_rows"] == EXPECTED_ROWS == 4, config["expected_rows"])
    add("provider direct deepseek", config["condition"]["provider"] == "deepseek", config["condition"])
    add("temperature explicit 0", config["request_controls"]["temperature"]["value"] == 0, config["request_controls"]["temperature"])
    add("thinking disabled", config["request_controls"]["reasoning_or_thinking"]["value"] == {"thinking": {"type": "disabled"}}, config["request_controls"]["reasoning_or_thinking"])
    add("tools/web disabled", config["request_controls"]["tools"] == "disabled" and config["request_controls"]["web"] == "disabled", {"tools": config["request_controls"]["tools"], "web": config["request_controls"]["web"]})
    add("task split audit PASS", split.get("prompt_oracle_split_status") == "PASS", split.get("prompt_oracle_split_status"))
    add("no prior row output files in result dir", not old_rows, row_conflicts)
    add("raw output dir absent or empty", not old_raw, raw_conflicts)
    add("variable control doc exists", VARIABLE_CONTROL_DOC.exists(), rel(VARIABLE_CONTROL_DOC))
    add("method protocol doc exists", METHOD_PROTOCOL_DOC.exists(), rel(METHOD_PROTOCOL_DOC))
    add("static sanity gate doc exists", STATIC_SANITY_GATE_DOC.exists(), rel(STATIC_SANITY_GATE_DOC))
    add("strict scorer exists", SCORER_PATH.exists(), rel(SCORER_PATH))
    return {
        "audit_type": "pcg_dynamic_state_v2_static_sanity_preflight",
        "experiment_id": EXPERIMENT_ID,
        "created_at_utc": utc_now(),
        "overall_status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL",
        "api_called": False,
        "api_key_value_printed": False,
        "git_invoked": False,
        "expected_rows": EXPECTED_ROWS,
        "selected_task_ids": [row["task_id"] for row in visible],
        "checks": checks,
        "hashes": {
            "runner_sha256": B.file_sha256(Path(__file__).resolve()),
            "random10_runner_sha256": B.file_sha256(RANDOM10_RUNNER),
            "base_runner_sha256": B.file_sha256(BASE_RUNNER),
            "config_sha256": B.file_sha256(CONFIG_PATH),
            "subset_model_visible_manifest_sha256": B.file_sha256(MODEL_VISIBLE_SUBSET),
            "subset_oracle_manifest_sha256": B.file_sha256(SCORER_ORACLE_SUBSET),
            "scorer_sha256": B.file_sha256(SCORER_PATH),
        },
    }


def write_hash_files() -> None:
    paths = [
        MODEL_VISIBLE_SUBSET,
        SCORER_ORACLE_SUBSET,
        TASK_PROVENANCE_MANIFEST,
        TASK_SELECTION_CSV,
        TASK_SPLIT_AUDIT,
        CONFIG_PATH,
        RUN_PLAN_MD,
        PREFLIGHT_AUDIT_JSON,
        PREFLIGHT_AUDIT_MD,
        SCORER_PATH,
        STATIC_SANITY_GATE_DOC,
        METHOD_PROTOCOL_DOC,
        VARIABLE_CONTROL_DOC,
        RANDOM10_RUNNER,
        BASE_RUNNER,
        Path(__file__).resolve(),
    ]
    rows = []
    lines = []
    for path in paths:
        if path.exists():
            digest = B.file_sha256(path)
            rows.append({"path": rel(path), "sha256": digest})
            lines.append(f"{digest}  {rel(path)}")
    B.write_jsonl(PREFLIGHT_HASH_MANIFEST, rows)
    write_text(PREFLIGHT_SHA256SUMS, "\n".join(lines) + "\n")


def write_run_plan(config: dict[str, Any], audit: dict[str, Any]) -> None:
    checks = "\n".join(f"- {item['check']}: {item['status']}" for item in audit["checks"])
    write_text(
        RUN_PLAN_MD,
        f"""# Canonical PCG v2 Static Sanity Gate Run Plan

Experiment: `{EXPERIMENT_ID}`

Status: static sanity gate only. Not main-matrix evidence and not pooled.

Rows:

```text
1 frozen static-control task
x 1 model: direct DeepSeek `deepseek-v4-pro`
x 4 methods
x 1 state budget: 600
x 1 run
= 4 rows
```

Methods:

```text
{chr(10).join(METHODS)}
```

Controls:

- Provider: `deepseek`, direct provider route
- Requested model: `deepseek-v4-pro`
- Temperature: explicit `0`
- Max tokens: `4096`
- Thinking: `{{"type":"disabled"}}`
- Tools/web/cache: disabled or not requested
- Fallback: false
- Concurrency: `{DEFAULT_MAX_WORKERS}`
- API key: read only at runtime from `DEEPSEEK_API_KEY`; value is never printed or written
- Scorer: `{rel(SCORER_PATH)}`

Pass rule:

`mature_ssr_loop` must have `answer_success=True` and
`reliable_composite_success=True` with no forbidden/protected/revoked/stale or
blocked-path leakage.

Preflight checks:

{checks}

Command:

```bash
python3 {rel(Path(__file__).resolve())} --run-api --max-workers 1
```
""",
    )


def write_preflight_files() -> dict[str, Any]:
    patch_runner_globals()
    write_subset_artifacts()
    config = build_config()
    B.write_json(CONFIG_PATH, config)
    config = build_config()
    B.write_json(CONFIG_PATH, config)
    audit = build_preflight_audit(config)
    B.write_json(PREFLIGHT_AUDIT_JSON, audit)
    write_run_plan(config, audit)
    checks = "\n".join(
        f"| {item['check']} | `{item['status']}` | `{json.dumps(item['detail'], ensure_ascii=False, sort_keys=True)[:220]}` |"
        for item in audit["checks"]
    )
    write_text(
        PREFLIGHT_AUDIT_MD,
        f"""# {EXPERIMENT_ID} Preflight Audit

Overall status: `{audit["overall_status"]}`

This is a canonical static sanity gate only.

| check | status | detail |
|---|---|---|
{checks}

## Hashes

- runner_sha256: `{audit["hashes"]["runner_sha256"]}`
- random10_runner_sha256: `{audit["hashes"]["random10_runner_sha256"]}`
- base_runner_sha256: `{audit["hashes"]["base_runner_sha256"]}`
- config_sha256: `{audit["hashes"]["config_sha256"]}`
- subset_model_visible_manifest_sha256: `{audit["hashes"]["subset_model_visible_manifest_sha256"]}`
- subset_oracle_manifest_sha256: `{audit["hashes"]["subset_oracle_manifest_sha256"]}`
- scorer_sha256: `{audit["hashes"]["scorer_sha256"]}`
""",
    )
    write_hash_files()
    return audit


def assert_preflight_passed(audit: dict[str, Any]) -> None:
    if audit.get("overall_status") != "PASS":
        failed = [item for item in audit["checks"] if item["status"] != "PASS"]
        raise SystemExit("Preflight failed:\n" + "\n".join(f"- {item['check']}: {item['detail']}" for item in failed))


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_method = {method: B.method_summary(rows, method) for method in METHODS}
    mature = next((row for row in rows if row["method"] == "mature_ssr_loop"), None)
    pass_rule = bool(
        mature
        and mature.get("gate_status") == "measured"
        and mature.get("answer_success")
        and mature.get("reliable_composite_success")
        and not mature.get("forbidden_token_leakage")
        and not mature.get("protected_token_leakage")
        and not mature.get("revoked_token_leakage")
        and not mature.get("stale_token_leakage")
        and not mature.get("blocked_path_leakage")
    )
    return {
        "rows": len(rows),
        "expected_rows": EXPECTED_ROWS,
        "rerun_required_rows": sum(1 for row in rows if row.get("gate_status") == "rerun_required"),
        "excluded_rows": sum(1 for row in rows if row.get("gate_status") == "excluded"),
        "by_method": by_method,
        "mature_ssr_loop_pass_rule": pass_rule,
        "gate_status": "PASS" if pass_rule else "FAIL",
    }


def write_reports(rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    summary_lines = "\n".join(
        "| `{method}` | {rows} | {answer_success_rate:.3f} | {state_governance_success_rate:.3f} | {reliable_composite_success_rate:.3f} | {final_exact_success_rate:.3f} | {avg_provider_call_count:.2f} | {state_hard_cap_rows} |".format(
            method=method,
            **stats,
        )
        for method, stats in summary["by_method"].items()
    )
    row_lines = "\n".join(
        f"| `{row['method']}` | `{row.get('gate_status')}` | `{row.get('gate_reason')}` | `{row.get('answer_success')}` | `{row.get('state_governance_success')}` | `{row.get('reliable_composite_success')}` | `{row.get('provider_call_count')}` |"
        for row in rows
    )
    text = f"""# Canonical Static Sanity Gate Report

Experiment: `{EXPERIMENT_ID}`

Status: `{summary["gate_status"]}`

Rows: `{summary["rows"]}` / expected `{EXPECTED_ROWS}`

This packet is a runner-discrimination gate. It is not main-matrix evidence
and must not be pooled with PCG v2 pilot rows or historical ECVS static rows.

## Gate Rule

`mature_ssr_loop` must have `answer_success=True` and
`reliable_composite_success=True` with no boundary leakage.

Gate result: `{summary["gate_status"]}`

## Rows

| method | gate | reason | answer | governance | reliable | provider calls |
|---|---|---|---:|---:|---:|---:|
{row_lines}

## Success By Method

| method | rows | answer_success | state_governance_success | reliable_composite_success | final_exact_success | avg_provider_calls | state_hard_cap_rows |
|---|---:|---:|---:|---:|---:|---:|---:|
{summary_lines}

## Interpretation

If `PASS`, this closes the narrow runner-validity objection that the 2026-06-22
canonical `mature_ssr_loop` slot compiler is trivially broken on a static
control. It does not upgrade mature SSR to a primary method and does not change
the PCG v2 downgrade evidence chain by itself.
"""
    write_text(POST_RUN_AUDIT_MD, text)
    write_text(STATIC_SANITY_REPORT_MD, text)


def run_api(max_workers: int) -> None:
    patch_runner_globals()
    audit = json.loads(PREFLIGHT_AUDIT_JSON.read_text(encoding="utf-8"))
    assert_preflight_passed(audit)
    credential = B.get_api_key()
    visible = read_jsonl(MODEL_VISIBLE_SUBSET)
    oracle_by_id = {row["task_id"]: row for row in read_jsonl(SCORER_ORACLE_SUBSET)}
    config_sha256 = B.file_sha256(CONFIG_PATH)
    runner_sha256 = B.file_sha256(Path(__file__).resolve())
    scorer_sha256 = B.file_sha256(SCORER_PATH)
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
            pool.submit(B.run_one_row, task, oracle, method, budget, run_id, credential, config_sha256, runner_sha256, scorer_sha256)
            for task, oracle, method, budget, run_id in work_items
        ]
        for future in as_completed(futures):
            rows.append(future.result())
            print(f"completed {len(rows)}/{len(work_items)}", flush=True)
    rows.sort(key=lambda row: (row["task_id"], row["method"], int(row["state_budget"]), int(row["run_id"])))
    B.write_jsonl(CONTROLLED_ROWS, rows)
    metric_keys = {
        "task_id",
        "method",
        "model",
        "budget",
        "run_id",
        "state_budget",
        "required_token_recall",
        "required_token_missing_count",
        "missing_required_tokens",
        "forbidden_token_leakage",
        "forbidden_token_hits",
        "protected_token_leakage",
        "protected_token_hits",
        "revoked_token_leakage",
        "revoked_token_hits",
        "stale_token_leakage",
        "stale_token_hits",
        "blocked_path_leakage",
        "blocked_path_hits",
        "boundary_violation",
        "state_label_accuracy",
        "state_transition_accuracy",
        "final_exact_success",
        "answer_success",
        "state_governance_success",
        "state_carry_surface_present",
        "state_governance_success_legacy_no_conflict_only",
        "reliable_composite_success",
        "reliable_success",
        "state_required_token_present",
        "state_required_token_negated",
        "state_internal_conflict",
        "output_bearing_state_conflict",
        "exclusion_field_conflict",
        "state_forbidden_token_present",
        "state_forbidden_token_negated",
        "mechanical_carry_failure_mode_detected",
        "provider_call_count",
        "final_output_construction",
    }
    score_rows = [{key: value for key, value in row.items() if key in metric_keys} for row in rows]
    B.write_jsonl(SCORES_JSONL, score_rows)
    B.write_csv(SCORES_CSV, score_rows)
    write_hash_files()
    summary = summarize(rows)
    B.write_json(RESULT_DIR / "STATIC_SANITY_SUMMARY.json", summary)
    write_reports(rows, summary)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-api", action="store_true")
    parser.add_argument("--max-workers", type=int, default=DEFAULT_MAX_WORKERS)
    args = parser.parse_args()
    audit = write_preflight_files()
    print(
        json.dumps(
            {
                "experiment_id": EXPERIMENT_ID,
                "preflight_status": audit["overall_status"],
                "expected_rows": EXPECTED_ROWS,
                "selected_tasks": audit["selected_task_ids"],
                "config": rel(CONFIG_PATH),
                "run_plan": rel(RUN_PLAN_MD),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    if args.run_api:
        run_api(max_workers=args.max_workers)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
