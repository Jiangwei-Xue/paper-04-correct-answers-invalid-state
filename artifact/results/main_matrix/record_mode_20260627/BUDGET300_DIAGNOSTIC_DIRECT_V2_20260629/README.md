# Budget-300 Direct-Network Diagnostic Runs

Status: complete diagnostic sidecar execution.

This namespace stores the v2 direct-network budget-300 diagnostic probe. It is
not part of the 7,200-row confirmatory primary matrix.

Protocol boundary:

```text
../../../protocol/main_matrix/BUDGET300_DIRECT_NETWORK_DIAGNOSTIC_PROTOCOL_20260629.md
```

The full diagnostic sidecar shape is:

```text
40 tasks x 5 models x 4 core methods x 1 budget x 1 run = 800 rows
```

Each completed model condition contributes 160 rows.

## Analysis Boundary

Rows in this namespace must not enter:

- primary claim tables;
- confirmatory mixed-effects models;
- method ranking;
- overall method averages.

They are retained only for floor-effect, truncation, and carry-failure
diagnosis.

## Current Contents

| model condition | role | status | rows | backend rows | parse+score success | VCR audit |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `openrouter_claude48` | `budget300_diagnostic` | `COMPLETE` | 160 | 0 | 158 | cache miss 0, failure 0 |
| `openrouter_gpt55` | `budget300_diagnostic` | `COMPLETE` | 160 | 0 | 160 | cache miss 0, failure 0 |
| `deepseek_v4pro` | `budget300_diagnostic` | `COMPLETE` | 160 | 0 | 160 | cache miss 0, failure 0 |
| `qwen37max` | `budget300_diagnostic` | `COMPLETE` | 160 | 0 | 160 | cache miss 0, failure 0 |
| `kimi_k26` | `budget300_diagnostic` | `COMPLETE` | 160 | 0 | 160 | cache miss 0, failure 0 |
| `TOTAL` | `budget300_diagnostic` | `COMPLETE` | 800 | 0 | 798 | cache miss 0, failure 0 |

Diagnostic execution closure:

```text
BUDGET300_DIAGNOSTIC_DIRECT_V2_EXECUTION_CLOSURE_20260629.md
BUDGET300_DIAGNOSTIC_DIRECT_V2_MODEL_STATUS_20260629.csv
```

## Completed OpenRouter Slices

`openrouter_claude48/budget300_diagnostic/`:

- expected rows: 160;
- score rows: 160;
- backend-error rows: 0;
- parse+score success: 158;
- API calls performed: 960;
- VCR record/replay/audit closed with cache miss 0 and failure 0;
- hash manifest rows: 15, verified with 0 failures.

`openrouter_gpt55/budget300_diagnostic/`:

- expected rows: 160;
- score rows: 160;
- backend-error rows: 0;
- parse+score success: 160;
- API calls performed: 960;
- VCR record/replay/audit closed with cache miss 0 and failure 0;
- hash manifest rows: 15, verified with 0 failures.

`deepseek_v4pro/budget300_diagnostic/`:

- expected rows: 160;
- score rows: 160;
- backend-error rows: 0;
- parse+score success: 160;
- API calls performed: 960;
- VCR record/replay/audit closed with cache miss 0 and failure 0;
- hash manifest rows: 15, verified with 0 failures.

`qwen37max/budget300_diagnostic/`:

- expected rows: 160;
- score rows: 160;
- backend-error rows: 0;
- parse+score success: 160;
- API calls performed: 960;
- VCR record/replay/audit closed with cache miss 0 and failure 0;
- hash manifest rows: 15, verified with 0 failures.

`kimi_k26/budget300_diagnostic/`:

- expected rows: 160;
- score rows: 160;
- backend-error rows: 0;
- parse+score success: 160;
- API calls performed: 960;
- VCR record/replay/audit closed with cache miss 0 and failure 0;
- hash manifest rows: 15, verified with 0 failures.

## Output Contract

Each completed model directory contains:

- model-slice config;
- row manifest;
- controlled rows;
- adapter-source rows;
- score JSONL and CSV;
- VCR cassette;
- replay output;
- VCR audit log;
- run report;
- hash manifest;
- runner log.
