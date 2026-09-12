# GPT Clean-V2 Confirmatory Record-Mode Batch

Date: 2026-06-28 UTC

Model condition: `openrouter_gpt55`

Role: `confirmatory_primary`

Status: `COMPLETE`

## Scope

This batch is the GPT clean-v2 from-zero slice of the frozen confirmatory main
matrix:

```text
40 tasks x 1 model x 6 methods x 2 budgets x 3 runs = 1,440 rows
```

It is part of the OpenRouter clean-v2 GPT/Claude execution namespace. It does
not reuse earlier GPT first-pass rows, pause packets, recovery rows, canary
rows, or old partial outputs.

## Live Record Summary

| field | value |
| --- | ---: |
| expected rows | 1,440 |
| controlled rows | 1,440 |
| score rows | 1,440 |
| adapter rows | 1,440 |
| parse+score success | 1,433 |
| backend-error rows | 0 |
| API calls performed | 8,760 |
| elapsed seconds | 3,029.170 |

All 1,440 provider calls returned HTTP 200 and no backend-error rows were
observed. The seven parse-failure rows are retained as row-level outcomes. They
were not rerun, deleted, or replaced.

## Parse-Failure Rows

```json
[{"backend_error": false, "budget": 1200, "finish_reason": "stop", "http_status": 200, "method": "rolling_summary", "row_id": "pcgds_v2_00003_api_migration_state_transition_medium::openrouter_gpt55::rolling_summary::budget1200::run2", "run_id": 2}, {"backend_error": false, "budget": 600, "finish_reason": "stop", "http_status": 200, "method": "rolling_summary", "row_id": "pcgds_v2_00006_api_migration_state_transition_hard::openrouter_gpt55::rolling_summary::budget600::run2", "run_id": 2}, {"backend_error": false, "budget": 600, "finish_reason": "stop", "http_status": 200, "method": "rolling_summary", "row_id": "pcgds_v2_00017_requirement_overwrite_cumulative_active_easy::openrouter_gpt55::rolling_summary::budget600::run3", "run_id": 3}, {"backend_error": false, "budget": 600, "finish_reason": "stop", "http_status": 200, "method": "rolling_visible_carry_forward", "row_id": "pcgds_v2_00022_requirement_overwrite_cumulative_active_hard::openrouter_gpt55::rolling_visible_carry_forward::budget600::run2", "run_id": 2}, {"backend_error": false, "budget": 600, "finish_reason": "stop", "http_status": 200, "method": "rolling_summary", "row_id": "pcgds_v2_00028_decoy_heavy_same_prefix_config_medium::openrouter_gpt55::rolling_summary::budget600::run2", "run_id": 2}, {"backend_error": false, "budget": 600, "finish_reason": "stop", "http_status": 200, "method": "rolling_summary", "row_id": "pcgds_v2_00034_protected_information_redaction_under_task_pressure_easy::openrouter_gpt55::rolling_summary::budget600::run3", "run_id": 3}, {"backend_error": false, "budget": 1200, "finish_reason": "stop", "http_status": 200, "method": "rolling_summary", "row_id": "pcgds_v2_00036_protected_information_redaction_under_task_pressure_medium::openrouter_gpt55::rolling_summary::budget1200::run1", "run_id": 1}]
```

## VCR Closure

The batch closed through:

```text
adapter_source -> VCR record -> cassette -> replay -> audit
```

VCR audit result:

```text
rows_checked: 1440
cassette_entries_checked: 1440
cache_miss_count: 0
failure_count: 0
api_calls_performed: 0
```

## Output Files

- Config: `openrouter_gpt55_confirmatory.config.json`
- Row manifest: `openrouter_gpt55_confirmatory.rows.jsonl`
- Controlled rows: `CONTROLLED_ROWS.confirmatory.jsonl`
- Score rows: `scores.confirmatory.jsonl`
- Score CSV: `scores.confirmatory.csv`
- Provider-adapter source: `adapter_source.confirmatory.jsonl`
- Cassette: `openrouter_gpt55_confirmatory.cassette.jsonl`
- Replay output: `openrouter_gpt55_confirmatory.replay.jsonl`
- Summary: `summary.confirmatory.json`
- Runner log: `run_logs/gpt55_clean_v2_20260628_220014.log`
- Hash manifest: `HASH_MANIFEST.confirmatory.jsonl`

## Boundary

This file records one completed clean-v2 OpenRouter model slice. The earlier
GPT first-pass partial rows remain append-only diagnostic evidence and are not
pooled into this clean-v2 primary slice.
