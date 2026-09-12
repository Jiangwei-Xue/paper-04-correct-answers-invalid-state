# Experiment Variable-Control Overview

Date: 2026-06-27

This is the reviewer-facing entry point for the PCG dynamic-state v2 main
matrix. It summarizes the variable-control protocol in one place. The underlying
source files remain separate because they are hash-locked for different audit
purposes: matrix shape, method semantics, model/provider routing, API policy,
budget disposition, preregistered decision rules, and freeze manifests.

## Current Gate

The clean-v2 primary execution layer is complete. The current execution gate is:

```text
CLEAN_V2_EXECUTION_CLOSURE_COMPLETE
```

All five frozen model conditions completed from row zero under the v2
direct-network execution boundary. The submission aggregate result tables are
frozen under `paper/submission_tables/`. The full public DOI/hosting release remains a
separate release layer.

## Primary Matrix

The confirmatory matrix is:

```text
40 tasks x 5 models x 6 methods x 2 budgets x 3 runs = 7,200 rows
```

The separate budget-300 diagnostic probe is:

```text
40 tasks x 5 models x 4 methods x 1 budget x 1 run = 800 rows
```

Budget `300` is diagnostic only. It is excluded from confirmatory inference,
mixed-effects models, model ranking, method ranking, and overall averages.

## Matrix Axes

The allowed matrix axes are:

- `task_id`;
- `model_condition_id`;
- `method`;
- `budget`;
- `run_id`.

Everything else is a frozen control or recorded metadata.

## Task Axis

The task axis contains 40 PCG dynamic-state v2 tasks. Model-visible task content
and scorer-only oracle content are split. The runner may use only model-visible
content; the scorer may use oracle fields only at scoring time.

The task split, model-visible manifest, scorer oracle manifest, and task split
audit are hash-locked in the freeze packet.

## Model Axis

The model axis contains five conditions:

| model condition | route |
| --- | --- |
| `openrouter_gpt55` | OpenRouter to OpenAI |
| `openrouter_claude48` | OpenRouter to Anthropic |
| `deepseek_v4pro` | direct DeepSeek-compatible endpoint |
| `kimi_k26` | direct Moonshot-compatible endpoint |
| `qwen37max` | direct DashScope-compatible endpoint |

OpenRouter is not an experimental treatment. It is the fixed provider route for
the GPT and Claude model conditions.

For OpenRouter GPT/Claude:

- fallback is disabled;
- tools and web are disabled;
- `reasoning.effort = none`;
- temperature is intentionally omitted;
- returned model must exactly match the frozen expected string;
- provider metadata and response hashes must be recorded;
- replay must close through the VCR cassette without cache misses.

## Method Axis

The method axis contains exactly six conditions:

- `loop_only`;
- `rolling_summary`;
- `rolling_visible_carry_forward`;
- `rolling_visible_fields_only`;
- `ssr_no_visible_carry`;
- `mature_ssr_loop`.

Provider route is not a method. OpenRouter routing must not be interpreted as a
mechanism arm.

The core mechanism design is a two-by-two schema/carry comparison:

| | no schema | schema |
| --- | --- | --- |
| no deterministic visible carry | `rolling_summary` | `ssr_no_visible_carry` |
| deterministic visible carry | `rolling_visible_carry_forward` | `mature_ssr_loop` |

`loop_only` is a floor and empty-governance diagnostic. `rolling_visible_fields_only`
is a mechanical-field negative control.

## Budget Axis

The confirmatory budget axis contains:

- `600`;
- `1200`.

Budget `300` is retained only as a low-budget diagnostic probe because this
regime can create severe truncation, floor effects, and carry-failure behavior.

## Run Axis

The confirmatory matrix uses three repeats per cell:

```text
run_id in {1, 2, 3}
```

The budget-300 diagnostic probe uses one run per cell.

## Request And Runtime Controls

All live record-mode rows must use the frozen request controls:

- `max_tokens: 4096`;
- `stream: false`;
- tools disabled;
- web disabled;
- provider fallback disabled;
- cache not requested;
- timeout `120` seconds;
- at most two transport attempts under the retry policy;
- global live-adapter concurrency `10`, not 10 per provider;
- replay from cassette only after live record output exists.

Invalid JSON, parser failure, backend failure, timeout, and provider errors are
row outcomes. They must be preserved and included in missingness accounting.

### V1 Proxy-Path And V2 Direct-Network Execution Boundary

The global concurrency-10 policy passed admission. During formal v1 record-mode
execution, however, proxy-mediated execution-path instability appeared at a
larger scale than admission smoke could expose. The first signal was high
provider-specific backend-error heterogeneity for `openrouter_gpt55`; later,
`openrouter_claude48` also triggered the backend-error guard. After Claude was
run under the adjusted direct-network path with 0 backend-error rows, the v1
logs for Qwen and Kimi were reviewed and found to contain proxy/transport-like
backend evidence for a subset of rows.

Proxy-mediated execution was therefore recognized as an uncontrolled v1
execution-environment condition. The final primary execution boundary is now
all-model v2 direct-network from row zero, governed by:

```text
V2_DIRECT_NETWORK_EXECUTION_PROTOCOL_20260628.md
```

The earlier OpenRouter-only clean-v2 decision remains historical execution
evidence. Completed v1 DeepSeek, Qwen, and Kimi batches, earlier GPT/Claude
partial outputs, pause packets, and clean-v2 transition packets remain locked
append-only. They are not pooled with v2 direct-network rows for final primary
aggregation.

The submission aggregation layer is generated from the tracked v2 score CSV files
by:

```text
artifact/verification/summarize_submission_tables.py
```

## Outcome Discipline

The primary metric is:

```text
reliable_composite_success = answer_success AND state_governance_success
```

`answer_success` and `state_governance_success` are reported as paired
decomposition metrics. Standalone governance is diagnostic only. A row that
looks clean because it carries no output-bearing state does not establish
reliable success.

## Statistical Analysis Boundary

The primary confirmatory estimand is design-based, not model-first. The
statistical analysis plan uses paired risk differences within matched
task x model x budget x run blocks, with task-cluster bootstrap confidence
intervals. The primary contrast is:

```text
rolling_visible_carry_forward - ssr_no_visible_carry
```

`mature_ssr_loop - rolling_visible_carry_forward` is the key secondary
schema-given-carry contrast. GLMMs are model-assisted sensitivity analyses and
do not replace the paired risk-difference estimands.

## Disallowed Pooling

The following rows must not enter the primary matrix:

- historical calibration runs;
- legacy or old-repo packets;
- admission smoke rows;
- provider live-refresh rows;
- static sanity rows;
- targeted backfills;
- budget-300 diagnostic rows;
- sentinel drift probes;
- routed-provider rows without frozen route equivalence.

## One-Document Reading Rule

For a quick review, this file is the entry point. For audit, the controlled
source files are:

| source file | role |
| --- | --- |
| `FINAL_MAIN_MATRIX_DEFINITION.md` | row count, axes, primary/diagnostic split |
| `VARIABLE_CONTROL.md` | matrix axes versus frozen controls |
| `METHOD_CONDITIONS.md` | method arms and mechanism interpretation |
| `BUDGET_300_DIAGNOSTIC_DISPOSITION.md` | why budget `300` is diagnostic only |
| `MODEL_AXIS_DISPOSITION.md` | included/excluded model endpoints |
| `MAIN_RUN_API_POLICY.md` | retry, timeout, concurrency, cache, missingness |
| `OPENROUTER_GPT_CLAUDE_CLEAN_V2_FROM_ZERO_PROTOCOL_20260627.md` | from-zero clean-v2 OpenRouter GPT/Claude primary-slice decision |
| `PREREGISTERED_DECISION_RULES.md` | outcome and reporting rules |
| `STATISTICAL_ANALYSIS_PLAN.md` | primary estimand, bootstrap CI, contrast hierarchy |
| `admission/VARIABLE_FREEZE_SPEC_20260625.yaml` | freeze spec and hash references |
| `admission/PROVIDER_SUPPORTED_PARAMETER_SNAPSHOT_20260625.json` | provider/request controls |
| `admission/OPENROUTER_VARIABLE_CONTROL_20260626.md` | OpenRouter route boundary |

If this overview conflicts with a hash-locked source file, the hash-locked source
file controls. The intended role of this overview is readability, not replacing
the audit chain.
