# openrouter_claude48 Budget-300 Diagnostic Direct-Network Run

Date: 2026-06-29 UTC

Model condition: `openrouter_claude48`

Role: `budget300_diagnostic`

Status: `COMPLETE`

## Scope

This batch is a v2 direct-network budget-300 diagnostic probe:

```text
40 tasks x 1 model x 4 core methods x 1 budget x 1 run = 160 rows
```

It is diagnostic only. It must not enter primary claim tables, confirmatory mixed-effects models, method ranking, or overall method averages. Its intended use is floor-effect, truncation, and carry-failure diagnosis.

## Live Record Summary

| field | value |
| --- | ---: |
| expected rows | 160 |
| controlled rows | 160 |
| score rows | 160 |
| adapter rows | 160 |
| parse+score success | 158 |
| backend-error rows | 0 |
| API calls performed | 960 |
| elapsed seconds | 448.29 |

HTTP status distribution: `{"200": 160}`

## Parse-Failure Rows

```json
[{"backend_error": false, "budget": 300, "http_status": 200, "method": "rolling_visible_carry_forward", "row_id": "pcgds_v2_00004_api_migration_state_transition_medium::openrouter_claude48::rolling_visible_carry_forward::budget300::run1", "run_id": 1}, {"backend_error": false, "budget": 300, "http_status": 200, "method": "rolling_visible_carry_forward", "row_id": "pcgds_v2_00035_protected_information_redaction_under_task_pressure_medium::openrouter_claude48::rolling_visible_carry_forward::budget300::run1", "run_id": 1}]
```

## VCR Closure

```text
adapter_source -> VCR record -> cassette -> replay -> audit
```

VCR audit result:

```text
rows_checked: 160
cassette_entries_checked: 160
cache_miss_count: 0
failure_count: 0
api_calls_performed: 0
```

## Output Files

- Config: `openrouter_claude48_budget300_diagnostic.config.json`
- Row manifest: `openrouter_claude48_budget300_diagnostic.rows.jsonl`
- Controlled rows: `CONTROLLED_ROWS.budget300_diagnostic.jsonl`
- Score rows: `scores.budget300_diagnostic.jsonl`
- Score CSV: `scores.budget300_diagnostic.csv`
- Provider-adapter source: `adapter_source.budget300_diagnostic.jsonl`
- Cassette: `openrouter_claude48_budget300_diagnostic.cassette.jsonl`
- Replay output: `openrouter_claude48_budget300_diagnostic.replay.jsonl`
- Summary: `summary.budget300_diagnostic.json`
- Runtime hardening controls: `OPENROUTER_RUNTIME_HARDENING_EFFECTIVE_CONTROLS.json`
- VCR logs: `vcr_record.budget300_diagnostic.log`, `vcr_replay.budget300_diagnostic.log`, `vcr_audit.budget300_diagnostic.log`
- Runner logs: `run_logs/`
- Hash manifest: `HASH_MANIFEST.budget300_diagnostic.jsonl`
