# Kimi Direct Clean-V2 Confirmatory Record-Mode Batch

Date: 2026-06-29 UTC

Model condition: `kimi_k26`

Role: `confirmatory_primary`

Status: `COMPLETE`

## Scope

This batch is the Kimi v2 direct-network from-zero slice of the frozen
confirmatory main matrix:

```text
40 tasks x 1 model x 6 methods x 2 budgets x 3 runs = 1,440 rows
```

It does not reuse the earlier v1 Kimi record-mode slice.

## Live Record Summary

| field | value |
| --- | ---: |
| expected rows | 1,440 |
| controlled rows | 1,440 |
| score rows | 1,440 |
| adapter rows | 1,440 |
| parse+score success | 1,438 |
| backend-error rows | 7 |
| API calls performed | 8,760 |
| elapsed seconds | 6,934.379 |

HTTP status distribution in score rows:

| http status | rows |
| --- | ---: |
| 200 | 1,437 |
| null | 3 |

## Backend Rows

The seven backend-flagged rows are retained as row outcomes under the frozen
analysis policy. They are not deleted, retried, or replaced.

Two backend rows failed on the final provider call after timeout-class
transport failures and are also parse-failure rows. Five backend rows still
have parse-success scores; these rows carry backend metadata because one or
more intermediate calls timed out, or because the deterministic mature-SSR slot
compiler path retained backend metadata even though a score row was emitted.

```json
[
  {"budget": 1200, "final_http_status": 200, "method": "rolling_visible_carry_forward", "parse_success": true, "row_id": "pcgds_v2_00005_api_migration_state_transition_medium::kimi_k26::rolling_visible_carry_forward::budget1200::run1", "run_id": 1, "signature": "state_update_transport_timeout"},
  {"budget": 1200, "final_http_status": 200, "method": "mature_ssr_loop", "parse_success": true, "row_id": "pcgds_v2_00006_api_migration_state_transition_hard::kimi_k26::mature_ssr_loop::budget1200::run3", "run_id": 3, "signature": "deterministic_mature_ssr_slot_compiler_with_state_update_timeout"},
  {"budget": 600, "final_http_status": 200, "method": "rolling_visible_carry_forward", "parse_success": true, "row_id": "pcgds_v2_00008_api_migration_state_transition_hard::kimi_k26::rolling_visible_carry_forward::budget600::run3", "run_id": 3, "signature": "state_update_transport_timeout"},
  {"budget": 1200, "final_http_status": null, "method": "loop_only", "parse_success": false, "row_id": "pcgds_v2_00026_decoy_heavy_same_prefix_config_easy::kimi_k26::loop_only::budget1200::run3", "run_id": 3, "signature": "final_call_transport_timeout_x2"},
  {"budget": 1200, "final_http_status": 200, "method": "rolling_summary", "parse_success": true, "row_id": "pcgds_v2_00031_decoy_heavy_same_prefix_config_hard::kimi_k26::rolling_summary::budget1200::run2", "run_id": 2, "signature": "state_update_transport_timeout"},
  {"budget": 1200, "final_http_status": null, "method": "mature_ssr_loop", "parse_success": true, "row_id": "pcgds_v2_00039_protected_information_redaction_under_task_pressure_hard::kimi_k26::mature_ssr_loop::budget1200::run1", "run_id": 1, "signature": "deterministic_mature_ssr_slot_compiler_with_state_update_timeout"},
  {"budget": 600, "final_http_status": null, "method": "rolling_summary", "parse_success": false, "row_id": "pcgds_v2_00040_protected_information_redaction_under_task_pressure_hard::kimi_k26::rolling_summary::budget600::run1", "run_id": 1, "signature": "final_call_transport_timeout_x2"}
]
```

## Parse-Failure Rows

Both parse-failure rows are backend-error rows with null final HTTP status.
They are retained as row-level outcomes.

```json
[
  {"backend_error": true, "budget": 1200, "finish_reason": null, "http_status": null, "method": "loop_only", "row_id": "pcgds_v2_00026_decoy_heavy_same_prefix_config_easy::kimi_k26::loop_only::budget1200::run3", "run_id": 3},
  {"backend_error": true, "budget": 600, "finish_reason": null, "http_status": null, "method": "rolling_summary", "row_id": "pcgds_v2_00040_protected_information_redaction_under_task_pressure_hard::kimi_k26::rolling_summary::budget600::run1", "run_id": 1}
]
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

- Config: `kimi_k26_confirmatory.config.json`
- Row manifest: `kimi_k26_confirmatory.rows.jsonl`
- Controlled rows: `CONTROLLED_ROWS.confirmatory.jsonl`
- Score rows: `scores.confirmatory.jsonl`
- Score CSV: `scores.confirmatory.csv`
- Provider-adapter source: `adapter_source.confirmatory.jsonl`
- Cassette: `kimi_k26_confirmatory.cassette.jsonl`
- Replay output: `kimi_k26_confirmatory.replay.jsonl`
- Summary: `summary.confirmatory.json`
- Runner log: `run_logs/kimi_k26_direct_clean_v2_20260629_093109.log`
- Hash manifest: `HASH_MANIFEST.confirmatory.jsonl`

## Boundary

This file records one completed v2 direct-network model slice. The earlier v1
Kimi record-mode slice remains append-only audit evidence and is not pooled
into this clean-v2 primary slice.
