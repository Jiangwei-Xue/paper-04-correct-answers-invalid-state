# OpenRouter Post-Pause Runtime Hardening

Status: clean-v2 execution-control addendum for future OpenRouter calls

Created: 2026-06-27

Scope: `openrouter_gpt55` and `openrouter_claude48` clean-v2 execution only.
This document does not apply to completed DeepSeek, Qwen, or Kimi slices, and
it does not alter any existing output row.

## Decision

After the OpenRouter-mediated GPT and Claude slices showed backend-error
clustering during full-scale execution, the OpenRouter primary slices are
restarted from row zero under a clean-v2 namespace. Clean-v2 calls must use an
explicit runtime-hardening mode. The hardening mode is an execution-control
patch, not a new method arm and not a model condition.

The runner now exposes this mode as:

```bash
python3 artifact/verification/run_main_matrix_model_slice.py \
  --model-condition openrouter_gpt55 \
  --role confirmatory \
  --max-workers 10 \
  --openrouter-runtime-hardening \
  --out-root artifact/results/main_matrix/record_mode_20260627/OPENROUTER_GPT_CLAUDE_CLEAN_V2_FROM_ZERO_20260627
```

The flag is opt-in. Ordinary first-attempt rows and existing recorded outputs
are not rewritten.

## What The Hardening Changes

When `--openrouter-runtime-hardening` is enabled for an OpenRouter model
condition, the runner applies these controls to future requests:

| control | value |
| --- | --- |
| provider order | `["openai"]` for `openrouter_gpt55`; `["anthropic"]` for `openrouter_claude48` |
| provider fallback | `allow_fallbacks: false` |
| provider parameter support | `require_parameters: true` |
| context compression | `plugins: [{"id": "context-compression", "enabled": false}]` |
| routing metadata header | `X-OpenRouter-Metadata: enabled` |
| retry policy | bounded backoff over HTTP `408`, `429`, `500`, `502`, `503`, `504` |
| local transport-path guard | halt the OpenRouter slice on the first pre-HTTP local transport failure |

The retry policy is:

```json
{
  "policy_id": "openrouter_post_pause_bounded_backoff_20260627",
  "max_transport_attempts": 5,
  "retryable_http_statuses": [408, 429, 500, 502, 503, 504],
  "backoff_seconds": [2.0, 4.0, 8.0, 16.0],
  "respect_retry_after": true,
  "max_sleep_seconds": 180.0
}
```

The main-matrix runner also refuses this mode unless:

```text
max_workers <= 10
submission_interval_seconds >= 0
provider_call_interval_seconds >= 0
```

The local transport-path guard is deliberately stricter than the bounded backend
retry policy. If an OpenRouter call fails before an HTTP provider response exists
with a local transport exception, the runner records the failure class,
exception type, sanitized exception message, message hash, attempt metadata,
and pacing metadata, writes a `LOCAL_TRANSPORT_PATH_FAILURE_HALT.*.json`
sidecar, stops submitting new rows, and returns a non-zero exit code. This
prevents a local network/transport-path outage from being silently mixed into
model/provider backend-error rates.

Because max-workers is `10`, there may already be in-flight rows at the moment
the first transport failure is detected. The halt rule stops new submissions and
records in-flight row ids; it does not claim to hard-kill already submitted
Python worker threads.

## Why This Is A Runtime Control, Not A Result Filter

The observed backend-error pattern is consistent with provider-side capacity,
rate-limit, or gateway-protection behavior, but the artifact does not claim to
prove a specific upstream token-bucket implementation. The supported claim is
narrower:

- admission-scale checks did not expose the OpenRouter/GPT and OpenRouter/Claude
  backend-error clustering;
- full-scale execution exposed provider-path heterogeneity;
- all first-pass evidence was frozen append-only;
- valid model outputs are locked and are not replaced;
- local transport-path failures stop the clean-v2 packet instead of being
  silently retried;
- answer failures, governance failures, and complete malformed model outputs
  are not made retry-eligible just because their outcomes are unfavorable.

This is a conservative execution-management response to infrastructure
heterogeneity. It is not an ex post outcome filter.

The hardened mode may create multiple OpenRouter execution packets for the same
model condition because a slice can be paused, halted, and later continued
under a documented execution-management rule. That packet structure is expected.
The audit requirement is not "one uninterrupted run"; it is append-only
preservation of all attempts, explicit continuation linkage, and no replacement
of valid model outputs.

The main endpoint remains model-output behavior under the frozen experimental
conditions. Local network/transport-path failures are reported as
execution-site infrastructure and are not used as evidence about typical model
stability, deployability, or end-to-end provider availability for most users.

## Official Documentation Basis

OpenRouter's provider-routing documentation defines the request-body
`provider` object, including `order`, `allow_fallbacks`, `require_parameters`,
and `only`. It also states that setting `order` disables default load balancing.

OpenRouter's message-transform documentation defines the context-compression
plugin and states that default context compression can be disabled with:

```json
{"plugins": [{"id": "context-compression", "enabled": false}]}
```

OpenRouter's errors documentation lists `408`, `429`, `502`, and `503` as
request/provider error categories and says `429` and `503` responses may include
the standard `Retry-After` header. OpenRouter's limits documentation also states
that limits can vary by model and that capacity is governed globally.

Documentation URLs:

- `https://openrouter.ai/docs/guides/routing/provider-selection.md`
- `https://openrouter.ai/docs/guides/features/message-transforms.md`
- `https://openrouter.ai/docs/api/reference/errors-and-debugging.md`
- `https://openrouter.ai/docs/api/reference/limits.md`

## Audit Requirements

Every hardened OpenRouter packet must preserve:

- the original row id and task/method/budget/run identity;
- the actual request payload hash for every provider call;
- the runtime-control override sidecar:
  `OPENROUTER_RUNTIME_HARDENING_EFFECTIVE_CONTROLS.json`;
- the retry policy id and retry policy hash;
- per-call attempt count, HTTP statuses, `Retry-After` values when present, and
  planned retry sleeps;
- provider-call pacing metadata for every attempt, including whether pacing was
  enabled, the configured interval, and the observed pre-call wait;
- local transport-path failure classes, exception types, sanitized attempt
  messages, and message hashes when transport failures occur;
- halt sidecars for any `confirmed_local_transport_path_failure`;
- raw response hashes and VCR record/replay/audit closure;
- the statement that hardened execution does not modify already recorded rows.

Rows produced under this mode are clean-v2 OpenRouter rows only if they are
created inside the clean-v2 namespace and pass VCR record/replay/audit closure.
Earlier GPT/Claude attempts remain diagnostic evidence and are not pooled into
clean-v2 primary results.

Later boundary note: this hardening document remains valid as historical
OpenRouter runtime-control evidence. The final primary execution boundary was
later widened to all-model v2 direct-network from row zero in
`V2_DIRECT_NETWORK_EXECUTION_PROTOCOL_20260628.md`.
