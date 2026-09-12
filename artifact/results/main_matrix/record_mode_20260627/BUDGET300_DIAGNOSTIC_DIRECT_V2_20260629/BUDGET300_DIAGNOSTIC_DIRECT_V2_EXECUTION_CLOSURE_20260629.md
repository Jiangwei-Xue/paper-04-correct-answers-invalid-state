# Budget-300 Diagnostic Direct-V2 Execution Closure

Date: 2026-06-29 UTC

Scope: PCG dynamic-state v2 budget-300 diagnostic sidecar execution closure.

This closure covers the separate 800-row budget-300 diagnostic probe only. It is
not part of the 7,200-row confirmatory primary matrix and does not alter the
primary analysis population.

## Decision

Diagnostic execution closure status: `COMPLETE`.

All five model-condition slices completed under the v2 direct-network diagnostic
namespace and closed through VCR record/replay/audit with zero cache misses.

```text
40 tasks x 5 models x 4 core methods x 1 budget x 1 run = 800 rows
```

## Analysis Boundary

Rows in this diagnostic sidecar must not enter:

- primary claim tables;
- confirmatory mixed-effects models;
- method ranking;
- overall method averages.

They are retained only for floor-effect, truncation, and carry-failure
diagnosis.

## Completed Diagnostic Slices

| model condition | rows | backend rows | parse+score success | VCR audit | hash manifest |
| --- | ---: | ---: | ---: | --- | --- |
| `openrouter_claude48` | 160 | 0 | 158 | cache miss 0, failure 0 | 15 rows, 0 failures |
| `openrouter_gpt55` | 160 | 0 | 160 | cache miss 0, failure 0 | 15 rows, 0 failures |
| `deepseek_v4pro` | 160 | 0 | 160 | cache miss 0, failure 0 | 15 rows, 0 failures |
| `qwen37max` | 160 | 0 | 160 | cache miss 0, failure 0 | 15 rows, 0 failures |
| `kimi_k26` | 160 | 0 | 160 | cache miss 0, failure 0 | 15 rows, 0 failures |
| `TOTAL` | 800 | 0 | 798 | cache miss 0, failure 0 | 75 rows, 0 failures |

Machine-readable status table:

```text
BUDGET300_DIAGNOSTIC_DIRECT_V2_MODEL_STATUS_20260629.csv
```

## Missingness And Backend Policy

No diagnostic rows are missing. All controlled rows, adapter-source rows, score
rows, cassettes, and replay outputs contain 800 rows in aggregate.

Backend row accounting:

- Total backend-error rows: 0.
- Backend parse-failure rows: 0.
- Backend parse-success rows: 0.

Parse-failure accounting:

- Total parse-failure rows: 2.
- Non-backend parse-failure rows: 2.

## Evidence Closure

Each included model slice has:

- model-slice config;
- row manifest;
- controlled rows;
- adapter-source rows;
- score JSONL and CSV;
- summary JSON;
- VCR cassette;
- VCR replay output;
- VCR audit with cache miss 0 and failure 0;
- run report;
- hash manifest;
- runner log.

Hash-manifest verification was re-run for all five diagnostic slices and found
zero failures.

## Boundary

This closure supports using the 800 rows for descriptive low-budget diagnostics.
It does not support primary method ranking, primary claim tables, confirmatory
mixed-effects models, or overall method averages.
