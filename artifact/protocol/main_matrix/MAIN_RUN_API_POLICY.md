# Main-Run API Policy

This policy applies to live `record` execution for the 7,200-row confirmatory
matrix and the separate 800-row budget-300 diagnostic probe. It is
pre-execution protocol provenance, not a result table. At the five-model
benchmark-smoke admission gate, the decision was `READY_FOR_MAIN_RECORD_MODE`;
that historical gate authorized record-mode execution under the frozen controls
but did not create primary result rows.

## Frozen Request Controls

Each row must use the request controls frozen in the main-matrix config and
provider snapshot:

- `max_tokens: 4096`;
- `stream: false`;
- tools disabled;
- web disabled;
- provider fallback disabled;
- cache not requested;
- OpenRouter GPT/Claude: `reasoning: {"effort": "none"}`;
- direct-provider thinking controls disabled where the provider accepts that
  parameter;
- Moonshot Kimi: `kimi-k2.6` is the frozen Kimi condition because official Kimi
  documentation permits `thinking.type = "disabled"` for K2.6; Kimi K2.7 Code is
  outside the primary model axis because official documentation makes it a
  mandatory-thinking condition;
- temperature sent exactly as recorded by each model condition, including
  intentionally omitted temperature for GPT/Claude.

Omitted sampling parameters are not informal defaults. They are frozen by
`send_mode: omitted`, by the request payload hash, and by the logical request
hash. If a provider policy changes and requires an explicit replacement, the
matrix must be refrozen before live execution.

## Retry And Timeout

The live adapter must treat every row as an immutable request payload.

- `request_timeout_seconds: 120`;
- `max_transport_retries: 2`;
- retry reasons allowed: transport exception, timeout, HTTP `429`, and HTTP
  `5xx`;
- retry reasons not allowed: parse failure, scoring failure, answer failure,
  governance failure, or disliked content;
- retry payload mutation is prohibited;
- every attempt must be logged with timestamp, HTTP status or exception class,
  request payload hash, response/error hash when available, and retry index.

If all attempts fail, the row is emitted as a measured backend failure with its
attempt log. It must not be silently dropped.

## Concurrency And Rate Limits

The frozen live adapter concurrency is:

```text
max_concurrent_requests: 10
```

This is a global ceiling across the live adapter, not 10 requests per provider.
At most 10 provider requests may be in flight at the same time across the
current run. Provider-specific rate-limit waiting is allowed, but it must not
raise the global ceiling, change request payloads, or change row identity.

Any batching mode, provider-specific concurrency override, or larger concurrency
must be frozen before execution and must change the adapter/config hash.

Rate-limit behavior must not enable provider fallback. A rate-limited row either
retries under the retry policy above or becomes a logged backend failure.

## Cache And Replay

Live `record` execution must not read from an existing cassette to fill a row.
The cassette is created from explicit provider-adapter output after live
responses are obtained. Offline `replay` may read only the cassette and must
fail on cache miss.

No response cache, prompt cache, or hidden provider-side continuation may be used
as a substitute for a row-level recorded raw response. Provider-reported cache
usage may be preserved as metadata but does not decide cassette identity.

## Missingness And Backfill

Invalid JSON, parser failure, backend failure, timeout, and provider errors are
row outcomes. They must be preserved and included in missingness accounting.

Targeted reruns or backfills, if needed, are separate corrective actions. They
require their own config hash, raw-output hashes, scorer hashes, and H5/E5
manifest linkage, and they remain outside primary aggregation until explicitly
admitted by a post-run audit.

## V1 Proxy-Path And V2 Direct-Network Exception Handling

The frozen concurrency-10 policy passed admission as the canonical first-attempt
execution policy. During v1 record-mode execution on 2026-06-27, however, the
proxy-mediated execution environment produced backend/transport evidence that
was not exposed by admission smoke. The `openrouter_gpt55` condition showed a
high raw backend-error rate and execution was paused in an append-only packet
under:

```text
artifact/results/main_matrix/record_mode_20260627/EXECUTION_PAUSE_BACKEND_ERROR_HETEROGENEITY_20260627_101959/
```

Later the `openrouter_claude48` condition also triggered the backend-error guard
during continuous concurrency-10 execution. After a direct-network Claude
transition run produced 0 backend-error rows, the v1 Qwen/Kimi logs were also
reviewed and found to contain proxy/transport-like backend evidence for a subset
of rows.

The earlier OpenRouter-only primary boundary was clean-v2 from row zero:

```text
OPENROUTER_GPT_CLAUDE_CLEAN_V2_FROM_ZERO_PROTOCOL_20260627.md
```

The final primary boundary is now all-model v2 direct-network from row zero:

```text
V2_DIRECT_NETWORK_EXECUTION_PROTOCOL_20260628.md
```

The v1 outputs remain append-only diagnostic/audit evidence. This policy does
not allow v1 proxy-mediated rows to be mixed into v2 direct-network primary
results.
