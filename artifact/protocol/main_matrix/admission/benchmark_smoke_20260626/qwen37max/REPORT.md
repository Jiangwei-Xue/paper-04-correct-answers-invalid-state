# Benchmark Admission Smoke - qwen37max

Date: 20260626

Task: `pcgds_v2_00001_api_migration_state_transition_easy`

Decision: `ADMIT_MODEL`

## Confirmatory Smoke

| field | count | denominator |
| --- | ---: | ---: |
| final_json_parse_success and score_row_emitted | 12 | 12 |
| backend_error | 0 | 12 |
| reasoning_content_present | 0 | 12 |
| answer_success | 5 | 12 |
| state_governance_success | 6 | 12 |
| reliable_composite_success | 4 | 12 |

Outcome fields above are reported, not used as admission filters.

## Budget-300 Diagnostic Smoke

| field | count | denominator |
| --- | ---: | ---: |
| final_json_parse_success and score_row_emitted | 4 | 4 |
| backend_error | 0 | 4 |
| reliable_composite_success | 0 | 4 |
