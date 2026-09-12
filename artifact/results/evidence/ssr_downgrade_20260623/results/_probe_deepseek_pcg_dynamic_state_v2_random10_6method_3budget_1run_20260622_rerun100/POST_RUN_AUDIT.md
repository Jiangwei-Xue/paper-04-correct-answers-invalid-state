# DeepSeek Random-10 New-Matrix Pilot Post-Run Audit

Experiment: `_probe_deepseek_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_rerun100`

Rows: `180` / expected `180`

Status: local calibration only, not formal main-matrix evidence.

Reasoning content present rows: `0`

Backend/rerun rows: `1`

## Execution Stability Note

This rerun used `max_workers=100` after the prior private `max_workers=200`
probe produced backend/empty rows across the run. The 100-worker rerun completed
all `180` expected rows, with `179` measured rows and `1` rerun-required row.

The only rerun-required row is:

- `method=loop_only`, `task_id=pcgds_v2_00032_decoy_heavy_same_prefix_config_hard`,
  `budget=300`, `run_id=1`, `gate_reason=backend_or_empty_output`.

Treat this as an interpretable local calibration signal, not formal evidence.
Before any formal matrix claim, rerun or replace the single failed row under the
frozen protocol.

## Success By Method

| method | rows | answer_success | state_governance_success | reliable_composite_success | final_exact_success | avg_provider_calls | state_hard_cap_rows |
|---|---:|---:|---:|---:|---:|---:|---:|
| `loop_only` | 30 | 0.000 | 0.000 | 0.000 | 0.000 | 6.60 | 18 |
| `rolling_summary` | 30 | 0.033 | 0.533 | 0.000 | 0.033 | 6.60 | 12 |
| `rolling_visible_carry_forward` | 30 | 0.433 | 0.433 | 0.300 | 0.433 | 6.60 | 11 |
| `rolling_visible_fields_only` | 30 | 0.000 | 0.000 | 0.000 | 0.000 | 6.60 | 10 |
| `ssr_no_visible_carry` | 30 | 0.433 | 0.267 | 0.000 | 0.433 | 6.60 | 3 |
| `mature_ssr_loop` | 30 | 0.000 | 0.100 | 0.000 | 0.000 | 5.60 | 6 |

## Mechanism Comparisons

| comparison | contrast | point diff | 95% bootstrap CI | paired units |
|---|---|---:|---:|---:|
| `carry_main_effect_no_schema_visible_minus_rolling` | `rolling_visible_carry_forward - rolling_summary` | 0.300 | [0.133, 0.467] | 30 |
| `schema_main_effect_no_carry_ssr_minus_rolling` | `ssr_no_visible_carry - rolling_summary` | 0.000 | [0.000, 0.000] | 30 |
| `schema_plus_carry_mature_minus_visible` | `mature_ssr_loop - rolling_visible_carry_forward` | -0.300 | [-0.467, -0.133] | 30 |
| `visible_crux_visible_minus_ssr_no_carry` | `rolling_visible_carry_forward - ssr_no_visible_carry` | 0.300 | [0.133, 0.467] | 30 |
| `fields_probe_fields_minus_visible` | `rolling_visible_fields_only - rolling_visible_carry_forward` | -0.300 | [-0.467, -0.133] | 30 |

## Non-Pooling

These rows are not formal main-matrix rows and must not be pooled with Fresh v2,
DeepSeek-only historical probes, or the future 5-model PCG v2 governance matrix.
