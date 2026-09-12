# Model Admission Criteria

Date: 2026-06-26

Scope: this file defines how the post-freeze benchmark smoke decides whether a
model condition may enter the full 7,200-row confirmatory record run. It applies
after the provider live refresh and static freeze verifier have already passed.

The gate is not a capability ranking. It checks whether a model condition can
produce auditable rows under the frozen protocol.

## Required Smoke Shape

The required confirmatory admission smoke is:

```text
1 task x 5 models x 6 methods x 2 budgets x 1 run = 60 rows
```

Each model therefore contributes 12 confirmatory smoke rows. These rows are
admission-only. They must stay outside `artifact/results/main_matrix/` and must
not enter primary aggregation.

The optional diagnostic smoke is:

```text
1 task x 5 models x 4 methods x 1 budget x 1 run = 20 rows
```

The diagnostic smoke uses budget `300`. It can decide whether the low-budget
diagnostic probe is executable, but it cannot block the `600/1200`
confirmatory matrix because of low answer, governance, or composite scores.

## Hard Engineering Gates

A model condition cannot enter the main matrix if any of these checks fail after
the frozen retry policy in `MAIN_RUN_API_POLICY.md`:

- returned model string is missing or does not match the frozen endpoint
  condition;
- provider fallback, tools, web access, or disallowed reasoning payload appears;
- request payload hash, logical request hash, row id, raw response hash, or
  score-row hash is missing;
- cassette `record`, `replay`, or `audit` fails;
- replay has any cache miss;
- scorer or parser crashes instead of emitting a structured score row;
- provider/backend failure remains after the frozen transport retry policy;
- row metadata cannot be linked to the frozen config, task manifest, scorer, and
  runner hashes.

A transient provider incident may be retried only under the frozen policy. A
payload mutation, prompt edit, parser edit, scorer edit, or request-control
change requires refreezing before the model can be admitted.

## Structured-Output Gate

The smoke must show that the model condition can produce rows the scorer can
parse and score.

Per-model threshold:

```text
final_json_parse_success and score_row_emitted >= 11 / 12 rows
```

Global threshold:

```text
final_json_parse_success and score_row_emitted >= 57 / 60 rows
```

If a model condition falls below 11/12, the matrix decision becomes
`HOLD_FOR_PROMPT_OR_ADAPTER_FIX` for that model condition. It cannot be moved
into the 7,200-row run by judgment call.

If the global smoke falls below 57/60, the whole matrix remains on hold until
the failure source is isolated. If the fix changes prompt text, adapter behavior,
parser behavior, scorer code, or request controls, the freeze packet must be
rebuilt and reverified.

## Outcome Fields Are Not Admission Filters

The following fields are measured outcomes, not admission filters:

- `answer_success`;
- `state_governance_success`;
- `reliable_composite_success`;
- forbidden-token leakage caused by model output;
- boundary or governance violations caused by model output.

Low answer success, low governance success, or low reliable co-success is a
scientific result for the main matrix. Filtering models for these outcomes would
turn the admission smoke into outcome selection.

The exception is an integrity failure: scorer-only oracle leakage, prompt
contamination, provider fallback, tool/web use, or unhashable output is not a
model behavior result. It is a protocol failure and blocks admission.

## Decisions

Use these labels after the smoke:

- `ADMIT_MODEL`: hard engineering gates pass, per-model parse/scoring threshold
  is at least 11/12, and all rows are linked to frozen hashes.
- `HOLD_FOR_RERUN`: a transient provider/backend failure occurred and the frozen
  retry or rerun policy has not yet been exhausted.
- `HOLD_FOR_PROMPT_OR_ADAPTER_FIX`: parse/scoring rows fall below threshold, or
  adapter output is malformed, and a fix may recover the condition.
- `EXCLUDE_MODEL`: the model condition repeatedly fails engineering or
  parse/scoring gates under the frozen policy, or cannot provide the required
  route/control guarantees.
- `HOLD_MATRIX`: more than one model condition is unresolved, the global 57/60
  threshold fails, or the fix would change frozen variables for all conditions.

Any exclusion must be recorded in `EXCLUDED_RUNS_20260625.csv` or its successor.
Any rerun or fix must be recorded in `RERUN_REQUIRED_20260625.csv` or its
successor. A model-level exclusion is allowed only if the remaining matrix
design and analysis plan are explicitly revised before execution.

## Reporting Boundary

Admission smoke rows are not evidence for method ranking, model ranking, or the
paper's co-success finding. They answer one narrow question: can the frozen
runner, provider route, parser, scorer, VCR cassette, and hash chain produce
auditable rows for this model condition?
