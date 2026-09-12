# Method Conditions

The final PCG dynamic-state v2 main matrix uses six method conditions:

- `loop_only`
- `rolling_summary`
- `rolling_visible_carry_forward`
- `rolling_visible_fields_only`
- `ssr_no_visible_carry`
- `mature_ssr_loop`

Provider route is not a method condition. OpenRouter routing for GPT/Claude is
handled as model-axis provenance and variable control, not as a mechanism arm.

## Shared Boundary

All methods may use only model-visible task content and prior model-visible
state. No method may read scorer-only oracle fields, hidden answers,
required-token arrays, forbidden-token arrays, protected-token arrays, raw
scoring metadata, or external context while constructing prompts or state.

## Two-By-Two Mechanism Core

The core mechanism comparison separates schema from deterministic visible
carry-forward:

| | no schema | schema |
|---|---|---|
| no deterministic visible carry | `rolling_summary` | `ssr_no_visible_carry` |
| deterministic visible carry | `rolling_visible_carry_forward` | `mature_ssr_loop` |

This design supports three estimands:

- carry main effect;
- schema main effect;
- schema-by-carry interaction.

These are mechanism-attribution estimands for reliable co-success. They should
not be used to frame the paper as an SSR method paper. SSR appears here as one
typed-schema factor level and as a diagnostic ablation case.

## Reference And Control Arms

`loop_only`

Current-segment loop-check baseline. It does not preserve prior-segment details
unless they appear in the current segment. It is a floor and empty-governance
diagnostic, not a competitive method candidate. Its role is to expose why a
no-conflict-only governance metric is insufficient: a method can look clean by
carrying little or no output-bearing state while still failing answer recovery.
Under the strict scorer, absent output-bearing carry fails
`state_governance_success`.

`rolling_visible_fields_only`

Mechanical-field negative control. The runner replaces broad notes with compact
deterministic visible fields:

- `VISIBLE_KEEP`
- `VISIBLE_ALLOWED_SCOPE`
- `VISIBLE_BOUNDARY`
- `VISIBLE_NOTE`

Only `VISIBLE_KEEP` and `VISIBLE_ALLOWED_SCOPE` are output-bearing. Boundary
and note fields are diagnostic. This arm tests whether mechanical carry surface
alone is sufficient and must be labeled as a negative control in tables and
text.

## SSR Conditions

`ssr_no_visible_carry`

SSR schema without deterministic visible carry. The canonical contract uses
`OUT`, `ALW`, `NO`, `B`, `G`, `N`, and `CK`; final-answer required tokens may
derive only from `OUT`, and allowed paths may derive only from `ALW`.

`mature_ssr_loop`

SSR schema plus deterministic visible-carry support. The canonical contract
uses `OUT`, `ALW`, `NO`, `B`, `G`, `N`, `CK`, and `LOOP`; final-answer required
tokens may derive only from `OUT`, and allowed paths may derive only from
`ALW`. `NO`, `B`, `G`, `N`, `CK`, and `LOOP` are diagnostic or exclusion fields
and must not seed output-bearing final answers.

## Downgrade Boundary

The 2026-06-23 downgrade evidence supports treating `mature_ssr_loop` as an
ablation and diagnostic condition, not as a primary advantage-seeking SSR arm.
The paper should not use this evidence to claim that SSR methods universally
fail.
