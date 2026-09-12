# Variable Control

Main-matrix interpretation depends on keeping matrix axes separate from frozen
controls.

## Matrix Axes

- task id;
- model endpoint;
- method condition;
- confirmatory budget level;
- repeat id.

The method axis is exactly:

- `loop_only`;
- `rolling_summary`;
- `rolling_visible_carry_forward`;
- `rolling_visible_fields_only`;
- `ssr_no_visible_carry`;
- `mature_ssr_loop`.

The confirmatory budget axis is exactly:

- `600`;
- `1200`.

Budget `300` is a separate low-budget diagnostic probe. It must be analyzed
descriptively for floor-effect, truncation, and carry-failure behavior, not
pooled into confirmatory inference.

The evidence basis is recorded in `BUDGET_300_DIAGNOSTIC_DISPOSITION.md`.

## Frozen Controls

The following should be fixed or logged before primary execution:

- task manifest and task split;
- scorer oracle manifest;
- prompt templates;
- provider route configuration;
- request payload construction;
- retry, timeout, concurrency, rate-limit, cache, and missingness policy;
- decoding parameters;
- scorer code;
- scorer metric contract: `reliable_composite_success` is primary,
  `answer_success` and strict `state_governance_success` are paired
  decomposition metrics, and standalone governance is diagnostic only;
- paper framing contract: the primary empirical target is reliable co-success,
  with SSR treated as a mechanism/diagnostic arm rather than a proposed method;
- statistical analysis plan: primary confirmatory inference uses design-based
  paired risk differences with task-cluster bootstrap confidence intervals;
- parser code;
- hash-manifest schema;
- aggregation scripts;
- local verification environment.

OpenRouter-specific provider-route controls are recorded in
`admission/OPENROUTER_VARIABLE_CONTROL_20260626.md`. They do not add a new
matrix axis. For GPT/Claude conditions, OpenRouter is a frozen access path with
fallback disabled, tools/web disabled, reasoning disabled by
`reasoning.effort = none`, returned-model exact matching, and temperature
omitted by design.

## Disallowed Pooling

Do not pool into the primary matrix:

- historical calibration runs;
- admission or triage probes;
- static sanity rows;
- targeted backfills used only to close evidence-packet missingness;
- low-budget `300` diagnostic probe rows;
- sentinel drift probes;
- direct-provider and routed-provider runs unless route equivalence was frozen
  before the run.

## Closed-Model Boundary

Closed-model weights, backend versions, provider routing, and server-side
decoding details cannot be frozen locally. The artifact therefore freezes the
request-side inputs, observed outputs, metadata, scorers, and hash chain.
