# Clean-V2 Matrix Execution Closure

Date: 2026-06-29 UTC

Scope: PCG dynamic-state v2 confirmatory primary matrix execution closure.

This packet closes the clean-v2 execution layer for the five admitted model
conditions. It is not a final paper-level gate report and does not evaluate
scientific claims or paper external validity.

This closure covers the 7,200-row confirmatory primary matrix only. The
800-row budget-300 probe is a separate diagnostic sidecar by protocol and is
not required for closing the confirmatory clean-v2 matrix.

## Decision

Execution closure status: `COMPLETE`.

The clean-v2 confirmatory matrix has all five model slices completed from row
zero and closed through VCR record/replay/audit with zero cache misses.

```text
40 tasks x 5 models x 6 methods x 2 budgets x 3 runs = 7,200 rows
```

## Included Primary-Candidate Slices

| model condition | namespace | rows | backend rows | parse+score success | VCR audit |
| --- | --- | ---: | ---: | ---: | --- |
| `deepseek_v4pro` | `ALL_MODEL_DIRECT_CLEAN_V2_FROM_ZERO_20260628` | 1,440 | 6 | 1,434 | cache miss 0, failure 0 |
| `qwen37max` | `ALL_MODEL_DIRECT_CLEAN_V2_FROM_ZERO_20260628` | 1,440 | 0 | 1,440 | cache miss 0, failure 0 |
| `kimi_k26` | `ALL_MODEL_DIRECT_CLEAN_V2_FROM_ZERO_20260628` | 1,440 | 7 | 1,438 | cache miss 0, failure 0 |
| `openrouter_claude48` | `OPENROUTER_GPT_CLAUDE_CLEAN_V2_FROM_ZERO_20260627` | 1,440 | 0 | 1,439 | cache miss 0, failure 0 |
| `openrouter_gpt55` | `OPENROUTER_GPT_CLAUDE_CLEAN_V2_FROM_ZERO_20260627` | 1,440 | 0 | 1,433 | cache miss 0, failure 0 |
| `TOTAL` | clean-v2 execution closure | 7,200 | 13 | 7,184 | cache miss 0, failure 0 |

Machine-readable status table:

```text
CLEAN_V2_MATRIX_MODEL_STATUS_20260629.csv
```

## Missingness And Backend Policy

No rows are missing. All `CONTROLLED_ROWS`, `adapter_source`, `scores`,
cassette, and replay outputs contain 7,200 rows in aggregate.

Backend and parse-failure rows are retained as frozen row outcomes. They are
not deleted, retried, or replaced after outcome inspection.

Backend row accounting:

- DeepSeek: 6 backend rows; 1 backend parse-failure row and 5 backend
  parse-success rows.
- Qwen: 0 backend rows.
- Kimi: 7 backend rows; 2 backend parse-failure rows and 5 backend
  parse-success rows.
- Claude: 0 backend rows.
- GPT: 0 backend rows.

Parse-failure accounting:

- Backend parse-failure rows: 3.
- Non-backend parse-failure rows: 13.
- Total parse-failure rows: 16.

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
- run log copied into the result directory.

Hash-manifest verification was re-run for all five included slices:

| model condition | manifest rows | hash verification failures |
| --- | ---: | ---: |
| `deepseek_v4pro` | 14 | 0 |
| `qwen37max` | 14 | 0 |
| `kimi_k26` | 14 | 0 |
| `openrouter_claude48` | 12 | 0 |
| `openrouter_gpt55` | 12 | 0 |

## Excluded Or Non-Primary Evidence

The following artifacts remain append-only audit or diagnostic evidence and are
not pooled into the clean-v2 primary-candidate matrix:

- v1 proxy-mediated model slices under sibling model directories;
- excluded first-pass/proxy-mediated history under
  `excluded_history/proxy_mediated_first_pass_20260627/`, including stopped
  GPT and Claude partial slices;
- OpenRouter pause and network-classification packets;
- Claude network/runtime canary;
- DeepSeek 23-row launch/monitoring fragment from the execution startup phase;
  it was superseded by the complete 1,440-row slice and is not included in the
  reviewer-facing primary matrix namespace.

## Boundary

This closure supports proceeding to aggregation and statistical analysis using
the five clean-v2 primary-candidate slices listed above.

The 800-row budget-300 run, if executed next, is a v2 direct-network diagnostic
probe. It should receive its own diagnostic namespace, VCR closure, run reports,
and hash manifests. It must not enter:

- primary claim tables;
- confirmatory mixed-effects models;
- method ranking;
- overall method averages.

Its only intended use is floor-effect, truncation, and carry-failure diagnosis.

It does not by itself close paper-level claims, final contamination review,
statistical interpretation, or venue-facing conclusions.
