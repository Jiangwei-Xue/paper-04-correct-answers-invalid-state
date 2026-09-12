# OpenRouter Variable Control

Date: 2026-06-26

This note records the OpenRouter-specific variable controls for the frozen PCG
dynamic-state v2 main-matrix admission path. It is a post-freeze documentation
addendum. It does not change the matrix axes, method definitions, or primary
aggregation rules.

## Status

OpenRouter is not an experimental treatment. It is the fixed access path for
two closed-model conditions in the model axis:

| model condition | requested model | expected returned model | route |
| --- | --- | --- | --- |
| `openrouter_gpt55` | `openai/gpt-5.5` | `openai/gpt-5.5-20260423` | OpenRouter to OpenAI |
| `openrouter_claude48` | `anthropic/claude-opus-4.8` | `anthropic/claude-4.8-opus-20260528` | OpenRouter to Anthropic |

The main matrix must not be interpreted as an OpenRouter-versus-official-API
comparison. Provider route is a frozen control inside each model condition.

## Frozen Request Controls

For both OpenRouter-routed model conditions:

- base URL: `https://openrouter.ai/api/v1`;
- endpoint family: chat completions;
- API key variable: `OPENROUTER_API_KEY`;
- `max_tokens: 4096`;
- `stream: false`;
- `temperature`: omitted by design, not filled with an implicit local default;
- `provider.allow_fallbacks: false`;
- `reasoning: {"effort": "none"}`;
- tools disabled;
- web disabled;
- cache not requested;
- request timeout: `120` seconds;
- frozen live-adapter concurrency: global `10`, not 10 per provider;
- transport attempts: at most two attempts under the main-run API policy.

These controls are inherited from
`PROVIDER_SUPPORTED_PARAMETER_SNAPSHOT_20260625.json`,
`VARIABLE_FREEZE_SPEC_20260625.yaml`, and `MAIN_RUN_API_POLICY.md`.

## Hard Admission Checks

An OpenRouter-routed row is not admissible if any of the following occurs:

- the returned model string is missing;
- the returned model string differs from the expected exact model string;
- provider fallback occurs or cannot be shown disabled;
- a reasoning payload appears;
- reasoning tokens are nonzero;
- tool or web access is enabled;
- request payload hash, logical request hash, raw response hash, or score-row
  hash is missing;
- the scorer or parser fails to emit a structured score row;
- VCR `record`, `replay`, or `audit` fails;
- replay has any cache miss.

These are engineering and audit gates, not outcome filters. Low
`answer_success`, `state_governance_success`, or `reliable_composite_success`
is a measured outcome and must not be used to admit or exclude a model.

## Metadata Handling

OpenRouter `/generation` metadata is useful when available, but an error body is
not evidence that generation metadata is present. The frozen provider snapshot
therefore sets:

```text
openrouter_generation_error_body_counts_as_metadata_present: false
```

If generation metadata is unavailable with an error response, the raw error hash
may be preserved as audit evidence, but the row must not claim that metadata is
present.

Provider response identifiers such as `id` or `generation_id` are volatile
provider metadata. They may contain arbitrary base62 substrings. The admission
runner stores stable redacted digests for those identifier fields so accidental
matches against local anonymity patterns do not block archive construction. This
redaction applies to provider identifier fields only; it does not rewrite model
answer content.

## Historical Admission Evidence

This addendum records pre-execution admission evidence for the OpenRouter model
conditions. As of this addendum:

| model condition | benchmark smoke status | boundary |
| --- | --- | --- |
| `openrouter_gpt55` | `ADMIT_MODEL` | 12/12 confirmatory parse+score, hard failures 0, reasoning payload 0, returned-model match 12/12 |
| `openrouter_claude48` | `ADMIT_MODEL` | 12/12 confirmatory parse+score, hard failures 0, reasoning payload 0, returned-model match 12/12 |

The full five-model benchmark smoke was complete. The historical matrix gate was
`READY_FOR_MAIN_RECORD_MODE`, which authorized record-mode execution under the
frozen protocol but did not create primary result rows.

## Method-Axis Boundary

OpenRouter does not define or modify any method condition. The method axis
remains exactly:

- `loop_only`;
- `rolling_summary`;
- `rolling_visible_carry_forward`;
- `rolling_visible_fields_only`;
- `ssr_no_visible_carry`;
- `mature_ssr_loop`.

Any OpenRouter-specific effect is treated as provider-route provenance and
admission metadata, not as a mechanism factor or method arm.
