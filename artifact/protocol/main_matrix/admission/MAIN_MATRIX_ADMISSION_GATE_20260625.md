# Main Matrix Admission Gate

Date: 2026-06-25

Decision: `READY_FOR_MAIN_RECORD_MODE`

This gate belongs to the new anonymous-review repository. It does not inherit
GO/NO-GO state from the older pilot repository. The older repository is used
only as provenance for method semantics and endpoint-planning history.

## What Is Frozen

- Confirmatory config: `artifact/protocol/main_matrix/configs/pcg_dynamic_state_v2_confirmatory_40task_5model_6method_2budget_3run_20260625.json`
- Confirmatory rows: `artifact/protocol/main_matrix/configs/pcg_dynamic_state_v2_confirmatory_40task_5model_6method_2budget_3run_20260625.rows.jsonl`
- Diagnostic config: `artifact/protocol/main_matrix/configs/pcg_dynamic_state_v2_budget300_diagnostic_40task_5model_4method_1budget_1run_20260625.json`
- Diagnostic rows: `artifact/protocol/main_matrix/configs/pcg_dynamic_state_v2_budget300_diagnostic_40task_5model_4method_1budget_1run_20260625.rows.jsonl`
- Variable freeze spec: `artifact/protocol/main_matrix/admission/VARIABLE_FREEZE_SPEC_20260625.yaml`
- Model admission criteria: `artifact/protocol/main_matrix/admission/MODEL_ADMISSION_CRITERIA_20260626.md`
- Provider policy snapshot: `artifact/protocol/main_matrix/admission/PROVIDER_SUPPORTED_PARAMETER_SNAPSHOT_20260625.json`
- Provider live refresh: `artifact/protocol/main_matrix/admission/live_refresh_20260625/provider_live_refresh_summary.json`
- Hash manifest: `artifact/protocol/main_matrix/admission/HASH_MANIFEST_20260625.jsonl`

## Static Admission Result

Static freeze checks are expected to pass with:

```bash
python3 artifact/verification/verify_main_matrix_freeze.py
```

The static gate verifies row counts, budget separation, method separation, the
scorer metric contract, dataset/task hashes, scorer and runner hashes,
provider-policy fields, and manifest hashes.

## Provider Live Refresh Result

The five endpoint live refresh has passed on a non-benchmark prompt. GPT and
Claude are admitted as OpenRouter-routed conditions for this gate:

```text
openrouter_gpt55 -> openai/gpt-5.5 -> openai/gpt-5.5-20260423
openrouter_claude48 -> anthropic/claude-opus-4.8 -> anthropic/claude-4.8-opus-20260528
deepseek_v4pro -> deepseek-v4-pro
kimi_k26 -> kimi-k2.6
qwen37max -> qwen3.7-max
```

The provider-adapter JSONL closed through VCR `record`, `replay`, and
cassette `audit` for all five refresh rows. These rows are admission-only and
do not enter primary aggregation.

For the OpenRouter GPT and Claude rows, request controls explicitly set
`reasoning: {"effort": "none"}`. The live refresh observed
`reasoning_tokens = 0` and no returned reasoning payload for both rows.

## Benchmark Admission Work

The required benchmark smoke has completed:

```text
1 task x 5 models x 6 methods x 2 budgets x 1 run = 60 rows
```

Optionally add the diagnostic smoke:

```text
1 task x 5 models x 4 methods x 1 budget x 1 run = 20 rows
```

As of 2026-06-26, these model conditions have completed this smoke and are
marked `ADMIT_MODEL`:

```text
openrouter_gpt55
openrouter_claude48
deepseek_v4pro
qwen37max
kimi_k26
```

No model-condition blocker remains. The matrix gate is `READY_FOR_MAIN_RECORD_MODE`. This
authorizes full record-mode execution under the frozen protocol; it does not
create primary result rows.

Record-mode entry log: `artifact/protocol/main_matrix/admission/MAIN_MATRIX_RECORD_MODE_ENTRY_LOG_20260627.md`

Admission rows must stay outside `artifact/results/main_matrix/` and must not
enter primary aggregation.

The decision rule for those rows is frozen in
`artifact/protocol/main_matrix/admission/MODEL_ADMISSION_CRITERIA_20260626.md`.
Engineering, replay, hash, and structured output failures can block a model
condition. Low `answer_success`, `state_governance_success`, or
`reliable_composite_success` cannot block admission by itself, because those
fields are main-experiment outcomes.

## Non-Inheritance Rule

The old pilot repository may supply background and design lineage. It does not
license current primary rows. Current primary rows require the new config,
new row manifest, new request hashes, current provider snapshot, recorded raw
outputs, replay cassette, scorer hash, and post-run H5/E5 manifest.
