# Main Matrix Record-Mode Entry Log

Date: 2026-06-27

Decision: `READY_FOR_MAIN_RECORD_MODE`

This log records the admission event for the frozen PCG dynamic-state v2 main
matrix. The five frozen model conditions have passed the required main-matrix
admission tests. The main matrix may enter live `record` mode under the frozen
protocol.

This is an execution-entry decision. It is not a completed primary result
table, and it does not add any row to primary aggregation.

## Model Conditions

| model condition | route | admission decision |
| --- | --- | --- |
| `openrouter_gpt55` | OpenRouter to OpenAI | `ADMIT_MODEL` |
| `openrouter_claude48` | OpenRouter to Anthropic | `ADMIT_MODEL` |
| `deepseek_v4pro` | direct DeepSeek-compatible endpoint | `ADMIT_MODEL` |
| `qwen37max` | direct DashScope-compatible endpoint | `ADMIT_MODEL` |
| `kimi_k26` | direct Moonshot-compatible endpoint | `ADMIT_MODEL` |

## Admission Evidence

Provider live refresh passed for all five endpoints on a non-benchmark prompt.
The provider-adapter rows closed through VCR record, replay, and cassette
audit. For OpenRouter GPT and Claude, fallback was disabled, returned-model
strings matched the frozen expected strings, and `reasoning.effort` was set to
`none`.

Benchmark admission smoke also passed for all five frozen model conditions:

```text
1 task x 5 models x 6 methods x 2 budgets x 1 run = 60 confirmatory smoke rows
```

Global structured-output readiness:

```text
60/60 parse+score rows; threshold = 57/60
```

The proportional budget-300 admission diagnostic smoke also ran:

```text
1 task x 5 models x 4 methods x 1 budget x 1 run = 20 diagnostic smoke rows
```

Those budget-300 rows are diagnostic only and remain excluded from primary
aggregation.

## Boundary

The following statement is allowed:

```text
All five frozen model conditions passed main-matrix admission. The main matrix
can proceed to record-mode execution under the frozen protocol.
```

The following statement is not allowed:

```text
The main matrix results are complete.
```

The completed primary result table is still absent. It must be produced only by
the frozen main-matrix configs, recorded raw outputs, replay cassettes, scorer
hashes, and post-run audit manifests.

## Pointers

- Admission gate: `artifact/protocol/main_matrix/admission/MAIN_MATRIX_ADMISSION_GATE_20260625.md`
- Admission criteria: `artifact/protocol/main_matrix/admission/MODEL_ADMISSION_CRITERIA_20260626.md`
- Benchmark smoke summary: `artifact/protocol/main_matrix/admission/benchmark_smoke_20260626/SUMMARY.json`
- Benchmark smoke README: `artifact/protocol/main_matrix/admission/benchmark_smoke_20260626/README.md`
- Freeze summary: `artifact/protocol/main_matrix/admission/FREEZE_SUMMARY_20260625.json`
