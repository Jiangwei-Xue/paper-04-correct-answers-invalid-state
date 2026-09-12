# Canonical Static Sanity Gate Report

Experiment: `pcg_dynamic_state_v2_static_sanity_deepseek_1task_4method_budget600_1run_20260623`

Status: `PASS`

Rows: `4` / expected `4`

This packet is a runner-discrimination gate. It is not main-matrix evidence
and must not be pooled with PCG v2 pilot rows or historical ECVS static rows.

## Gate Rule

`mature_ssr_loop` must have `answer_success=True` and
`reliable_composite_success=True` with no boundary leakage.

Gate result: `PASS`

## Rows

| method | gate | reason | answer | governance | reliable | provider calls |
|---|---|---|---:|---:|---:|---:|
| `mature_ssr_loop` | `measured` | `ok` | `True` | `True` | `True` | `3` |
| `rolling_visible_carry_forward` | `measured` | `ok` | `True` | `False` | `False` | `4` |
| `rolling_visible_fields_only` | `measured` | `ok` | `False` | `False` | `False` | `4` |
| `ssr_no_visible_carry` | `measured` | `ok` | `False` | `True` | `False` | `4` |

## Success By Method

| method | rows | answer_success | state_governance_success | reliable_composite_success | final_exact_success | avg_provider_calls | state_hard_cap_rows |
|---|---:|---:|---:|---:|---:|---:|---:|
| `rolling_visible_carry_forward` | 1 | 1.000 | 0.000 | 0.000 | 1.000 | 4.00 | 0 |
| `rolling_visible_fields_only` | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 4.00 | 0 |
| `ssr_no_visible_carry` | 1 | 0.000 | 1.000 | 0.000 | 0.000 | 4.00 | 0 |
| `mature_ssr_loop` | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 3.00 | 0 |

## Interpretation

If `PASS`, this closes the narrow runner-validity objection that the 2026-06-22
canonical `mature_ssr_loop` slot compiler is trivially broken on a static
control. It does not upgrade mature SSR to a primary method and does not change
the PCG v2 downgrade evidence chain by itself.
