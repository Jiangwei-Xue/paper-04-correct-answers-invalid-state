# PCG Dynamic-State v2 Preregistered Decision Rules v2

Date: 2026-06-23

Status: decision-rule patch for the PCG dynamic-state v2 six-method governance
matrix. This file updates interpretation rules after the 2026-06-22 provider
pilot and audit records.

## Gate State

Default state is `HOLD_PRE_RUN` until the required implementation, provider,
and scorer gates pass.

## Primary Mechanism Comparisons

### Crux Carry-vs-Schema

Compare:

`rolling_visible_carry_forward` vs `ssr_no_visible_carry`

Report both:

- `answer_success`
- `reliable_composite_success`

Interpretation:

- If visible carry wins on `answer_success`, it is evidence that answer
  recovery depends on visible-state carry rather than typed schema alone.
- If `reliable_composite_success` remains low, answer recovery is not by itself
  governed reliability.

### Mature SSR Keep-or-Downgrade

Compare:

`mature_ssr_loop` vs `rolling_visible_carry_forward`

Report both:

- `answer_success`
- `reliable_composite_success`

Decision:

- Keep mature SSR as a main method only if it is superior under matched
  answer and reliable comparisons.
- Otherwise classify mature SSR as ablation/diagnostic.

## Negative Controls

`rolling_visible_fields_only` must be reported as a negative control. A zero
or near-zero answer/reliable score in this arm is not a failed method claim; it
is mechanism evidence that mechanical field surface alone does not solve the
task.

`loop_only` must be used to audit the legacy no-conflict-only governance hole.
High legacy governance with zero answer and zero strict governance supports the
need for carry-surface strict scoring.

## Provider Disposition

Direct-provider and OpenRouter-mediated rows must not be pooled.

OpenRouter rows are robustness/appendix rows unless a paired direct-vs-OpenRouter
packet covers the same tasks, methods, budgets, and row metadata. If a model
family appears through both routes, the main text must identify the route.

## Budget Disposition

Budgets `600` and `1200` are the confirmatory budget levels. Budget `300` is a
preregistered low-budget diagnostic probe only.

Rows from the `300` diagnostic probe are excluded from confirmatory
mixed-effects models, method ranking, and overall method averages. Report them
descriptively to diagnose low-budget floor effects, truncation, and
carry-failure modes.

## Real-SWE Disposition

Real-SWE execution assets are future-work or appendix assets unless a separate
execution-layer protocol reaches its own GO gate. PCG v2 main results must not
be described as real-SWE execution performance.

## Row Admission

A row is not safe for primary aggregation if any of the following are missing
or violated:

- canonical runner hash;
- parser hash;
- strict scorer hash;
- task and oracle manifest hashes;
- request, raw response, parsed output, metric, and manifest-entry hashes;
- prompt/oracle split;
- provider-purity disposition;
- no fallback or recorded fallback-disabled status;
- reasoning/thinking disabled or no-reasoning policy;
- tools/web disabled;
- retry/failure retention policy.
