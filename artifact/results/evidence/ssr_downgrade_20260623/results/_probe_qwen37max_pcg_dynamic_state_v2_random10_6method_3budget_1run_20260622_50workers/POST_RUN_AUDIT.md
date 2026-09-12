# Qwen3.7-Max Random-10 New-Matrix Pilot Post-Run Audit

Experiment: `_probe_qwen37max_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_50workers`

Rows: `180` / expected `180`

Status: local calibration only, not formal main-matrix evidence.

Provider/model: `dashscope` / `qwen3.7-max`

Concurrency: `50`

Reasoning content present rows: `0`

Backend/rerun rows: `0`

Measured/ok rows: `180`

## Non-Measured Or Rerun Rows

- none

## Success By Method

| method | rows | answer_success | state_governance_success | reliable_composite_success | final_exact_success | avg_provider_calls | state_hard_cap_rows |
|---|---:|---:|---:|---:|---:|---:|---:|
| `loop_only` | 30 | 0.000 | 0.000 | 0.000 | 0.000 | 6.60 | 12 |
| `rolling_summary` | 30 | 0.267 | 0.433 | 0.067 | 0.267 | 6.60 | 11 |
| `rolling_visible_carry_forward` | 30 | 0.600 | 0.333 | 0.233 | 0.600 | 6.60 | 20 |
| `rolling_visible_fields_only` | 30 | 0.000 | 0.000 | 0.000 | 0.000 | 6.60 | 10 |
| `ssr_no_visible_carry` | 30 | 0.133 | 0.600 | 0.067 | 0.133 | 6.60 | 6 |
| `mature_ssr_loop` | 30 | 0.200 | 0.400 | 0.100 | 0.200 | 5.60 | 8 |

## Mechanism Comparisons

| comparison | contrast | point diff | 95% bootstrap CI | paired units |
|---|---|---:|---:|---:|
| `carry_main_effect_no_schema_visible_minus_rolling` | `rolling_visible_carry_forward - rolling_summary` | 0.167 | [-0.033, 0.367] | 30 |
| `schema_main_effect_no_carry_ssr_minus_rolling` | `ssr_no_visible_carry - rolling_summary` | 0.000 | [-0.133, 0.133] | 30 |
| `schema_plus_carry_mature_minus_visible` | `mature_ssr_loop - rolling_visible_carry_forward` | -0.133 | [-0.300, 0.033] | 30 |
| `visible_crux_visible_minus_ssr_no_carry` | `rolling_visible_carry_forward - ssr_no_visible_carry` | 0.167 | [0.000, 0.333] | 30 |
| `fields_probe_fields_minus_visible` | `rolling_visible_fields_only - rolling_visible_carry_forward` | -0.233 | [-0.400, -0.100] | 30 |

## Non-Pooling

These rows are not formal main-matrix rows and must not be pooled with Fresh v2,
DeepSeek-only historical probes, or the future 5-model PCG v2 governance matrix.
