#!/usr/bin/env python3
"""DeepSeek PCG v2 random-10 six-method pilot.

Default mode is preflight-only.  API execution requires --run-api.
This is a local calibration/pilot packet, not formal main-matrix evidence.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASE_RUNNER = PROJECT_ROOT / "tools" / "run_ecvs_deepseek_pcg_dynamic_state_v2_e10_h3_decisive_4method_2budget_1run.py"


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location("deepseek_pcg_v2_base_runner", BASE_RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import base runner: {BASE_RUNNER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


B = load_base()

EXPERIMENT_ID = "_probe_deepseek_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622"
POSITIONING = "local_calibration_only_not_primary_not_admission_not_main_matrix"
SELECTION_SEED = "20260622_deepseek_new_matrix_10task_pilot_v1"

BASE_DATA_DIR = PROJECT_ROOT / "data" / "pcg_dynamic_state_v2" / "main_matrix_v1"
BASE_MODEL_VISIBLE = BASE_DATA_DIR / "MODEL_VISIBLE_TASK_MANIFEST.jsonl"
BASE_ORACLE = BASE_DATA_DIR / "SCORER_ORACLE_MANIFEST.jsonl"
BASE_PROVENANCE = BASE_DATA_DIR / "TASK_PROVENANCE_MANIFEST.jsonl"
BASE_SPLIT_AUDIT = BASE_DATA_DIR / "TASK_SPLIT_AUDIT.json"

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
APPLICATION_MD = Path("<LOCAL_PATH_REDACTED>/DEEPSEEK_RANDOM10_NEW_MATRIX_PILOT_APPLICATION_20260622.md")

VARIABLE_CONTROL_DOC = Path("<AUTHOR_LOCAL_PROTOCOL_DIR>/LATEST_EXPERIMENT_VARIABLE_REQUIREMENTS_GOVERNANCE_MAIN_MATRIX_v1_20260621.md")
METHOD_PROTOCOL_DOC = Path("<AUTHOR_LOCAL_PROTOCOL_DIR>/METHOD_CONDITION_PROTOCOLS_GOVERNANCE_MAIN_MATRIX_v1_20260621.md")
SCORER_PATH = PROJECT_ROOT / "tools" / "pcg_dynamic_state_v2" / "score_pcg_dynamic_state_v2_main_matrix.py"

METHODS = [
    "loop_only",
    "rolling_summary",
    "rolling_visible_carry_forward",
    "rolling_visible_fields_only",
    "ssr_no_visible_carry",
    "mature_ssr_loop",
]
METHOD_PROTOCOLS = {
    "loop_only": "segment_loop_no_persistent_carry_v1_ecvs_safe_visible_only",
    "rolling_summary": "plain_natural_language_rolling_summary_v1_ecvs_safe_visible_only",
    "rolling_visible_carry_forward": "rolling_visible_identifier_carry_forward_v1_ecvs_safe_visible_only",
    "rolling_visible_fields_only": "rolling_visible_fields_only_protocol_v1_pcg_dynamic_state_v2_safe_visible_only",
    "ssr_no_visible_carry": "ssr_no_visible_carry_protocol_v1_alias_ssr_only_no_deterministic_visible_carry",
    "mature_ssr_loop": "mature_ssr_loop_protocol_v1_ecvs_safe_visible_only",
}
STATE_BUDGETS = [300, 600, 1200]
RUNS = 1
TASKS_PER_FAMILY = 2
EXPECTED_TASKS = 10
EXPECTED_ROWS = EXPECTED_TASKS * len(METHODS) * len(STATE_BUDGETS) * RUNS
DEFAULT_MAX_WORKERS = 10

NEGATIVE_TERMS = [
    "revoked",
    "stale",
    "forbidden",
    "protected",
    "blocked",
    "archive-only",
    "archive only",
    "rollback-only",
    "rollback only",
    "decoy",
    "not outputtable",
    "must not",
    "do not",
    "excluded",
]
POSITIVE_TERMS = [
    "initial active",
    "active tokens",
    "currently active",
    "current allowed",
    "allowed path",
    "allowed implementation path",
    "final active",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rel(path: Path) -> str:
    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return str(path)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def select_random10() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    visible = read_jsonl(BASE_MODEL_VISIBLE)
    oracle_by_id = {row["task_id"]: row for row in read_jsonl(BASE_ORACLE)}
    provenance_by_id = {row["task_id"]: row for row in read_jsonl(BASE_PROVENANCE)}
    by_family: dict[str, list[dict[str, Any]]] = {}
    for row in visible:
        by_family.setdefault(row["family"], []).append(row)

    rng = random.Random(SELECTION_SEED)
    selected_visible: list[dict[str, Any]] = []
    selection_rows: list[dict[str, Any]] = []
    for family in sorted(by_family):
        candidates = sorted(by_family[family], key=lambda item: item["task_id"])
        picked = sorted(rng.sample(candidates, TASKS_PER_FAMILY), key=lambda item: item["task_id"])
        for row in picked:
            selected_visible.append(row)

    selected_visible.sort(key=lambda item: (item["family"], item["difficulty"], item["task_id"]))
    selected_oracle = [oracle_by_id[row["task_id"]] for row in selected_visible]
    selected_provenance = [provenance_by_id[row["task_id"]] for row in selected_visible]
    for order, row in enumerate(selected_visible, start=1):
        task_id = row["task_id"]
        selection_rows.append(
            {
                "selection_order": order,
                "task_id": task_id,
                "family": row["family"],
                "difficulty": row["difficulty"],
                "selection_rule": "stratified_random_2_per_family_from_frozen_pcg_v2_main_matrix_v1",
                "selection_seed": SELECTION_SEED,
                "no_outcome_selection": "true",
                "source_model_visible_sha256": B.sha256_json(row),
                "source_oracle_sha256": B.sha256_json(oracle_by_id[task_id]),
                "source_provenance_sha256": B.sha256_json(provenance_by_id[task_id]),
            }
        )
    return selected_visible, selected_oracle, selected_provenance, selection_rows


def write_subset_artifacts() -> None:
    visible, oracle, provenance, selection = select_random10()
    B.write_jsonl(MODEL_VISIBLE_SUBSET, visible)
    B.write_jsonl(SCORER_ORACLE_SUBSET, oracle)
    B.write_jsonl(TASK_PROVENANCE_MANIFEST, provenance)
    B.write_csv(TASK_SELECTION_CSV, selection)
    B.write_json(TASK_SPLIT_AUDIT, B.build_task_split_audit(visible, oracle))


def visible_field_candidates(visible_text: str) -> tuple[list[str], list[str]]:
    tokens = B.dedupe_preserve(B.NEUTRAL_TOKEN_RE.findall(visible_text))
    keep: list[str] = []
    excluded: list[str] = []
    lowered = visible_text.lower()
    for token in tokens:
        positions = [idx for idx in range(len(visible_text)) if visible_text.startswith(token, idx)]
        windows = [lowered[max(0, idx - 100) : min(len(lowered), idx + len(token) + 100)] for idx in positions]
        has_negative = any(any(term in window for term in NEGATIVE_TERMS) for window in windows)
        has_positive = any(any(term in window for term in POSITIVE_TERMS) for window in windows)
        if has_negative and not has_positive:
            excluded.append(token)
        elif not has_negative or has_positive:
            keep.append(token)
    return B.dedupe_preserve(keep), B.dedupe_preserve(excluded)


def visible_allowed_paths(visible_text: str) -> tuple[list[str], list[str]]:
    paths = B.dedupe_preserve(B.PATH_RE.findall(visible_text))
    allowed: list[str] = []
    blocked: list[str] = []
    lowered = visible_text.lower()
    for path in paths:
        positions = [idx for idx in range(len(visible_text)) if visible_text.startswith(path, idx)]
        windows = [lowered[max(0, idx - 90) : min(len(lowered), idx + len(path) + 90)] for idx in positions]
        if any("blocked" in window or "attractive path" in window for window in windows):
            blocked.append(path)
        else:
            allowed.append(path)
    return B.dedupe_preserve(allowed), B.dedupe_preserve(blocked)


def build_update_prompt(method: str, task: dict[str, Any], segment: dict[str, Any], state: str, budget: int, visible_text_so_far: str) -> str:
    common = f"""Task id: {task["task_id"]}
Difficulty: {task["difficulty"]}
Family: {task["family"]}
State budget after deterministic fitting: {budget} characters

Prior transferred state:
{state or "[empty]"}

Current segment {segment["segment_id"]}/{len(task["segments"])} ({segment["role"]}):
{segment["text"]}
"""
    if method == "loop_only":
        method_block = """You are writing only a current-segment loop check.
Do not preserve prior-segment details unless they appear in the current segment.
Do not use SSR fields or deterministic visible carry.
Do not use hidden answers, oracle fields, scoring metadata, or required/forbidden arrays.
Return JSON only: {"CURRENT_GOAL":"...", "GAP":"...", "NEXT_MISTAKE_TO_AVOID":"..."}"""
    elif method == "rolling_summary":
        method_block = """You are maintaining the plain natural-language rolling-summary baseline.
Use the same base behavior as visible-carry methods, but without deterministic VISIBLE_KEEP.
Do not use SSR fields or hidden oracle/scoring material.
Return JSON only: {"SUMMARY":"..."}"""
    elif method == "rolling_visible_carry_forward":
        method_block = """You are maintaining the plain natural-language rolling-summary base.
The runner will append deterministic VISIBLE_KEEP after your state update.
Do not use SSR fields OUT/ALW/NO/B/G/N/CK/LOOP and do not use hidden oracle/scoring material.
Return JSON only: {"NOTE":"...", "BOUNDARY":"..."}"""
    elif method == "rolling_visible_fields_only":
        method_block = """You are maintaining the same natural-language rolling-summary base.
The runner will replace broad notes with compact deterministic visible fields only.
Do not use SSR fields OUT/ALW/NO/B/G/N/CK/LOOP and do not use hidden oracle/scoring material.
Return JSON only: {"NOTE":"...", "BOUNDARY":"..."}"""
    elif method == "ssr_no_visible_carry":
        method_block = """You are maintaining SSR schema without runner-side deterministic visible carry.
Use only model-visible text and prior model-visible SSR state.
Do not append all visible candidates mechanically.
NO/B may contain generic exclusion categories but must not seed the final answer.
Return JSON only: {"OUT":"...", "ALW":"...", "NO":"...", "B":"...", "G":"...", "N":"...", "CK":"..."}"""
    else:
        method_block = """You are maintaining mature SSR schema with deterministic visible-carry support.
Use only model-visible text and prior model-visible state.
NO/B may contain generic exclusion categories but must not seed the final answer.
Return JSON only: {"OUT":"...", "ALW":"...", "NO":"...", "B":"...", "G":"...", "N":"...", "CK":"...", "LOOP":"..."}"""
    return f"{method_block}\n\n{common}"


def compile_state(method: str, raw_state: str, visible_text_so_far: str, budget: int) -> tuple[str, dict[str, Any]]:
    candidates = B.extract_visible_candidates(visible_text_so_far)
    field_keep, field_excluded = visible_field_candidates(visible_text_so_far)
    allowed_paths, blocked_paths = visible_allowed_paths(visible_text_so_far)
    protocol = METHOD_PROTOCOLS[method]
    raw = raw_state.strip()
    if method in {"rolling_summary", "loop_only"}:
        rendered = raw
    elif method == "rolling_visible_carry_forward":
        rendered = f"VISIBLE_KEEP={','.join(candidates)}\nNOTE={raw}"
    elif method == "rolling_visible_fields_only":
        rendered = (
            f"VISIBLE_KEEP={','.join(field_keep)}\n"
            f"VISIBLE_ALLOWED_SCOPE={','.join(allowed_paths)}\n"
            f"VISIBLE_BOUNDARY=excluded_count:{len(field_excluded)}; blocked_path_count:{len(blocked_paths)}\n"
            "VISIBLE_NOTE=compact deterministic visible fields only"
        )
    elif method == "ssr_no_visible_carry":
        rendered = raw
    else:
        fields = B.parse_state_fields(raw)
        if fields:
            out = fields.get("OUT", "")
            alw = fields.get("ALW", fields.get("ALLOW", ""))
            no = fields.get("NO", fields.get("B", "excluded categories only"))
            rest = "\n".join(f"{k}={v}" for k, v in fields.items() if k not in {"OUT", "ALW", "ALLOW", "NO", "B"})
            rendered = f"OUT={out or ','.join(field_keep)}\nALW={alw or ','.join(allowed_paths)}\nNO={no}\nB=no forbidden/protected/revoked/stale/blocked/archive-only/rollback-only output\n{rest}"
        else:
            rendered = f"OUT={','.join(field_keep)}\nALW={','.join(allowed_paths)}\nNO=excluded categories only\nB=no forbidden/protected/revoked/stale/blocked/archive-only/rollback-only output\nG=solve final active allowed set\nN=continue\nCK=check state labels\nLOOP=boundary-risk check"
    fitted, hard_cap, before, after = B.fit_state(rendered, budget)
    audit = {
        "method_protocol_version": protocol,
        "visible_identifier_candidates_count": len(candidates),
        "visible_field_keep_count": len(field_keep),
        "visible_field_excluded_count": len(field_excluded),
        "visible_allowed_path_count": len(allowed_paths),
        "visible_blocked_path_count": len(blocked_paths),
        "visible_identifier_candidates_sha256": B.sha256_json(candidates),
        "visible_field_keep_sha256": B.sha256_json(field_keep),
        "compiler_input_visible_text_sha256": B.sha256_bytes(visible_text_so_far.encode("utf-8")),
        "compiler_input_raw_state_sha256": B.sha256_bytes(raw_state.encode("utf-8")),
        "compiler_output_state_sha256": B.sha256_bytes(fitted.encode("utf-8")),
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
        method_specific = """Mature SSR final-solve contract:
- final_answer.required_tokens must derive only from OUT.
- final_answer.allowed_paths must derive only from ALW.
- Never copy material from NO/B/G/N/CK/LOOP into required_tokens or allowed_paths."""
    elif method == "ssr_no_visible_carry":
        method_specific = """SSR-without-carry final-solve contract:
- final_answer.required_tokens must derive only from OUT.
- final_answer.allowed_paths must derive only from ALW.
- NO/B/excluded fields must not contribute output-bearing tokens."""
    elif method == "rolling_visible_fields_only":
        method_specific = """Visible-fields-only rule:
- VISIBLE_KEEP is output-bearing.
- VISIBLE_ALLOWED_SCOPE is allowed-scope evidence.
- VISIBLE_BOUNDARY and VISIBLE_NOTE are not output-bearing."""
    elif method == "rolling_visible_carry_forward":
        method_specific = """Visible-carry rule:
- VISIBLE_KEEP is output-bearing candidate state.
- NOTE/BOUNDARY may be used only to decide which visible candidates remain safe."""
    elif method == "rolling_summary":
        method_specific = "Use only the transferred natural-language summary."
    else:
        method_specific = "Use only the current-segment loop notes."
    return f"""Use only the transferred state below and the output schema instruction.
Do not use hidden answers, oracle fields, scoring metadata, or external context.
{method_specific}

Task id: {task["task_id"]}
Method: {method}

Transferred state:
{state}

Output schema instruction:
{task["final_instruction"]}

Return JSON only.
"""


def build_config() -> dict[str, Any]:
    visible = read_jsonl(MODEL_VISIBLE_SUBSET)
    family_counts: dict[str, int] = {}
    difficulty_counts: dict[str, int] = {}
    for row in visible:
        family_counts[row["family"]] = family_counts.get(row["family"], 0) + 1
        difficulty_counts[row["difficulty"]] = difficulty_counts.get(row["difficulty"], 0) + 1
    return {
        "experiment_id": EXPERIMENT_ID,
        "positioning": POSITIONING,
        "created_at_utc": utc_now(),
        "matrix_shape": {
            "tasks": EXPECTED_TASKS,
            "models": 1,
            "methods": len(METHODS),
            "state_budgets": len(STATE_BUDGETS),
            "runs": RUNS,
            "expected_rows": EXPECTED_ROWS,
        },
        "task_source": {
            "base_model_visible_manifest": rel(BASE_MODEL_VISIBLE),
            "base_oracle_manifest": rel(BASE_ORACLE),
            "base_provenance_manifest": rel(BASE_PROVENANCE),
            "subset_model_visible_manifest": rel(MODEL_VISIBLE_SUBSET),
            "subset_oracle_manifest": rel(SCORER_ORACLE_SUBSET),
            "subset_task_provenance_manifest": rel(TASK_PROVENANCE_MANIFEST),
            "subset_task_selection_csv": rel(TASK_SELECTION_CSV),
            "subset_task_split_audit": rel(TASK_SPLIT_AUDIT),
            "selection_rule": "stratified_random_2_per_family_from_frozen_pcg_v2_main_matrix_v1",
            "selection_seed": SELECTION_SEED,
            "family_counts": family_counts,
            "difficulty_counts": difficulty_counts,
            "selection_used_model_outcomes": False,
        },
        "task_hashes": {
            "base_model_visible_manifest_sha256": B.file_sha256(BASE_MODEL_VISIBLE),
            "base_oracle_manifest_sha256": B.file_sha256(BASE_ORACLE),
            "base_provenance_manifest_sha256": B.file_sha256(BASE_PROVENANCE),
            "base_split_audit_sha256": B.file_sha256(BASE_SPLIT_AUDIT),
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
            "policy_id": "deepseek_random10_new_matrix_pilot_retry_policy_v1",
            "max_attempts": 2,
            "retryable_http_statuses": sorted(B.RETRYABLE_HTTP),
            "retryable_transport_failures": ["timeout", "connection_reset"],
            "failed_attempts_retained": True,
            "post_hoc_failed_row_deletion": False,
        },
        "variable_control_doc": str(VARIABLE_CONTROL_DOC),
        "method_protocol_doc": str(METHOD_PROTOCOL_DOC),
        "implementation": {
            "runner": rel(Path(__file__).resolve()),
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


def patch_base_globals() -> None:
    B.EXPERIMENT_ID = EXPERIMENT_ID
    B.POSITIONING = POSITIONING
    B.BASE_MODEL_VISIBLE = BASE_MODEL_VISIBLE
    B.BASE_ORACLE = BASE_ORACLE
    B.BASE_MANIFEST = BASE_PROVENANCE
    B.BASE_SHA256S = BASE_SPLIT_AUDIT
    B.SUBSET_DIR = SUBSET_DIR
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
    B.VARIABLE_CONTROL_DOC = VARIABLE_CONTROL_DOC
    B.METHOD_PROTOCOL_DOC = METHOD_PROTOCOL_DOC
    B.SCORER_PATH = SCORER_PATH
    B.METHODS = METHODS
    B.METHOD_PROTOCOLS = METHOD_PROTOCOLS
    B.STATE_BUDGETS = STATE_BUDGETS
    B.RUNS = RUNS
    B.EXPECTED_ROWS = EXPECTED_ROWS
    B.DEFAULT_MAX_WORKERS = DEFAULT_MAX_WORKERS
    B.write_subset_artifacts = write_subset_artifacts
    B.build_config = build_config
    B.build_update_prompt = build_update_prompt
    B.compile_state = compile_state
    B.build_final_prompt = build_final_prompt
    B.git_commit = lambda: "git_not_invoked_by_policy"


def result_dir_has_old_rows() -> tuple[bool, list[str]]:
    if not RESULT_DIR.exists():
        return False, []
    names = ["CONTROLLED_ROWS.jsonl", "scores.jsonl", "scores.csv", "POST_RUN_AUDIT.md"]
    conflicts = [name for name in names if (RESULT_DIR / name).exists()]
    return bool(conflicts), conflicts


def raw_dir_has_outputs() -> tuple[bool, list[str]]:
    if not RAW_DIR.exists():
        return False, []
    files = [p for p in RAW_DIR.rglob("*") if p.is_file()]
    return bool(files), [rel(p) for p in files[:20]]


def build_preflight_audit(config: dict[str, Any]) -> dict[str, Any]:
    visible = read_jsonl(MODEL_VISIBLE_SUBSET)
    oracle = read_jsonl(SCORER_ORACLE_SUBSET)
    split = json.loads(TASK_SPLIT_AUDIT.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def add(name: str, ok: bool, detail: Any) -> None:
        checks.append({"check": name, "status": "PASS" if ok else "FAIL", "detail": detail})

    family_counts: dict[str, int] = {}
    difficulty_counts: dict[str, int] = {}
    for row in visible:
        family_counts[row["family"]] = family_counts.get(row["family"], 0) + 1
        difficulty_counts[row["difficulty"]] = difficulty_counts.get(row["difficulty"], 0) + 1
    old_rows, row_conflicts = result_dir_has_old_rows()
    old_raw, raw_conflicts = raw_dir_has_outputs()
    add("selected task rows = 10", len(visible) == 10, len(visible))
    add("oracle rows = 10", len(oracle) == 10, len(oracle))
    add("family split = 2 each", set(family_counts.values()) == {2} and len(family_counts) == 5, family_counts)
    add("method list = six-method new matrix", config["methods"] == METHODS, config["methods"])
    add("state budgets = 300/600/1200", config["state_budget_chars"] == STATE_BUDGETS, config["state_budget_chars"])
    add("runs = 1", config["runs"] == 1, config["runs"])
    add("expected rows = 180", config["expected_rows"] == EXPECTED_ROWS == 180, config["expected_rows"])
    add("provider direct deepseek", config["condition"]["provider"] == "deepseek", config["condition"])
    add("temperature explicit 0", config["request_controls"]["temperature"]["value"] == 0, config["request_controls"]["temperature"])
    add("thinking disabled", config["request_controls"]["reasoning_or_thinking"]["value"] == {"thinking": {"type": "disabled"}}, config["request_controls"]["reasoning_or_thinking"])
    add("tools/web disabled", config["request_controls"]["tools"] == "disabled" and config["request_controls"]["web"] == "disabled", {"tools": config["request_controls"]["tools"], "web": config["request_controls"]["web"]})
    add("task split audit PASS", split.get("prompt_oracle_split_status") == "PASS", split.get("prompt_oracle_split_status"))
    add("no prior row output files in result dir", not old_rows, row_conflicts)
    add("raw output dir absent or empty", not old_raw, raw_conflicts)
    add("variable control doc exists", VARIABLE_CONTROL_DOC.exists(), str(VARIABLE_CONTROL_DOC))
    add("method protocol doc exists", METHOD_PROTOCOL_DOC.exists(), str(METHOD_PROTOCOL_DOC))
    add("strict scorer exists", SCORER_PATH.exists(), rel(SCORER_PATH))
    return {
        "audit_type": "deepseek_random10_new_matrix_pilot_preflight",
        "experiment_id": EXPERIMENT_ID,
        "created_at_utc": utc_now(),
        "overall_status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL",
        "api_called": False,
        "api_key_value_printed": False,
        "git_invoked": False,
        "expected_rows": EXPECTED_ROWS,
        "selected_task_ids": [row["task_id"] for row in visible],
        "family_counts": family_counts,
        "difficulty_counts": difficulty_counts,
        "checks": checks,
        "hashes": {
            "runner_sha256": B.file_sha256(Path(__file__).resolve()),
            "base_runner_sha256": B.file_sha256(BASE_RUNNER),
            "config_sha256": B.file_sha256(CONFIG_PATH),
            "subset_model_visible_manifest_sha256": B.file_sha256(MODEL_VISIBLE_SUBSET),
            "subset_oracle_manifest_sha256": B.file_sha256(SCORER_ORACLE_SUBSET),
            "scorer_sha256": B.file_sha256(SCORER_PATH),
        },
    }


def write_run_plan_and_application(config: dict[str, Any], audit: dict[str, Any]) -> None:
    selected = "\n".join(f"- `{task_id}`" for task_id in audit["selected_task_ids"])
    text = f"""# DeepSeek Random-10 New-Matrix Pilot Application

Date: 2026-06-22

Status: application/preflight packet for a local calibration run. This is not
formal main-matrix evidence, not admission evidence, and not a paper result row
unless separately promoted before execution.

## Requested Run

```text
10 frozen PCG dynamic-state v2 tasks
x 1 model: deepseek_v4pro
x 6 methods
x 3 state budgets
x 1 run
= 180 scored rows
```

## Methods

```text
loop_only
rolling_summary
rolling_visible_carry_forward
rolling_visible_fields_only
ssr_no_visible_carry
mature_ssr_loop
```

## Controls

- Provider: `deepseek`
- Requested model: `deepseek-v4-pro`
- Base URL: `https://api.deepseek.com`
- Temperature: explicit `0`
- Max tokens: `4096`
- Thinking: `{{"type":"disabled"}}`
- Tools/web: disabled
- Fallback: false
- State budgets: `300`, `600`, `1200`
- Runs: `1`
- Concurrency: `{DEFAULT_MAX_WORKERS}`
- Retry: maximum 2 attempts, failed attempts retained
- Scorer: strict PCG v2 main-matrix scorer
- API key: read only at runtime from `DEEPSEEK_API_KEY`; value is never printed or written
- Git: not invoked

## Random Task Selection

- Source: frozen PCG dynamic-state v2 main-matrix v1 40-task packet
- Rule: stratified random 2 tasks per family
- Seed: `{SELECTION_SEED}`
- Family counts: `{json.dumps(audit["family_counts"], ensure_ascii=False, sort_keys=True)}`
- Difficulty counts: `{json.dumps(audit["difficulty_counts"], ensure_ascii=False, sort_keys=True)}`

## Selected Tasks

{selected}

## Files

- Runner: `{rel(Path(__file__).resolve())}`
- Config: `{rel(CONFIG_PATH)}`
- Preflight audit: `{rel(PREFLIGHT_AUDIT_MD)}`
- Result dir: `{rel(RESULT_DIR)}`
- Raw private dir: `{rel(RAW_DIR)}`
- Variable protocol: `{config["variable_control_doc"]}`
- Method protocol: `{config["method_protocol_doc"]}`

## Command

```bash
python3 tools/run_deepseek_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622.py --run-api --max-workers {DEFAULT_MAX_WORKERS}
```
"""
    write_text(RUN_PLAN_MD, text)
    write_text(APPLICATION_MD, text)


def write_hash_files() -> None:
    paths = [
        MODEL_VISIBLE_SUBSET,
        SCORER_ORACLE_SUBSET,
        TASK_PROVENANCE_MANIFEST,
        TASK_SELECTION_CSV,
        TASK_SPLIT_AUDIT,
        CONFIG_PATH,
        RUN_PLAN_MD,
        APPLICATION_MD,
        PREFLIGHT_AUDIT_JSON,
        PREFLIGHT_AUDIT_MD,
        SCORER_PATH,
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


def write_preflight_files() -> dict[str, Any]:
    patch_base_globals()
    write_subset_artifacts()
    config = build_config()
    B.write_json(CONFIG_PATH, config)
    config = build_config()
    B.write_json(CONFIG_PATH, config)
    audit = build_preflight_audit(config)
    B.write_json(PREFLIGHT_AUDIT_JSON, audit)
    write_run_plan_and_application(config, audit)
    checks = "\n".join(
        f"| {item['check']} | `{item['status']}` | `{json.dumps(item['detail'], ensure_ascii=False, sort_keys=True)[:220]}` |"
        for item in audit["checks"]
    )
    write_text(
        PREFLIGHT_AUDIT_MD,
        f"""# {EXPERIMENT_ID} Preflight Audit

Overall status: `{audit["overall_status"]}`

This is a local calibration run packet only.

| check | status | detail |
|---|---|---|
{checks}

## Hashes

- runner_sha256: `{audit["hashes"]["runner_sha256"]}`
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


def method_summary(rows: list[dict[str, Any]], method: str) -> dict[str, Any]:
    return B.method_summary(rows, method)


def compare(rows: list[dict[str, Any]], left: str, right: str) -> dict[str, Any]:
    return B.bootstrap_diff_ci(rows, left, right, "reliable_composite_success", samples=5000)


def run_api(max_workers: int) -> None:
    patch_base_globals()
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
    summaries = {method: method_summary(rows, method) for method in METHODS}
    comparisons = {
        "carry_main_effect_no_schema_visible_minus_rolling": compare(rows, "rolling_visible_carry_forward", "rolling_summary"),
        "schema_main_effect_no_carry_ssr_minus_rolling": compare(rows, "ssr_no_visible_carry", "rolling_summary"),
        "schema_plus_carry_mature_minus_visible": compare(rows, "mature_ssr_loop", "rolling_visible_carry_forward"),
        "visible_crux_visible_minus_ssr_no_carry": compare(rows, "rolling_visible_carry_forward", "ssr_no_visible_carry"),
        "fields_probe_fields_minus_visible": compare(rows, "rolling_visible_fields_only", "rolling_visible_carry_forward"),
    }
    write_hash_files()
    summary_lines = "\n".join(
        "| `{method}` | {rows} | {answer_success_rate:.3f} | {state_governance_success_rate:.3f} | {reliable_composite_success_rate:.3f} | {final_exact_success_rate:.3f} | {avg_provider_call_count:.2f} | {state_hard_cap_rows} |".format(method=method, **stats)
        for method, stats in summaries.items()
    )
    comparison_lines = "\n".join(
        f"| `{name}` | `{value['left_method']} - {value['right_method']}` | {value['point_diff']:.3f} | [{value['ci_lower']:.3f}, {value['ci_upper']:.3f}] | {value['paired_units']} |"
        for name, value in comparisons.items()
    )
    POST_RUN_AUDIT_MD.write_text(
        f"""# DeepSeek Random-10 New-Matrix Pilot Post-Run Audit

Experiment: `{EXPERIMENT_ID}`

Rows: `{len(rows)}` / expected `{EXPECTED_ROWS}`

Status: local calibration only, not formal main-matrix evidence.

Reasoning content present rows: `{sum(1 for row in rows if row.get('reasoning_content_present'))}`

Backend/rerun rows: `{sum(1 for row in rows if row.get('backend_error'))}`

## Success By Method

| method | rows | answer_success | state_governance_success | reliable_composite_success | final_exact_success | avg_provider_calls | state_hard_cap_rows |
|---|---:|---:|---:|---:|---:|---:|---:|
{summary_lines}

## Mechanism Comparisons

| comparison | contrast | point diff | 95% bootstrap CI | paired units |
|---|---|---:|---:|---:|
{comparison_lines}

## Non-Pooling

These rows are not formal main-matrix rows and must not be pooled with Fresh v2,
DeepSeek-only historical probes, or the future 5-model PCG v2 governance matrix.
""",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({"rows": len(rows), "summary_by_method": summaries, "comparisons": comparisons}, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-api", action="store_true")
    parser.add_argument("--max-workers", type=int, default=DEFAULT_MAX_WORKERS)
    args = parser.parse_args()
    audit = write_preflight_files()
    print(json.dumps({
        "experiment_id": EXPERIMENT_ID,
        "preflight_status": audit["overall_status"],
        "expected_rows": EXPECTED_ROWS,
        "selected_tasks": audit["selected_task_ids"],
        "application": str(APPLICATION_MD),
        "config": rel(CONFIG_PATH),
        "run_plan": rel(RUN_PLAN_MD),
    }, ensure_ascii=False, indent=2))
    if args.run_api:
        run_api(max_workers=args.max_workers)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
