# Kimi K2.6 Random-10 New-Matrix Pilot Post-Run Audit

Experiment: `_probe_kimi_k26_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_50workers`

Rows: `180` / expected `180`

Status: local calibration only, not formal main-matrix evidence.

Provider/model: `moonshot` / `kimi-k2.6`

Concurrency: `50`

Reasoning content present rows: `0`

Backend/rerun rows: `0`

Measured/ok rows: `180`

## Non-Measured Or Rerun Rows

- none

## Success By Method

| method | rows | answer_success | state_governance_success | reliable_composite_success | final_exact_success | avg_provider_calls | state_hard_cap_rows |
|---|---:|---:|---:|---:|---:|---:|---:|
| `loop_only` | 30 | 0.000 | 0.000 | 0.000 | 0.000 | 6.60 | 20 |
| `rolling_summary` | 30 | 0.133 | 0.167 | 0.000 | 0.133 | 6.60 | 21 |
| `rolling_visible_carry_forward` | 30 | 0.500 | 0.167 | 0.100 | 0.500 | 6.60 | 23 |
| `rolling_visible_fields_only` | 30 | 0.000 | 0.000 | 0.000 | 0.000 | 6.60 | 10 |
| `ssr_no_visible_carry` | 30 | 0.133 | 0.200 | 0.067 | 0.133 | 6.60 | 21 |
| `mature_ssr_loop` | 30 | 0.000 | 0.067 | 0.000 | 0.000 | 5.60 | 22 |

## Mechanism Comparisons

| comparison | contrast | point diff | 95% bootstrap CI | paired units |
|---|---|---:|---:|---:|
| `carry_main_effect_no_schema_visible_minus_rolling` | `rolling_visible_carry_forward - rolling_summary` | 0.100 | [0.000, 0.233] | 30 |
| `schema_main_effect_no_carry_ssr_minus_rolling` | `ssr_no_visible_carry - rolling_summary` | 0.067 | [0.000, 0.167] | 30 |
| `schema_plus_carry_mature_minus_visible` | `mature_ssr_loop - rolling_visible_carry_forward` | -0.100 | [-0.233, 0.000] | 30 |
| `visible_crux_visible_minus_ssr_no_carry` | `rolling_visible_carry_forward - ssr_no_visible_carry` | 0.033 | [-0.100, 0.167] | 30 |
| `fields_probe_fields_minus_visible` | `rolling_visible_fields_only - rolling_visible_carry_forward` | -0.100 | [-0.233, 0.000] | 30 |

## Non-Pooling

These rows are not formal main-matrix rows and must not be pooled with Fresh v2,
DeepSeek-only historical probes, or the future 5-model PCG v2 governance matrix.
