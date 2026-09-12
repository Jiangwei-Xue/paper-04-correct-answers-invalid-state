# Qwen3-Coder Open-Weight Supplemental Protocol

Date: 2026-06-29

Status: protocol for an open-weight supplemental experiment, not a sixth
primary model condition.

## Decision

We add one open-weight, open-licensed model experiment to improve
reproducibility. The primary matrix remains the five frozen model conditions
defined in `FINAL_MAIN_MATRIX_DEFINITION.md`; this supplement is reported
separately.

The selected model route is:

```text
requested model: qwen/qwen3-coder
expected returned model: qwen/qwen3-coder-480b-a35b-07-25
provider: Alibaba
provider tag: alibaba/opensource
fallback: disabled
```

This experiment does not enter the five-model primary claim table,
confirmatory mixed-effects models, method ranking, overall method/model
averages, or abstract-level claims. Its role is narrower: it asks whether the
same output-contract and state-governance measurements remain interpretable on
a high-capability open-weight coder under the closest feasible subset of the
clean-v2 controls.

## Why Add An Open-Weight Model

Closed-model API experiments can freeze request payloads, route policies,
metadata capture, parser/scorer code, VCR replay, and hash manifests. They
cannot freeze closed weights or provider-internal serving revisions. An
open-weight supplemental model gives reviewers a second kind of evidence: a
model whose license and model card are public, and whose route can be described
without treating the vendor model itself as a black box.

This does not make the supplement identical to the closed-model matrix. It
does make the reproducibility boundary clearer. The comparison is therefore
reported as an open-weight supplement, not as a primary matrix expansion.

## Why Qwen3-Coder-480B

Qwen3-Coder-480B-A35B-Instruct is the best fit for this supplement for four
reasons.

First, the model is open-weight and Apache-2.0 licensed. The Hugging Face model
card lists `license: apache-2.0` and links to the model license. That makes the
license boundary cleaner than Llama-family or Gemma-family alternatives, whose
terms are not the same as Apache/MIT-style open licenses.

Second, it is a high-capability coder. The model card describes the released
variant as a 480B-total, 35B-activated MoE coder with a native 262,144-token
context. A smaller open-weight coder can be useful, but Qwen3-Coder-480B is a
stronger robustness check: poor output-contract behavior would be harder to
explain away as merely a small-model limitation.

Third, the reasoning boundary is closer to the main matrix. The model card
states that this model supports only non-thinking mode and does not generate
`<think></think>` blocks. Current OpenRouter endpoint metadata for
`qwen/qwen3-coder` lists seven providers; none expose `reasoning`,
`reasoning_effort`, or `include_reasoning` in `supported_parameters`. The
selected Alibaba route exposes ordinary generation controls and tool/format
capabilities, not a separate reasoning-budget interface.

Fourth, it is a code model. The benchmark evaluates strict output-contract
compliance and state-governance reliability under code-like state transfer
tasks. A general open-weight chat model would be less aligned with that task
shape.

## Non-Selected Open-Weight Candidates

The supplement does not give special reporting status to every open-weight
candidate we considered. Non-selected candidates are treated as candidate
disposition, not as standalone results.

`qwen/qwen-2.5-coder-32b-instruct` is one such candidate. It remains relevant as
an Apache-2.0 coder model, but it is not the selected supplement. An attempted
32B run is retained only in private audit archives and is not included in the
paper or submitted artifact. The reason is a post-run reasoning-control
disposition: the route did not expose an explicit reasoning-off control, so the
audit could not exclude the risk that the run was affected by hidden or
provider-side reasoning behavior to the same standard used for the five primary
model conditions and the Qwen3-Coder-480B supplement. Its outcomes are therefore
not reported, summarized, or used for model comparison. This is a variable-
control exclusion, not an outcome-based selection rule.

DeepSeek R1, Qwen3 Thinking, gpt-oss, and Nemotron-style reasoning models are
not the right default for this supplement. They are useful if the question is a
separate reasoning-on diagnostic. That is not the question here. The main
matrix is a no-explicit-reasoning output-contract benchmark. Adding a model
whose route exposes or enforces reasoning would introduce a new model-policy
variable.

Mistral Small, Llama, and Gemma-family models remain plausible background
alternatives, but they are weaker choices for this exact supplement. Mistral
Small is smaller and less code-specialized. Llama and Gemma have more complex
license terms than Apache-2.0. None gives the same combination of high-capacity
coder specialization, open license, and documented non-thinking output mode.

## Matrix Boundary

The supplement reuses the task, method, budget, parser, scorer, VCR, and hash
discipline of clean-v2 wherever feasible:

- same 40 PCG dynamic-state v2 tasks;
- same six confirmatory method conditions;
- same confirmatory budgets, `600` and `1200`;
- same three repeats per confirmatory cell;
- same separate budget-`300` diagnostic role if the low-budget rows are run;
- same primary metric contract:
  `reliable_composite_success = answer_success AND state_governance_success`;
- same parser/scorer and missingness accounting;
- same VCR record/replay/audit closure;
- same row-level hash-manifest requirement.

The supplement still remains outside primary aggregation because model family,
provider route, open-weight serving metadata, and endpoint capability surface
are not part of the frozen five-model matrix.

## Provider Route Policy

The selected OpenRouter route is the Alibaba `alibaba/opensource` endpoint.
This choice prioritizes source-proximity to the Qwen/Alibaba model ecosystem
over a third-party route that exposes a more explicit precision label. That is
a route-documentation judgment, not a claim that the Alibaba endpoint is the
strongest Qwen3-Coder serving path or that it uses the released weights at a
known original precision.

The endpoint snapshot reports `quantization=unknown`. That uncertainty is
retained rather than normalized away. The supplement therefore must not claim
that the route is original-precision, BF16/FP16, or superior to other
Qwen3-Coder routes such as WandB BF16, DeepInfra FP4, or other provider
implementations. It also must not treat the Alibaba route as equivalent to
self-hosting the released weights. Provider name and provider tag are recorded
route metadata; they do not expose the provider-internal serving stack, GPU
topology, batching policy, or numerical implementation details.

The reproducibility boundary is API/provider-route reproducibility. The run
records requested model id, expected returned model, provider name, provider
tag, quantization label, supported-parameter surface, fallback policy,
returned-model matching, VCR closure, and hash manifests. These fields define
the fixed route condition for this supplement.

This provider-route choice is a controlled execution condition, not a method
axis and not a source of primary-matrix eligibility. Downstream tables,
figures, and captions should label the route as Alibaba `alibaba/opensource`
with `quantization=unknown` when provider details are relevant. If future work
compares Alibaba with WandB BF16, DeepInfra FP4, or any other Qwen3-Coder
route, that comparison should be reported as a separate provider-route
sensitivity analysis rather than being folded into this supplement.

## Parameter Policy

The supplemental route should use:

```text
model: qwen/qwen3-coder
expected returned model: qwen/qwen3-coder-480b-a35b-07-25
provider: Alibaba
provider order: ["alibaba"]
fallback: disabled
require_parameters: true
temperature: 0
top_p: 1
top_k: not sent unless the selected route exposes it and the protocol is
       refrozen before the run
max_tokens: 4096
stream: false
tools/function calling: not requested
tool_choice: not requested
structured output forcing: not requested
response_format: not requested
web/retrieval/agent mode: not requested
context-compression plugin: disabled where applicable
provider tag and quantization: recorded
```

Transport handling follows the clean-v2 OpenRouter bounded-backoff policy. A
confirmed local transport-path failure is a hard halt because it indicates that
the execution path, not the model, is broken. Ordinary transient remote
disconnects or retryable HTTP failures are retried under the frozen bounded
policy rather than being counted as model behavior.

The production run is executed on a remote direct-network host through a
detached process. The process clears `HTTP_PROXY`, `HTTPS_PROXY`, and
`ALL_PROXY`, sets `NO_PROXY=*`, and disables Python `urllib` proxy discovery
before endpoint snapshotting or model calls. After launch, the experiment must
not depend on the local workstation terminal, local proxy state, or an active
SSH session. Local interaction is limited to log/status inspection and artifact
sync after completion.

The selected Alibaba route should be snapshotted before the run. The snapshot
must record provider name, provider tag, quantization, context length,
max-completion-token limit, and `supported_parameters`.

## Reasoning Controls

No explicit reasoning mode is requested.

The protocol records the Qwen3-Coder route as:

```text
reasoning controls not exposed; no reasoning mode requested
```

If a future selected provider route exposes `reasoning`,
`reasoning_effort`, or `include_reasoning`, the run must be refrozen before
execution. The replacement policy must either disable the reasoning channel in
the provider-supported syntax or exclude that route from the no-explicit-
reasoning supplement.

Tool use, function calling, retrieval, web access, agent mode, response-format
forcing, and structured-output forcing are not enabled. The experiment tests
output-contract compliance and state-governance reliability under a frozen
final-output protocol. It is not an agentic coding, retrieval, tool-use, or
visible-chain-of-thought evaluation.

Reason-token fields are metadata only. If the provider returns
`completion_tokens_details.reasoning_tokens` or an equivalent field, the value
is recorded. A zero value supports the no-returned-reasoning audit trail. It
does not expose hidden chain-of-thought, and it does not prove that the model
performed no internal computation. If a nonzero value or a returned
`message.reasoning` payload appears, the run is flagged for protocol review
before any result is reported.

## Why Temperature 0

We use deterministic decoding because the measured object is output-contract
compliance under a frozen scoring protocol, not creative code-generation
diversity.

Each row must be reproducible, hashable, replayable through VCR, and auditable.
Higher-temperature or multi-sample settings would add a sampling-policy
variable. They would make parse failure and governance failure harder to
attribute.

The Qwen3-Coder model card recommends `temperature=0.7`, `top_p=0.8`,
`top_k=20`, and a larger output length for general coding use. That is a good
default for broad model use; it is not the cleanest setting for this benchmark.
Here the task is not to encourage exploratory agent behavior. The task is to
ask whether the model can emit parseable, scoreable, state-consistent final
answers under a fixed contract.

We do not use `temperature=0.1` or `0.5` because partial sampling still adds a
decoding-policy variable without giving the benchmark a multi-candidate
selection mechanism. We do not use `temperature=0.8` or multi-sample reranking
because the clean-v2 matrix has no reranker. Adding one for Qwen3-Coder would
create a new method variable.

## Why Top-P 1 And No Top-K

`top_p=1` keeps nucleus filtering neutral under deterministic decoding.
`top_k` is not sent for the selected Alibaba route because the route snapshot
does not expose `top_k` in `supported_parameters`. The run must not rely on a
provider-specific sampling trick to improve formatting.

If a future route exposes `top_k`, that does not automatically authorize
setting it. Changing the sampling policy requires a new protocol freeze.

## Why Max Tokens Is Not Relaxed

`max_tokens=4096` follows the clean-v2 output cap. Qwen3-Coder should not
receive a larger output budget merely because its model card supports longer
generations. A wider output cap would make parse improvements ambiguous: the
change could come from model capability, from a looser budget, or from both.

The supplement therefore keeps the same output cap as the main matrix unless a
separate, explicitly labeled budget diagnostic is created.

## Source Trail

Local protocol sources:

- `FINAL_MAIN_MATRIX_DEFINITION.md`: five-model primary matrix definition.
- `VARIABLE_CONTROL.md`: matrix axes, frozen controls, and disallowed pooling.
- `MAIN_RUN_API_POLICY.md`: request, retry, timeout, cache, and missingness
  controls.
- `EXPERIMENT_VARIABLE_CONTROL_OVERVIEW.md`: single-entry summary of clean-v2
  variable control.

External model and endpoint sources checked on 2026-06-29:

- Qwen3-Coder-480B-A35B-Instruct model card:
  https://huggingface.co/Qwen/Qwen3-Coder-480B-A35B-Instruct
- Qwen3-Coder license:
  https://huggingface.co/Qwen/Qwen3-Coder-480B-A35B-Instruct/blob/main/LICENSE
- Qwen2.5-Coder-32B-Instruct model card:
  https://huggingface.co/Qwen/Qwen2.5-Coder-32B-Instruct
- OpenRouter Qwen3-Coder page:
  https://openrouter.ai/qwen/qwen3-coder
- OpenRouter Qwen3-Coder endpoint API:
  https://openrouter.ai/api/v1/models/qwen/qwen3-coder/endpoints
- OpenRouter reasoning-token documentation:
  https://openrouter.ai/docs/guides/best-practices/reasoning-tokens
- OpenRouter DeepSeek R1 page:
  https://openrouter.ai/deepseek/deepseek-r1
- OpenRouter Qwen3 Thinking page:
  https://openrouter.ai/qwen/qwen3-235b-a22b-thinking-2507
- OpenRouter gpt-oss-120b page:
  https://openrouter.ai/openai/gpt-oss-120b
- Mistral Small 3.2 model card:
  https://huggingface.co/mistralai/Mistral-Small-3.2-24B-Instruct-2506
- Meta Llama 3.3 70B Instruct model card:
  https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct
- Gemma terms:
  https://ai.google.dev/gemma/terms
