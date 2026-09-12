# Benchmark Card

Name: PCG Dynamic-State v2 reliable co-success benchmark

Status: reviewer-facing benchmark documentation. This card documents the
benchmark substrate and protocol boundary. submission aggregate result tables are
frozen under `paper/submission_tables/`.

## What The Benchmark Measures

The benchmark measures whether an LLM condition can recover an exact answer
and maintain governed, output-bearing state in the same row under bounded
state transfer.

Primary metric:

```text
reliable_composite_success = answer_success AND state_governance_success
```

The two component metrics are reported together:

- `answer_success`: whether the final answer satisfies the task oracle.
- `state_governance_success`: whether the carried state is governed and
  output-bearing under the strict scorer.

Standalone governance is diagnostic only. A row that is clean because it
carries no output-bearing state is not counted as governed reliability.

## What The Benchmark Does Not Measure

This benchmark does not measure:

- general model intelligence or broad reasoning ability;
- open-ended task quality;
- human preference, helpfulness, or style;
- safety in the policy or harm-prevention sense;
- live API reproducibility years after the run;
- OpenRouter versus official-provider performance;
- universal success or failure of SSR-style methods.

Provider route is provenance and variable control, not a mechanism arm.

## Current Matrix Shape

The confirmatory matrix is preregistered as:

```text
40 tasks x 5 models x 6 methods x 2 budgets x 3 runs = 7,200 rows
```

Confirmatory budgets are `600` and `1200`.

The separate budget-`300` diagnostic probe is:

```text
40 tasks x 5 models x 4 methods x 1 budget x 1 run = 800 rows
```

Budget `300` is excluded from confirmatory inference, method ranking, model
ranking, mixed-effects models, and overall averages. It is used only to
describe floor effects, truncation, and carry-failure behavior under extreme
compression.

Current gate:

```text
CLEAN_V2_EXECUTION_CLOSURE_COMPLETE
```

The clean-v2 five-model execution layer is complete, and the submission aggregate
tables are present under `paper/submission_tables/tables/`. The full public DOI/hosting
release remains a separate release layer.

## Task Construction

The benchmark uses 40 PCG dynamic-state v2 tasks. Each task is designed around
state transfer across bounded segments. The model sees only model-visible task
content and prior visible state. The scorer has separate oracle fields for
checking exact answers and governance constraints.

The task substrate is a controlled benchmark after protocol calibration, not a
claim of an untouched public held-out test set.

Hash-locked task surfaces:

- model-visible task manifest;
- scorer-only oracle manifest;
- task provenance manifest;
- task split audit.

The runner must not read scorer-only oracle fields, hidden answers,
required-token arrays, forbidden-token arrays, protected-token arrays, raw
scoring metadata, or external context while constructing prompts or state.

## Method Conditions

The six confirmatory method conditions are:

- `loop_only`;
- `rolling_summary`;
- `rolling_visible_carry_forward`;
- `rolling_visible_fields_only`;
- `ssr_no_visible_carry`;
- `mature_ssr_loop`.

The core mechanism comparison is schema by deterministic visible carry:

| | no schema | schema |
| --- | --- | --- |
| no deterministic visible carry | `rolling_summary` | `ssr_no_visible_carry` |
| deterministic visible carry | `rolling_visible_carry_forward` | `mature_ssr_loop` |

`loop_only` is a floor and empty-governance diagnostic. `rolling_visible_fields_only`
is a mechanical-field negative control. SSR conditions are mechanism factors,
not the paper's proposed method.

## Model And Provider Conditions

The frozen model axis contains five model conditions:

| model condition | route |
| --- | --- |
| `openrouter_gpt55` | OpenRouter to OpenAI |
| `openrouter_claude48` | OpenRouter to Anthropic |
| `deepseek_v4pro` | direct DeepSeek-compatible endpoint |
| `kimi_k26` | direct Moonshot-compatible endpoint |
| `qwen37max` | direct DashScope-compatible endpoint |

For OpenRouter-routed conditions, fallback is disabled, tools and web are
disabled, `reasoning.effort` is `none`, temperature is intentionally omitted,
and returned model strings must exactly match the frozen expected strings.

## Expected Use

Appropriate uses:

- evaluate reliable co-success under bounded state transfer;
- separate exact-answer success from state-governance success;
- test whether marginal successes co-occur in the same row;
- compare state-transfer mechanisms under frozen prompts, tasks, methods,
  budgets, and provider routes;
- verify saved-output evidence without API keys through replay and hash locks.

Inappropriate uses:

- ranking general LLM quality;
- treating budget `300` as a confirmatory budget level;
- pooling admission, drift, historical, or diagnostic rows into primary
  aggregates;
- interpreting saved-output replay as a guarantee that current live APIs will
  produce the same outputs;
- treating OpenRouter as an experimental method or intervention.

## Known Failure Modes

Known failure modes include:

- invalid or unparsable final JSON;
- correct answer with state-governance failure;
- governed-looking state with answer failure;
- empty or non-bearing state that would pass a weak no-conflict metric;
- truncation and hard-cap effects, especially at budget `300`;
- provider/backend failure or timeout;
- provider routing drift outside saved-output replay;
- live API outputs changing after the original run.

These failures are part of the measurement target unless they are protocol
integrity failures such as oracle leakage, provider fallback, tool/web use, or
missing hash linkage.

## Reproducibility Boundary

The artifact targets evidence reproducibility. Reviewers can verify saved
outputs, manifests, parser/scorer behavior, VCR cassettes, and hash chains
without API keys or provider calls.

Replay mode reproduces reported scores from recorded model outputs. It does
not claim that current live APIs will reproduce identical outputs.

## Primary Source Files

- `artifact/protocol/main_matrix/EXPERIMENT_VARIABLE_CONTROL_OVERVIEW.md`
- `artifact/protocol/main_matrix/FINAL_MAIN_MATRIX_DEFINITION.md`
- `artifact/protocol/main_matrix/METHOD_CONDITIONS.md`
- `artifact/protocol/main_matrix/PREREGISTERED_DECISION_RULES.md`
- `artifact/protocol/main_matrix/STATISTICAL_ANALYSIS_PLAN.md`
- `artifact/protocol/main_matrix/BUDGET_300_DIAGNOSTIC_DISPOSITION.md`
- `artifact/protocol/main_matrix/admission/MODEL_ADMISSION_CRITERIA_20260626.md`
- `artifact/protocol/main_matrix/admission/OPENROUTER_VARIABLE_CONTROL_20260626.md`
- `docs/RAI_ETHICS_LIMITATIONS.md`
