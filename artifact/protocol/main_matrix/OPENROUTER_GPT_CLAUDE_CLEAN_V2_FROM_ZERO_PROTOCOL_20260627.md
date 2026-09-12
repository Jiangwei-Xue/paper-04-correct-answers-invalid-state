# OpenRouter GPT/Claude Clean V2 From-Zero Protocol

Status: protocol decision for future OpenRouter GPT/Claude record-mode
execution

Created: 2026-06-27

Supersession note: this document records the earlier OpenRouter-only clean-v2
decision. For final primary aggregation, it is superseded by the all-model
v2 direct-network from-zero protocol:

```text
artifact/protocol/main_matrix/V2_DIRECT_NETWORK_EXECUTION_PROTOCOL_20260628.md
```

Scope: `openrouter_gpt55` and `openrouter_claude48` only. This protocol does
not rerun DeepSeek, Qwen, or Kimi, and it does not delete, overwrite, or hide
any existing GPT/Claude first-pass, pause, canary, or recovery packet.

## Decision

The OpenRouter GPT and Claude primary slices should be restarted from row zero
under a new clean-v2 execution namespace instead of mixing earlier GPT/Claude
valid rows with later hardened-control rows.

The new namespace is:

```text
artifact/results/main_matrix/record_mode_20260627/OPENROUTER_GPT_CLAUDE_CLEAN_V2_FROM_ZERO_20260627/
```

The earlier OpenRouter GPT/Claude attempts remain append-only diagnostic
evidence about the execution environment. They are not deleted and are not
pooled into the clean-v2 primary slice.

## Rationale

The earlier OpenRouter GPT/Claude attempts are scientifically useful but not a
clean primary execution slice. They include admission-unseen backend-error
clustering, pause packets, local network/transport-path failure classification,
and runner hardening changes.

Those changes are execution controls rather than method variables, but mixing
old valid rows with later hardened-control rows would create a reviewer-facing
execution heterogeneity problem. A clean-v2 from-zero slice is
therefore cleaner than continuing the old GPT/Claude outputs into the primary
matrix.

At the time of this OpenRouter-only decision, the direct-provider DeepSeek,
Qwen, and Kimi slices were treated as canonical first-run slices. A later
all-model v2 direct-network decision widened the execution-environment control
after proxy/transport-like evidence was found in the v1 logs.

## Inclusion Rule

For `openrouter_gpt55` and `openrouter_claude48`, primary inclusion requires a
completed clean-v2 confirmatory slice:

```text
40 tasks x 6 methods x 2 budgets x 3 runs = 1,440 rows per model
```

The two OpenRouter models together therefore require:

```text
2 models x 1,440 rows = 2,880 clean-v2 confirmatory rows
```

The clean-v2 slice is eligible for primary aggregation only if:

- it starts from the frozen row manifest at row zero;
- it does not use old GPT/Claude adapter rows as completed rows;
- it uses the same task, method, budget, run, prompt, parser, scorer, and model
  condition definitions as the frozen main matrix;
- it uses the hardened OpenRouter runtime controls below for every row;
- it preserves raw outputs, adapter rows, score rows, VCR cassette, replay, and
  audit closure;
- any pause/halt/restart inside the clean-v2 namespace is retained append-only;
- no valid model output is replaced because its score is bad.

## Exclusion Rule For Earlier GPT/Claude Attempts

Earlier `openrouter_gpt55` and `openrouter_claude48` outputs remain audit
evidence only. This includes:

- first-pass partial GPT rows;
- first-pass partial Claude rows;
- pause packets, hard-stop packets, and network/transport classification
  packets.

These packets may be cited to explain why clean v2 was introduced. They must
not be combined with clean-v2 rows in the primary GPT/Claude result table.

## Runtime Controls

Clean-v2 OpenRouter GPT/Claude execution must use:

| control | value |
| --- | --- |
| max workers | `10` |
| row submission interval | `0` seconds unless an operator pauses between packets |
| provider-call interval | `0` seconds unless a later written protocol changes it |
| OpenRouter runtime hardening | enabled |
| provider order | `["openai"]` for GPT; `["anthropic"]` for Claude |
| fallback | disabled |
| `require_parameters` | true |
| context compression | disabled |
| metadata header | enabled |
| retry policy | bounded backoff over `408`, `429`, `500`, `502`, `503`, `504` |
| local transport-path guard | halt immediately on the first detected local transport-path failure |

If clean v2 hits a local transport-path failure before an HTTP provider response
exists, the runner must halt and write a
`LOCAL_TRANSPORT_PATH_FAILURE_HALT.*.json` sidecar. The sidecar must record the
row id, failure class, exception type, sanitized exception message, attempt
hashes, in-flight row ids, and queued rows not submitted. Do not continue the
slice until the halt packet is frozen and a continuation decision is written
inside the clean-v2 namespace.

Clean v2 is frozen at max-workers `10`. Do not silently lower the concurrency
inside the same run. Any later concurrency change requires a new protocol
decision and must preserve the max-workers-`10` halt evidence.

## Execution Shape

Clean v2 may be executed as one long run or as operational chunks. Chunking is
allowed only for scheduling and execution stability. It does not authorize use
of old GPT/Claude rows.

Because this execution site has already shown local network/transport
instability, clean v2 may enter `pending`, `start`, pause, halt, and continuation
states more than once. That is an allowed execution-management pattern, not a
result-selection mechanism. The requirement is that every transition is
append-only and auditable.

This is a site-scoped execution statement. It is not a claim that the same
failure mode is typical for OpenRouter, GPT, Claude, or most operators. The
artifact intentionally describes the issue at the network/transport-path level
and does not disclose operator-specific local network implementation details.

For repeated pending/continuation events:

- preserve each started packet, runner log, summary, and halt sidecar;
- do not overwrite or delete a failed packet after a later continuation
  succeeds;
- make the continuation point explicit: row count already written, row ids
  already completed inside the clean-v2 namespace, and rows still pending;
- resume only from clean-v2 adapter rows in the same output namespace;
- do not treat earlier first-pass GPT/Claude rows, canaries, or old recovery
  rows as completed clean-v2 rows;
- classify confirmed local transport-path failures as execution-site
  infrastructure, not model output;
- never retry a valid model output merely because the answer, governance state,
  or parser result is unfavorable.

For chunked execution:

- use the clean-v2 output root above;
- do not pass an old `--resume-source-adapter`;
- resume only from adapter rows already written inside the clean-v2 output
  root;
- keep every chunk log and summary in the clean-v2 packet;
- after the final chunk, run VCR record, replay, and audit over the completed
  clean-v2 slice.

## Commands

GPT clean-v2 confirmatory execution:

```bash
python3 artifact/verification/run_main_matrix_model_slice.py \
  --model-condition openrouter_gpt55 \
  --role confirmatory \
  --max-workers 10 \
  --openrouter-runtime-hardening \
  --out-root artifact/results/main_matrix/record_mode_20260627/OPENROUTER_GPT_CLAUDE_CLEAN_V2_FROM_ZERO_20260627
```

Claude clean-v2 confirmatory execution:

```bash
python3 artifact/verification/run_main_matrix_model_slice.py \
  --model-condition openrouter_claude48 \
  --role confirmatory \
  --max-workers 10 \
  --openrouter-runtime-hardening \
  --out-root artifact/results/main_matrix/record_mode_20260627/OPENROUTER_GPT_CLAUDE_CLEAN_V2_FROM_ZERO_20260627
```

For 100-row operational chunks, add:

```bash
--max-new-rows 100
```

Do not add `--resume-source-adapter` for clean v2. For the first clean-v2 chunk,
the output directory should not contain prior clean-v2 adapter rows. Later
chunks may resume from clean-v2 rows already written in the same output root.

## Budget-300 Diagnostic

The clean-v2 decision is primarily about the confirmatory GPT/Claude slices.
Budget `300` remains diagnostic and outside primary aggregation. If the
budget-`300` OpenRouter diagnostic probe is run later, it must use the same
clean-v2 output namespace and runtime controls, but it must be reported
separately from the `600`/`1200` confirmatory rows.

## Reporting Rule

The paper and artifact should report:

- DeepSeek/Qwen/Kimi direct-provider slices as their completed canonical
  first-run slices;
- GPT/Claude clean-v2 rows as the OpenRouter GPT/Claude primary rows only if
  clean-v2 completion and VCR audit closure succeed;
- earlier GPT/Claude attempts as execution-environment diagnostic evidence;
- local network/transport-path failures as execution-site infrastructure, not
  model behavior and not typical model deployability evidence.

The phrase "full main matrix" must not count old GPT/Claude first-pass rows and
clean-v2 GPT/Claude rows together.

## Current State

This document authorizes drafting and future clean-v2 execution. It does not
perform API calls, does not create clean-v2 result rows, and does not modify any
canonical output files.
