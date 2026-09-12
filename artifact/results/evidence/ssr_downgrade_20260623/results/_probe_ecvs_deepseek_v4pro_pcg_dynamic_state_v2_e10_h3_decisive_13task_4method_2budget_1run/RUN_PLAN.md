# _probe_ecvs_deepseek_v4pro_pcg_dynamic_state_v2_e10_h3_decisive_13task_4method_2budget_1run Run Plan

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
- Expected result rows: `104`
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
- `thinking`: `{"type": "disabled"}`
- `top_p`, `top_k`, `min_p`, `top_a`, penalties, stop, seed: omitted
- `stream`: `false`
- tools/web/cache: disabled or not requested
- fallback: disabled

## Selected Tasks

- `pcgds_v2_00001_api_migration_state_transition_easy`
- `pcgds_v2_00002_api_migration_state_transition_easy`
- `pcgds_v2_00009_permission_boundary_with_attractive_blocked_path_easy`
- `pcgds_v2_00010_permission_boundary_with_attractive_blocked_path_easy`
- `pcgds_v2_00017_requirement_overwrite_cumulative_active_easy`
- `pcgds_v2_00018_requirement_overwrite_cumulative_active_easy`
- `pcgds_v2_00025_decoy_heavy_same_prefix_config_easy`
- `pcgds_v2_00026_decoy_heavy_same_prefix_config_easy`
- `pcgds_v2_00033_protected_information_redaction_under_task_pressure_easy`
- `pcgds_v2_00034_protected_information_redaction_under_task_pressure_easy`
- `pcgds_v2_00014_permission_boundary_with_attractive_blocked_path_hard`
- `pcgds_v2_00030_decoy_heavy_same_prefix_config_hard`
- `pcgds_v2_00038_protected_information_redaction_under_task_pressure_hard`

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

- Variable control doc: `<AUTHOR_LOCAL_WORKSPACE>/stateful-reasoning-benchmark-release/docs/protocol/fresh_main_matrix_v2/LATEST_EXPERIMENT_VARIABLE_REQUIREMENTS_ROLLING_VISIBLE_CARRY_FORWARD_LOCAL.md`
- Method protocol doc: `<AUTHOR_LOCAL_WORKSPACE>/stateful-reasoning-benchmark-release/docs/protocol/fresh_main_matrix_v2/LATEST_EXPERIMENT_VARIABLE_REQUIREMENTS_ROLLING_VISIBLE_CARRY_FORWARD_LOCAL.md`
