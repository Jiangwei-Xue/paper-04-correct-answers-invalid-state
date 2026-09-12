# Preregistered Decision Rules

The primary analysis should be defined before main-matrix execution and should
avoid retroactive pooling of probes or historical runs.

The statistical estimands, contrast hierarchy, task-cluster bootstrap rule,
failure coding, and model-assisted sensitivity boundary are fixed in
`STATISTICAL_ANALYSIS_PLAN.md`.

## Primary Outcome

Use the fixed scorer for each task and report:

- `answer_success`;
- strict `state_governance_success`;
- `reliable_composite_success = answer_success AND state_governance_success`.

The composite is the governed reliability signal. `answer_success` is the
mechanism signal for whether a method recovers the answer. Standalone
`state_governance_success` is diagnostic and must not override answer failure.
The central paper-level comparison is reliable co-success: whether answer
success and strict governance success occur on the same row.

Strict `state_governance_success` is not a no-conflict-only metric. It requires
both absence of output-bearing conflict and a present output-bearing carry
surface:

```text
state_governance_success =
  legacy_no_conflict_governance AND state_carry_surface_present
```

The no-conflict-only governance score, if recomputed, is an appendix diagnostic
for the empty-state loophole. It must not be used for method ranking,
confirmatory aggregation, or a standalone success claim.

## Missingness

Rows with provider failures, parser failures, or invalid responses should be
classified before aggregation. Any targeted rerun/backfill must be logged as a
separate corrective action with its own hash manifest.

## Method Disposition

`mature_ssr_loop` is included as an ablation and diagnostic condition. It should
not be promoted to a primary advantage claim unless the main-matrix decision
rules specify that before the run.

`rolling_visible_fields_only` is a negative control, not a competitive method
arm. It should be reported as a control for mechanical field surface, not as a
full visible-carry method.

`loop_only` is a floor/reference arm and an empty-state diagnostic. Clean-looking
governance from `loop_only` is not evidence of successful state governance when
answer recovery fails; under the strict scorer, absent output-bearing carry earns
no governance credit.

Method comparisons should be reported as mechanism attribution. The paper may
ask whether typed schema, deterministic visible carry, or their interaction
improves reliable co-success. It should not frame SSR as the proposed method or
interpret a typed-schema deficit as a universal SSR failure.

The primary confirmatory contrast is the crux comparison
`rolling_visible_carry_forward - ssr_no_visible_carry` on
`reliable_composite_success`. The schema-given-carry contrast
`mature_ssr_loop - rolling_visible_carry_forward` is key secondary.

## RQ Alignment

Use the research questions in `PAPER_FRAMING_AND_RQS.md`. Before the full
main-matrix run, use preregistration language: the matrix is designed to test
whether scoped answer-governance non-overlap persists across the frozen method,
model, budget, and task-family axes.

## Budget Disposition

The confirmatory budget levels are `600` and `1200`. Budget `300` is a
preregistered low-budget diagnostic probe only. It is excluded from
confirmatory mixed-effects models, method ranking, and overall method averages.

Report `300` descriptively to diagnose low-budget floor effects, truncation,
and carry-failure modes under extreme state compression.

The evidence basis for this disposition is recorded in
`BUDGET_300_DIAGNOSTIC_DISPOSITION.md`.

## Drift And Reruns

Endpoint drift probes, if used, audit endpoint stability across the run window.
They are not primary rows and do not enter primary outcome estimation.

Closed-model API reruns are optional diagnostics. They are not expected to be
byte-identical and should not replace verification from saved outputs.
