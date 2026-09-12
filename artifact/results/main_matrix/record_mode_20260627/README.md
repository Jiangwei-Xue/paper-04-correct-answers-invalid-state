# Record-Mode Main-Matrix Runs 2026-06-27

This directory stores live record-mode batches for the frozen PCG dynamic-state
v2 main matrix.

Current contents:

| model condition | role | status | rows | replay closure |
| --- | --- | --- | ---: | --- |
| `deepseek_v4pro` | `confirmatory_primary` | `COMPLETE` | 1,440 | VCR audit passed, cache miss 0 |
| `qwen37max` | `confirmatory_primary` | `COMPLETE` | 1,440 | VCR audit passed, cache miss 0 |
| `kimi_k26` | `confirmatory_primary` | `COMPLETE` | 1,440 | VCR audit passed, cache miss 0 |
| `openrouter_gpt55` | `diagnostic first-pass partial` | `PAUSED` | 395 attempted / 1,440 planned | pause packet frozen |
| `openrouter_claude48` | `diagnostic first-pass partial` | `PAUSED` | 128 attempted / 1,440 planned | pause packet frozen |
| `openrouter_gpt55` | `clean-v2 transition slice` | `COMPLETE` | 1,440 | VCR audit passed, cache miss 0 |
| `openrouter_claude48` | `clean-v2 transition slice` | `COMPLETE` | 1,440 | VCR audit passed, cache miss 0 |
| `deepseek_v4pro` | `all-model direct clean-v2 slice` | `COMPLETE` | 1,440 | VCR audit passed, cache miss 0 |
| `qwen37max` | `all-model direct clean-v2 slice` | `COMPLETE` | 1,440 | VCR audit passed, cache miss 0 |
| `kimi_k26` | `all-model direct clean-v2 slice` | `COMPLETE` | 1,440 | VCR audit passed, cache miss 0 |
| `openrouter_claude48` | `budget300 diagnostic sidecar` | `COMPLETE` | 160 | VCR audit passed, cache miss 0 |
| `openrouter_gpt55` | `budget300 diagnostic sidecar` | `COMPLETE` | 160 | VCR audit passed, cache miss 0 |
| `deepseek_v4pro` | `budget300 diagnostic sidecar` | `COMPLETE` | 160 | VCR audit passed, cache miss 0 |
| `qwen37max` | `budget300 diagnostic sidecar` | `COMPLETE` | 160 | VCR audit passed, cache miss 0 |
| `kimi_k26` | `budget300 diagnostic sidecar` | `COMPLETE` | 160 | VCR audit passed, cache miss 0 |

Clean-v2 execution closure:

```text
CLEAN_V2_MATRIX_EXECUTION_CLOSURE_20260629.md
CLEAN_V2_MATRIX_MODEL_STATUS_20260629.csv
```

Budget-300 diagnostic execution boundary:

```text
../../../protocol/main_matrix/BUDGET300_DIRECT_NETWORK_DIAGNOSTIC_PROTOCOL_20260629.md
```

The 800 budget-`300` rows are a separate v2 direct-network diagnostic probe.
The first completed sidecar slices are stored under:

```text
BUDGET300_DIAGNOSTIC_DIRECT_V2_20260629/
```

They must not enter:

- primary claim tables;
- confirmatory mixed-effects models;
- method ranking;
- overall method averages.

They should be used only for floor-effect, truncation, and carry-failure
diagnosis.

Budget-300 diagnostic execution closure:

```text
BUDGET300_DIAGNOSTIC_DIRECT_V2_20260629/BUDGET300_DIAGNOSTIC_DIRECT_V2_EXECUTION_CLOSURE_20260629.md
BUDGET300_DIAGNOSTIC_DIRECT_V2_20260629/BUDGET300_DIAGNOSTIC_DIRECT_V2_MODEL_STATUS_20260629.csv
```

This is not the completed full main matrix. These 2026-06-27 outputs are v1
record-mode audit evidence from the proxy-mediated execution environment.
Earlier OpenRouter GPT/Claude attempts remain append-only diagnostic evidence,
and the completed DeepSeek, Qwen, and Kimi v1 slices remain preserved with full
logs, cassettes, replay outputs, score rows, and hash manifests. The
OpenRouter clean-v2 GPT and Claude transition slices are also preserved
append-only and do not use earlier first-pass partial rows. The
`ALL_MODEL_DIRECT_CLEAN_V2_FROM_ZERO_20260628/` namespace contains the later
all-model v2 direct-network from-zero slices, including the completed DeepSeek
Qwen, and Kimi slices.

The earlier OpenRouter primary plan was clean-v2 from row zero:

```text
../../../protocol/main_matrix/OPENROUTER_GPT_CLAUDE_CLEAN_V2_FROM_ZERO_PROTOCOL_20260627.md
```

That plan is superseded for final primary aggregation by the all-model
v2 direct-network from-zero protocol:

```text
../../../protocol/main_matrix/V2_DIRECT_NETWORK_EXECUTION_PROTOCOL_20260628.md
```

The reason is that proxy-path instability was not exposed during admission and
therefore was not treated as a controlled v1 variable. Later review found
proxy/transport-like backend evidence in v1 logs, and the Claude direct-network
transition run produced 0 backend-error rows. The v2 direct-network protocol
therefore reruns all five model conditions from row zero under one execution
environment instead of pooling v1 proxy-mediated rows with v2 direct-network
rows.

Clean-v2 keeps max-workers `10`, uses explicit OpenRouter runtime controls, and
halts on the first detected pre-HTTP local transport-path failure. A halt writes
a `LOCAL_TRANSPORT_PATH_FAILURE_HALT.*.json` sidecar containing the row id,
failure class, exception type, sanitized exception message, message hash,
in-flight row ids, and queued rows not submitted.

The GPT first-pass pause packet is:

```text
EXECUTION_PAUSE_BACKEND_ERROR_HETEROGENEITY_20260627_101959/
```

The Claude first-pass pause packet is:

```text
CLAUDE_PAUSE_BACKEND_ERROR_GUARD_20260627_042947/
```

The OpenRouter network/transport failure classification packet is:

```text
NETWORK_TRANSPORT_FAILURE_CLASSIFICATION_20260627/
```

That classification packet explains why clean-v2 was introduced. It does not
modify canonical outputs and does not create primary result rows.

All admitted primary model conditions have completed under the v2
direct-network protocol and closed through VCR record/replay/audit. The next
layer is primary aggregation, statistical interpretation, and paper-level claim
tables; this directory by itself is execution closure, not final interpretation.
