# Paper Framing And Research Questions

This note fixes the paper framing the artifact is meant to support. It sets
claim boundaries; it is not a result table.

## Main Framing

Frame the paper as a measurement paper about reliable co-success. It introduces
a leakage-controlled, field-aware instrument for measuring exact answer
recovery and governed state transfer separately, then asks whether those two
successes co-occur under bounded state transfer.

The stable one-sentence framing is:

```text
A measurement paper about reliable co-success, with an empirical test of
answer-governance non-overlap under bounded state transfer.
```

Do not frame it as a new memory method, a universal negative result about SSR,
or a theoretical proof that exact answer success and governance are mutually
exclusive.

## Claim Hierarchy

- Contribution: measurement instrument, scorer, benchmark substrate, and
  replayable artifact.
- Primary empirical question: whether exact-answer success and state-governance
  success co-occur on the same row.
- Mechanism question: which state-transfer mechanism moves success along the
  answer axis, the governance axis, or both.
- SSR disposition: diagnostic mechanism arm and ablation case, not the paper's
  central method contribution.

## Research Questions

RQ1 -- Measurement validity.

Can a leakage-controlled, field-aware scorer separately measure exact-answer
success and state-governance success while rejecting empty or non-bearing state
surfaces?

RQ2 -- Co-success deficit.

To what extent do exact-answer success and state-governance success co-occur
across tested methods, models, budgets, and task families?

RQ3 -- Mechanism attribution.

Which state-transfer mechanisms move success along the answer axis, which move
success along the governance axis, and which, if any, improve reliable
co-success?

RQ4 -- Stability and scope.

Does the observed co-success deficit persist across providers, budgets, and
pressure profiles under the preregistered confirmatory matrix?

## Language Discipline

Use scope-bound language:

- "reliable co-success deficit"
- "answer-governance non-overlap"
- "the two successes often occur on different rows"
- "no tested condition reaches the preregistered high co-success region"
- "typed-schema independent advantage is not established"

Avoid overclaiming:

- "mutual exclusion"
- "impossible to achieve both"
- "SSR fails"
- "no method solves stateful reasoning"
- "state governance succeeds" when answer recovery fails and the row has no
  output-bearing carry surface.

In pre-execution protocol text, use preregistration language:

```text
We preregister a confirmatory matrix to test whether the scoped probe pattern
persists across models, budgets, and task families.
```

For submission, the clean-v2 7,200-row primary matrix has execution closure and
aggregate tables under `paper/submission_tables/`. Keep interpretation tied to
the tested methods and model conditions in this benchmark.
