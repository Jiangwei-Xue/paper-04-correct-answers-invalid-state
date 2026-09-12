# Claude Next Execution Decision After GPT Provider-Path Pause

Status: operational execution decision, not a protocol redesign

Created: 2026-06-27

Scope: deciding whether the `openrouter_claude48` confirmatory model slice may
proceed while the `openrouter_gpt55` provider-path issue remains unresolved.

Later supersession note: this was an operational decision made before the
all-model v2 direct-network protocol. It remains historical audit evidence. The
current final primary boundary is:

```text
artifact/protocol/main_matrix/V2_DIRECT_NETWORK_EXECUTION_PROTOCOL_20260628.md
```

## Decision

Proceed with `openrouter_claude48` under the registered record-mode execution
policy:

```text
model_condition_id: openrouter_claude48
matrix_role: confirmatory_primary
planned_rows: 1440
max_concurrent_requests: 10
provider_route: OpenRouter to Anthropic/Claude
fallback_enabled: false
canonical_merge_with_gpt: none
```

This does not resolve the GPT/OpenRouter root cause. It only prevents the GPT
provider-path exception from blocking an independent frozen model condition.

## Rationale

The GPT pause established that the `openrouter_gpt55` path showed high
backend-error heterogeneity during formal execution that was not visible at
admission scale. Root-cause attribution remains unresolved. The available
evidence cannot cleanly distinguish among OpenRouter gateway behavior,
OpenRouter-to-upstream routing, OpenAI/GPT backend availability, and transient
time-window effects.

The Claude slice should therefore be treated as a separate model condition, not
as a fix for GPT and not as a root-cause experiment. Running Claude next is
methodologically acceptable because:

- Claude already passed the frozen admission smoke;
- Claude has its own model condition and row manifest;
- the registered main-run policy still uses a 10-request global live-adapter
  ceiling unless a provider-specific exception is documented;
- at that time, completed DeepSeek, Qwen, and Kimi slices were treated as
  canonical;
- GPT remains paused and is not silently repaired, rerun, or merged while
  Claude runs.

## Guardrail For Claude

Claude may start at the registered 10-concurrency setting, but the operator must
monitor backend-error behavior before treating the slice as routine.

Pause Claude execution and create an append-only pause packet if either
condition is met:

- the first 100 attempted Claude rows exceed 10% raw backend-error rate;
- any later rolling 100-row window exceeds 10% raw backend-error rate.

If a Claude pause is triggered, do not retry failed rows inline. Freeze the
attempts first, summarize backend-error distribution by method/budget/task
family, and document whether the issue appears shared with GPT/OpenRouter or
specific to the Claude route.

Backend/API failures remain separate from answer failures, governance failures,
parse failures from complete model outputs, and reliable-composite failures.

## Boundary

This decision does not:

- replace GPT recovery policy;
- authorize any GPT retry before the Claude slice finishes;
- change prompts, method conditions, budgets, scorer, parser, task set, or
  statistical analysis plan;
- authorize a global rerun of completed model slices;
- treat Claude behavior as proof of GPT root cause.

If Claude completes cleanly at 10 concurrency, the GPT problem remains a
provider-path exception requiring separate GPT recovery handling. If Claude also
shows high backend-error rates at 10 concurrency, the artifact should treat the
problem as potentially shared OpenRouter/runtime instability and pause before
any further OpenRouter-routed full-slice execution.

## Reviewer-Facing Wording

After the GPT/OpenRouter slice showed admission-unseen backend-error
heterogeneity under the registered 10-concurrency policy, we froze the GPT
partial execution and did not infer a single root cause. Because the Claude
condition is a separate frozen model condition that had passed admission, we
allowed it to proceed under the registered 10-concurrency execution policy with
an explicit backend-error pause rule. GPT recovery was deferred until after the
Claude slice, and no GPT valid-output rows were rerun or replaced during the
Claude execution decision.
