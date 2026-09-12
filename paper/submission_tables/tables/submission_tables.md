# Submission Aggregate Tables

These tables are generated from tracked score CSV files by
`artifact/verification/summarize_submission_tables.py`. They do not call
model APIs or use private files.

## primary_overall

| population | rows | backend_error_rows | backend_error_rate | parse_and_score_success_rows | parse_and_score_success_rate | answer_success_rows | answer_success_rate | state_governance_success_rows | state_governance_success_rate | reliable_composite_success_rows | reliable_composite_success_rate | hard_cap_rows | hard_cap_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| primary_clean_v2_7200 | 7200 | 13 | 0.001806 | 7184 | 0.997778 | 1349 | 0.187361 | 1583 | 0.219861 | 448 | 0.062222 | 2039 | 0.283194 |

## primary_by_model

| model_condition_id | rows | backend_error_rows | backend_error_rate | parse_and_score_success_rows | parse_and_score_success_rate | answer_success_rows | answer_success_rate | state_governance_success_rows | state_governance_success_rate | reliable_composite_success_rows | reliable_composite_success_rate | hard_cap_rows | hard_cap_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deepseek_v4pro | 1440 | 6 | 0.004167 | 1434 | 0.995833 | 361 | 0.250694 | 333 | 0.231250 | 142 | 0.098611 | 138 | 0.095833 |
| kimi_k26 | 1440 | 7 | 0.004861 | 1438 | 0.998611 | 202 | 0.140278 | 219 | 0.152083 | 55 | 0.038194 | 554 | 0.384722 |
| openrouter_claude48 | 1440 | 0 | 0.000000 | 1439 | 0.999306 | 219 | 0.152083 | 281 | 0.195139 | 39 | 0.027083 | 613 | 0.425694 |
| openrouter_gpt55 | 1440 | 0 | 0.000000 | 1433 | 0.995139 | 213 | 0.147917 | 290 | 0.201389 | 47 | 0.032639 | 497 | 0.345139 |
| qwen37max | 1440 | 0 | 0.000000 | 1440 | 1.000000 | 354 | 0.245833 | 460 | 0.319444 | 165 | 0.114583 | 237 | 0.164583 |

## primary_by_method

| method | rows | backend_error_rows | backend_error_rate | parse_and_score_success_rows | parse_and_score_success_rate | answer_success_rows | answer_success_rate | state_governance_success_rows | state_governance_success_rate | reliable_composite_success_rows | reliable_composite_success_rate | hard_cap_rows | hard_cap_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| loop_only | 1200 | 2 | 0.001667 | 1194 | 0.995000 | 0 | 0.000000 | 0 | 0.000000 | 0 | 0.000000 | 313 | 0.260833 |
| mature_ssr_loop | 1200 | 2 | 0.001667 | 1200 | 1.000000 | 157 | 0.130833 | 407 | 0.339167 | 114 | 0.095000 | 310 | 0.258333 |
| rolling_summary | 1200 | 3 | 0.002500 | 1192 | 0.993333 | 250 | 0.208333 | 394 | 0.328333 | 69 | 0.057500 | 569 | 0.474167 |
| rolling_visible_carry_forward | 1200 | 4 | 0.003333 | 1199 | 0.999167 | 748 | 0.623333 | 315 | 0.262500 | 224 | 0.186667 | 626 | 0.521667 |
| rolling_visible_fields_only | 1200 | 1 | 0.000833 | 1200 | 1.000000 | 0 | 0.000000 | 0 | 0.000000 | 0 | 0.000000 | 0 | 0.000000 |
| ssr_no_visible_carry | 1200 | 1 | 0.000833 | 1199 | 0.999167 | 194 | 0.161667 | 467 | 0.389167 | 41 | 0.034167 | 221 | 0.184167 |

## primary_by_budget

| budget | rows | backend_error_rows | backend_error_rate | parse_and_score_success_rows | parse_and_score_success_rate | answer_success_rows | answer_success_rate | state_governance_success_rows | state_governance_success_rate | reliable_composite_success_rows | reliable_composite_success_rate | hard_cap_rows | hard_cap_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1200 | 3600 | 9 | 0.002500 | 3592 | 0.997778 | 588 | 0.163333 | 839 | 0.233056 | 247 | 0.068611 | 440 | 0.122222 |
| 600 | 3600 | 4 | 0.001111 | 3592 | 0.997778 | 761 | 0.211389 | 744 | 0.206667 | 201 | 0.055833 | 1599 | 0.444167 |

## budget300_diagnostic_overall

| population | rows | backend_error_rows | backend_error_rate | parse_and_score_success_rows | parse_and_score_success_rate | answer_success_rows | answer_success_rate | state_governance_success_rows | state_governance_success_rate | reliable_composite_success_rows | reliable_composite_success_rate | hard_cap_rows | hard_cap_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| budget300_diagnostic_800 | 800 | 0 | 0.000000 | 798 | 0.997500 | 189 | 0.236250 | 235 | 0.293750 | 44 | 0.055000 | 673 | 0.841250 |

## budget300_diagnostic_by_model

| model_condition_id | rows | backend_error_rows | backend_error_rate | parse_and_score_success_rows | parse_and_score_success_rate | answer_success_rows | answer_success_rate | state_governance_success_rows | state_governance_success_rate | reliable_composite_success_rows | reliable_composite_success_rate | hard_cap_rows | hard_cap_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deepseek_v4pro | 160 | 0 | 0.000000 | 160 | 1.000000 | 40 | 0.250000 | 29 | 0.181250 | 9 | 0.056250 | 104 | 0.650000 |
| kimi_k26 | 160 | 0 | 0.000000 | 160 | 1.000000 | 23 | 0.143750 | 27 | 0.168750 | 1 | 0.006250 | 154 | 0.962500 |
| openrouter_claude48 | 160 | 0 | 0.000000 | 158 | 0.987500 | 23 | 0.143750 | 50 | 0.312500 | 5 | 0.031250 | 159 | 0.993750 |
| openrouter_gpt55 | 160 | 0 | 0.000000 | 160 | 1.000000 | 57 | 0.356250 | 47 | 0.293750 | 10 | 0.062500 | 157 | 0.981250 |
| qwen37max | 160 | 0 | 0.000000 | 160 | 1.000000 | 46 | 0.287500 | 82 | 0.512500 | 19 | 0.118750 | 99 | 0.618750 |

## budget300_diagnostic_by_method

| method | rows | backend_error_rows | backend_error_rate | parse_and_score_success_rows | parse_and_score_success_rate | answer_success_rows | answer_success_rate | state_governance_success_rows | state_governance_success_rate | reliable_composite_success_rows | reliable_composite_success_rate | hard_cap_rows | hard_cap_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mature_ssr_loop | 200 | 0 | 0.000000 | 200 | 1.000000 | 32 | 0.160000 | 77 | 0.385000 | 23 | 0.115000 | 161 | 0.805000 |
| rolling_summary | 200 | 0 | 0.000000 | 200 | 1.000000 | 32 | 0.160000 | 58 | 0.290000 | 9 | 0.045000 | 167 | 0.835000 |
| rolling_visible_carry_forward | 200 | 0 | 0.000000 | 198 | 0.990000 | 88 | 0.440000 | 2 | 0.010000 | 0 | 0.000000 | 200 | 1.000000 |
| ssr_no_visible_carry | 200 | 0 | 0.000000 | 200 | 1.000000 | 37 | 0.185000 | 98 | 0.490000 | 12 | 0.060000 | 145 | 0.725000 |

## qwen3_coder_supplement_overall

| population | rows | backend_error_rows | backend_error_rate | parse_and_score_success_rows | parse_and_score_success_rate | answer_success_rows | answer_success_rate | state_governance_success_rows | state_governance_success_rate | reliable_composite_success_rows | reliable_composite_success_rate | hard_cap_rows | hard_cap_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen3_coder_supplement_1440 | 1440 | 0 | 0.000000 | 1439 | 0.999306 | 280 | 0.194444 | 298 | 0.206944 | 113 | 0.078472 | 324 | 0.225000 |

## qwen3_coder_supplement_by_method

| method | rows | backend_error_rows | backend_error_rate | parse_and_score_success_rows | parse_and_score_success_rate | answer_success_rows | answer_success_rate | state_governance_success_rows | state_governance_success_rate | reliable_composite_success_rows | reliable_composite_success_rate | hard_cap_rows | hard_cap_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| loop_only | 240 | 0 | 0.000000 | 239 | 0.995833 | 0 | 0.000000 | 0 | 0.000000 | 0 | 0.000000 | 15 | 0.062500 |
| mature_ssr_loop | 240 | 0 | 0.000000 | 240 | 1.000000 | 33 | 0.137500 | 51 | 0.212500 | 24 | 0.100000 | 12 | 0.050000 |
| rolling_summary | 240 | 0 | 0.000000 | 240 | 1.000000 | 42 | 0.175000 | 102 | 0.425000 | 16 | 0.066667 | 105 | 0.437500 |
| rolling_visible_carry_forward | 240 | 0 | 0.000000 | 240 | 1.000000 | 137 | 0.570833 | 85 | 0.354167 | 53 | 0.220833 | 126 | 0.525000 |
| rolling_visible_fields_only | 240 | 0 | 0.000000 | 240 | 1.000000 | 0 | 0.000000 | 0 | 0.000000 | 0 | 0.000000 | 0 | 0.000000 |
| ssr_no_visible_carry | 240 | 0 | 0.000000 | 240 | 1.000000 | 68 | 0.283333 | 60 | 0.250000 | 20 | 0.083333 | 66 | 0.275000 |

## qwen3_coder_supplement_by_budget

| budget | rows | backend_error_rows | backend_error_rate | parse_and_score_success_rows | parse_and_score_success_rate | answer_success_rows | answer_success_rate | state_governance_success_rows | state_governance_success_rate | reliable_composite_success_rows | reliable_composite_success_rate | hard_cap_rows | hard_cap_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1200 | 720 | 0 | 0.000000 | 720 | 1.000000 | 150 | 0.208333 | 187 | 0.259722 | 75 | 0.104167 | 47 | 0.065278 |
| 600 | 720 | 0 | 0.000000 | 719 | 0.998611 | 130 | 0.180556 | 111 | 0.154167 | 38 | 0.052778 | 277 | 0.384722 |
