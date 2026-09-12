# Post-Run Audit

Experiment: `_probe_ecvs_deepseek_v4pro_pcg_dynamic_state_v2_e10_h3_decisive_13task_4method_2budget_1run`

Rows: `104` / expected `104`

Reasoning content present rows: `0`

Backend/rerun rows: `1`

## Success By Method

| method | rows | final_exact | final_exact_rate | answer | answer_rate | state_gov | state_gov_rate | reliable_composite | reliable_rate | avg_output_tokens | avg_provider_calls | state_hard_cap_rows |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `rolling_summary` | 26 | 8 | 0.308 | 8 | 0.308 | 6 | 0.231 | 2 | 0.077 | 999.000 | 4.923 | 5 |
| `loop_only` | 26 | 0 | 0.000 | 0 | 0.000 | 25 | 0.962 | 0 | 0.000 | 668.692 | 4.923 | 1 |
| `rolling_visible_carry_forward` | 26 | 21 | 0.808 | 21 | 0.808 | 17 | 0.654 | 13 | 0.500 | 757.385 | 4.923 | 3 |
| `mature_ssr_loop` | 26 | 5 | 0.192 | 5 | 0.192 | 6 | 0.231 | 3 | 0.115 | 665.808 | 3.923 | 4 |

## Pre-Registered Decision

Decision: `DOWNGRADE_MATURE_SSR_TO_ABLATION_DIAGNOSTIC`

Bootstrap reliable composite diff (`mature_ssr_loop - rolling_visible_carry_forward`): point `-0.385`, 95% CI `[-0.577, -0.154]`, paired units `26`.

Criteria:

- `mature_answer_success_rate_at_least_0_70`: `False`
- `mature_reliable_advantage_at_least_0_10_over_visible`: `False`
- `mature_reliable_exceeds_weak_baselines`: `True`
