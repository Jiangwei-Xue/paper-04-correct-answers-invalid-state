#!/usr/bin/env python3
"""Build the new-repo main-matrix freeze packet."""

from __future__ import annotations

import csv
import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
FREEZE_DATE = "2026-06-25"
FREEZE_TIMESTAMP = "2026-06-25T00:00:00Z"

TASK_DIR = ROOT / "artifact/results/evidence/ssr_downgrade_20260623/data/pcg_dynamic_state_v2/main_matrix_v1"
VISIBLE_TASKS = TASK_DIR / "MODEL_VISIBLE_TASK_MANIFEST.jsonl"
ORACLE_TASKS = TASK_DIR / "SCORER_ORACLE_MANIFEST.jsonl"
TASK_PROVENANCE = TASK_DIR / "TASK_PROVENANCE_MANIFEST.jsonl"
TASK_SPLIT_AUDIT = TASK_DIR / "TASK_SPLIT_AUDIT.json"

CONFIG_DIR = ROOT / "artifact/protocol/main_matrix/configs"
ADMISSION_DIR = ROOT / "artifact/protocol/main_matrix/admission"
MAIN_MATRIX_PROTOCOL_DIR = ROOT / "artifact/protocol/main_matrix"
EXPERIMENT_VARIABLE_OVERVIEW_PATH = MAIN_MATRIX_PROTOCOL_DIR / "EXPERIMENT_VARIABLE_CONTROL_OVERVIEW.md"
DECISION_RULES_PATH = MAIN_MATRIX_PROTOCOL_DIR / "PREREGISTERED_DECISION_RULES.md"
STATISTICAL_ANALYSIS_PLAN_PATH = MAIN_MATRIX_PROTOCOL_DIR / "STATISTICAL_ANALYSIS_PLAN.md"
API_POLICY_PATH = MAIN_MATRIX_PROTOCOL_DIR / "MAIN_RUN_API_POLICY.md"
FRAMING_PATH = MAIN_MATRIX_PROTOCOL_DIR / "PAPER_FRAMING_AND_RQS.md"
METHOD_CONDITIONS_PATH = MAIN_MATRIX_PROTOCOL_DIR / "METHOD_CONDITIONS.md"
VARIABLE_CONTROL_PATH = MAIN_MATRIX_PROTOCOL_DIR / "VARIABLE_CONTROL.md"
MODEL_AXIS_DISPOSITION_PATH = MAIN_MATRIX_PROTOCOL_DIR / "MODEL_AXIS_DISPOSITION.md"
OPENROUTER_VARIABLE_CONTROL_PATH = ADMISSION_DIR / "OPENROUTER_VARIABLE_CONTROL_20260626.md"
CLAIM_MAP_PATH = ROOT / "docs/CLAIM_TO_ARTIFACT_MAP.md"
QUICKSTART_PATH = ROOT / "docs/REVIEWER_QUICKSTART.md"
BENCHMARK_CARD_PATH = ROOT / "artifact/BENCHMARK_CARD.md"
CROISSANT_JSON_PATH = ROOT / "artifact/metadata/croissant.json"
CROISSANT_MAPPING_PATH = ROOT / "artifact/metadata/CROISSANT_MAPPING.md"
RAI_LIMITATIONS_PATH = ROOT / "docs/RAI_ETHICS_LIMITATIONS.md"
HOSTING_PLAN_PATH = ROOT / "docs/HOSTING_AND_RELEASE_PLAN.md"
VERIFY_DIR = ROOT / "artifact/verification"
SCORER_PATH = ROOT / "artifact/results/evidence/ssr_downgrade_20260623/tools/pcg_dynamic_state_v2/score_pcg_dynamic_state_v2_main_matrix.py"
BASE_SCORER_PATH = ROOT / "artifact/results/evidence/ssr_downgrade_20260623/tools/pcg_dynamic_state_v2/score_pcg_dynamic_state_v2_outputs.py"
RUNNER_PATH = VERIFY_DIR / "main_matrix_vcr_runner.py"

CONFIRMATORY_ID = "pcg_dynamic_state_v2_confirmatory_40task_5model_6method_2budget_3run_20260625"
DIAGNOSTIC_ID = "pcg_dynamic_state_v2_budget300_diagnostic_40task_5model_4method_1budget_1run_20260625"

CONFIRMATORY_CONFIG = CONFIG_DIR / f"{CONFIRMATORY_ID}.json"
CONFIRMATORY_ROWS = CONFIG_DIR / f"{CONFIRMATORY_ID}.rows.jsonl"
DIAGNOSTIC_CONFIG = CONFIG_DIR / f"{DIAGNOSTIC_ID}.json"
DIAGNOSTIC_ROWS = CONFIG_DIR / f"{DIAGNOSTIC_ID}.rows.jsonl"

PROVIDER_SNAPSHOT = ADMISSION_DIR / f"PROVIDER_SUPPORTED_PARAMETER_SNAPSHOT_{FREEZE_DATE.replace('-', '')}.json"
MODEL_ADMISSION_CRITERIA = ADMISSION_DIR / "MODEL_ADMISSION_CRITERIA_20260626.md"
VARIABLE_FREEZE_SPEC = ADMISSION_DIR / f"VARIABLE_FREEZE_SPEC_{FREEZE_DATE.replace('-', '')}.yaml"
ADMISSION_GATE = ADMISSION_DIR / f"MAIN_MATRIX_ADMISSION_GATE_{FREEZE_DATE.replace('-', '')}.md"
RECORD_MODE_ENTRY_LOG = ADMISSION_DIR / "MAIN_MATRIX_RECORD_MODE_ENTRY_LOG_20260627.md"
AUDIT_LEDGER = ADMISSION_DIR / f"AUDIT_LEDGER_{FREEZE_DATE.replace('-', '')}.jsonl"
SAFE_RUNS = ADMISSION_DIR / f"SAFE_RUNS_{FREEZE_DATE.replace('-', '')}.csv"
EXCLUDED_RUNS = ADMISSION_DIR / f"EXCLUDED_RUNS_{FREEZE_DATE.replace('-', '')}.csv"
RERUN_REQUIRED = ADMISSION_DIR / f"RERUN_REQUIRED_{FREEZE_DATE.replace('-', '')}.csv"
HASH_MANIFEST = ADMISSION_DIR / f"HASH_MANIFEST_{FREEZE_DATE.replace('-', '')}.jsonl"
FREEZE_SUMMARY = ADMISSION_DIR / f"FREEZE_SUMMARY_{FREEZE_DATE.replace('-', '')}.json"

LIVE_REFRESH_DIR = ADMISSION_DIR / f"live_refresh_{FREEZE_DATE.replace('-', '')}"
LIVE_REFRESH_SUMMARY = LIVE_REFRESH_DIR / "provider_live_refresh_summary.json"
LIVE_REFRESH_REPORT = LIVE_REFRESH_DIR / "PROVIDER_LIVE_REFRESH_REPORT.md"
LIVE_REFRESH_ADAPTER_SOURCE = LIVE_REFRESH_DIR / "provider_adapter_record_source.jsonl"
LIVE_REFRESH_CASSETTE = LIVE_REFRESH_DIR / "provider_live_refresh.cassette.jsonl"
LIVE_REFRESH_REPLAY = LIVE_REFRESH_DIR / "provider_live_refresh.replay.jsonl"
LIVE_REFRESH_SMOKE_CONFIG = LIVE_REFRESH_DIR / "provider_live_refresh_smoke_config.json"
LIVE_REFRESH_SMOKE_ROWS = LIVE_REFRESH_DIR / "provider_live_refresh_smoke_config.rows.jsonl"

BENCHMARK_SMOKE_DIR = ADMISSION_DIR / "benchmark_smoke_20260626"
BENCHMARK_SMOKE_SUMMARY = BENCHMARK_SMOKE_DIR / "SUMMARY.json"
BENCHMARK_SMOKE_README = BENCHMARK_SMOKE_DIR / "README.md"

METHODS = [
    "loop_only",
    "rolling_summary",
    "rolling_visible_carry_forward",
    "rolling_visible_fields_only",
    "ssr_no_visible_carry",
    "mature_ssr_loop",
]
CORE_METHODS = [
    "rolling_summary",
    "ssr_no_visible_carry",
    "rolling_visible_carry_forward",
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

MODEL_ENDPOINTS = [
    {
        "condition_id": "openrouter_gpt55",
        "provider": "openrouter",
        "provider_route_hint": "openai",
        "access_path": "openrouter_chat_completions_api",
        "base_url": "https://openrouter.ai/api/v1",
        "requested_model": "openai/gpt-5.5",
        "expected_exact_model_string": "openai/gpt-5.5-20260423",
        "api_key_env": "OPENROUTER_API_KEY",
        "openrouter_used": True,
        "fallback_enabled": False,
        "request_controls": {
            "max_tokens": 4096,
            "temperature": {"send_mode": "omitted", "value": None},
            "provider": {"send_mode": "explicit", "value": {"allow_fallbacks": False}},
            "reasoning_or_thinking": {
                "send_mode": "explicit",
                "value": {"reasoning": {"effort": "none"}},
                "reasoning_disable_mode": "openrouter_reasoning_effort_none",
            },
            "stream": {"send_mode": "explicit", "value": False},
            "tools": "disabled",
            "web": "disabled",
            "cache": "not_requested",
        },
        "snapshot_status": "requires_live_refresh_before_api_execution",
    },
    {
        "condition_id": "openrouter_claude48",
        "provider": "openrouter",
        "provider_route_hint": "anthropic",
        "access_path": "openrouter_chat_completions_api",
        "base_url": "https://openrouter.ai/api/v1",
        "requested_model": "anthropic/claude-opus-4.8",
        "expected_exact_model_string": "anthropic/claude-4.8-opus-20260528",
        "api_key_env": "OPENROUTER_API_KEY",
        "openrouter_used": True,
        "fallback_enabled": False,
        "request_controls": {
            "max_tokens": 4096,
            "temperature": {"send_mode": "omitted", "value": None},
            "reasoning_or_thinking": {
                "send_mode": "explicit",
                "value": {"reasoning": {"effort": "none"}},
                "reasoning_disable_mode": "openrouter_reasoning_effort_none",
            },
            "provider": {"send_mode": "explicit", "value": {"allow_fallbacks": False}},
            "stream": {"send_mode": "explicit", "value": False},
            "tools": "disabled",
            "web": "disabled",
            "cache": "not_requested",
        },
        "snapshot_status": "requires_live_refresh_before_api_execution",
    },
    {
        "condition_id": "deepseek_v4pro",
        "provider": "deepseek",
        "access_path": "direct_provider_openai_compatible",
        "base_url": "https://api.deepseek.com",
        "requested_model": "deepseek-v4-pro",
        "api_key_env": "DEEPSEEK_API_KEY",
        "openrouter_used": False,
        "fallback_enabled": False,
        "request_controls": {
            "max_tokens": 4096,
            "temperature": {"send_mode": "explicit", "value": 0},
            "reasoning_or_thinking": {"send_mode": "explicit", "value": {"thinking": {"type": "disabled"}}},
            "stream": {"send_mode": "explicit", "value": False},
            "tools": "disabled",
            "web": "disabled",
            "cache": "not_requested",
        },
        "snapshot_status": "requires_live_refresh_before_api_execution",
    },
    {
        "condition_id": "kimi_k26",
        "provider": "moonshot",
        "access_path": "direct_provider_openai_compatible",
        "base_url": "https://api.moonshot.cn/v1",
        "requested_model": "kimi-k2.6",
        "api_key_env": "MOONSHOT_API_KEY",
        "openrouter_used": False,
        "fallback_enabled": False,
        "request_controls": {
            "max_tokens": 4096,
            "temperature": {"send_mode": "explicit", "value": 0.6},
            "reasoning_or_thinking": {"send_mode": "explicit", "value": {"thinking": {"type": "disabled"}}},
            "stream": {"send_mode": "explicit", "value": False},
            "tools": "disabled",
            "web": "disabled",
            "cache": "not_requested",
        },
        "snapshot_status": "requires_live_refresh_before_api_execution",
    },
    {
        "condition_id": "qwen37max",
        "provider": "dashscope",
        "access_path": "direct_provider_openai_compatible",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "requested_model": "qwen3.7-max",
        "api_key_env": "DASHSCOPE_API_KEY",
        "openrouter_used": False,
        "fallback_enabled": False,
        "request_controls": {
            "max_tokens": 4096,
            "temperature": {"send_mode": "explicit", "value": 0.7},
            "reasoning_or_thinking": {"send_mode": "explicit", "value": {"thinking": {"type": "disabled"}}},
            "stream": {"send_mode": "explicit", "value": False},
            "tools": "disabled",
            "web": "disabled",
            "cache": "not_requested",
        },
        "snapshot_status": "requires_live_refresh_before_api_execution",
    },
]


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_json(value: Any) -> str:
    return sha256_bytes(canonical_json(value).encode("utf-8"))


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def current_live_refresh_summary() -> dict[str, Any] | None:
    if not LIVE_REFRESH_SUMMARY.exists():
        return None
    required_paths = [
        LIVE_REFRESH_REPORT,
        LIVE_REFRESH_ADAPTER_SOURCE,
        LIVE_REFRESH_CASSETTE,
        LIVE_REFRESH_REPLAY,
        LIVE_REFRESH_SMOKE_CONFIG,
        LIVE_REFRESH_SMOKE_ROWS,
    ]
    if any(not path.exists() for path in required_paths):
        return None
    summary = read_json(LIVE_REFRESH_SUMMARY)
    if (
        summary.get("passed") is True
        and summary.get("endpoint_count") == 5
        and summary.get("successful_adapter_rows") == 5
        and summary.get("failure_count") == 0
    ):
        return summary
    return None


def current_benchmark_smoke_summary() -> dict[str, Any] | None:
    if not BENCHMARK_SMOKE_SUMMARY.exists():
        return None
    summary = read_json(BENCHMARK_SMOKE_SUMMARY)
    if (
        summary.get("schema_version") == "pcg_dynamic_state_v2.benchmark_admission_smoke_summary.v1"
        and isinstance(summary.get("completed_model_conditions"), list)
        and isinstance(summary.get("pending_model_conditions"), list)
    ):
        return summary
    return None


def benchmark_smoke_complete(summary: dict[str, Any] | None = None) -> bool:
    smoke_summary = current_benchmark_smoke_summary() if summary is None else summary
    if smoke_summary is None:
        return False
    return (
        smoke_summary.get("full_five_model_smoke_complete") is True
        and smoke_summary.get("pending_model_conditions") == []
        and len(smoke_summary.get("completed_model_conditions", [])) == 5
        and smoke_summary.get("global_threshold_passed") is True
    )


def admission_decision(
    live_summary: dict[str, Any] | None = None,
    smoke_summary: dict[str, Any] | None = None,
) -> str:
    live_summary = current_live_refresh_summary() if live_summary is None else live_summary
    smoke_summary = current_benchmark_smoke_summary() if smoke_summary is None else smoke_summary
    if live_summary is not None:
        if benchmark_smoke_complete(smoke_summary):
            return "READY_FOR_MAIN_RECORD_MODE"
        return "HOLD_FOR_TINY_SMOKE"
    return "HOLD_FOR_PROVIDER_LIVE_REFRESH_AND_TINY_SMOKE"


def live_refresh_metadata(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "passed": True,
        "endpoint_count": summary["endpoint_count"],
        "successful_adapter_rows": summary["successful_adapter_rows"],
        "summary": rel(LIVE_REFRESH_SUMMARY),
        "report": rel(LIVE_REFRESH_REPORT),
        "adapter_record_source": rel(LIVE_REFRESH_ADAPTER_SOURCE),
        "cassette": rel(LIVE_REFRESH_CASSETTE),
        "replay_output": rel(LIVE_REFRESH_REPLAY),
    }


def frozen_model_endpoints(summary: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    endpoints = deepcopy(MODEL_ENDPOINTS)
    if summary is None:
        return endpoints

    results_by_condition = {item["condition_id"]: item for item in summary.get("results", [])}
    for endpoint in endpoints:
        result = results_by_condition.get(endpoint["condition_id"])
        if not result:
            continue
        endpoint["snapshot_status"] = "live_refresh_passed_nonbenchmark_prompt"
        endpoint["live_refresh_result"] = {
            "content_exact_ok": result.get("content_exact_ok"),
            "finish_reason": result.get("finish_reason"),
            "http_status": result.get("http_status"),
            "message_reasoning_present": result.get("message_reasoning_present"),
            "openrouter_generation_metadata_error_body_present": result.get("openrouter_generation_metadata_error_body_present"),
            "openrouter_generation_metadata_http_status": result.get("openrouter_generation_metadata_http_status"),
            "openrouter_generation_metadata_present": result.get("openrouter_generation_metadata_present"),
            "openrouter_generation_metadata_raw_sha256": result.get("openrouter_generation_metadata_raw_sha256"),
            "openrouter_generation_metadata_sha256": result.get("openrouter_generation_metadata_sha256"),
            "openrouter_generation_metadata_status": result.get("openrouter_generation_metadata_status"),
            "raw_response_sha256": result.get("raw_response_sha256"),
            "reasoning_details_present": result.get("reasoning_details_present"),
            "reasoning_tokens": result.get("reasoning_tokens"),
            "request_payload_sha256": result.get("request_payload_sha256"),
            "returned_model": result.get("returned_model"),
        }
    return endpoints


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(canonical_json(row) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def prompt_template_fingerprint(method: str) -> str:
    if method == "rolling_summary":
        method_block = "plain natural-language rolling summary; no typed fields; no deterministic visible-token carry"
    elif method == "loop_only":
        method_block = "current segment only; no persistent carry"
    elif method == "rolling_visible_carry_forward":
        method_block = "visible-only rolling state with VISIBLE_KEEP-style output-bearing carry"
    elif method == "rolling_visible_fields_only":
        method_block = "visible-field negative control; deterministic field carry without SSR attribution"
    elif method == "ssr_no_visible_carry":
        method_block = "SSR schema without deterministic visible-token carry"
    else:
        method_block = "mature SSR loop with OUT/ALW/NO/B/G/N/CK/LOOP slots"
    template = {
        "prompt_builder_version": "pcg_dynamic_state_v2_state_transfer_prompt_builder_20260623_v1",
        "method": method,
        "method_protocol_version": METHOD_PROTOCOLS[method],
        "state_update_policy": method_block,
        "final_prompt_policy": "use only transferred state plus output schema; no hidden answers, oracle fields, scoring metadata, or external context",
        "state_budget_in_prompt": True,
        "task_segments_in_prompt": True,
    }
    return sha256_json(template)


def initial_user_prompt_hash(task: dict[str, Any], method: str, budget: int) -> str:
    segment = task["segments"][0]
    prompt = {
        "prompt_builder_version": "pcg_dynamic_state_v2_state_transfer_prompt_builder_20260623_v1",
        "method": method,
        "task_id": task["task_id"],
        "difficulty": task["difficulty"],
        "family": task["family"],
        "state_budget": budget,
        "prior_transferred_state": "[empty]",
        "segment_id": segment["segment_id"],
        "segment_role": segment["role"],
        "segment_text": segment["text"],
        "output_schema": "method-specific JSON state update",
    }
    return sha256_json(prompt)


def build_rows(experiment_id: str, matrix_role: str, methods: list[str], budgets: list[int], runs: list[int], primary: bool) -> list[dict[str, Any]]:
    visible_rows = read_jsonl(VISIBLE_TASKS)
    oracle_by_id = {row["task_id"]: row for row in read_jsonl(ORACLE_TASKS)}
    model_endpoints = frozen_model_endpoints(current_live_refresh_summary())
    rows: list[dict[str, Any]] = []
    index = 0
    for task in visible_rows:
        task_hash = sha256_json(task)
        oracle_hash = sha256_json(oracle_by_id[task["task_id"]])
        for model in model_endpoints:
            model_controls_hash = sha256_json(model["request_controls"])
            for method in methods:
                prompt_template_hash = prompt_template_fingerprint(method)
                for budget in budgets:
                    for run_id in runs:
                        index += 1
                        row_id = (
                            f"{task['task_id']}::{model['condition_id']}::{method}"
                            f"::budget{budget}::run{run_id}"
                        )
                        logical_key = {
                            "schema_version": "pcg_dynamic_state_v2.logical_request_key.v1",
                            "task_id": task["task_id"],
                            "method": method,
                            "budget": budget,
                            "run_id": run_id,
                            "model_name": model["requested_model"],
                            "model_condition_id": model["condition_id"],
                            "provider": model["provider"],
                            "access_path": model["access_path"],
                            "temperature": model["request_controls"].get("temperature"),
                            "max_tokens": model["request_controls"].get("max_tokens")
                            or model["request_controls"].get("max_completion_tokens"),
                            "prompt_version": "pcg_dynamic_state_v2_state_transfer_prompt_builder_20260623_v1",
                            "scorer_version": "strict_main_matrix_scorer_20260623_v1",
                            "task_manifest_entry_sha256": task_hash,
                            "prompt_template_sha256": prompt_template_hash,
                            "initial_user_prompt_sha256": initial_user_prompt_hash(task, method, budget),
                            "request_controls_sha256": model_controls_hash,
                        }
                        rows.append(
                            {
                                "schema_version": "pcg_dynamic_state_v2.main_matrix_row_freeze.v1",
                                "row_index": index,
                                "experiment_id": experiment_id,
                                "matrix_role": matrix_role,
                                "primary_analysis_eligible": primary,
                                "row_id": row_id,
                                "global_artifact_id": f"{experiment_id}::{row_id}",
                                "task_id": task["task_id"],
                                "task_family": task["family"],
                                "task_difficulty": task["difficulty"],
                                "task_manifest_entry_sha256": task_hash,
                                "oracle_entry_sha256": oracle_hash,
                                "model_condition_id": model["condition_id"],
                                "provider": model["provider"],
                                "access_path": model["access_path"],
                                "requested_model": model["requested_model"],
                                "openrouter_used": model["openrouter_used"],
                                "fallback_enabled": model["fallback_enabled"],
                                "method": method,
                                "method_protocol_version": METHOD_PROTOCOLS[method],
                                "budget": budget,
                                "run_id": run_id,
                                "prompt_template_sha256": prompt_template_hash,
                                "initial_user_prompt_sha256": logical_key["initial_user_prompt_sha256"],
                                "request_controls_sha256": model_controls_hash,
                                "logical_request_key": logical_key,
                                "logical_request_hash": sha256_json(logical_key),
                            }
                        )
    return rows


def build_config(experiment_id: str, matrix_role: str, methods: list[str], budgets: list[int], runs: list[int], rows_path: Path, rows_sha: str, primary: bool) -> dict[str, Any]:
    live_summary = current_live_refresh_summary()
    return {
        "schema_version": "pcg_dynamic_state_v2.main_matrix_config.v1",
        "experiment_id": experiment_id,
        "created_at_utc": FREEZE_TIMESTAMP,
        "matrix_role": matrix_role,
        "primary_analysis_eligible": primary,
        "matrix_shape": {
            "tasks": 40,
            "models": 5,
            "methods": len(methods),
            "budgets": len(budgets),
            "runs": len(runs),
            "expected_rows": 40 * 5 * len(methods) * len(budgets) * len(runs),
        },
        "axes": {
            "tasks": {"count": 40, "source": rel(VISIBLE_TASKS), "oracle": rel(ORACLE_TASKS)},
            "models": [model["condition_id"] for model in MODEL_ENDPOINTS],
            "methods": methods,
            "budgets": budgets,
            "runs": runs,
        },
        "model_endpoint_axis": frozen_model_endpoints(live_summary),
        "method_protocol_versions": {method: METHOD_PROTOCOLS[method] for method in methods},
        "task_source_hashes": {
            "model_visible_manifest_sha256": file_sha256(VISIBLE_TASKS),
            "scorer_oracle_manifest_sha256": file_sha256(ORACLE_TASKS),
            "task_provenance_manifest_sha256": file_sha256(TASK_PROVENANCE),
            "task_split_audit_sha256": file_sha256(TASK_SPLIT_AUDIT),
        },
        "implementation": {
            "runner_contract": rel(RUNNER_PATH),
            "runner_contract_sha256": file_sha256(RUNNER_PATH),
            "strict_scorer": rel(SCORER_PATH),
            "strict_scorer_sha256": file_sha256(SCORER_PATH),
            "base_scorer": rel(BASE_SCORER_PATH),
            "base_scorer_sha256": file_sha256(BASE_SCORER_PATH),
        },
        "main_run_api_policy": {"path": rel(API_POLICY_PATH), "sha256": file_sha256(API_POLICY_PATH)},
        "statistical_analysis_plan": {
            "path": rel(STATISTICAL_ANALYSIS_PLAN_PATH),
            "sha256": file_sha256(STATISTICAL_ANALYSIS_PLAN_PATH),
        },
        "model_axis_disposition": {
            "path": rel(MODEL_AXIS_DISPOSITION_PATH),
            "sha256": file_sha256(MODEL_AXIS_DISPOSITION_PATH),
        },
        "row_manifest": {"path": rel(rows_path), "sha256": rows_sha},
        "request_key_contract": {
            "included_fields": [
                "task_id",
                "method",
                "budget",
                "run_id",
                "model_name",
                "model_condition_id",
                "provider",
                "access_path",
                "temperature",
                "max_tokens",
                "prompt_version",
                "scorer_version",
                "task_manifest_entry_sha256",
                "prompt_template_sha256",
                "initial_user_prompt_sha256",
                "request_controls_sha256",
            ],
            "excluded_volatile_fields": ["timestamp", "api_request_id", "latency_ms", "usage", "cost_usd"],
        },
        "analysis_boundary": {
            "confirmatory_primary": primary,
            "budget_300_excluded_from_primary": 300 in budgets,
            "historical_or_admission_rows_excluded": True,
        },
    }


def write_provider_snapshot() -> None:
    live_summary = current_live_refresh_summary()
    smoke_summary = current_benchmark_smoke_summary()
    smoke_complete = benchmark_smoke_complete(smoke_summary)
    snapshot = {
        "schema_version": "pcg_dynamic_state_v2.provider_supported_parameter_snapshot.v1",
        "created_at_utc": FREEZE_TIMESTAMP,
        "snapshot_scope": "new-repo main-matrix admission",
        "status": (
            "LIVE_REFRESH_PASSED_NONBENCHMARK_PROMPT"
            if live_summary is not None
            else "LOCAL_POLICY_TEMPLATE_ONLY_LIVE_REFRESH_REQUIRED"
        ),
        "blocking_before_api_execution": live_summary is None,
        "reason": (
            (
                "Endpoint strings and request controls are frozen from current protocol; the 2026-06-25 nonbenchmark live refresh passed for all five endpoints. OpenRouter GPT/Claude rows explicitly set reasoning.effort=none and returned zero reasoning tokens. The five-model benchmark smoke has passed."
                if smoke_complete
                else "Endpoint strings and request controls are frozen from current protocol; the 2026-06-25 nonbenchmark live refresh passed for all five endpoints. OpenRouter GPT/Claude rows explicitly set reasoning.effort=none and returned zero reasoning tokens. Tiny benchmark smoke remains required before full record-mode execution."
            )
            if live_summary is not None
            else "Endpoint strings and request controls are frozen from current protocol and inherited pilot configs; live provider-supported-parameter checks must be rerun with credentials immediately before record-mode execution."
        ),
        "endpoint_count": len(MODEL_ENDPOINTS),
        "endpoints": frozen_model_endpoints(live_summary),
        "global_controls": {
            "openrouter_used_in_primary_axis": True,
            "openrouter_conditions": ["openrouter_gpt55", "openrouter_claude48"],
            "direct_provider_conditions": ["deepseek_v4pro", "kimi_k26", "qwen37max"],
            "fallback_allowed": False,
            "tools_allowed": False,
            "web_allowed": False,
            "main_run_api_policy": rel(API_POLICY_PATH),
            "model_axis_disposition": rel(MODEL_AXIS_DISPOSITION_PATH),
            "raw_provider_metadata_required": True,
            "openrouter_generation_error_body_counts_as_metadata_present": False,
            "returned_model_string_required": True,
        },
    }
    if live_summary is not None:
        snapshot["live_refresh"] = live_refresh_metadata(live_summary)
    write_json(PROVIDER_SNAPSHOT, snapshot)


def write_variable_freeze_spec() -> None:
    live_summary = current_live_refresh_summary()
    live_refresh_required = "false" if live_summary is not None else "true"
    live_refresh_summary_line = (
        f"  live_refresh_summary: {rel(LIVE_REFRESH_SUMMARY)}\n"
        if live_summary is not None
        else ""
    )
    text = f"""schema_version: pcg_dynamic_state_v2.variable_freeze_spec.v1
created_at_utc: {FREEZE_TIMESTAMP}
scope: new-repo main-matrix admission
allowed_matrix_axes:
  - task_id
  - model_condition_id
  - method
  - budget
  - run_id
confirmatory_matrix:
  config: {rel(CONFIRMATORY_CONFIG)}
  row_manifest: {rel(CONFIRMATORY_ROWS)}
  budgets: [600, 1200]
  primary_analysis_eligible: true
diagnostic_matrix:
  config: {rel(DIAGNOSTIC_CONFIG)}
  row_manifest: {rel(DIAGNOSTIC_ROWS)}
  budgets: [300]
  primary_analysis_eligible: false
frozen_dataset:
  model_visible_manifest: {rel(VISIBLE_TASKS)}
  model_visible_manifest_sha256: {file_sha256(VISIBLE_TASKS)}
  scorer_oracle_manifest: {rel(ORACLE_TASKS)}
  scorer_oracle_manifest_sha256: {file_sha256(ORACLE_TASKS)}
  task_split_audit: {rel(TASK_SPLIT_AUDIT)}
  task_split_audit_sha256: {file_sha256(TASK_SPLIT_AUDIT)}
frozen_implementation:
  runner_contract: {rel(RUNNER_PATH)}
  runner_contract_sha256: {file_sha256(RUNNER_PATH)}
  strict_scorer: {rel(SCORER_PATH)}
  strict_scorer_sha256: {file_sha256(SCORER_PATH)}
  base_scorer: {rel(BASE_SCORER_PATH)}
  base_scorer_sha256: {file_sha256(BASE_SCORER_PATH)}
main_run_api_policy:
  path: {rel(API_POLICY_PATH)}
  sha256: {file_sha256(API_POLICY_PATH)}
  request_timeout_seconds: 120
  max_transport_retries: 2
  max_concurrent_requests: 10
  concurrency_scope: global_live_adapter
  cache_policy: no_live_cache_replay_only_after_record
statistical_analysis_plan:
  path: {rel(STATISTICAL_ANALYSIS_PLAN_PATH)}
  sha256: {file_sha256(STATISTICAL_ANALYSIS_PLAN_PATH)}
  primary_estimator: design_based_paired_risk_difference
  primary_ci: task_cluster_bootstrap_10000
  primary_contrast: rolling_visible_carry_forward_minus_ssr_no_visible_carry
  key_secondary_contrast: mature_ssr_loop_minus_rolling_visible_carry_forward
  glmm_role: model_assisted_sensitivity_only
  budget300_role: diagnostic_only_excluded_from_primary
model_axis_disposition:
  path: {rel(MODEL_AXIS_DISPOSITION_PATH)}
  sha256: {file_sha256(MODEL_AXIS_DISPOSITION_PATH)}
  kimi_axis: kimi_k26
  kimi_k27_code_status: excluded_before_primary_execution_mandatory_thinking
model_admission_criteria:
  path: {rel(MODEL_ADMISSION_CRITERIA)}
  sha256: {file_sha256(MODEL_ADMISSION_CRITERIA)}
  required_confirmatory_smoke_rows: 60
  per_model_parse_score_threshold: 11/12
  global_parse_score_threshold: 57/60
  outcome_fields_as_admission_filters: false
scorer_metric_contract:
  primary_metric: reliable_composite_success
  decomposition_metrics: [answer_success, state_governance_success]
  strict_governance_requires: state_carry_surface_present
  standalone_state_governance_use: diagnostic_only_not_primary_ranking
  empty_state_diagnostic_arm: loop_only
paper_framing_contract:
  path: {rel(FRAMING_PATH)}
  sha256: {file_sha256(FRAMING_PATH)}
  primary_frame: measurement_paper_about_reliable_co_success
  ssr_role: mechanism_diagnostic_arm_not_primary_method_contribution
frozen_provider_policy:
  snapshot: {rel(PROVIDER_SNAPSHOT)}
  openrouter_variable_control: {rel(OPENROUTER_VARIABLE_CONTROL_PATH)}
  openrouter_variable_control_sha256: {file_sha256(OPENROUTER_VARIABLE_CONTROL_PATH)}
  openrouter_used_in_primary_axis: true
  openrouter_conditions: [openrouter_gpt55, openrouter_claude48]
  direct_provider_conditions: [deepseek_v4pro, kimi_k26, qwen37max]
  fallback_allowed: false
  live_refresh_required_before_api_execution: {live_refresh_required}
{live_refresh_summary_line.rstrip()}
disallowed_pooling:
  - historical_calibration_runs
  - admission_smoke_rows
  - static_sanity_rows
  - targeted_backfills
  - budget_300_diagnostic_rows
  - sentinel_drift_probe_rows
  - routed_provider_rows_without_frozen_route_equivalence
"""
    VARIABLE_FREEZE_SPEC.parent.mkdir(parents=True, exist_ok=True)
    VARIABLE_FREEZE_SPEC.write_text(text, encoding="utf-8", newline="\n")


def write_admission_gate() -> None:
    live_summary = current_live_refresh_summary()
    smoke_summary = current_benchmark_smoke_summary()
    decision = admission_decision(live_summary, smoke_summary)
    smoke_complete = benchmark_smoke_complete(smoke_summary)
    provider_frozen_line = (
        f"- Provider live refresh: `{rel(LIVE_REFRESH_SUMMARY)}`\n"
        if live_summary is not None
        else ""
    )
    if live_summary is not None:
        results_by_condition = {item["condition_id"]: item for item in live_summary.get("results", [])}
        route_lines = []
        for endpoint in MODEL_ENDPOINTS:
            result = results_by_condition.get(endpoint["condition_id"], {})
            returned_model = result.get("returned_model", endpoint["requested_model"])
            if endpoint["openrouter_used"]:
                route_lines.append(f"{endpoint['condition_id']} -> {endpoint['requested_model']} -> {returned_model}")
            else:
                route_lines.append(f"{endpoint['condition_id']} -> {returned_model}")
        provider_section = f"""## Provider Live Refresh Result

The five endpoint live refresh has passed on a non-benchmark prompt. GPT and
Claude are admitted as OpenRouter-routed conditions for this gate:

```text
{chr(10).join(route_lines)}
```

The provider-adapter JSONL closed through VCR `record`, `replay`, and
cassette `audit` for all five refresh rows. These rows are admission-only and
do not enter primary aggregation.

For the OpenRouter GPT and Claude rows, request controls explicitly set
`reasoning: {{"effort": "none"}}`. The live refresh observed
`reasoning_tokens = 0` and no returned reasoning payload for both rows.
"""
        if smoke_complete:
            remaining_intro = "The required benchmark smoke has completed:"
        else:
            remaining_intro = "The matrix is not yet admitted for full API execution. The required tiny\nbenchmark smoke shape is:"
    else:
        provider_section = ""
        remaining_intro = "The matrix is not yet admitted for full API execution. Before record-mode\nexecution, run a live provider refresh and a tiny smoke:"

    smoke_progress = ""
    if smoke_summary is not None:
        completed = smoke_summary.get("completed_model_conditions", [])
        pending = smoke_summary.get("pending_model_conditions", [])
        if completed:
            smoke_progress += f"""As of 2026-06-26, these model conditions have completed this smoke and are
marked `ADMIT_MODEL`:

```text
{chr(10).join(completed)}
```
"""
        if pending:
            smoke_progress += f"""
The remaining blocker is:

```text
{chr(10).join(pending)}
```

The matrix remains `HOLD_FOR_TINY_SMOKE` until the remaining model condition
passes the same benchmark smoke or the model axis is explicitly revised before
execution.
"""
        elif smoke_complete:
            smoke_progress += f"""
No model-condition blocker remains. The matrix gate is `{decision}`. This
authorizes full record-mode execution under the frozen protocol; it does not
create primary result rows.

Record-mode entry log: `{rel(RECORD_MODE_ENTRY_LOG)}`
"""
        smoke_progress = smoke_progress.rstrip() + "\n"

    if not smoke_progress:
        smoke_progress = ""

    text = f"""# Main Matrix Admission Gate

Date: {FREEZE_DATE}

Decision: `{decision}`

This gate belongs to the new anonymous-review repository. It does not inherit
GO/NO-GO state from the older pilot repository. The older repository is used
only as provenance for method semantics and endpoint-planning history.

## What Is Frozen

- Confirmatory config: `{rel(CONFIRMATORY_CONFIG)}`
- Confirmatory rows: `{rel(CONFIRMATORY_ROWS)}`
- Diagnostic config: `{rel(DIAGNOSTIC_CONFIG)}`
- Diagnostic rows: `{rel(DIAGNOSTIC_ROWS)}`
- Variable freeze spec: `{rel(VARIABLE_FREEZE_SPEC)}`
- Model admission criteria: `{rel(MODEL_ADMISSION_CRITERIA)}`
- Provider policy snapshot: `{rel(PROVIDER_SNAPSHOT)}`
- Provider live refresh: `{rel(LIVE_REFRESH_SUMMARY)}`
- Hash manifest: `{rel(HASH_MANIFEST)}`

## Static Admission Result

Static freeze checks are expected to pass with:

```bash
python3 artifact/verification/verify_main_matrix_freeze.py
```

The static gate verifies row counts, budget separation, method separation, the
scorer metric contract, dataset/task hashes, scorer and runner hashes,
provider-policy fields, and manifest hashes.

{provider_section}
## Benchmark Admission Work

{remaining_intro}

```text
1 task x 5 models x 6 methods x 2 budgets x 1 run = 60 rows
```

Optionally add the diagnostic smoke:

```text
1 task x 5 models x 4 methods x 1 budget x 1 run = 20 rows
```

{smoke_progress}
Admission rows must stay outside `artifact/results/main_matrix/` and must not
enter primary aggregation.

The decision rule for those rows is frozen in
`{rel(MODEL_ADMISSION_CRITERIA)}`.
Engineering, replay, hash, and structured output failures can block a model
condition. Low `answer_success`, `state_governance_success`, or
`reliable_composite_success` cannot block admission by itself, because those
fields are main-experiment outcomes.

## Non-Inheritance Rule

The old pilot repository may supply background and design lineage. It does not
license current primary rows. Current primary rows require the new config,
new row manifest, new request hashes, current provider snapshot, recorded raw
outputs, replay cassette, scorer hash, and post-run H5/E5 manifest.
"""
    if live_summary is None:
        text = text.replace(f"- Provider live refresh: `{rel(LIVE_REFRESH_SUMMARY)}`\n", "")
    ADMISSION_GATE.parent.mkdir(parents=True, exist_ok=True)
    ADMISSION_GATE.write_text(text, encoding="utf-8", newline="\n")


def write_audit_tables() -> None:
    live_summary = current_live_refresh_summary()
    smoke_summary = current_benchmark_smoke_summary()
    smoke_complete = benchmark_smoke_complete(smoke_summary)
    ledger_rows = [
        {
            "claim_id": "new_repo_confirmatory_config_frozen",
            "agent": "matrixgate_static_freeze",
            "claim": "The confirmatory matrix is frozen as 40 tasks x 5 models x 6 methods x 2 budgets x 3 runs.",
            "evidence_strength": "E4",
            "artifact_refs": [rel(CONFIRMATORY_CONFIG), rel(CONFIRMATORY_ROWS)],
            "hash_refs": [],
            "run_refs": [],
            "risk": "R1",
            "blocks_main_matrix": False,
            "resolved": True,
        },
        {
            "claim_id": "budget300_diagnostic_separated",
            "agent": "prematrix_variable_control",
            "claim": "Budget 300 rows are generated only in a diagnostic config and marked ineligible for primary analysis.",
            "evidence_strength": "E4",
            "artifact_refs": [rel(DIAGNOSTIC_CONFIG), rel(DIAGNOSTIC_ROWS)],
            "hash_refs": [],
            "run_refs": [],
            "risk": "R1",
            "blocks_main_matrix": False,
            "resolved": True,
        },
        {
            "claim_id": "strict_scorer_empty_state_loophole_closed",
            "agent": "prematrix_variable_control",
            "claim": "The main-matrix scorer contract uses reliable_composite_success as the primary metric, reports answer and strict governance jointly, and treats standalone governance as diagnostic only.",
            "evidence_strength": "E4",
            "artifact_refs": [
                rel(DECISION_RULES_PATH),
                rel(METHOD_CONDITIONS_PATH),
                rel(VARIABLE_CONTROL_PATH),
                rel(CLAIM_MAP_PATH),
                rel(VARIABLE_FREEZE_SPEC),
                rel(SCORER_PATH),
                rel(BASE_SCORER_PATH),
            ],
            "hash_refs": [],
            "run_refs": [],
            "risk": "R1",
            "blocks_main_matrix": False,
            "resolved": True,
        },
        {
            "claim_id": "paper_framing_measurement_first",
            "agent": "matrixgate_static_freeze",
            "claim": "The paper framing is fixed as reliable co-success measurement; SSR is a mechanism/diagnostic arm and not the central method contribution.",
            "evidence_strength": "E4",
            "artifact_refs": [rel(FRAMING_PATH), rel(CLAIM_MAP_PATH), rel(DECISION_RULES_PATH), rel(METHOD_CONDITIONS_PATH)],
            "hash_refs": [],
            "run_refs": [],
            "risk": "R1",
            "blocks_main_matrix": False,
            "resolved": True,
        },
        {
            "claim_id": "statistical_analysis_plan_frozen",
            "agent": "matrixgate_static_freeze",
            "claim": "Primary confirmatory inference is frozen as design-based paired risk differences with task-cluster bootstrap confidence intervals; GLMMs are sensitivity analyses.",
            "evidence_strength": "E4",
            "artifact_refs": [
                rel(STATISTICAL_ANALYSIS_PLAN_PATH),
                rel(DECISION_RULES_PATH),
                rel(VARIABLE_FREEZE_SPEC),
            ],
            "hash_refs": [],
            "run_refs": [],
            "risk": "R1",
            "blocks_main_matrix": False,
            "resolved": True,
        },
        {
            "claim_id": "main_run_api_policy_frozen",
            "agent": "prematrix_variable_control",
            "claim": "Retry, timeout, concurrency, cache, and missingness policy is frozen before main-run execution.",
            "evidence_strength": "E4",
            "artifact_refs": [rel(API_POLICY_PATH), rel(VARIABLE_CONTROL_PATH), rel(VARIABLE_FREEZE_SPEC)],
            "hash_refs": [],
            "run_refs": [],
            "risk": "R1",
            "blocks_main_matrix": False,
            "resolved": True,
        },
        {
            "claim_id": "openrouter_variable_control_frozen",
            "agent": "openrouter_normalization",
            "claim": "OpenRouter is frozen as the GPT/Claude provider route, not as a method arm or independent treatment; fallback, reasoning, returned-model, metadata, and replay controls are specified.",
            "evidence_strength": "E4",
            "artifact_refs": [
                rel(OPENROUTER_VARIABLE_CONTROL_PATH),
                rel(PROVIDER_SNAPSHOT),
                rel(VARIABLE_CONTROL_PATH),
                rel(METHOD_CONDITIONS_PATH),
                rel(VARIABLE_FREEZE_SPEC),
            ],
            "hash_refs": [],
                    "run_refs": [
                        "provider_live_refresh_20260625",
                        "benchmark_smoke_20260626/openrouter_gpt55",
                        "benchmark_smoke_20260626/openrouter_claude48",
                    ],
            "risk": "R1",
            "blocks_main_matrix": False,
            "resolved": True,
        },
        {
            "claim_id": "model_admission_criteria_frozen",
            "agent": "matrixgate_static_freeze",
            "claim": "Model-level tiny-smoke admission criteria are frozen before benchmark smoke execution; outcome fields are not admission filters.",
            "evidence_strength": "E4",
            "artifact_refs": [rel(MODEL_ADMISSION_CRITERIA), rel(VARIABLE_FREEZE_SPEC), rel(ADMISSION_GATE)],
            "hash_refs": [],
            "run_refs": [],
            "risk": "R1",
            "blocks_main_matrix": False,
            "resolved": True,
        },
        {
            "claim_id": "kimi_k27_reasoning_exclusion_frozen",
            "agent": "openrouter_normalization",
            "claim": "Kimi K2.7 Code is outside the primary model axis because official Kimi documentation makes it a mandatory-thinking condition; Kimi K2.6 is the frozen Kimi condition with explicit thinking disablement.",
            "evidence_strength": "E4",
            "artifact_refs": [rel(MODEL_AXIS_DISPOSITION_PATH), rel(API_POLICY_PATH), rel(PROVIDER_SNAPSHOT)],
            "hash_refs": [],
            "run_refs": [],
            "risk": "R1",
            "blocks_main_matrix": False,
            "resolved": True,
        },
    ]
    if live_summary is None:
        ledger_rows.append(
            {
                "claim_id": "provider_live_refresh_pending",
                "agent": "openrouter_normalization",
                "claim": "Provider policy is locally frozen, but live supported-parameter refresh and returned-model checks remain required before API execution.",
                "evidence_strength": "E3",
                "artifact_refs": [rel(PROVIDER_SNAPSHOT)],
                "hash_refs": [],
                "run_refs": [],
                "risk": "R3",
                "blocks_main_matrix": True,
                "resolved": False,
            }
        )
        safe_rows: list[dict[str, Any]] = []
        rerun_rows = [
            {
                "run_id": "provider_live_refresh",
                "reason": "five endpoint supported-parameter and fallback/offline policy snapshot must be refreshed before API execution",
                "notes": "not a result row",
            },
            {
                "run_id": "tiny_live_smoke",
                "reason": "runner/cassette/logging smoke must pass before 7200-row record mode",
                "notes": "admission only; excluded from primary aggregation",
            },
        ]
    else:
        ledger_rows.extend(
            [
                {
                    "claim_id": "provider_live_refresh_passed_nonbenchmark",
                    "agent": "openrouter_normalization",
                    "claim": "The five endpoint provider live refresh passed on a nonbenchmark prompt; OpenRouter GPT/Claude returned expected exact model strings and adapter rows were available.",
                    "evidence_strength": "E4",
                    "artifact_refs": [rel(LIVE_REFRESH_SUMMARY), rel(LIVE_REFRESH_REPORT), rel(LIVE_REFRESH_ADAPTER_SOURCE)],
                    "hash_refs": [],
                    "run_refs": [],
                    "risk": "R1",
                    "blocks_main_matrix": False,
                    "resolved": True,
                },
                {
                    "claim_id": "vcr_adapter_record_replay_closed",
                    "agent": "hash_interlock",
                    "claim": "Provider-adapter JSONL closed through VCR record, replay, and cassette audit for five live refresh rows.",
                    "evidence_strength": "E4",
                    "artifact_refs": [rel(LIVE_REFRESH_CASSETTE), rel(LIVE_REFRESH_REPLAY), rel(LIVE_REFRESH_SMOKE_CONFIG)],
                    "hash_refs": [],
                    "run_refs": ["provider_live_refresh"],
                    "risk": "R1",
                    "blocks_main_matrix": False,
                    "resolved": True,
                },
            ]
        )
        if smoke_complete:
            ledger_rows.append(
                {
                    "claim_id": "five_model_benchmark_smoke_passed",
                    "agent": "matrixgate_static_freeze",
                    "claim": "All five frozen model conditions passed benchmark admission smoke; the main matrix is ready for record-mode execution under the frozen protocol.",
                    "evidence_strength": "E4",
                    "artifact_refs": [
                        rel(BENCHMARK_SMOKE_SUMMARY),
                        rel(BENCHMARK_SMOKE_README),
                        rel(ADMISSION_GATE),
                        rel(RECORD_MODE_ENTRY_LOG),
                    ],
                    "hash_refs": [],
                    "run_refs": ["benchmark_smoke_20260626"],
                    "risk": "R1",
                    "blocks_main_matrix": False,
                    "resolved": True,
                }
            )
        safe_rows = [
            {
                "run_id": "provider_live_refresh",
                "status": "SAFE_ADMISSION_ONLY",
                "notes": "five endpoint nonbenchmark live refresh passed; excluded from primary aggregation",
            }
        ]
        if smoke_complete:
            safe_rows.append(
                {
                    "run_id": "benchmark_smoke_20260626",
                    "status": "SAFE_ADMISSION_ONLY",
                    "notes": "five-model benchmark admission smoke passed; excluded from primary aggregation",
                }
            )
            rerun_rows = []
        else:
            rerun_rows = [
                {
                    "run_id": "tiny_live_smoke",
                    "reason": "runner/cassette/logging smoke must pass before 7200-row record mode",
                    "notes": "admission only; excluded from primary aggregation",
                }
            ]
    write_jsonl(AUDIT_LEDGER, ledger_rows)
    write_csv(SAFE_RUNS, safe_rows, ["run_id", "status", "notes"])
    write_csv(EXCLUDED_RUNS, [], ["run_id", "reason", "notes"])
    write_csv(RERUN_REQUIRED, rerun_rows, ["run_id", "reason", "notes"])


def artifact_manifest_rows() -> list[dict[str, Any]]:
    paths = [
        VISIBLE_TASKS,
        ORACLE_TASKS,
        TASK_PROVENANCE,
        TASK_SPLIT_AUDIT,
        EXPERIMENT_VARIABLE_OVERVIEW_PATH,
        DECISION_RULES_PATH,
        STATISTICAL_ANALYSIS_PLAN_PATH,
        API_POLICY_PATH,
        FRAMING_PATH,
        METHOD_CONDITIONS_PATH,
        VARIABLE_CONTROL_PATH,
        MODEL_AXIS_DISPOSITION_PATH,
        OPENROUTER_VARIABLE_CONTROL_PATH,
        CLAIM_MAP_PATH,
        QUICKSTART_PATH,
        BENCHMARK_CARD_PATH,
        CROISSANT_JSON_PATH,
        CROISSANT_MAPPING_PATH,
        RAI_LIMITATIONS_PATH,
        HOSTING_PLAN_PATH,
        SCORER_PATH,
        BASE_SCORER_PATH,
        RUNNER_PATH,
        VERIFY_DIR / "build_main_matrix_freeze.py",
        VERIFY_DIR / "verify_main_matrix_freeze.py",
        VERIFY_DIR / "refresh_main_matrix_providers.py",
        CONFIRMATORY_CONFIG,
        CONFIRMATORY_ROWS,
        DIAGNOSTIC_CONFIG,
        DIAGNOSTIC_ROWS,
        PROVIDER_SNAPSHOT,
        MODEL_ADMISSION_CRITERIA,
        VARIABLE_FREEZE_SPEC,
        ADMISSION_GATE,
        RECORD_MODE_ENTRY_LOG,
        AUDIT_LEDGER,
        SAFE_RUNS,
        EXCLUDED_RUNS,
        RERUN_REQUIRED,
        BENCHMARK_SMOKE_README,
        BENCHMARK_SMOKE_SUMMARY,
    ]
    if LIVE_REFRESH_DIR.exists():
        paths.extend(
            [
                LIVE_REFRESH_REPORT,
                LIVE_REFRESH_ADAPTER_SOURCE,
                LIVE_REFRESH_CASSETTE,
                LIVE_REFRESH_REPLAY,
                LIVE_REFRESH_SMOKE_CONFIG,
                LIVE_REFRESH_SMOKE_ROWS,
                LIVE_REFRESH_SUMMARY,
            ]
        )
    rows = []
    for path in paths:
        if not path.exists():
            continue
        rows.append(
            {
                "schema_version": "pcg_dynamic_state_v2.freeze_hash_manifest.v1",
                "path": rel(path),
                "artifact_type": classify(path),
                "sha256": file_sha256(path),
                "size_bytes": path.stat().st_size,
                "notes": "new-repo main-matrix freeze packet",
            }
        )
    return rows


def classify(path: Path) -> str:
    name = path.name.lower()
    if "manifest" in name or "config" in name or path.suffix == ".json":
        return "config"
    if path.suffix == ".py":
        return "code"
    if path.suffix == ".yaml":
        return "variable_freeze_spec"
    if path.suffix == ".csv":
        return "gate_table"
    if path.suffix == ".md":
        return "protocol"
    return "artifact"


def build_all() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    ADMISSION_DIR.mkdir(parents=True, exist_ok=True)
    live_summary = current_live_refresh_summary()
    decision = admission_decision(live_summary)

    confirmatory_rows = build_rows(CONFIRMATORY_ID, "confirmatory_primary", METHODS, [600, 1200], [1, 2, 3], True)
    write_jsonl(CONFIRMATORY_ROWS, confirmatory_rows)
    confirmatory_config = build_config(
        CONFIRMATORY_ID,
        "confirmatory_primary",
        METHODS,
        [600, 1200],
        [1, 2, 3],
        CONFIRMATORY_ROWS,
        file_sha256(CONFIRMATORY_ROWS),
        True,
    )
    write_json(CONFIRMATORY_CONFIG, confirmatory_config)

    diagnostic_rows = build_rows(DIAGNOSTIC_ID, "budget300_diagnostic", CORE_METHODS, [300], [1], False)
    write_jsonl(DIAGNOSTIC_ROWS, diagnostic_rows)
    diagnostic_config = build_config(
        DIAGNOSTIC_ID,
        "budget300_diagnostic",
        CORE_METHODS,
        [300],
        [1],
        DIAGNOSTIC_ROWS,
        file_sha256(DIAGNOSTIC_ROWS),
        False,
    )
    write_json(DIAGNOSTIC_CONFIG, diagnostic_config)

    write_provider_snapshot()
    write_variable_freeze_spec()
    write_admission_gate()
    write_audit_tables()
    manifest_rows = artifact_manifest_rows()
    write_jsonl(HASH_MANIFEST, manifest_rows)
    summary = {
        "schema_version": "pcg_dynamic_state_v2.freeze_summary.v1",
        "created_at_utc": FREEZE_TIMESTAMP,
        "decision": decision,
        "confirmatory_config": rel(CONFIRMATORY_CONFIG),
        "confirmatory_config_sha256": file_sha256(CONFIRMATORY_CONFIG),
        "confirmatory_rows": rel(CONFIRMATORY_ROWS),
        "confirmatory_rows_sha256": file_sha256(CONFIRMATORY_ROWS),
        "confirmatory_row_count": len(confirmatory_rows),
        "diagnostic_config": rel(DIAGNOSTIC_CONFIG),
        "diagnostic_config_sha256": file_sha256(DIAGNOSTIC_CONFIG),
        "diagnostic_rows": rel(DIAGNOSTIC_ROWS),
        "diagnostic_rows_sha256": file_sha256(DIAGNOSTIC_ROWS),
        "diagnostic_row_count": len(diagnostic_rows),
        "provider_snapshot": rel(PROVIDER_SNAPSHOT),
        "provider_snapshot_sha256": file_sha256(PROVIDER_SNAPSHOT),
        "hash_manifest": rel(HASH_MANIFEST),
        "hash_manifest_sha256": file_sha256(HASH_MANIFEST),
    }
    if live_summary is not None:
        summary["provider_live_refresh_passed"] = True
        summary["provider_live_refresh_successful_adapter_rows"] = live_summary["successful_adapter_rows"]
        summary["provider_live_refresh_summary"] = rel(LIVE_REFRESH_SUMMARY)
    write_json(FREEZE_SUMMARY, summary)


def main() -> int:
    build_all()
    print(
        canonical_json(
            {
                "built": True,
                "confirmatory_rows": 7200,
                "diagnostic_rows": 800,
                "admission_decision": admission_decision(),
                "freeze_summary": rel(FREEZE_SUMMARY),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
