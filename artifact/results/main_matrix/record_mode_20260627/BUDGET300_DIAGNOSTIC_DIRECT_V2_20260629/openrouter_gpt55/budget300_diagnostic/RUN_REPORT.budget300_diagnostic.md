# openrouter_gpt55 Budget-300 Diagnostic Direct-Network Run

Date: 2026-06-29 UTC

Model condition: `openrouter_gpt55`

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
| parse+score success | 160 |
| backend-error rows | 0 |
| API calls performed | 960 |
| elapsed seconds | 251.774 |

HTTP status distribution: `{"200": 160}`

## Parse-Failure Rows

```json
[]
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

- Config: `openrouter_gpt55_budget300_diagnostic.config.json`
- Row manifest: `openrouter_gpt55_budget300_diagnostic.rows.jsonl`
- Controlled rows: `CONTROLLED_ROWS.budget300_diagnostic.jsonl`
- Score rows: `scores.budget300_diagnostic.jsonl`
- Score CSV: `scores.budget300_diagnostic.csv`
- Provider-adapter source: `adapter_source.budget300_diagnostic.jsonl`
- Cassette: `openrouter_gpt55_budget300_diagnostic.cassette.jsonl`
- Replay output: `openrouter_gpt55_budget300_diagnostic.replay.jsonl`
- Summary: `summary.budget300_diagnostic.json`
- Runtime hardening controls: `OPENROUTER_RUNTIME_HARDENING_EFFECTIVE_CONTROLS.json`
- VCR logs: `vcr_record.budget300_diagnostic.log`, `vcr_replay.budget300_diagnostic.log`, `vcr_audit.budget300_diagnostic.log`
- Runner logs: `run_logs/`
- Hash manifest: `HASH_MANIFEST.budget300_diagnostic.jsonl`
