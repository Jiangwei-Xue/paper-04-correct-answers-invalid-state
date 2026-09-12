#!/usr/bin/env python3
"""Kimi K2.6 PCG v2 random-10 six-method pilot.

This wrapper reuses the fixed random-10 PCG v2 matrix and scorer used by the
DeepSeek/Qwen local calibration probes. It changes only the model condition and
provider-specific request controls for Moonshot Kimi K2.6.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
QWEN_WRAPPER = PROJECT_ROOT / "tools" / "run_qwen37max_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622.py"


def load_qwen_wrapper() -> Any:
    spec = importlib.util.spec_from_file_location("pcg_v2_random10_qwen_wrapper_for_kimi", QWEN_WRAPPER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import Qwen wrapper: {QWEN_WRAPPER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


Q = load_qwen_wrapper()
R = Q.R
B = Q.B

EXPERIMENT_ID = "_probe_kimi_k26_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_50workers"
CONDITION_ID = "kimi_k26"
PROVIDER = "moonshot"
BASE_URL = "https://api.moonshot.cn/v1"
CHAT_COMPLETIONS_URL = f"{BASE_URL}/chat/completions"
REQUESTED_MODEL = "kimi-k2.6"
API_KEY_ENV = "MOONSHOT_API_KEY"
TEMPERATURE = 0.6
MAX_TOKENS = 4096
REASONING_CONTROL = {"thinking": {"type": "disabled"}}
REASONING_DISABLE_MODE = "thinking.type=disabled"
DEFAULT_MAX_WORKERS = 50
APPLICATION_MD = Path("<LOCAL_PATH_REDACTED>/KIMI_K26_RANDOM10_NEW_MATRIX_PILOT_APPLICATION_20260622_50WORKERS.md")


def configure_paths() -> None:
    R.EXPERIMENT_ID = EXPERIMENT_ID
    R.DEFAULT_MAX_WORKERS = DEFAULT_MAX_WORKERS
    R.SUBSET_DIR = R.PROJECT_ROOT / "data" / "pcg_dynamic_state_v2" / EXPERIMENT_ID
    R.MODEL_VISIBLE_SUBSET = R.SUBSET_DIR / "MODEL_VISIBLE_TASK_MANIFEST.jsonl"
    R.SCORER_ORACLE_SUBSET = R.SUBSET_DIR / "SCORER_ORACLE_MANIFEST.jsonl"
    R.TASK_PROVENANCE_MANIFEST = R.SUBSET_DIR / "TASK_PROVENANCE_MANIFEST.jsonl"
    R.TASK_SELECTION_CSV = R.SUBSET_DIR / "TASK_SELECTION.csv"
    R.TASK_SPLIT_AUDIT = R.SUBSET_DIR / "TASK_SPLIT_AUDIT.json"
    R.CONFIG_PATH = R.PROJECT_ROOT / "configs" / f"{EXPERIMENT_ID}.json"
    R.RESULT_DIR = R.PROJECT_ROOT / "results" / EXPERIMENT_ID
    R.RAW_DIR = R.PROJECT_ROOT / "private" / "model_outputs" / EXPERIMENT_ID / "kimi_k26"
    R.RUN_PLAN_MD = R.RESULT_DIR / "RUN_PLAN.md"
    R.PREFLIGHT_AUDIT_JSON = R.RESULT_DIR / "PREFLIGHT_AUDIT.json"
    R.PREFLIGHT_AUDIT_MD = R.RESULT_DIR / "PREFLIGHT_AUDIT.md"
    R.PREFLIGHT_HASH_MANIFEST = R.RESULT_DIR / "PREFLIGHT_HASH_MANIFEST.jsonl"
    R.PREFLIGHT_SHA256SUMS = R.RESULT_DIR / "PREFLIGHT_SHA256SUMS.txt"
    R.CONTROLLED_ROWS = R.RESULT_DIR / "CONTROLLED_ROWS.jsonl"
    R.SCORES_JSONL = R.RESULT_DIR / "scores.jsonl"
    R.SCORES_CSV = R.RESULT_DIR / "scores.csv"
    R.POST_RUN_AUDIT_MD = R.RESULT_DIR / "POST_RUN_AUDIT.md"
    R.APPLICATION_MD = APPLICATION_MD


def patch_base_globals_kimi() -> None:
    Q.ORIGINAL_PATCH_BASE_GLOBALS()
    B.CONDITION_ID = CONDITION_ID
    B.PROVIDER = PROVIDER
    B.BASE_URL = BASE_URL
    B.CHAT_COMPLETIONS_URL = CHAT_COMPLETIONS_URL
    B.REQUESTED_MODEL = REQUESTED_MODEL
    B.API_KEY_ENV = API_KEY_ENV
    B.MAX_TOKENS = MAX_TOKENS
    B.TEMPERATURE = TEMPERATURE
    B.THINKING_CONTROL = REASONING_CONTROL
    B.git_commit = lambda: "git_not_invoked_by_policy"


def build_config_kimi() -> dict[str, Any]:
    config = Q.ORIGINAL_BUILD_CONFIG()
    config["experiment_id"] = EXPERIMENT_ID
    config["condition"] = {
        "condition_id": CONDITION_ID,
        "provider": PROVIDER,
        "access_path": "direct_provider",
        "base_url": BASE_URL,
        "requested_model": REQUESTED_MODEL,
        "api_key_env": API_KEY_ENV,
        "api_key_env_alternates_recorded_not_printed": ["KIMI_API_KEY"],
        "fallback_enabled": False,
    }
    config["default_max_workers"] = DEFAULT_MAX_WORKERS
    config["request_controls"]["temperature"] = {"send_mode": "explicit", "value": TEMPERATURE}
    config["request_controls"]["max_tokens"] = MAX_TOKENS
    config["request_controls"]["reasoning_or_thinking"] = {"send_mode": "explicit", "value": REASONING_CONTROL}
    config["retry_policy"]["policy_id"] = "kimi_k26_random10_new_matrix_pilot_retry_policy_v1"
    config["implementation"]["wrapper_runner"] = R.rel(Path(__file__).resolve())
    config["implementation"]["qwen_wrapper_reused_for_structure"] = R.rel(QWEN_WRAPPER)
    config["implementation"]["random10_runner_reused"] = R.rel(Q.RANDOM_RUNNER)
    config["safety"]["api_key_runtime_env"] = API_KEY_ENV
    return config


def result_dir_has_old_rows() -> tuple[bool, list[str]]:
    if not R.RESULT_DIR.exists():
        return False, []
    row_files = ["CONTROLLED_ROWS.jsonl", "scores.jsonl", "scores.csv", "POST_RUN_AUDIT.md"]
    conflicts = [name for name in row_files if (R.RESULT_DIR / name).exists()]
    return bool(conflicts), conflicts


def raw_dir_has_outputs() -> tuple[bool, list[str]]:
    if not R.RAW_DIR.exists():
        return False, []
    files = [path for path in R.RAW_DIR.rglob("*") if path.is_file()]
    return bool(files), [R.rel(path) for path in files[:20]]


def build_preflight_audit_kimi(config: dict[str, Any]) -> dict[str, Any]:
    visible = R.read_jsonl(R.MODEL_VISIBLE_SUBSET)
    oracle = R.read_jsonl(R.SCORER_ORACLE_SUBSET)
    split = json.loads(R.TASK_SPLIT_AUDIT.read_text(encoding="utf-8"))
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
    add("method list = six-method new matrix", config["methods"] == R.METHODS, config["methods"])
    add("state budgets = 300/600/1200", config["state_budget_chars"] == R.STATE_BUDGETS, config["state_budget_chars"])
    add("runs = 1", config["runs"] == 1, config["runs"])
    add("expected rows = 180", config["expected_rows"] == R.EXPECTED_ROWS == 180, config["expected_rows"])
    add(
        "provider direct kimi_k26",
        config["condition"]["provider"] == PROVIDER
        and config["condition"]["requested_model"] == REQUESTED_MODEL
        and config["condition"]["api_key_env"] == API_KEY_ENV
        and not config["condition"]["fallback_enabled"],
        config["condition"],
    )
    add("temperature explicit Kimi provider setting", config["request_controls"]["temperature"]["value"] == TEMPERATURE, config["request_controls"]["temperature"])
    add(
        "Kimi thinking disabled",
        config["request_controls"]["reasoning_or_thinking"]["value"] == REASONING_CONTROL,
        config["request_controls"]["reasoning_or_thinking"],
    )
    add(
        "tools/web disabled",
        config["request_controls"]["tools"] == "disabled" and config["request_controls"]["web"] == "disabled",
        {"tools": config["request_controls"]["tools"], "web": config["request_controls"]["web"]},
    )
    add("task split audit PASS", split.get("prompt_oracle_split_status") == "PASS", split.get("prompt_oracle_split_status"))
    add("no prior row output files in result dir", not old_rows, row_conflicts)
    add("raw output dir absent or empty", not old_raw, raw_conflicts)
    add("variable control doc exists", R.VARIABLE_CONTROL_DOC.exists(), str(R.VARIABLE_CONTROL_DOC))
    add("method protocol doc exists", R.METHOD_PROTOCOL_DOC.exists(), str(R.METHOD_PROTOCOL_DOC))
    add("strict scorer exists", R.SCORER_PATH.exists(), R.rel(R.SCORER_PATH))
    return {
        "audit_type": "kimi_k26_random10_new_matrix_pilot_preflight",
        "experiment_id": EXPERIMENT_ID,
        "created_at_utc": R.utc_now(),
        "overall_status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL",
        "api_called": False,
        "api_key_value_printed": False,
        "git_invoked": False,
        "expected_rows": R.EXPECTED_ROWS,
        "selected_task_ids": [row["task_id"] for row in visible],
        "family_counts": family_counts,
        "difficulty_counts": difficulty_counts,
        "checks": checks,
        "hashes": {
            "runner_sha256": B.file_sha256(Path(__file__).resolve()),
            "base_runner_sha256": B.file_sha256(R.BASE_RUNNER),
            "random10_runner_sha256": B.file_sha256(Q.RANDOM_RUNNER),
            "qwen_wrapper_sha256": B.file_sha256(QWEN_WRAPPER),
            "config_sha256": B.file_sha256(R.CONFIG_PATH),
            "subset_model_visible_manifest_sha256": B.file_sha256(R.MODEL_VISIBLE_SUBSET),
            "subset_oracle_manifest_sha256": B.file_sha256(R.SCORER_ORACLE_SUBSET),
            "scorer_sha256": B.file_sha256(R.SCORER_PATH),
        },
    }


def write_run_plan_and_application_kimi(config: dict[str, Any], audit: dict[str, Any]) -> None:
    selected = "\n".join(f"- `{task_id}`" for task_id in audit["selected_task_ids"])
    text = f"""# Kimi K2.6 Random-10 New-Matrix Pilot Application

Date: 2026-06-22

Status: application/preflight packet for a local calibration run. This is not
formal main-matrix evidence, not admission evidence, and not a paper result row
unless separately promoted before execution.

## Requested Run

```text
10 frozen PCG dynamic-state v2 tasks
x 1 model: kimi_k26
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

- Provider: `moonshot`
- Requested model: `kimi-k2.6`
- Base URL: `https://api.moonshot.cn/v1`
- Temperature: explicit `0.6`
- Max tokens: `4096`
- Thinking: `{{"type":"disabled"}}`
- Tools/web: disabled
- Fallback: false
- State budgets: `300`, `600`, `1200`
- Runs: `1`
- Concurrency: `{DEFAULT_MAX_WORKERS}`
- Retry: maximum 2 attempts, failed attempts retained
- Scorer: strict PCG v2 main-matrix scorer
- API key: read only at runtime from `MOONSHOT_API_KEY`; alternate `KIMI_API_KEY` is recorded but value is never printed or written
- Git: not invoked

## Random Task Selection

- Source: frozen PCG dynamic-state v2 main-matrix v1 40-task packet
- Rule: stratified random 2 tasks per family
- Seed: `{R.SELECTION_SEED}`
- Family counts: `{json.dumps(audit["family_counts"], ensure_ascii=False, sort_keys=True)}`
- Difficulty counts: `{json.dumps(audit["difficulty_counts"], ensure_ascii=False, sort_keys=True)}`

## Selected Tasks

{selected}

## Files

- Runner: `{R.rel(Path(__file__).resolve())}`
- Reused Qwen wrapper for structure: `{R.rel(QWEN_WRAPPER)}`
- Config: `{R.rel(R.CONFIG_PATH)}`
- Preflight audit: `{R.rel(R.PREFLIGHT_AUDIT_MD)}`
- Result dir: `{R.rel(R.RESULT_DIR)}`
- Raw private dir: `{R.rel(R.RAW_DIR)}`
- Variable protocol: `{config["variable_control_doc"]}`
- Method protocol: `{config["method_protocol_doc"]}`

## Command

```bash
python3 tools/run_kimi_k26_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622.py --run-api --max-workers {DEFAULT_MAX_WORKERS}
```
"""
    R.write_text(R.RUN_PLAN_MD, text)
    R.write_text(APPLICATION_MD, text)


def write_hash_files_kimi() -> None:
    paths = [
        R.MODEL_VISIBLE_SUBSET,
        R.SCORER_ORACLE_SUBSET,
        R.TASK_PROVENANCE_MANIFEST,
        R.TASK_SELECTION_CSV,
        R.TASK_SPLIT_AUDIT,
        R.CONFIG_PATH,
        R.RUN_PLAN_MD,
        APPLICATION_MD,
        R.PREFLIGHT_AUDIT_JSON,
        R.PREFLIGHT_AUDIT_MD,
        R.SCORER_PATH,
        R.BASE_RUNNER,
        Q.RANDOM_RUNNER,
        QWEN_WRAPPER,
        Path(__file__).resolve(),
    ]
    rows = []
    lines = []
    for path in paths:
        if path.exists():
            digest = B.file_sha256(path)
            rows.append({"path": R.rel(path), "sha256": digest})
            lines.append(f"{digest}  {R.rel(path)}")
    B.write_jsonl(R.PREFLIGHT_HASH_MANIFEST, rows)
    R.write_text(R.PREFLIGHT_SHA256SUMS, "\n".join(lines) + "\n")


def run_one_row_kimi(*args: Any, **kwargs: Any) -> dict[str, Any]:
    row = Q.ORIGINAL_B_RUN_ONE_ROW(*args, **kwargs)
    row["condition_id"] = CONDITION_ID
    row["provider"] = PROVIDER
    row["base_url"] = BASE_URL
    row["requested_model"] = REQUESTED_MODEL
    row["temperature_value"] = TEMPERATURE
    row["reasoning_disable_mode"] = REASONING_DISABLE_MODE
    row["reasoning_control_request_sha256"] = B.sha256_json(REASONING_CONTROL)
    return row


def write_post_run_audit_kimi() -> None:
    rows = R.read_jsonl(R.CONTROLLED_ROWS)
    summaries = {method: R.method_summary(rows, method) for method in R.METHODS}
    comparisons = {
        "carry_main_effect_no_schema_visible_minus_rolling": R.compare(rows, "rolling_visible_carry_forward", "rolling_summary"),
        "schema_main_effect_no_carry_ssr_minus_rolling": R.compare(rows, "ssr_no_visible_carry", "rolling_summary"),
        "schema_plus_carry_mature_minus_visible": R.compare(rows, "mature_ssr_loop", "rolling_visible_carry_forward"),
        "visible_crux_visible_minus_ssr_no_carry": R.compare(rows, "rolling_visible_carry_forward", "ssr_no_visible_carry"),
        "fields_probe_fields_minus_visible": R.compare(rows, "rolling_visible_fields_only", "rolling_visible_carry_forward"),
    }
    summary_lines = "\n".join(
        "| `{method}` | {rows} | {answer_success_rate:.3f} | {state_governance_success_rate:.3f} | {reliable_composite_success_rate:.3f} | {final_exact_success_rate:.3f} | {avg_provider_call_count:.2f} | {state_hard_cap_rows} |".format(method=method, **stats)
        for method, stats in summaries.items()
    )
    comparison_lines = "\n".join(
        f"| `{name}` | `{value['left_method']} - {value['right_method']}` | {value['point_diff']:.3f} | [{value['ci_lower']:.3f}, {value['ci_upper']:.3f}] | {value['paired_units']} |"
        for name, value in comparisons.items()
    )
    failed_rows = [
        row
        for row in rows
        if row.get("gate_status") != "measured" or row.get("gate_reason") != "ok"
    ]
    failed_lines = "\n".join(
        f"- `method={row.get('method')}`, `task_id={row.get('task_id')}`, `budget={row.get('state_budget')}`, `run_id={row.get('run_id')}`, `gate_reason={row.get('gate_reason')}`"
        for row in failed_rows
    ) or "- none"
    R.POST_RUN_AUDIT_MD.write_text(
        f"""# Kimi K2.6 Random-10 New-Matrix Pilot Post-Run Audit

Experiment: `{EXPERIMENT_ID}`

Rows: `{len(rows)}` / expected `{R.EXPECTED_ROWS}`

Status: local calibration only, not formal main-matrix evidence.

Provider/model: `moonshot` / `kimi-k2.6`

Concurrency: `{DEFAULT_MAX_WORKERS}`

Reasoning content present rows: `{sum(1 for row in rows if row.get('reasoning_content_present'))}`

Backend/rerun rows: `{sum(1 for row in rows if row.get('backend_error'))}`

Measured/ok rows: `{sum(1 for row in rows if row.get('gate_status') == 'measured' and row.get('gate_reason') == 'ok')}`

## Non-Measured Or Rerun Rows

{failed_lines}

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


def run_api_kimi(max_workers: int) -> None:
    if max_workers < 1 or max_workers > 50:
        raise SystemExit("For this Kimi local calibration runner, use --max-workers between 1 and 50.")
    Q.ORIGINAL_RUN_API(max_workers=max_workers)
    write_post_run_audit_kimi()


def install_kimi_overrides() -> None:
    configure_paths()
    R.patch_base_globals = patch_base_globals_kimi
    R.build_config = build_config_kimi
    R.build_preflight_audit = build_preflight_audit_kimi
    R.write_run_plan_and_application = write_run_plan_and_application_kimi
    R.write_hash_files = write_hash_files_kimi
    R.run_api = run_api_kimi
    B.run_one_row = run_one_row_kimi
    patch_base_globals_kimi()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-api", action="store_true")
    parser.add_argument("--max-workers", type=int, default=DEFAULT_MAX_WORKERS)
    args = parser.parse_args()
    install_kimi_overrides()
    audit = R.write_preflight_files()
    print(
        json.dumps(
            {
                "experiment_id": EXPERIMENT_ID,
                "preflight_status": audit["overall_status"],
                "expected_rows": R.EXPECTED_ROWS,
                "selected_tasks": audit["selected_task_ids"],
                "application": str(APPLICATION_MD),
                "config": R.rel(R.CONFIG_PATH),
                "run_plan": R.rel(R.RUN_PLAN_MD),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    if args.run_api:
        R.run_api(max_workers=args.max_workers)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
