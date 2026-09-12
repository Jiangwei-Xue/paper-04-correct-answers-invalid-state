# Paper results map

This map links the claim-bearing V3 results of **When Correct Answers Carry Invalid State: Evaluating Explicit State Carriers in Stateful LLM Agents** ([DOI 10.5281/zenodo.22720976](https://doi.org/10.5281/zenodo.22720976)) to released evidence and deterministic replay stages. The reproduction repository is [https://github.com/Jiangwei-Xue/paper-04-correct-answers-invalid-state](https://github.com/Jiangwei-Xue/paper-04-correct-answers-invalid-state). Exact PDF, LaTeX, and figure hashes are recorded in `LATEST_PAPER.json`.

| Paper item | Experiment/config | Raw or normalized input | Processed result | Generation or validation stage |
|---|---|---|---|---|
| Primary V3 totals and answer/state decomposition | primary 7,200-row matrix | `results/metric_v3/inputs/primary.jsonl` | `results/metric_v3/scores_v3/primary.production.jsonl`; `reports/metric_v3/rescore_summary_v3.json` | V3 scorer and aggregate stages |
| V3 component pass counts | primary matrix | primary V3 scores | `reports/metric_v3/rescore_summary_v3.json` | aggregate stage |
| Protocol profiles | primary matrix | primary V3 scores | `reports/metric_v3/rescore_summary_v3.json` | method aggregation |
| Method-blocked executor contrasts | primary matrix and V3 scores | `results/metric_v3/executor/primary.executor.jsonl` | `reports/metric_v3/independent_executor_v3_report.json` | executor reconstruction and task-cluster bootstrap |
| Answer-denominator and V2-to-V3 crosswalks | primary V2/V3 tiers | row-level score files | `reports/metric_v2/rescore_summary.json`; `reports/metric_v3/rescore_summary_v3.json` | V2/V3 aggregate stages |
| Model-by-budget hard-cap diagnostic | primary matrix | hash-verified saved provider records and V3 scores | `reports/metric_v3/primary_model_budget_cap_v3.csv` | model-budget summary stage |
| Representation-invariance result | canonical cases in three formats | `reports/metric_v3/gates/representation_invariance_suite.json` and serializers | verifier output | `scripts/test_metric_v3_invariance.py` |
| Metamorphic and mutation validation | deterministic V2 fixtures and mutants | `tests/metric_v2/` | verifier output | `scripts/test_metric_v2_properties.py` |
| Primary legacy sensitivity tables | frozen main-matrix score records | row-level scored evidence | `paper/submission_tables/tables/` | frozen aggregate verification |
| Budget-300 diagnostic | 800-row diagnostic config | saved diagnostic records | `paper/submission_tables/tables/budget300_diagnostic_*` | VCR and frozen-summary checks |
| Qwen supplement | 1,440 supplement and 160 diagnostic rows | saved Qwen records | V2/V3 supplement reports and legacy tables | supplement replay stages |
| DeepSeek sanity | 40 saved rows | sanity cassette | V2/V3 sanity scores | sanity replay stage |
| Deterministic validity suite | 36,000 local controls | generated deterministic inputs | V2/V3 deterministic scores | local suite regeneration |

The manuscript is not bundled. The map covers the numeric inputs and generated results used by its claim-bearing tables and figures.
