# Qwen Direct Clean-V2 Confirmatory Record-Mode Batch

Date: 2026-06-28 UTC

Model condition: `qwen37max`

Role: `confirmatory_primary`

Status: `COMPLETE`

## Scope

This batch is the Qwen v2 direct-network from-zero slice of the frozen
confirmatory main matrix:

```text
40 tasks x 1 model x 6 methods x 2 budgets x 3 runs = 1,440 rows
```

It does not reuse the earlier v1 Qwen record-mode slice.

## Live Record Summary

| field | value |
| --- | ---: |
| expected rows | 1,440 |
| controlled rows | 1,440 |
| score rows | 1,440 |
| adapter rows | 1,440 |
| parse+score success | 1,440 |
| backend-error rows | 0 |
| API calls performed | 8,760 |
| elapsed seconds | 3,972.994 |

HTTP status distribution in score rows:

| http status | rows |
| --- | ---: |
| 200 | 1,440 |

All 1,440 rows returned HTTP 200, parse-success scores, and no backend-error
rows. No rows were rerun, deleted, or replaced.

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

- Config: `qwen37max_confirmatory.config.json`
- Row manifest: `qwen37max_confirmatory.rows.jsonl`
- Controlled rows: `CONTROLLED_ROWS.confirmatory.jsonl`
- Score rows: `scores.confirmatory.jsonl`
- Score CSV: `scores.confirmatory.csv`
- Provider-adapter source: `adapter_source.confirmatory.jsonl`
- Cassette: `qwen37max_confirmatory.cassette.jsonl`
- Replay output: `qwen37max_confirmatory.replay.jsonl`
- Summary: `summary.confirmatory.json`
- Runner log: `run_logs/qwen37max_direct_clean_v2_20260629_012628.log`
- Hash manifest: `HASH_MANIFEST.confirmatory.jsonl`

## Boundary

This file records one completed v2 direct-network model slice. The earlier v1
Qwen record-mode slice remains append-only audit evidence and is not pooled
into this clean-v2 primary slice.
