# Network/Transport Failure Classification And Recovery Policy

Status: OpenRouter execution-validity addendum for clean-v2 execution

Created: 2026-06-27

Scope: OpenRouter-mediated `openrouter_gpt55` and `openrouter_claude48`
execution only. This policy does not alter completed direct-provider slices and
does not delete or overwrite any first-pass attempt.

## Decision

OpenRouter transport failures are no longer treated as a single undifferentiated
`backend_error` bucket. Older packets are classified for diagnosis. Clean-v2
packets use the same taxonomy but halt immediately when a local transport-path
failure is detected before an HTTP provider response exists.

When an older attempt fails before provider contact with:

```text
URLError: Tunnel connection failed: 503 Service Unavailable
http_status: None
```

the failure is classified as:

```text
confirmed_local_transport_path_failure
```

This is a local execution-infrastructure failure. It is not a model-output
failure and must not be counted as evidence that the model produced an invalid
answer.

## Failure Classes

| class | evidence | recovery eligible |
| --- | --- | --- |
| `confirmed_local_transport_path_failure` | `Tunnel connection failed: 503 Service Unavailable`, no HTTP status, no valid provider response | Yes, if no valid parsed/scored final output was received |
| `network_suspect_infra_failure` | empty content or `http_status: None`, but the old runner did not preserve the intermediate exception message | Yes only if no valid parsed/scored final output was received; otherwise locked as diagnostic evidence |
| `provider_http_error` | OpenRouter/provider returned an HTTP error such as `429`, `502`, `503`, or `504` with an HTTP response | Yes only if no valid parsed/scored final output was received; report as provider-infrastructure recovery |
| `model_output_failure` | malformed JSON, parser failure over a complete model output, answer failure, governance failure, or boundary violation | No |

The key boundary is response validity. A row is not recovery-eligible merely
because its answer or governance score is bad.

## Current Evidence

The frozen first-pass OpenRouter evidence supports the following scoped
classification:

| condition | first-pass rows inspected | backend-error rows | confirmed local transport-path failures | network-suspect / unclassified infra | strict row-recovery eligible |
| --- | ---: | ---: | ---: | ---: | ---: |
| `openrouter_claude48` | 128 | 14 | 14 | 0 | 14 |
| `openrouter_gpt55` | 395 | 80 | 40 | 40 | 34 |

For Claude, all 14 backend-error rows include the explicit tunnel-failure
message. For GPT, 40 rows include the explicit tunnel-failure message. The other
40 GPT backend rows show empty intermediate state-update content or
`http_status: None`, but the old runner did not preserve the full intermediate
transport exception message. They are therefore classified only as
`network_suspect_infra_failure`, not as confirmed local transport-path failures.
Under the strict row-level recovery rule, only rows without a valid
parsed/scored final output are recovery targets: `34` GPT rows and `14` Claude
rows in the current first-pass packets.

## Recovery Rule

For older diagnostic packets, targeted recovery may be run only for rows that
meet all of these conditions:

- the original attempt is preserved append-only;
- no valid parsed/scored final model output was received for the row;
- the row is classified as `confirmed_local_transport_path_failure`,
  `network_suspect_infra_failure`, or `provider_http_error`;
- the recovery attempt uses the same task, method, budget, run id, prompt
  builder, scorer, parser, model condition, and provider route unless a separate
  protocol revision says otherwise;
- the recovered row carries a recovery annotation.

Rows with valid model outputs are locked. Malformed complete outputs, parser
failures over complete outputs, answer failures, governance failures, and
boundary violations are not eligible for network recovery.

If an intermediate state-update call failed but the row still produced a valid
parsed/scored final output, the row is retained as first-pass diagnostic
evidence rather than silently rerun. A later protocol may analyze such rows
separately, but they are not part of the strict network-recovery target set.

For clean-v2 GPT/Claude, this policy does not authorize automatic recovery
inside the same packet. A local transport-path failure halts the packet first.
Any later continuation must be separately documented and must resume only from
clean-v2 rows already written in the clean-v2 namespace.

Multiple pending/start/continuation events are allowed for OpenRouter-mediated
GPT/Claude only when they arise from documented execution-infrastructure
recovery. They are not hidden or collapsed into a single clean first attempt.
Every packet must preserve its own attempt records, and recovered rows must
carry enough metadata to link the recovery to the frozen failed attempt.

This policy does not define an end-to-end deployability metric. Confirmed local
transport-path failures are execution-site-specific operator-environment events,
not model behavior. They are not assumed to represent the usual model stability
or deployment availability seen by most users. They are therefore reported
outside the model/method endpoint rather than folded into a combined success
rate that multiplies model success by a provider or transport failure rate.

## Runtime Guard

Future clean-v2 OpenRouter runs must stop immediately when the runner detects a
pre-HTTP local transport-path failure. The main runner writes a
`LOCAL_TRANSPORT_PATH_FAILURE_HALT.*.json` sidecar and stops submitting
additional rows. The halt sidecar records the row id, failure class, exception
type, sanitized exception message, message hash, attempts observed before the
halt, the retry policy, in-flight rows, and queued rows not submitted.

This guard prevents a local network/transport-path outage from being silently
aggregated into model/provider backend-error rates.

With max-workers `10`, a small number of rows may already be in flight when the
first halt-triggering failure is observed. These in-flight row ids are listed in
the halt sidecar. The halt rule means no new rows are submitted after the first
observed local transport-path failure.

## Reporting Rule

Reports must distinguish:

- first-pass valid model outputs;
- confirmed local transport-path failures;
- network-suspect infra failures;
- provider HTTP errors;
- model-output failures.

Recovered rows must not be described as clean first-attempt rows. They should be
reported as targeted execution-infrastructure recovery.
