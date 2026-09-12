# Benchmark Admission Smoke 2026-06-26

This directory records the benchmark admission smoke rows for the frozen PCG
dynamic-state v2 main matrix. The rows are admission-only. They must not enter
primary aggregation, method ranking, model ranking, or the paper's co-success
estimates.

The smoke used the frozen task, model, method, budget, request-control, runner,
scorer, replay policy, and statistical-analysis boundary recorded in the
main-matrix freeze packet. The single smoke task was:

```text
pcgds_v2_00001_api_migration_state_transition_easy
```

## Scope

Completed in this packet:

| model condition | confirmatory rows | budget-300 diagnostic rows | live API calls | decision |
| --- | ---: | ---: | ---: | --- |
| `openrouter_gpt55` | 12 | 4 | 61 | `ADMIT_MODEL` |
| `openrouter_claude48` | 12 | 4 | 61 | `ADMIT_MODEL` |
| `deepseek_v4pro` | 12 | 4 | 61 | `ADMIT_MODEL` |
| `qwen37max` | 12 | 4 | 61 | `ADMIT_MODEL` |
| `kimi_k26` | 12 | 4 | 61 | `ADMIT_MODEL` |

The full five-model tiny smoke is complete:

```text
1 task x 5 models x 6 methods x 2 budgets x 1 run = 60 confirmatory rows
```

All five model conditions are marked `ADMIT_MODEL`. This closes the tiny-smoke
blocker for record-mode entry; it does not create primary result rows.

## Gate Results

The admission decision uses only hard engineering gates and structured-output
readiness. Answer, state-governance, and reliable-composite outcomes are
reported but are not admission filters.

| model condition | parse+score success | hard failures | reasoning payload | admission decision |
| --- | ---: | ---: | ---: | --- |
| `openrouter_gpt55` | 12/12 | 0 | 0 | `ADMIT_MODEL` |
| `openrouter_claude48` | 12/12 | 0 | 0 | `ADMIT_MODEL` |
| `deepseek_v4pro` | 12/12 | 0 | 0 | `ADMIT_MODEL` |
| `qwen37max` | 12/12 | 0 | 0 | `ADMIT_MODEL` |
| `kimi_k26` | 12/12 | 0 | 0 | `ADMIT_MODEL` |

Global parse+score result:

```text
60/60 rows
```

The frozen global threshold is `57/60`.

## Outcome Snapshot

These fields are diagnostic only for admission.

| model condition | confirmatory answer success | confirmatory state-governance success | confirmatory reliable-composite success | budget-300 parse+score | budget-300 reliable-composite success |
| --- | ---: | ---: | ---: | ---: | ---: |
| `openrouter_gpt55` | 4/12 | 1/12 | 1/12 | 4/4 | 0/4 |
| `openrouter_claude48` | 4/12 | 3/12 | 2/12 | 4/4 | 0/4 |
| `deepseek_v4pro` | 4/12 | 5/12 | 3/12 | 4/4 | 2/4 |
| `qwen37max` | 5/12 | 6/12 | 4/12 | 4/4 | 0/4 |
| `kimi_k26` | 1/12 | 3/12 | 0/12 | 4/4 | 0/4 |

## Replay Closure

For each completed model condition, both confirmatory and budget-300 diagnostic
rows closed through:

```text
adapter_source -> VCR record -> cassette -> replay -> audit
```

All ten cassette audits passed with zero cache misses.

## Metadata Relock

After the SAP freeze, the admission smoke metadata was relocked without API
calls so every smoke config points to the current variable freeze spec and
`STATISTICAL_ANALYSIS_PLAN.md`.

```text
api_calls_performed: 0
variable_freeze_spec_sha256: 83871f5d9aae7f42366909bdeb0284a2fef34ce65e92ca7857d3e17da84f419a
statistical_analysis_plan_sha256: efcb9e52ccc4621a573c9eb7430d99216cbe6aa2baf6f9fbba65950a9f96a2c5
```
