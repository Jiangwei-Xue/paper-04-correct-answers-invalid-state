# Submission Results Freeze

Date: 2026-06-30

This directory is the paper-level aggregation freeze for submission. It is built
from tracked score CSV files only. It does not call model APIs, read private
files, or replace any row-level artifact.

## Freeze Boundary

The submission primary result boundary is the clean-v2 five-model confirmatory
matrix:

```text
40 tasks x 5 models x 6 methods x 2 budgets x 3 runs = 7,200 rows
```

The row-level execution closure is already recorded under:

```text
artifact/results/main_matrix/record_mode_20260627/CLEAN_V2_MATRIX_EXECUTION_CLOSURE_20260629.md
```

The submission paper-level aggregate tables are now present under:

```text
paper/submission_tables/tables/
```

The table source is deterministic:

```text
artifact/verification/summarize_submission_tables.py
```

Run:

```bash
python3 artifact/verification/summarize_submission_tables.py --check
```

## Primary Aggregate

The primary 7,200-row aggregate is:

| rows | backend_error_rows | parse_and_score_success_rows | answer_success_rows | state_governance_success_rows | reliable_composite_success_rows | hard_cap_rows |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7,200 | 13 | 7,184 | 1,349 | 1,583 | 448 | 2,039 |

The primary reliable composite success rate is `448 / 7200 = 0.062222`.

Primary tables:

- `tables/primary_overall.csv`
- `tables/primary_by_model.csv`
- `tables/primary_by_method.csv`
- `tables/primary_by_budget.csv`
- `tables/submission_tables.md`
- `tables/submission_summary.json`

## Diagnostic And Supplement Boundaries

Budget `300` is a v2 direct-network diagnostic sidecar. It is retained and
reported descriptively for floor-effect, truncation, hard-cap, and carry-failure
diagnosis. It does not enter primary claim tables, confirmatory mixed-effects
models, method ranking, or overall method averages.

Budget-300 diagnostic tables:

- `tables/budget300_diagnostic_overall.csv`
- `tables/budget300_diagnostic_by_model.csv`
- `tables/budget300_diagnostic_by_method.csv`

Qwen3-Coder-480B is an open-weight supplement. It is retained and reported as a
separate robustness/sensitivity surface. It is not a sixth primary model and is
not pooled with the five primary model conditions.

Qwen3-Coder supplement tables:

- `tables/qwen3_coder_supplement_overall.csv`
- `tables/qwen3_coder_supplement_by_method.csv`
- `tables/qwen3_coder_supplement_by_budget.csv`

## Reproducibility Boundary

This freeze supports TMLR submission writing and review-time table reproduction. The
full anonymous review artifact and final public DOI release remain separate
release layers.

Saved-output replay verifies recorded outputs and scoring behavior. It does not
guarantee that future live closed-model API calls will be bit-identical.

`artifact/metadata/croissant.json` remains an anonymous-review and final-hosting
metadata draft. Its placeholder hosting URLs, DOI, license, and archive
checksum fields should be replaced during final public hosting. Those
placeholders do not block this submission table/results freeze.

## Claim Boundary

The submission result language should stay within this scope:

- answer-state co-success;
- state-governance correctness;
- reliable composite success;
- co-success deficit under this measurement contract;
- tested methods and model conditions in this benchmark.

The submission tables do not support a universal SSR-failure claim, a general
model leaderboard, a claim that Qwen3-Coder is a sixth primary model, or a claim
that budget `300` participates in the primary confirmatory ranking.
