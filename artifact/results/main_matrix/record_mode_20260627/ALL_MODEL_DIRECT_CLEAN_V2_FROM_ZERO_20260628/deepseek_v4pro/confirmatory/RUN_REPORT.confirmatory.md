# DeepSeek Direct Clean-V2 Confirmatory Record-Mode Batch

Date: 2026-06-28 UTC

Model condition: `deepseek_v4pro`

Role: `confirmatory_primary`

Status: `COMPLETE`

## Scope

This batch is the DeepSeek v2 direct-network from-zero slice of the frozen
confirmatory main matrix:

```text
40 tasks x 1 model x 6 methods x 2 budgets x 3 runs = 1,440 rows
```

It does not reuse the earlier v1 DeepSeek record-mode slice or the superseded
23-row local launch/monitoring fragment from the execution startup phase.

## Live Record Summary

| field | value |
| --- | ---: |
| expected rows | 1,440 |
| controlled rows | 1,440 |
| score rows | 1,440 |
| adapter rows | 1,440 |
| parse+score success | 1,434 |
| backend-error rows | 6 |
| API calls performed | 8,760 |
| elapsed seconds | 4,415.812 |

HTTP status distribution in score rows:

| http status | rows |
| --- | ---: |
| 200 | 1,439 |
| null | 1 |

## Backend Rows

The six backend-flagged rows are retained as row outcomes under the frozen
analysis policy. They are not deleted, retried, or replaced.

One backend row failed on the final provider call after two
`RemoteDisconnected` attempts and has no final HTTP status. Five backend rows
had successful final calls (`http_status=200`) and parse-success scores, but
carry backend metadata because one or more intermediate state-update calls
encountered `RemoteDisconnected` under the frozen retry policy.

```json
[
  {"budget": 1200, "final_http_status": null, "method": "rolling_summary", "parse_success": false, "row_id": "pcgds_v2_00010_permission_boundary_with_attractive_blocked_path_easy::deepseek_v4pro::rolling_summary::budget1200::run1", "run_id": 1, "signature": "final_call_remote_disconnected_x2"},
  {"budget": 1200, "final_http_status": 200, "method": "ssr_no_visible_carry", "parse_success": true, "row_id": "pcgds_v2_00012_permission_boundary_with_attractive_blocked_path_medium::deepseek_v4pro::ssr_no_visible_carry::budget1200::run3", "run_id": 3, "signature": "state_update_remote_disconnected"},
  {"budget": 600, "final_http_status": 200, "method": "rolling_visible_fields_only", "parse_success": true, "row_id": "pcgds_v2_00013_permission_boundary_with_attractive_blocked_path_medium::deepseek_v4pro::rolling_visible_fields_only::budget600::run1", "run_id": 1, "signature": "state_update_remote_disconnected"},
  {"budget": 600, "final_http_status": 200, "method": "rolling_visible_carry_forward", "parse_success": true, "row_id": "pcgds_v2_00014_permission_boundary_with_attractive_blocked_path_hard::deepseek_v4pro::rolling_visible_carry_forward::budget600::run2", "run_id": 2, "signature": "state_update_remote_disconnected"},
  {"budget": 1200, "final_http_status": 200, "method": "loop_only", "parse_success": true, "row_id": "pcgds_v2_00027_decoy_heavy_same_prefix_config_medium::deepseek_v4pro::loop_only::budget1200::run2", "run_id": 2, "signature": "state_update_remote_disconnected"},
  {"budget": 1200, "final_http_status": 200, "method": "rolling_visible_carry_forward", "parse_success": true, "row_id": "pcgds_v2_00040_protected_information_redaction_under_task_pressure_hard::deepseek_v4pro::rolling_visible_carry_forward::budget1200::run3", "run_id": 3, "signature": "state_update_remote_disconnected"}
]
```

## Non-Backend Parse-Failure Rows

Five rows returned HTTP 200 and were not backend-error rows, but their final
answers were not parse-success rows. They are retained as row-level model
outcomes.

```json
[
  {"budget": 1200, "finish_reason": "stop", "http_status": 200, "method": "loop_only", "row_id": "pcgds_v2_00001_api_migration_state_transition_easy::deepseek_v4pro::loop_only::budget1200::run1", "run_id": 1},
  {"budget": 600, "finish_reason": "stop", "http_status": 200, "method": "loop_only", "row_id": "pcgds_v2_00010_permission_boundary_with_attractive_blocked_path_easy::deepseek_v4pro::loop_only::budget600::run1", "run_id": 1},
  {"budget": 600, "finish_reason": "stop", "http_status": 200, "method": "loop_only", "row_id": "pcgds_v2_00018_requirement_overwrite_cumulative_active_easy::deepseek_v4pro::loop_only::budget600::run1", "run_id": 1},
  {"budget": 1200, "finish_reason": "stop", "http_status": 200, "method": "ssr_no_visible_carry", "row_id": "pcgds_v2_00028_decoy_heavy_same_prefix_config_medium::deepseek_v4pro::ssr_no_visible_carry::budget1200::run1", "run_id": 1},
  {"budget": 1200, "finish_reason": "stop", "http_status": 200, "method": "loop_only", "row_id": "pcgds_v2_00034_protected_information_redaction_under_task_pressure_easy::deepseek_v4pro::loop_only::budget1200::run1", "run_id": 1}
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

- Config: `deepseek_v4pro_confirmatory.config.json`
- Row manifest: `deepseek_v4pro_confirmatory.rows.jsonl`
- Controlled rows: `CONTROLLED_ROWS.confirmatory.jsonl`
- Score rows: `scores.confirmatory.jsonl`
- Score CSV: `scores.confirmatory.csv`
- Provider-adapter source: `adapter_source.confirmatory.jsonl`
- Cassette: `deepseek_v4pro_confirmatory.cassette.jsonl`
- Replay output: `deepseek_v4pro_confirmatory.replay.jsonl`
- Summary: `summary.confirmatory.json`
- Runner log: `run_logs/deepseek_v4pro_direct_clean_v2_20260628_234637.log`
- Hash manifest: `HASH_MANIFEST.confirmatory.jsonl`

## Boundary

This file records one completed v2 direct-network model slice. The earlier v1
DeepSeek record-mode slice remains append-only audit evidence and is not pooled
into this clean-v2 primary slice.
