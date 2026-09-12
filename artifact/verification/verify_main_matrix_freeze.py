#!/usr/bin/env python3
"""Verify the new-repo main-matrix freeze packet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DATE = "20260625"
CONFIG_DIR = ROOT / "artifact/protocol/main_matrix/configs"
ADMISSION_DIR = ROOT / "artifact/protocol/main_matrix/admission"
MAIN_MATRIX_PROTOCOL_DIR = ROOT / "artifact/protocol/main_matrix"

CONFIRMATORY_ID = "pcg_dynamic_state_v2_confirmatory_40task_5model_6method_2budget_3run_20260625"
DIAGNOSTIC_ID = "pcg_dynamic_state_v2_budget300_diagnostic_40task_5model_4method_1budget_1run_20260625"

CONFIRMATORY_CONFIG = CONFIG_DIR / f"{CONFIRMATORY_ID}.json"
CONFIRMATORY_ROWS = CONFIG_DIR / f"{CONFIRMATORY_ID}.rows.jsonl"
DIAGNOSTIC_CONFIG = CONFIG_DIR / f"{DIAGNOSTIC_ID}.json"
DIAGNOSTIC_ROWS = CONFIG_DIR / f"{DIAGNOSTIC_ID}.rows.jsonl"
PROVIDER_SNAPSHOT = ADMISSION_DIR / f"PROVIDER_SUPPORTED_PARAMETER_SNAPSHOT_{DATE}.json"
MODEL_ADMISSION_CRITERIA = ADMISSION_DIR / "MODEL_ADMISSION_CRITERIA_20260626.md"
HASH_MANIFEST = ADMISSION_DIR / f"HASH_MANIFEST_{DATE}.jsonl"
FREEZE_SUMMARY = ADMISSION_DIR / f"FREEZE_SUMMARY_{DATE}.json"
VARIABLE_FREEZE_SPEC = ADMISSION_DIR / f"VARIABLE_FREEZE_SPEC_{DATE}.yaml"
AUDIT_LEDGER = ADMISSION_DIR / f"AUDIT_LEDGER_{DATE}.jsonl"
LIVE_REFRESH_DIR = ADMISSION_DIR / f"live_refresh_{DATE}"
LIVE_REFRESH_SUMMARY = LIVE_REFRESH_DIR / "provider_live_refresh_summary.json"
EXPERIMENT_VARIABLE_OVERVIEW = MAIN_MATRIX_PROTOCOL_DIR / "EXPERIMENT_VARIABLE_CONTROL_OVERVIEW.md"
STATISTICAL_ANALYSIS_PLAN = MAIN_MATRIX_PROTOCOL_DIR / "STATISTICAL_ANALYSIS_PLAN.md"
MAIN_RUN_API_POLICY = MAIN_MATRIX_PROTOCOL_DIR / "MAIN_RUN_API_POLICY.md"
PAPER_FRAMING = MAIN_MATRIX_PROTOCOL_DIR / "PAPER_FRAMING_AND_RQS.md"
MODEL_AXIS_DISPOSITION = MAIN_MATRIX_PROTOCOL_DIR / "MODEL_AXIS_DISPOSITION.md"
OPENROUTER_VARIABLE_CONTROL = ADMISSION_DIR / "OPENROUTER_VARIABLE_CONTROL_20260626.md"


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if line.strip():
                row = json.loads(line)
                row["_line_number"] = line_number
                rows.append(row)
    return rows


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def add(failures: list[str], condition: bool, message: str) -> None:
    if not condition:
        failures.append(message)


def verify_declared_hash(
    failures: list[str],
    owner: str,
    declared_path: str | None,
    declared_sha: str | None,
    label: str,
) -> None:
    add(failures, bool(declared_path), f"{owner}: missing {label} path")
    add(failures, bool(declared_sha), f"{owner}: missing {label} sha256")
    if not declared_path:
        return
    path = ROOT / declared_path
    add(failures, path.exists(), f"{owner}: {label} path missing: {declared_path}")
    if path.exists() and declared_sha:
        add(failures, declared_sha == file_sha256(path), f"{owner}: {label} hash mismatch")


def verify_config(config_path: Path, rows_path: Path, expected: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    config = read_json(config_path)
    rows = read_jsonl(rows_path)
    shape = config["matrix_shape"]

    add(failures, shape["expected_rows"] == expected["rows"], f"{config_path.name}: expected_rows mismatch")
    add(failures, len(rows) == expected["rows"], f"{rows_path.name}: row count {len(rows)} != {expected['rows']}")
    add(failures, config["axes"]["budgets"] == expected["budgets"], f"{config_path.name}: budgets mismatch")
    add(failures, config["axes"]["methods"] == expected["methods"], f"{config_path.name}: methods mismatch")
    add(failures, config["axes"]["runs"] == expected["runs"], f"{config_path.name}: runs mismatch")
    add(failures, config["primary_analysis_eligible"] is expected["primary"], f"{config_path.name}: primary flag mismatch")
    add(failures, config["row_manifest"]["sha256"] == file_sha256(rows_path), f"{config_path.name}: row manifest hash mismatch")

    implementation = config.get("implementation", {})
    verify_declared_hash(
        failures,
        config_path.name,
        implementation.get("runner_contract"),
        implementation.get("runner_contract_sha256"),
        "runner contract",
    )
    verify_declared_hash(
        failures,
        config_path.name,
        implementation.get("strict_scorer"),
        implementation.get("strict_scorer_sha256"),
        "strict scorer",
    )
    verify_declared_hash(
        failures,
        config_path.name,
        implementation.get("base_scorer"),
        implementation.get("base_scorer_sha256"),
        "base scorer",
    )
    policy = config.get("main_run_api_policy", {})
    verify_declared_hash(
        failures,
        config_path.name,
        policy.get("path"),
        policy.get("sha256"),
        "main-run API policy",
    )
    sap = config.get("statistical_analysis_plan", {})
    verify_declared_hash(
        failures,
        config_path.name,
        sap.get("path"),
        sap.get("sha256"),
        "statistical analysis plan",
    )
    model_axis = config.get("model_axis_disposition", {})
    verify_declared_hash(
        failures,
        config_path.name,
        model_axis.get("path"),
        model_axis.get("sha256"),
        "model axis disposition",
    )

    row_ids = set()
    request_hashes = set()
    budgets = set()
    methods = set()
    runs = set()
    models = set()
    primary_flags = set()
    openrouter_flags = set()
    fallback_flags = set()
    openrouter_by_model: dict[str, bool] = {}
    for row in rows:
        row_id = row.get("row_id")
        request_hash = row.get("logical_request_hash")
        add(failures, row_id not in row_ids, f"duplicate row_id {row_id}")
        row_ids.add(row_id)
        add(failures, request_hash not in request_hashes, f"duplicate logical_request_hash {request_hash}")
        request_hashes.add(request_hash)
        budgets.add(row["budget"])
        methods.add(row["method"])
        runs.add(row["run_id"])
        models.add(row["model_condition_id"])
        primary_flags.add(row["primary_analysis_eligible"])
        openrouter_flags.add(row["openrouter_used"])
        openrouter_by_model[row["model_condition_id"]] = bool(row["openrouter_used"])
        fallback_flags.add(row["fallback_enabled"])
        add(failures, row["logical_request_key"]["task_id"] == row["task_id"], f"{row_id}: request key task mismatch")
        add(failures, row["logical_request_key"]["method"] == row["method"], f"{row_id}: request key method mismatch")
        add(failures, row["logical_request_key"]["budget"] == row["budget"], f"{row_id}: request key budget mismatch")

    add(failures, budgets == set(expected["budgets"]), f"{rows_path.name}: observed budgets {sorted(budgets)}")
    add(failures, methods == set(expected["methods"]), f"{rows_path.name}: observed methods {sorted(methods)}")
    add(failures, runs == set(expected["runs"]), f"{rows_path.name}: observed runs {sorted(runs)}")
    add(failures, len(models) == 5, f"{rows_path.name}: observed model count {len(models)}")
    add(failures, primary_flags == {expected["primary"]}, f"{rows_path.name}: primary flags {primary_flags}")
    add(failures, openrouter_flags == {False, True}, f"{rows_path.name}: openrouter flags {openrouter_flags}")
    add(
        failures,
        openrouter_by_model == {
            "openrouter_gpt55": True,
            "openrouter_claude48": True,
            "deepseek_v4pro": False,
            "kimi_k26": False,
            "qwen37max": False,
        },
        f"{rows_path.name}: OpenRouter model mapping {openrouter_by_model}",
    )
    add(failures, fallback_flags == {False}, f"{rows_path.name}: fallback flags {fallback_flags}")
    return failures


def verify_provider_snapshot() -> list[str]:
    failures: list[str] = []
    snapshot = read_json(PROVIDER_SNAPSHOT)
    endpoints = snapshot["endpoints"]
    openrouter_conditions = {"openrouter_gpt55", "openrouter_claude48"}
    add(failures, len(endpoints) == 5, "provider snapshot must contain five endpoints")
    add(failures, snapshot["global_controls"]["openrouter_used_in_primary_axis"] is True, "OpenRouter must be recorded for GPT/Claude primary conditions")
    add(failures, snapshot["global_controls"]["fallback_allowed"] is False, "fallback must be globally disallowed")
    add(
        failures,
        snapshot["global_controls"].get("openrouter_generation_error_body_counts_as_metadata_present") is False,
        "OpenRouter error bodies must not count as present generation metadata",
    )
    api_policy_path = snapshot["global_controls"].get("main_run_api_policy")
    add(failures, api_policy_path == rel(MAIN_RUN_API_POLICY), "provider snapshot main-run API policy path mismatch")
    add(failures, (ROOT / api_policy_path).exists() if api_policy_path else False, "provider snapshot main-run API policy missing")
    model_axis_path = snapshot["global_controls"].get("model_axis_disposition")
    add(failures, model_axis_path == rel(MODEL_AXIS_DISPOSITION), "provider snapshot model-axis disposition path mismatch")
    add(failures, (ROOT / model_axis_path).exists() if model_axis_path else False, "provider snapshot model-axis disposition missing")
    live_refresh_passed = snapshot.get("status") == "LIVE_REFRESH_PASSED_NONBENCHMARK_PROMPT"
    if live_refresh_passed:
        add(failures, snapshot.get("blocking_before_api_execution") is False, "live-passed provider snapshot must not block API execution")
        add(failures, snapshot.get("live_refresh", {}).get("passed") is True, "live-passed provider snapshot missing live_refresh evidence")
        add(failures, LIVE_REFRESH_SUMMARY.exists(), "live-passed provider snapshot references missing live refresh summary")
    for endpoint in endpoints:
        cid = endpoint["condition_id"]
        add(failures, endpoint["fallback_enabled"] is False, f"{cid}: fallback enabled")
        add(
            failures,
            bool(endpoint["openrouter_used"]) == (cid in openrouter_conditions),
            f"{cid}: OpenRouter route flag mismatch",
        )
        controls = endpoint["request_controls"]
        add(failures, controls.get("tools") == "disabled", f"{cid}: tools not disabled")
        add(failures, controls.get("web") == "disabled", f"{cid}: web not disabled")
        add(failures, bool(endpoint.get("requested_model")), f"{cid}: missing requested_model")
        if live_refresh_passed:
            add(
                failures,
                endpoint.get("snapshot_status") == "live_refresh_passed_nonbenchmark_prompt",
                f"{cid}: live refresh snapshot status missing",
            )
            result = endpoint.get("live_refresh_result", {})
            add(failures, result.get("http_status") == 200, f"{cid}: live refresh http status not 200")
            add(failures, result.get("content_exact_ok") is True, f"{cid}: live refresh content was not exact OK")
            add(failures, bool(result.get("raw_response_sha256")), f"{cid}: missing live refresh raw response hash")
            add(failures, bool(result.get("request_payload_sha256")), f"{cid}: missing live refresh request payload hash")
        if cid in openrouter_conditions:
            add(failures, endpoint["provider"] == "openrouter", f"{cid}: provider must be openrouter")
            add(failures, endpoint["access_path"] == "openrouter_chat_completions_api", f"{cid}: access path must be OpenRouter")
            add(failures, controls.get("provider", {}).get("value", {}).get("allow_fallbacks") is False, f"{cid}: OpenRouter fallback policy missing")
            reasoning = controls.get("reasoning_or_thinking", {})
            add(failures, reasoning.get("send_mode") == "explicit", f"{cid}: OpenRouter reasoning control must be explicit")
            add(
                failures,
                reasoning.get("value", {}).get("reasoning", {}).get("effort") == "none",
                f"{cid}: OpenRouter reasoning effort must be none",
            )
            if live_refresh_passed:
                result = endpoint.get("live_refresh_result", {})
                add(failures, result.get("returned_model") == endpoint.get("expected_exact_model_string"), f"{cid}: returned model mismatch")
                metadata_status = result.get("openrouter_generation_metadata_status")
                metadata_present = result.get("openrouter_generation_metadata_present")
                metadata_http_status = result.get("openrouter_generation_metadata_http_status")
                add(
                    failures,
                    metadata_status in {"present", "unavailable_error"},
                    f"{cid}: OpenRouter generation metadata status invalid: {metadata_status}",
                )
                if metadata_status == "present":
                    add(failures, metadata_present is True, f"{cid}: present OpenRouter metadata not marked present")
                    add(failures, 200 <= int(metadata_http_status or 0) < 300, f"{cid}: present OpenRouter metadata has non-2xx status")
                    add(failures, bool(result.get("openrouter_generation_metadata_sha256")), f"{cid}: present OpenRouter metadata missing hash")
                    add(failures, result.get("openrouter_generation_metadata_error_body_present") is False, f"{cid}: present OpenRouter metadata has error body")
                if metadata_status == "unavailable_error":
                    add(failures, metadata_present is False, f"{cid}: error OpenRouter metadata must not be marked present")
                    add(failures, bool(result.get("openrouter_generation_metadata_raw_sha256")), f"{cid}: unavailable OpenRouter metadata missing raw error hash")
                add(failures, result.get("reasoning_tokens") == 0, f"{cid}: OpenRouter reasoning tokens not zero")
                add(failures, result.get("message_reasoning_present") is False, f"{cid}: message reasoning payload present")
                add(failures, result.get("reasoning_details_present") is False, f"{cid}: reasoning details payload present")
    return failures


def verify_hash_manifest() -> list[str]:
    failures: list[str] = []
    rows = read_jsonl(HASH_MANIFEST)
    add(failures, len(rows) >= 10, "hash manifest is unexpectedly small")
    for row in rows:
        path = ROOT / row["path"]
        add(failures, path.exists(), f"manifest path missing: {row['path']}")
        if path.exists():
            add(failures, row["sha256"] == file_sha256(path), f"manifest hash mismatch: {row['path']}")
    return failures


def verify_scorer_metric_contract() -> list[str]:
    failures: list[str] = []
    spec_text = VARIABLE_FREEZE_SPEC.read_text(encoding="utf-8")
    overview_text = EXPERIMENT_VARIABLE_OVERVIEW.read_text(encoding="utf-8")
    add(failures, "40 tasks x 5 models x 6 methods x 2 budgets x 3 runs = 7,200 rows" in overview_text, "variable overview missing confirmatory matrix shape")
    add(failures, "40 tasks x 5 models x 4 methods x 1 budget x 1 run = 800 rows" in overview_text, "variable overview missing diagnostic matrix shape")
    add(failures, "Everything else is a frozen control or recorded metadata" in overview_text, "variable overview missing axis/control boundary")
    add(failures, "If this overview conflicts with a hash-locked source file" in overview_text, "variable overview missing source-authority boundary")
    add(failures, "primary_metric: reliable_composite_success" in spec_text, "variable freeze missing primary metric")
    add(failures, "strict_governance_requires: state_carry_surface_present" in spec_text, "variable freeze missing strict governance requirement")
    add(
        failures,
        "standalone_state_governance_use: diagnostic_only_not_primary_ranking" in spec_text,
        "variable freeze missing diagnostic-only governance rule",
    )

    ledger_rows = read_jsonl(AUDIT_LEDGER)
    claim_ids = {row.get("claim_id") for row in ledger_rows}
    add(
        failures,
        "strict_scorer_empty_state_loophole_closed" in claim_ids,
        "audit ledger missing strict scorer empty-state claim",
    )
    add(
        failures,
        "main_run_api_policy_frozen" in claim_ids,
        "audit ledger missing main-run API policy claim",
    )
    add(failures, MAIN_RUN_API_POLICY.exists(), "main-run API policy file missing")
    add(failures, PAPER_FRAMING.exists(), "paper framing file missing")
    add(failures, STATISTICAL_ANALYSIS_PLAN.exists(), "statistical analysis plan file missing")
    add(failures, MODEL_ADMISSION_CRITERIA.exists(), "model admission criteria file missing")
    add(failures, "max_transport_retries: 2" in spec_text, "variable freeze missing retry policy")
    add(failures, "max_concurrent_requests: 10" in spec_text, "variable freeze missing concurrency policy")
    add(failures, "concurrency_scope: global_live_adapter" in spec_text, "variable freeze missing concurrency scope")
    add(failures, "required_confirmatory_smoke_rows: 60" in spec_text, "variable freeze missing model admission smoke size")
    add(failures, "per_model_parse_score_threshold: 11/12" in spec_text, "variable freeze missing per-model admission threshold")
    add(failures, "global_parse_score_threshold: 57/60" in spec_text, "variable freeze missing global admission threshold")
    add(failures, "kimi_axis: kimi_k26" in spec_text, "variable freeze missing Kimi axis decision")
    add(
        failures,
        "kimi_k27_code_status: excluded_before_primary_execution_mandatory_thinking" in spec_text,
        "variable freeze missing Kimi K2.7 reasoning exclusion",
    )
    add(
        failures,
        "outcome_fields_as_admission_filters: false" in spec_text,
        "variable freeze missing admission outcome-filter boundary",
    )
    add(
        failures,
        "primary_frame: measurement_paper_about_reliable_co_success" in spec_text,
        "variable freeze missing measurement-first framing",
    )
    add(
        failures,
        "primary_estimator: design_based_paired_risk_difference" in spec_text,
        "variable freeze missing SAP primary estimator",
    )
    add(
        failures,
        "primary_ci: task_cluster_bootstrap_10000" in spec_text,
        "variable freeze missing SAP bootstrap rule",
    )
    add(
        failures,
        "glmm_role: model_assisted_sensitivity_only" in spec_text,
        "variable freeze missing SAP GLMM sensitivity boundary",
    )
    add(
        failures,
        "paper_framing_measurement_first" in claim_ids,
        "audit ledger missing measurement-first framing claim",
    )
    add(
        failures,
        "statistical_analysis_plan_frozen" in claim_ids,
        "audit ledger missing statistical-analysis-plan claim",
    )
    add(
        failures,
        "model_admission_criteria_frozen" in claim_ids,
        "audit ledger missing model admission criteria claim",
    )
    add(
        failures,
        "kimi_k27_reasoning_exclusion_frozen" in claim_ids,
        "audit ledger missing Kimi K2.7 reasoning exclusion claim",
    )
    add(
        failures,
        "openrouter_variable_control_frozen" in claim_ids,
        "audit ledger missing OpenRouter variable-control claim",
    )
    model_axis_text = MODEL_AXIS_DISPOSITION.read_text(encoding="utf-8")
    add(failures, "Kimi K2.7 Code endpoint" in model_axis_text, "model-axis disposition missing Kimi K2.7 entry")
    add(failures, "kimi-k2.6" in model_axis_text, "model-axis disposition missing Kimi K2.6 basis")
    add(failures, "mandatory-thinking" in model_axis_text, "model-axis disposition missing mandatory-thinking basis")
    openrouter_text = OPENROUTER_VARIABLE_CONTROL.read_text(encoding="utf-8")
    add(failures, "OpenRouter is not an experimental treatment" in openrouter_text, "OpenRouter variable-control addendum missing treatment boundary")
    add(failures, "`provider.allow_fallbacks: false`" in openrouter_text, "OpenRouter variable-control addendum missing fallback control")
    add(failures, '`reasoning: {"effort": "none"}`' in openrouter_text, "OpenRouter variable-control addendum missing reasoning control")
    add(failures, "temperature`: omitted by design" in openrouter_text, "OpenRouter variable-control addendum missing temperature boundary")
    sap_text = STATISTICAL_ANALYSIS_PLAN.read_text(encoding="utf-8")
    add(failures, "Primary confirmatory inference is design-based" in sap_text, "SAP missing design-based inference boundary")
    add(failures, "rolling_visible_carry_forward - ssr_no_visible_carry" in sap_text, "SAP missing primary crux contrast")
    add(failures, "mature_ssr_loop - rolling_visible_carry_forward" in sap_text, "SAP missing key secondary contrast")
    add(failures, "Budget `300` is diagnostic only" in sap_text, "SAP missing budget-300 diagnostic boundary")
    add(failures, "Logistic mixed-effects models are model-assisted sensitivity analyses" in sap_text, "SAP missing GLMM sensitivity boundary")
    return failures


def main() -> int:
    failures: list[str] = []
    required_paths = [
        CONFIRMATORY_CONFIG,
        CONFIRMATORY_ROWS,
        DIAGNOSTIC_CONFIG,
        DIAGNOSTIC_ROWS,
        PROVIDER_SNAPSHOT,
        MODEL_ADMISSION_CRITERIA,
        EXPERIMENT_VARIABLE_OVERVIEW,
        STATISTICAL_ANALYSIS_PLAN,
        MAIN_RUN_API_POLICY,
        PAPER_FRAMING,
        MODEL_AXIS_DISPOSITION,
        OPENROUTER_VARIABLE_CONTROL,
        VARIABLE_FREEZE_SPEC,
        AUDIT_LEDGER,
        HASH_MANIFEST,
        FREEZE_SUMMARY,
    ]
    for path in required_paths:
        add(failures, path.exists(), f"missing required freeze file: {rel(path)}")
    if failures:
        print(canonical_json({"passed": False, "failure_count": len(failures), "failures": failures}))
        return 1

    failures.extend(
        verify_config(
            CONFIRMATORY_CONFIG,
            CONFIRMATORY_ROWS,
            {
                "rows": 7200,
                "budgets": [600, 1200],
                "methods": [
                    "loop_only",
                    "rolling_summary",
                    "rolling_visible_carry_forward",
                    "rolling_visible_fields_only",
                    "ssr_no_visible_carry",
                    "mature_ssr_loop",
                ],
                "runs": [1, 2, 3],
                "primary": True,
            },
        )
    )
    failures.extend(
        verify_config(
            DIAGNOSTIC_CONFIG,
            DIAGNOSTIC_ROWS,
            {
                "rows": 800,
                "budgets": [300],
                "methods": [
                    "rolling_summary",
                    "ssr_no_visible_carry",
                    "rolling_visible_carry_forward",
                    "mature_ssr_loop",
                ],
                "runs": [1],
                "primary": False,
            },
        )
    )
    failures.extend(verify_provider_snapshot())
    failures.extend(verify_scorer_metric_contract())
    failures.extend(verify_hash_manifest())

    freeze_summary = read_json(FREEZE_SUMMARY)
    live_refresh_passed = freeze_summary.get("provider_live_refresh_passed") is True
    decision = freeze_summary.get("decision")
    if decision == "READY_FOR_MAIN_RECORD_MODE":
        note = (
            "Static freeze verifier; provider live refresh and five-model "
            "benchmark smoke have passed. This command verifies the frozen "
            "protocol/admission layer, not clean-v2 execution closure or "
            "paper-level aggregation."
        )
    elif live_refresh_passed:
        note = "Static freeze verifier; provider live refresh has passed, tiny benchmark smoke remains."
    else:
        note = "Static freeze verifier; live provider refresh remains an admission requirement."

    summary = {
        "passed": not failures,
        "failure_count": len(failures),
        "failures": failures[:100],
        "confirmatory_rows": 7200,
        "diagnostic_rows": 800,
        "api_calls_performed": 0,
        "note": note,
    }
    print(canonical_json(summary))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
