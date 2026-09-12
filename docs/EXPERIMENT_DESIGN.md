# Experiment design

## Research object

The experiment evaluates whether a model output that contains a correct final answer also exports carried state that remains safe, sufficient, and usable by a later software component.

## Primary matrix

The frozen confirmatory matrix contains:

```text
40 tasks x 5 model conditions x 6 state-transfer protocols x 2 budgets x 3 repeats = 7,200 rows
```

The confirmatory budgets are 600 and 1,200 serialized characters. A separate 800-row budget-300 diagnostic is excluded from confirmatory comparisons.

## State-transfer protocols

The six conditions are:

- `loop_only`: current-segment floor control;
- `rolling_summary`: summary without deterministic visible carry;
- `rolling_visible_carry_forward`: deterministic visible carry without schema;
- `rolling_visible_fields_only`: mechanical-field negative control;
- `ssr_no_visible_carry`: structured schema without deterministic visible carry;
- `mature_ssr_loop`: structured schema with deterministic visible carry.

The four middle substantive conditions form the schema-by-carry mechanism core. The two control conditions are not competitive methods.

## Model conditions

The primary matrix uses five frozen model/provider conditions: Claude Opus 4.8, DeepSeek V4 Pro, GPT-5.5, Kimi K2.6, and Qwen 3.7 Max. Provider routing, parameter-support snapshots, and admission records are retained under `artifact/protocol/main_matrix/`.

## Fixed variables and randomness

Every primary cell reuses the same 40-task manifest. The matrix fixes task definitions, prompt construction, method implementation, scoring rules, budget interpretation, and retry policy. Three repeats are retained per confirmatory cell. Task-cluster bootstrap analyses use 10,000 replicates; the V3 executor analysis uses seed 20260813.

## Prompt and execution records

Formal request payloads and saved responses are retained in the VCR and raw-evidence surfaces under `artifact/results/`. Admission smoke rows, historical runs, drift probes, the budget-300 diagnostic, deterministic controls, and the Qwen supplement are not mixed into the 7,200-row primary denominator.

## Evaluation

- `A`: deterministic success on the dedicated final-answer surface.
- `V_I`: intrinsic carried-state validity after representation normalization.
- `V_A`: intrinsic validity plus alignment with the emitted final answer.
- `J`: joint success, `A AND V_A`.
- `E`: success of a separately implemented next-step executor consuming the canonical claimed state.

V3 is the claim-bearing carried-state construct. It checks parseability, actionable presence, exclusion safety, operational sufficiency, and answer-state consistency after three supported native representation families are normalized into a canonical state.

Executor contrasts are blocked by state-transfer protocol and use task-cluster bootstrap intervals. No pooled executor risk difference is treated as claim-bearing.

## Principal result

The primary offline replay contains 696 final-answer successes and 173 rows that also satisfy answer-aligned carried-state validity. Thus 24.86% of answer-correct rows satisfy the complete carried-state contract, while 75.14% do not.

Detailed freezes and protocol decisions remain under `artifact/protocol/main_matrix/`, `specs/`, and `docs/metric_v3_revision_analysis_plan.md`.

