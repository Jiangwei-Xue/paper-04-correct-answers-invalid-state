# Claim To Artifact Map

This file maps review claims to the files that support them.

## Main Matrix Design

The primary design is a PCG dynamic-state v2 confirmatory matrix with
40 tasks, 5 models, 6 methods, budgets `600` and `1200`, and 3 runs. A
separate `300`-budget diagnostic probe is retained for descriptive floor-effect
analysis only.

Supporting files:

- `artifact/BENCHMARK_CARD.md`
- `artifact/metadata/croissant.json`
- `artifact/metadata/CROISSANT_MAPPING.md`
- `artifact/protocol/main_matrix/PAPER_FRAMING_AND_RQS.md`
- `artifact/protocol/main_matrix/README.md`
- `artifact/protocol/main_matrix/FINAL_MAIN_MATRIX_DEFINITION.md`
- `artifact/protocol/main_matrix/METHOD_CONDITIONS.md`
- `artifact/protocol/main_matrix/VARIABLE_CONTROL.md`
- `artifact/protocol/main_matrix/STATISTICAL_ANALYSIS_PLAN.md`
- `artifact/protocol/main_matrix/BUDGET_300_DIAGNOSTIC_DISPOSITION.md`
- `artifact/protocol/main_matrix/PROTOCOL_LINEAGE.md`
- `artifact/results/evidence/budget_300_diagnostic_20260625/README.md`
- `paper/submission_tables/RESULTS_FREEZE.md`
- `paper/submission_tables/tables/`

The protocol files define the design. The clean-v2 five-model row-level
execution closure is stored under
`artifact/results/main_matrix/record_mode_20260627/`, and the submission
aggregate tables are frozen under `paper/submission_tables/`. The
`300`-budget diagnostic probe is excluded from confirmatory mixed-effects
models, method ranking, and overall method averages.

Task-substrate scope: the 40 PCG dynamic-state v2 tasks are the frozen
controlled substrate for the current matrix after protocol calibration. They
should not be described as a completely untouched held-out test set. Historical
pilot, calibration, and admission rows remain outside primary aggregation.

The six method labels are `loop_only`, `rolling_summary`,
`rolling_visible_carry_forward`, `rolling_visible_fields_only`,
`ssr_no_visible_carry`, and `mature_ssr_loop`.

## Statistical Analysis Plan

The future confirmatory analysis is preregistered as design-based paired risk
differences with task-cluster bootstrap confidence intervals. The primary
contrast is `rolling_visible_carry_forward - ssr_no_visible_carry`; the
schema-given-carry contrast `mature_ssr_loop - rolling_visible_carry_forward`
is key secondary. GLMMs are model-assisted sensitivity analyses and do not
replace the primary paired risk-difference estimands.

Supporting files:

- `artifact/protocol/main_matrix/STATISTICAL_ANALYSIS_PLAN.md`
- `artifact/protocol/main_matrix/PREREGISTERED_DECISION_RULES.md`
- `artifact/protocol/main_matrix/METHOD_CONDITIONS.md`
- `artifact/protocol/main_matrix/FINAL_MAIN_MATRIX_DEFINITION.md`
- `artifact/protocol/main_matrix/BUDGET_300_DIAGNOSTIC_DISPOSITION.md`
- `artifact/protocol/main_matrix/MAIN_RUN_API_POLICY.md`
- `artifact/protocol/main_matrix/admission/VARIABLE_FREEZE_SPEC_20260625.yaml`
- `artifact/protocol/main_matrix/admission/HASH_MANIFEST_20260625.jsonl`

This is an analysis protocol, not a completed results table. Budget `300`,
admission smoke rows, provider-refresh rows, sentinel drift rows, historical
rows, and audited protocol-violation rows are outside primary confirmatory
inference. Execution and parsing failures after the frozen retry policy are row
outcomes, not complete-case exclusions.

## Benchmark Documentation And Metadata

The artifact documents what the benchmark measures, what it does not measure,
intended use, limitations, release boundaries, and Croissant-style metadata
for dataset review.

Supporting files:

- `artifact/BENCHMARK_CARD.md`
- `artifact/metadata/croissant.json`
- `artifact/metadata/CROISSANT_MAPPING.md`
- `docs/RAI_ETHICS_LIMITATIONS.md`
- `docs/HOSTING_AND_RELEASE_PLAN.md`
- `REPRODUCIBILITY.md`

The Croissant file is an anonymous-review and final-hosting draft with
hosting, DOI, license, and final archive checksum placeholders. Those
placeholders are not submission table-freeze blockers. The submission result
layer is `paper/submission_tables/`.

## Paper Framing

The paper is a measurement paper about reliable co-success. It asks whether
exact-answer success and strict state-governance success co-occur under bounded
state transfer. It does not present SSR as a new method contribution and does
not claim theoretical mutual exclusion between answer success and governance.

Supporting files:

- `artifact/protocol/main_matrix/PAPER_FRAMING_AND_RQS.md`
- `artifact/protocol/main_matrix/PREREGISTERED_DECISION_RULES.md`
- `artifact/protocol/main_matrix/METHOD_CONDITIONS.md`
- `docs/TABLE_FIGURE_REPRODUCTION.md`

The clean-v2 `7,200`-row execution layer is closed, but paper-level
aggregation for submission is frozen separately under
`paper/submission_tables/`.

## Main-Text Table And Figure Source Map

The main-text results surfaces are traceable from manuscript table/figure
numbers back to tracked artifact score rows, generated manuscript table
sources, and offline recomputation scripts. Current numbering is from the
sibling TMLR source repository's `arxiv_submission/main.aux`.

Primary source set:

- `paper/submission_tables/tables/submission_summary.json`: lists the five
  primary score CSVs under `sources.primary` with row counts and SHA-256 hashes.
- `artifact/verification/summarize_submission_tables.py`: defines
  `PRIMARY_SCORE_FILES` and verifies the frozen submission aggregate tables.
- `artifact/results/main_matrix/record_mode_20260627/ALL_MODEL_DIRECT_CLEAN_V2_FROM_ZERO_20260628/*/confirmatory/scores.confirmatory.csv`
- `artifact/results/main_matrix/record_mode_20260627/OPENROUTER_GPT_CLAUDE_CLEAN_V2_FROM_ZERO_20260627/*/confirmatory/scores.confirmatory.csv`
- JSONL counterparts of the same score rows are the input expected by
  `../answer-state-cosuccess-tmlr/arxiv_submission/scripts/generate_interaction_diagnostics.py`
  and `../answer-state-cosuccess-tmlr/arxiv_submission/scripts/generate_statistical_uncertainty.py`.

Table map:

- Table 9, `tab:primary-outcome-crosstab`, manuscript source
  `../answer-state-cosuccess-tmlr/arxiv_submission/tables/table_primary_outcome_crosstab.tex`.
  The table is the 2x2 grouping of `answer_success` and
  `state_governance_success` over the five primary score CSVs. The primary
  denominator and marginal counts are cross-checked by
  `paper/submission_tables/tables/primary_overall.csv` and by
  `python3 artifact/verification/summarize_submission_tables.py --check`.
- Table 10, `tab:governance-landing-base-rate`, manuscript source
  `../answer-state-cosuccess-tmlr/arxiv_submission/tables/table_governance_landing_base_rate.tex`.
  It uses the same primary score rows and computes, for primary overall and the
  displayed method subsets, governance-success rows, `not answer_success and
  state_governance_success`, `P(not answer_success | state_governance_success)`,
  the subset base `P(not answer_success)`, and the delta in percentage points.
  This table does not have a standalone frozen CSV in the artifact.
- Table 11, `tab:answer-correct-state-failed`, generated manuscript source
  `../answer-state-cosuccess-tmlr/arxiv_submission/tables/table_answer_correct_state_failed.tex`.
  It is generated from deterministic scorer flags already present in the source
  score rows, not from human annotations. The source subset is
  `answer_success == true` and `state_governance_success == false` over the
  7,200 primary rows. The priority categories are:
  `output_bearing_state_conflict` -> 323 rows, parsed `RAW` plus
  `state_internal_conflict` -> 102 rows, missing `state_carry_surface_present`
  -> 7 rows, and `state_required_token_negated` or `exclusion_field_conflict`
  -> 469 rows. There is no separate frozen CSV; the verifier/recompute source
  is `generate_interaction_diagnostics.py`.
- Table 13, `tab:ssr-visible-overlap`, generated manuscript source
  `../answer-state-cosuccess-tmlr/arxiv_submission/tables/table_ssr_visible_overlap.tex`.
  It is generated by `generate_interaction_diagnostics.py` from the primary
  score-row JSONL files and frozen manifest, restricted to
  `rolling_visible_carry_forward` and `mature_ssr_loop`, and reports A, G,
  `A and G`, `A and not G`, `not A and G`, `G given A`, and hard-cap rows.

Figure map:

- Figure 2, `fig:primary-three-metrics`:
  `../answer-state-cosuccess-tmlr/arxiv_submission/figures/primary_three_metrics.pdf`.
  Generation path: `../answer-state-cosuccess-tmlr/arxiv_submission/scripts/generate_revision_figures.py`,
  `generate_primary_venn()`. Source counts are the Table 9 answer/governance
  cells and the same primary score rows summarized by `primary_overall.csv`.
- Figure 3, `fig:primary-method-metrics`:
  `../answer-state-cosuccess-tmlr/arxiv_submission/figures/primary_method_metrics.pdf`.
  Generation path: `generate_revision_figures.py`, `generate_primary_method_metrics()`.
  It reads `../answer-state-cosuccess-tmlr/arxiv_submission/tables/table_primary_by_method.tex`;
  the artifact aggregate source is `paper/submission_tables/tables/primary_by_method.csv`.
- Figure 4, `fig:mechanism-2x2`:
  `../answer-state-cosuccess-tmlr/arxiv_submission/figures/mechanism_2x2.pdf`.
  Generation path: `generate_revision_figures.py`, `generate_mechanism_2x2()`.
  It reads `../answer-state-cosuccess-tmlr/arxiv_submission/tables/table_primary_core_2x2.tex`,
  a manuscript table source derived from the primary score rows. There is no
  standalone artifact CSV for this exact 2x2 figure input.
- Figure 5, `fig:primary-contrast-forest`:
  `../answer-state-cosuccess-tmlr/arxiv_submission/figures/primary_contrast_forest.pdf`.
  Generation path: `generate_revision_figures.py`, `generate_primary_contrast_forest()`.
  It reads `../answer-state-cosuccess-tmlr/arxiv_submission/tables/table_primary_contrasts.tex`.
  The bootstrap recomputation path for the same contrast family is
  `../answer-state-cosuccess-tmlr/arxiv_submission/scripts/generate_statistical_uncertainty.py`
  over the primary score-row JSONL files.

Recompute commands:

```bash
python3 artifact/verification/summarize_submission_tables.py --check

cd ../answer-state-cosuccess-tmlr
python3 arxiv_submission/scripts/generate_interaction_diagnostics.py \
  --record-root ../answer-state-cosuccess-tmlr-artifact/artifact/results/main_matrix/record_mode_20260627 \
  --manifest ../answer-state-cosuccess-tmlr-artifact/artifact/protocol/main_matrix/configs/pcg_dynamic_state_v2_confirmatory_40task_5model_6method_2budget_3run_20260625.rows.jsonl

python3 arxiv_submission/scripts/generate_revision_figures.py
```

Tables 10, 11, 13 and Figures 2, 4, 5 are manuscript-generated surfaces
without one-to-one frozen CSVs in this artifact. They remain reviewer-facing
because their `.tex`/PDF outputs, generator scripts, and source score rows are
all named above. They should not be treated as new data.

## Scorer Construct Validity

The paper treats answer recovery and state governance as separate constructs,
but uses `reliable_composite_success` as the primary governed reliability
metric. Standalone `state_governance_success` is diagnostic only and must not
override answer failure. The strict scorer closes the empty-state loophole by
requiring an output-bearing carry surface for governance credit.

Supporting files:

- `artifact/protocol/main_matrix/PREREGISTERED_DECISION_RULES.md`
- `artifact/protocol/main_matrix/METHOD_CONDITIONS.md`
- `artifact/protocol/main_matrix/VARIABLE_CONTROL.md`
- `artifact/verification/replay_ssr_downgrade_from_saved_outputs.py`
- `artifact/results/evidence/ssr_downgrade_20260623/docs/protocol/pcg_dynamic_state_v2_main_matrix/VARIABLE_METHOD_RESULT_EVIDENCE_CHAIN_20260623.md`

This is a measurement and reporting discipline, not a new experiment axis.
`loop_only` is retained as a floor/reference arm and empty-state diagnostic; it
is not interpreted as successful governance when answer recovery fails.

## Deterministic Validity Suite

The deterministic validity suite gives local scale and scorer-ceiling checks
without adding model rows. The visible-only policies run over the frozen
7,200-row manifest, make no LLM calls, and do not read the scorer oracle during
generation. The oracle ceiling row is a scorer reachability check, not a model
baseline.

Supporting files:

- `artifact/results/baselines/minimal_validity_suite_20260706/baseline_config.json`
- `artifact/results/baselines/minimal_validity_suite_20260706/baseline_summary_by_policy.csv`
- `artifact/results/baselines/minimal_validity_suite_20260706/baseline_summary_by_policy_family_difficulty.csv`
- `artifact/results/baselines/minimal_validity_suite_20260706/HASH_MANIFEST.jsonl`
- `artifact/results/baselines/minimal_validity_suite_20260706/BASELINE_INTERLOCK_REPORT.md`
- `artifact/verification/run_minimal_baseline_validity_suite.py`

Verification:

```bash
python3 artifact/verification/run_minimal_baseline_validity_suite.py --check
```

Expected result: `passed: true`, `source_rows: 7200`,
`baseline_score_rows_recomputed: 36000`, `policy_count: 5`,
`api_calls_performed: 0`, and `failure_count: 0`.

Archive note: the compact TMLR archive omits the generated row-level baseline
outputs and scores to stay below the supplement-size limit. They are derived
from the frozen 7,200-row manifest and local deterministic policies; the
verifier rebuilds them under `.verification_build/` and compares regenerated
hashes and summaries with the checked-in compact evidence.

These rows are diagnostic scale checks. They are not pooled with the primary
matrix, Qwen supplement, or budget-300 diagnostics, and they are not used to
rank models or state-transfer methods.

## Qwen3-Coder Budget-300 Diagnostic Slice

The Qwen3-Coder budget-300 sidecar contains 160 diagnostic rows with its own
score and summary files. It is outside both the primary five-model
confirmatory matrix and the Qwen confirmatory supplement aggregation.

Supporting files:

- `artifact/results/main_matrix/record_mode_20260627/OPEN_WEIGHT_QWEN3_CODER_SUPPLEMENT_20260629/openrouter_qwen3_coder_alibaba_supplement/scores.budget300_diagnostic.csv`
- `artifact/results/main_matrix/record_mode_20260627/OPEN_WEIGHT_QWEN3_CODER_SUPPLEMENT_20260629/openrouter_qwen3_coder_alibaba_supplement/scores.budget300_diagnostic.jsonl`
- `artifact/results/main_matrix/record_mode_20260627/OPEN_WEIGHT_QWEN3_CODER_SUPPLEMENT_20260629/openrouter_qwen3_coder_alibaba_supplement/summary.budget300_diagnostic.json`
- `artifact/results/main_matrix/record_mode_20260627/OPEN_WEIGHT_QWEN3_CODER_SUPPLEMENT_20260629/openrouter_qwen3_coder_alibaba_supplement/RUN_REPORT.budget300_diagnostic.md`
- `artifact/results/main_matrix/record_mode_20260627/OPEN_WEIGHT_QWEN3_CODER_SUPPLEMENT_20260629/openrouter_qwen3_coder_alibaba_supplement/openrouter_qwen3_coder_alibaba_supplement_budget300_diagnostic.config.json`
- `artifact/results/main_matrix/record_mode_20260627/OPEN_WEIGHT_QWEN3_CODER_SUPPLEMENT_20260629/openrouter_qwen3_coder_alibaba_supplement/openrouter_qwen3_coder_alibaba_supplement_budget300_diagnostic.cassette.jsonl`
- `artifact/results/main_matrix/record_mode_20260627/OPEN_WEIGHT_QWEN3_CODER_SUPPLEMENT_20260629/openrouter_qwen3_coder_alibaba_supplement/HASH_MANIFEST.budget300_diagnostic.jsonl`

Verification:

```bash
python3 artifact/verification/main_matrix_vcr_runner.py --mode audit \
  --config artifact/results/main_matrix/record_mode_20260627/OPEN_WEIGHT_QWEN3_CODER_SUPPLEMENT_20260629/openrouter_qwen3_coder_alibaba_supplement/openrouter_qwen3_coder_alibaba_supplement_budget300_diagnostic.config.json \
  --cassette artifact/results/main_matrix/record_mode_20260627/OPEN_WEIGHT_QWEN3_CODER_SUPPLEMENT_20260629/openrouter_qwen3_coder_alibaba_supplement/openrouter_qwen3_coder_alibaba_supplement_budget300_diagnostic.cassette.jsonl
```

Expected result: `expected_rows: 160`, `rows_checked: 160`,
`cassette_entries_checked: 160`, `cache_miss_count: 0`,
`failure_count: 0`, and `api_calls_performed: 0`. The summary file records
`score_rows: 160`, `answer_success_count: 22`,
`state_governance_success_count: 40`, `reliable_composite_success_count: 7`,
and `primary_analysis_eligible: false`.

This open-weight supplement compression diagnostic is not used in
`paper/submission_tables/tables/qwen3_coder_supplement_*`, which cover the
1,440-row Qwen confirmatory supplement only.

## DeepSeek V4-Pro API Sanity Diagnostic

The small DeepSeek v4-pro sanity diagnostic gives a learned-policy scale
reference over 40 tasks and can be replayed from saved responses without future
API calls. It is neither a primary model condition nor a rerun of the 7,200-row
DeepSeek primary slice.

Supporting files:

- `artifact/results/baselines/deepseek_v4pro_api_sanity_20260706/deepseek_api_sanity_config.json`
- `artifact/results/baselines/deepseek_v4pro_api_sanity_20260706/deepseek_v4pro_api_sanity.cassette.jsonl`
- `artifact/results/baselines/deepseek_v4pro_api_sanity_20260706/deepseek_api_sanity_scores.jsonl`
- `artifact/results/baselines/deepseek_v4pro_api_sanity_20260706/deepseek_api_sanity_summary_by_policy.csv`
- `artifact/results/baselines/deepseek_v4pro_api_sanity_20260706/HASH_MANIFEST.jsonl`
- `artifact/results/baselines/deepseek_v4pro_api_sanity_20260706/DEEPSEEK_API_SANITY_REPORT.md`
- `artifact/verification/run_deepseek_v4pro_api_sanity.py`

Verification:

```bash
python3 artifact/verification/run_deepseek_v4pro_api_sanity.py --check
```

Expected result: `passed: true`, `rows_replayed: 40`,
`api_calls_performed: 0`, and `failure_count: 0`.

Record mode used direct `deepseek-v4-pro` with 10-way concurrency. Reviewer
verification uses saved-output replay. API keys are not included.

## Model Admission Criteria

Model conditions enter the full main matrix only after passing engineering,
replay, hash, and structured-output gates on the tiny benchmark smoke. Outcome
fields such as `answer_success`, `state_governance_success`, and
`reliable_composite_success` are measured results, not admission filters.

Supporting files:

- `artifact/protocol/main_matrix/admission/MODEL_ADMISSION_CRITERIA_20260626.md`
- `artifact/protocol/main_matrix/admission/MAIN_MATRIX_ADMISSION_GATE_20260625.md`
- `artifact/protocol/main_matrix/admission/benchmark_smoke_20260626/README.md`
- `artifact/protocol/main_matrix/admission/benchmark_smoke_20260626/SUMMARY.json`
- `artifact/protocol/main_matrix/MAIN_RUN_API_POLICY.md`
- `artifact/protocol/main_matrix/admission/VARIABLE_FREEZE_SPEC_20260625.yaml`
- `artifact/protocol/main_matrix/admission/AUDIT_LEDGER_20260625.jsonl`

This criterion does not create primary result rows by itself. The admission
gate was followed by clean-v2 record-mode execution for all five frozen model
conditions. The execution closure is recorded in
`artifact/results/main_matrix/record_mode_20260627/CLEAN_V2_MATRIX_EXECUTION_CLOSURE_20260629.md`;
it closes row-level execution and VCR audit, not final paper aggregation or
statistical interpretation. The submission aggregation layer is frozen under
`paper/submission_tables/`.

## Clean-V2 Main-Matrix Execution Closure

The five-model clean-v2 confirmatory execution layer completed under the v2
direct-network protocol, with VCR record/replay/audit closure for the
primary-candidate slices.

Supporting files:

- `artifact/results/main_matrix/record_mode_20260627/CLEAN_V2_MATRIX_EXECUTION_CLOSURE_20260629.md`
- `artifact/results/main_matrix/record_mode_20260627/CLEAN_V2_MATRIX_MODEL_STATUS_20260629.csv`
- `artifact/results/main_matrix/record_mode_20260627/ALL_MODEL_DIRECT_CLEAN_V2_FROM_ZERO_20260628/`
- `artifact/protocol/main_matrix/V2_DIRECT_NETWORK_EXECUTION_PROTOCOL_20260628.md`

This is execution closure, not the final aggregation table, mixed-effects model
output, method ranking, or abstract-level headline claim.
The submission descriptive aggregate tables are stored under
`paper/submission_tables/`.

## Excluded Proxy-Mediated First-Pass History

The old first-pass/proxy-mediated five-model run is retained as excluded
history and can be checked offline, but it is not part of the primary TMLR
result layer.

Supporting files:

- `artifact/results/main_matrix/record_mode_20260627/excluded_history/README.md`
- `artifact/results/main_matrix/record_mode_20260627/excluded_history/proxy_mediated_first_pass_20260627/README.md`
- `artifact/results/main_matrix/record_mode_20260627/excluded_history/proxy_mediated_first_pass_20260627/`
- `artifact/verification/verify_excluded_history_first_pass.py`

Verification:

```bash
python3 artifact/verification/verify_excluded_history_first_pass.py
```

Expected result: `passed: true`, `observed_rows_checked: 4843`,
`cassette_entries_checked: 4843`, `api_calls_performed: 0`, and
`failure_count: 0`.

This is audit-lineage evidence only. DeepSeek, Kimi, and Qwen keep their
original runner cassette/hash/summary closure. The stopped GPT and Claude old
slices did not have a found original runner cassette/hash/summary; they are
closed as observed partial saved-output replay from
`adapter_source.confirmatory.jsonl`. Do not substitute the later clean-v2
GPT/Claude 1,440-row cassettes into this old first-pass history.

## SSR Downgrade

The mature/schema-heavy SSR condition is retained as an ablation and
diagnostic condition, not as a primary method candidate.

Supporting files:

- `artifact/results/evidence/ssr_downgrade_20260623/README.md`
- `artifact/results/evidence/ssr_downgrade_20260623/E5_INTERLOCK_REPORT_20260623.md`
- `artifact/results/evidence/ssr_downgrade_20260623/docs/protocol/pcg_dynamic_state_v2_main_matrix/SSR_DOWNGRADE_EVIDENCE_CHAIN_20260623.md`
- `artifact/results/evidence/ssr_downgrade_20260623/docs/protocol/pcg_dynamic_state_v2_main_matrix/VARIABLE_METHOD_RESULT_EVIDENCE_CHAIN_20260623.md`
- `artifact/results/evidence/ssr_downgrade_20260623/docs/protocol/pcg_dynamic_state_v2_main_matrix/HASH_INTERLOCK_REPORT_20260623.md`

This is not a universal claim that all SSR methods fail.

## Historical Evidence Disposition

Older SSR-positive evidence was not inherited into the current primary matrix
without stricter controls.

Supporting files:

- `artifact/results/evidence/ssr_downgrade_20260623/historical_matrixgate_20260618/MAIN_MATRIX_GATE.md`
- `artifact/results/evidence/ssr_downgrade_20260623/HISTORICAL_EVIDENCE_PUBLIC_HASH_MANIFEST.jsonl`
- `artifact/protocol/main_matrix/LEGACY_RESULT_DISPOSITION.md`

Historical probes may be discussed as motivation or method lineage, not pooled
into the primary matrix.

## Hash And Raw-Output Verification

The included SSR downgrade evidence packet can be checked from released files.

Supporting files:

- `artifact/results/evidence/ssr_downgrade_20260623/verify_public_hash_locks.py`
- `artifact/results/evidence/ssr_downgrade_20260623/verify_e5_interlock.py`
- `artifact/results/evidence/ssr_downgrade_20260623/data/pcg_dynamic_state_v2/h5_release_lock_20260623/`
- `artifact/results/evidence/ssr_downgrade_20260623/data/pcg_dynamic_state_v2/h5_targeted_backfill_lock_20260623/`
- `artifact/results/evidence/ssr_downgrade_20260623/data/pcg_dynamic_state_v2/h5_static_sanity_lock_20260623/`
- `ARTIFACT_EVALUATION.md`

The strict E5 verifier uses Git metadata and repository cleanliness when run
from an anonymous Git clone. The generated `git archive` review package has no
`.git` directory, so archive-mode verification focuses on internal hash
closure and treats unpacked-directory Git cleanliness as not applicable.

## Sentinel Drift Audit

Sentinel probes, if run, audit endpoint stability during an experiment window.

Supporting files:

- `artifact/protocol/sentinel_drift_probe/README.md`
- `artifact/results/sentinel_drift_probe_results/README.md`

Sentinel probes are not included in the 7,200 primary rows or the 800-row
low-budget diagnostic probe, and are not used in primary outcome estimation.

## Release And Responsible-Use Boundary

Reviewer access should not require private requests to the authors, and the
artifact should not be used beyond its documented benchmark scope.

Supporting files:

- `docs/HOSTING_AND_RELEASE_PLAN.md`
- `docs/RAI_ETHICS_LIMITATIONS.md`
- `ANONYMITY.md`
- `ANONYMITY_CHECKLIST.md`
- `scripts/build_review_archive.sh`

Anonymous review can use this anonymized archive or an anonymous Git
repository. Public release should use a separate public-lite package unless the
raw/VCR release boundary is deliberately widened. Final public release should
update hosting URLs, Croissant fields, license, DOI, and final archive hashes.
