# Submission Build Notes

This note records how the submission aggregate result layer is built.

## Inputs

Primary clean-v2 score CSVs:

```text
artifact/results/main_matrix/record_mode_20260627/ALL_MODEL_DIRECT_CLEAN_V2_FROM_ZERO_20260628/*/confirmatory/scores.confirmatory.csv
artifact/results/main_matrix/record_mode_20260627/OPENROUTER_GPT_CLAUDE_CLEAN_V2_FROM_ZERO_20260627/*/confirmatory/scores.confirmatory.csv
artifact/results/main_matrix/record_mode_20260627/CLEAN_V2_MATRIX_MODEL_STATUS_20260629.csv
```

Diagnostic and supplement score CSVs:

```text
artifact/results/main_matrix/record_mode_20260627/BUDGET300_DIAGNOSTIC_DIRECT_V2_20260629/*/budget300_diagnostic/scores.budget300_diagnostic.csv
artifact/results/main_matrix/record_mode_20260627/OPEN_WEIGHT_QWEN3_CODER_SUPPLEMENT_20260629/openrouter_qwen3_coder_alibaba_supplement/scores.confirmatory.csv
```

## Build Command

```bash
python3 artifact/verification/summarize_submission_tables.py
```

The command writes deterministic CSV, Markdown, and JSON summaries under:

```text
paper/submission_tables/tables/
```

The same script checks the checked-in tables:

```bash
python3 artifact/verification/summarize_submission_tables.py --check
```

The script is read-only with respect to source data. It does not use network
access, provider SDKs, API keys, `.env` files, live model calls, or private
directories.

## Validation

The script recomputes:

- primary overall, by-model, by-method, and by-budget tables;
- budget-300 diagnostic overall, by-model, and by-method tables;
- Qwen3-Coder supplement overall, by-method, and by-budget tables;
- backend-error, parse-and-score, answer-success, state-governance-success,
  reliable-composite-success, and hard-cap counts and rates.

It also checks that primary row counts, backend rows, and parse-and-score rows
match `CLEAN_V2_MATRIX_MODEL_STATUS_20260629.csv`. A mismatch is a blocking
data inconsistency for submission table generation.

## Release Layers

The TMLR package uses `paper/submission_tables/` as the review-time result freeze. The full
anonymous review artifact and final public DOI release are separate layers.

Croissant metadata remains a hosting draft until final public hosting. Do not
insert placeholder DOI, hosting URL, license, or checksum values into paper text
as if they were final release identifiers.
