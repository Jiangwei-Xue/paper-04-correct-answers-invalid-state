# PCG Dynamic-State v2 Method Condition Protocols v2

Date: 2026-06-23

Status: method-condition protocol patch for the PCG dynamic-state v2 six-method
matrix. This file freezes method identities at the protocol level. It does not
run a model.

## Shared Boundary

All methods may use only model-visible task content and prior model-visible
state. No method may read scorer-only oracle fields, hidden answers,
required/forbidden arrays, protected tokens, raw scoring metadata, or external
context while constructing prompts or state.

## Methods

### `loop_only`

Current-segment loop-check baseline. It does not preserve prior-segment details
unless they appear in the current segment. It is expected to expose the legacy
no-conflict governance hole when answer-bearing state is absent.

### `rolling_summary`

Natural-language rolling-summary baseline. It has no deterministic visible
carry and no SSR fields.

### `rolling_visible_carry_forward`

Natural-language rolling-summary base plus deterministic `VISIBLE_KEEP` carry
from model-visible candidates. This is the visible-carry mechanism baseline.

### `rolling_visible_fields_only`

Mechanical-field negative control. The runner replaces broad notes with compact
deterministic visible fields:

- `VISIBLE_KEEP`
- `VISIBLE_ALLOWED_SCOPE`
- `VISIBLE_BOUNDARY`
- `VISIBLE_NOTE`

Only `VISIBLE_KEEP` and `VISIBLE_ALLOWED_SCOPE` are output-bearing. Boundary and
note fields are diagnostic. This arm tests whether mechanical surface presence
alone is sufficient; it must be labeled negative control in tables and text.

### `ssr_no_visible_carry`

SSR schema without deterministic visible carry. The canonical 2026-06-22
contract is:

- state fields: `OUT`, `ALW`, `NO`, `B`, `G`, `N`, `CK`;
- `final_answer.required_tokens` may derive only from `OUT`;
- `final_answer.allowed_paths` may derive only from `ALW`;
- `NO` and `B` may record generic exclusion categories but must not seed final
  output.

This method must not be described only as an alias to legacy `ssr_only`.

### `mature_ssr_loop`

SSR schema plus deterministic visible-carry support. The canonical 2026-06-22
contract is:

- state fields: `OUT`, `ALW`, `NO`, `B`, `G`, `N`, `CK`, `LOOP`;
- `final_answer.required_tokens` may derive only from `OUT`;
- `final_answer.allowed_paths` may derive only from `ALW`;
- `NO`, `B`, `G`, `N`, `CK`, and `LOOP` are not output-bearing fields.

This method must not be described only as an alias to legacy `ssr_loop`.

## Implementation Evidence Required

Before any API row enters a main matrix or admission packet, the run packet must
record:

- runner path and SHA-256;
- parser path and SHA-256;
- strict scorer path and SHA-256;
- base scorer path and SHA-256 when imported by the strict scorer;
- method list hash;
- `compile_state`/`build_final_prompt` contract audit;
- static sanity result for mature SSR;
- negative-control sanity result for `rolling_visible_fields_only`.
