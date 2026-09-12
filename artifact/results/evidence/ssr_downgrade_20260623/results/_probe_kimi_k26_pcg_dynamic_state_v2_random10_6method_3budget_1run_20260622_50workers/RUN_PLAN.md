# Kimi K2.6 Random-10 New-Matrix Pilot Application

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
- Thinking: `{"type":"disabled"}`
- Tools/web: disabled
- Fallback: false
- State budgets: `300`, `600`, `1200`
- Runs: `1`
- Concurrency: `50`
- Retry: maximum 2 attempts, failed attempts retained
- Scorer: strict PCG v2 main-matrix scorer
- API key: read only at runtime from `MOONSHOT_API_KEY`; alternate `KIMI_API_KEY` is recorded but value is never printed or written
- Git: not invoked

## Random Task Selection

- Source: frozen PCG dynamic-state v2 main-matrix v1 40-task packet
- Rule: stratified random 2 tasks per family
- Seed: `20260622_deepseek_new_matrix_10task_pilot_v1`
- Family counts: `{"api_migration_state_transition": 2, "decoy_heavy_same_prefix_config": 2, "permission_boundary_with_attractive_blocked_path": 2, "protected_information_redaction_under_task_pressure": 2, "requirement_overwrite_cumulative_active": 2}`
- Difficulty counts: `{"hard": 3, "medium": 7}`

## Selected Tasks

- `pcgds_v2_00008_api_migration_state_transition_hard`
- `pcgds_v2_00004_api_migration_state_transition_medium`
- `pcgds_v2_00030_decoy_heavy_same_prefix_config_hard`
- `pcgds_v2_00032_decoy_heavy_same_prefix_config_hard`
- `pcgds_v2_00012_permission_boundary_with_attractive_blocked_path_medium`
- `pcgds_v2_00013_permission_boundary_with_attractive_blocked_path_medium`
- `pcgds_v2_00035_protected_information_redaction_under_task_pressure_medium`
- `pcgds_v2_00036_protected_information_redaction_under_task_pressure_medium`
- `pcgds_v2_00019_requirement_overwrite_cumulative_active_medium`
- `pcgds_v2_00021_requirement_overwrite_cumulative_active_medium`

## Files

- Runner: `tools/run_kimi_k26_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622.py`
- Reused Qwen wrapper for structure: `tools/run_qwen37max_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622.py`
- Config: `configs/_probe_kimi_k26_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_50workers.json`
- Preflight audit: `results/_probe_kimi_k26_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_50workers/PREFLIGHT_AUDIT.md`
- Result dir: `results/_probe_kimi_k26_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_50workers`
- Raw private dir: `released_raw_outputs/model_outputs/_probe_kimi_k26_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_50workers/kimi_k26`
- Variable protocol: `<AUTHOR_LOCAL_PROTOCOL_DIR>/LATEST_EXPERIMENT_VARIABLE_REQUIREMENTS_GOVERNANCE_MAIN_MATRIX_v1_20260621.md`
- Method protocol: `<AUTHOR_LOCAL_PROTOCOL_DIR>/METHOD_CONDITION_PROTOCOLS_GOVERNANCE_MAIN_MATRIX_v1_20260621.md`

## Command

```bash
python3 tools/run_kimi_k26_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622.py --run-api --max-workers 50
```
