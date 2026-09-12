# PCG Dynamic-State v2 Latest Experiment Variable Requirements v2

Date: 2026-06-23

Status: protocol patch for the PCG dynamic-state v2 six-method governance
matrix. This document updates the 2026-06-21 freeze text with the 2026-06-22
pilot/audit findings. It does not create result rows and does not authorize an
API run by itself.

Supersession note: a later budget-disposition decision moved budget `300` out
of the confirmatory main matrix. The current confirmatory design uses only
`600` and `1200` (`40 x 5 x 6 x 2 x 3 = 7,200` rows), with `300` retained only
as a separate `40 x 5 x 4 x 1 x 1 = 800` low-budget diagnostic probe.

## Authority

This v2 patch controls PCG dynamic-state v2 method wording, provider purity,
metric interpretation, and pre-API gates. Historical Fresh v2 files remain
useful for prompt/oracle split, hash-chain, retry, and provider-control
patterns, but Fresh v2's four-method 9000-row matrix is not the PCG v2 main
matrix.

## Frozen Matrix Shape

Superseded candidate row plan:

`40 tasks x 5 model conditions x 6 methods x 3 budgets x 3 runs = 10800 rows`

Current confirmatory row plan:

`40 tasks x 5 model conditions x 6 methods x 2 budgets x 3 runs = 7200 rows`

Current low-budget diagnostic probe:

`40 tasks x 5 model conditions x 4 core methods x 1 budget x 1 run = 800 rows`

The six method labels remain:

- `loop_only`
- `rolling_summary`
- `rolling_visible_carry_forward`
- `rolling_visible_fields_only`
- `ssr_no_visible_carry`
- `mature_ssr_loop`

The confirmatory state budgets are `600` and `1200` characters. Budget `300` is
diagnostic only and is excluded from confirmatory mixed-effects models, method
ranking, and overall method averages. Report `300` descriptively to diagnose
low-budget floor effects, truncation, and carry-failure modes.

## Method Implementation Requirements

The `mature_ssr_loop` and `ssr_no_visible_carry` labels must not be treated as
loose aliases to legacy `ssr_loop` or `ssr_only`. They require the 2026-06-22
six-method runner contract:

- `compile_state` builds method-specific state from model-visible text only.
- `build_final_prompt` enforces final-answer source fields.
- For `mature_ssr_loop`, `final_answer.required_tokens` may derive only from
  `OUT`, and `final_answer.allowed_paths` may derive only from `ALW`.
- For `ssr_no_visible_carry`, the same `OUT`/`ALW` final-answer source rule
  applies, without runner-side deterministic visible carry.
- `NO`, `B`, `G`, `N`, `CK`, and `LOOP` are diagnostic or exclusion fields and
  must not seed output-bearing final answers.

`rolling_visible_fields_only` is a deterministic mechanical-field negative
control. It is not a competitive method arm. It carries compact visible field
surfaces and boundary counts to test whether mechanical carry surface alone can
recover answer/reliable success.

## Scoring And Claims

Primary composite:

`reliable_composite_success = answer_success AND strict state_governance_success`

Crux comparisons must be reported on both:

- `answer_success`: mechanism signal for whether carry recovers the answer.
- `reliable_composite_success`: governed reliability signal.

Standalone `state_governance_success` is diagnostic only. It must not override
answer failure.

Allowed claim scope:

- Tested PCG dynamic-state v2 methods and tested provider routes show
  answer/governance decoupling.
- Visible state carry-forward is a key mechanism to measure and control.
- Mature SSR is an ablation/diagnostic condition unless it is superior under
  matched answer and reliable comparisons.

Disallowed claim scope:

- Universal impossibility result for SSR or memory schemas.
- Completed Fresh v2 9000-row confirmatory matrix.
- Pooled OpenRouter and direct-provider model rows.
- Real-SWE execution performance result.

## Provider Purity

Rows mediated through OpenRouter are robustness/appendix rows unless a separate
paired direct-vs-OpenRouter packet is preregistered. Main effect tables must use
direct-provider or otherwise single-provider conditions. Direct-provider and
OpenRouter-mediated rows for the same model family must not be pooled.

Before any primary claim, each main-table model condition must record:

- provider or endpoint;
- exact model string returned or selected;
- supported-parameter snapshot;
- fallback status;
- route or provider metadata when exposed;
- runner/parser/scorer/environment hashes.

## Required Before API

No PCG v2 main-matrix API row is admissible until all of the following pass:

- task split audit;
- strict scorer dummy tests;
- discriminating static sanity test, showing the canonical mature SSR runner
  recovers high answer on a frozen static-control task where historical static
  SSR was near ceiling;
- method implementation audit for all six methods, including
  `rolling_visible_fields_only` negative-control behavior;
- canonical runner hash lock for `compile_state` and `build_final_prompt`;
- provider-purity gate or explicit OpenRouter robustness-only disposition;
- per-model supported-parameter/provider-policy snapshots;
- no prior rows for the target `experiment_id`.
