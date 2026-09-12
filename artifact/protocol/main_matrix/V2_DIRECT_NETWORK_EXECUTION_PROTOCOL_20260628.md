# All-Model Direct-Network V2 From-Zero Protocol

Status: protocol decision for final v2 primary matrix execution

Created UTC: 2026-06-28T13:11:50Z

Scope: all five admitted model conditions in the confirmatory main matrix.
This document supersedes the earlier OpenRouter-only clean-v2 primary-inclusion
plan for final primary aggregation. It does not delete, overwrite, or hide any
v1 record-mode output, pause packet, runner log, cassette, replay output, score
row, hash manifest, or report.

## Definitions

`v1` refers to the 2026-06-27 record-mode execution packets under:

```text
artifact/results/main_matrix/record_mode_20260627/
```

The v1 execution environment used a proxy-mediated network path. This was an
execution-site condition, not a model, method, prompt, parser, scorer, task, or
budget variable.

`v2 direct-network` refers to a unified direct execution network path for all
five model conditions. It is an execution-environment control intended to avoid
mixing proxy-mediated and direct-network rows inside the final primary matrix.

## Decision

The final v2 primary matrix must be recorded from row zero for all five admitted
model conditions under the unified v2 direct-network execution environment:

```text
40 tasks x 5 models x 6 methods x 2 budgets x 3 runs = 7,200 rows
```

The v2 primary matrix must use the frozen row manifests, task definitions,
method conditions, budgets, run ids, prompts, parser, scorer, retry policy,
VCR record/replay/audit closure, and hash-manifest rules unless a later written
protocol explicitly changes one of those controls before execution.

The v1 outputs remain append-only audit and diagnostic evidence. They are not
pooled with v2 direct-network rows for final primary aggregation.

## Rationale

During the v1 execution, proxy-mediated network behavior was not identified at
admission time as a variable requiring uniform control. The admission smoke
packets admitted the model conditions for record-mode execution, but they did
not expose the later proxy-path instability observed during the larger
record-mode run.

The issue became clearer after the Claude execution problem. The first-pass
Claude slice triggered a backend-error guard, while the later Claude run under
the adjusted direct-network execution path completed 1,440/1,440 rows with
0 backend-error rows. That contrast made it plausible that at least part of the
earlier backend-error behavior was caused by the execution network path rather
than by model behavior alone.

After that observation, the v1 logs for the other model conditions were
reviewed. GPT had already shown the clearest non-Claude infrastructure signal:
80 backend-error rows in 395 attempted rows, with the OpenRouter classification
packet assigning all 80 to confirmed local transport-path or network-suspect
infrastructure classes. The strict recovery-eligible subset was smaller because
valid final outputs remain locked even when a row contains infrastructure
evidence.

The completed Qwen and Kimi v1 logs also show proxy/transport-like signatures
for a subset of backend rows, including tunnel-503 style failures. Not every
Qwen or Kimi backend row can be attributed to proxy instability: some backend
rows have final HTTP 200 responses and are better treated as mixed
provider/adapter/state-update failures. The correct conclusion is therefore not
that all v1 backend rows were proxy-caused. The defensible conclusion is that
the v1 execution environment contained a proxy-path condition that was not
exposed during admission and was not uniformly controlled as an experimental
variable.

The v1 pause audit records this as a mixed pattern rather than a uniform
model-output pattern: Qwen had 46 backend-error rows, of which 25 were
retry-eligible infrastructure rows under the pause policy; Kimi had 73
backend-error rows, of which 35 were retry-eligible infrastructure rows under
the pause policy. DeepSeek had only 3 backend-error rows, but it was still
executed under the same v1 proxy-mediated environment. For final primary
comparability, the v2 execution-environment control is therefore applied to all
five model conditions, not only to the high-backend subsets.

Because that condition could confound model/provider backend rates, the cleanest
final primary design is to rerun all five admitted model conditions from row
zero under one v2 direct-network execution environment, rather than mixing
v1 proxy-mediated direct-provider rows with later direct-network GPT/Claude or
other v2 rows.

## V1 Preservation Rule

All v1 artifacts remain in the repository as audit evidence:

- completed DeepSeek, Qwen, and Kimi v1 slices;
- first-pass GPT and Claude partial slices;
- pause packets and backend-error classification packets;
- smoke/canary packets;
- runner logs, adapter sources, cassettes, replay outputs, score rows, reports,
  and hash manifests.

These artifacts may be cited to explain why v2 direct-network execution was
introduced. They must not be deleted, hidden, silently replaced, or pooled with
v2 primary rows.

## V2 Inclusion Rule

A model condition is eligible for v2 primary aggregation only if its v2
direct-network slice:

- starts from row zero in the frozen confirmatory row manifest;
- uses the same model-axis semantic target as the admitted model condition;
- uses the frozen tasks, methods, budgets, runs, prompts, parser, and scorer;
- is executed under the unified v2 direct-network environment;
- preserves all raw outputs, provider metadata, adapter rows, score rows,
  cassettes, replay outputs, audit outputs, runner logs, and hash manifests;
- records any pause, halt, restart, or retry boundary append-only;
- does not replace valid model outputs because their answer, governance, parser,
  or reliable-composite result is unfavorable.

## Reporting Rule

The paper and artifact should describe v1 as an audited proxy-mediated
record-mode attempt whose logs revealed backend/transport concerns not exposed
at admission. The final primary result table should be described as v2
direct-network from-zero execution if, and only if, all admitted model
conditions are recorded and closed under this protocol or a later written
revision.

The report should avoid over-claiming that every v1 backend row was caused by
proxy instability. The correct wording is that v1 contained proxy/transport-like
backend evidence, and that the v2 all-model direct-network rerun was introduced
to remove that execution-environment confound from the primary matrix.
