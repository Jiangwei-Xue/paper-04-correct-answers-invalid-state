# Croissant Metadata Mapping

This note explains how `croissant.json` maps the artifact to Croissant-style
dataset metadata. The Croissant file is a submission-time draft: hosting URLs,
DOI, license URL, and final archive checksums must be replaced after the
release host is chosen.

## Metadata Role

The artifact is described as an anonymous review artifact with:

- frozen benchmark protocol;
- task, oracle, config, and row manifests;
- admission and provider-route evidence;
- clean-v2 7,200-row execution closure records;
- scoped SSR-downgrade saved-output evidence;
- submission aggregate result tables under `paper/submission_tables/`;
- reserved locations for later public-hosting metadata and manuscript-level
  statistical interpretation.

It is described as an anonymous-review and final-hosting metadata draft. Hosting
URLs, DOI, license URL, and final archive checksums are still placeholders, but
those placeholders do not block the submission public-lite result freeze under
`paper/submission_tables/`.

## Distribution Objects

| Croissant id | Artifact path | Role |
| --- | --- | --- |
| `fo_benchmark_card` | `artifact/BENCHMARK_CARD.md` | reviewer-facing benchmark card |
| `fo_confirmatory_config` | `artifact/protocol/main_matrix/configs/pcg_dynamic_state_v2_confirmatory_40task_5model_6method_2budget_3run_20260625.json` | frozen confirmatory config |
| `fo_confirmatory_rows` | `artifact/protocol/main_matrix/configs/pcg_dynamic_state_v2_confirmatory_40task_5model_6method_2budget_3run_20260625.rows.jsonl` | 7,200 planned confirmatory rows |
| `fo_budget300_config` | `artifact/protocol/main_matrix/configs/pcg_dynamic_state_v2_budget300_diagnostic_40task_5model_4method_1budget_1run_20260625.json` | frozen budget-300 diagnostic config |
| `fo_budget300_rows` | `artifact/protocol/main_matrix/configs/pcg_dynamic_state_v2_budget300_diagnostic_40task_5model_4method_1budget_1run_20260625.rows.jsonl` | 800 planned diagnostic rows |
| `fo_freeze_summary` | `artifact/protocol/main_matrix/admission/FREEZE_SUMMARY_20260625.json` | row counts, hashes, current gate |
| `fo_variable_freeze_spec` | `artifact/protocol/main_matrix/admission/VARIABLE_FREEZE_SPEC_20260625.yaml` | frozen variables and manifest links |
| `fo_provider_snapshot` | `artifact/protocol/main_matrix/admission/PROVIDER_SUPPORTED_PARAMETER_SNAPSHOT_20260625.json` | provider/request controls |
| `fo_admission_summary` | `artifact/protocol/main_matrix/admission/benchmark_smoke_20260626/SUMMARY.json` | model-admission smoke summary |
| `fo_clean_v2_execution_closure` | `artifact/results/main_matrix/record_mode_20260627/CLEAN_V2_MATRIX_EXECUTION_CLOSURE_20260629.md` | clean-v2 row-level execution closure |
| `fo_clean_v2_model_status` | `artifact/results/main_matrix/record_mode_20260627/CLEAN_V2_MATRIX_MODEL_STATUS_20260629.csv` | per-model execution status |
| `fo_ssr_evidence_readme` | `artifact/results/evidence/ssr_downgrade_20260623/README.md` | scoped evidence packet boundary |
| `fo_ssr_e5_report` | `artifact/results/evidence/ssr_downgrade_20260623/E5_INTERLOCK_REPORT_20260623.md` | E5 interlock report |
| `fs_released_raw_outputs` | `artifact/results/evidence/ssr_downgrade_20260623/released_raw_outputs/model_outputs/` | released raw outputs for scoped evidence |

Reviewer archives should include only anonymized released files and must
exclude local-only directories.

## Record Sets

`rs_main_matrix_frozen_rows`

Source:

- `fo_confirmatory_rows`
- `fo_budget300_rows`

Representative fields:

- `row_id`
- `global_artifact_id`
- `task_id`
- `task_family`
- `task_difficulty`
- `model_condition_id`
- `provider`
- `access_path`
- `requested_model`
- `method`
- `method_protocol_version`
- `budget`
- `run_id`
- `matrix_role`
- `primary_analysis_eligible`
- `logical_request_hash`
- `prompt_template_sha256`
- `request_controls_sha256`
- `task_manifest_entry_sha256`
- `oracle_entry_sha256`
- `openrouter_used`
- `fallback_enabled`

`rs_task_manifests`

Source:

- `MODEL_VISIBLE_TASK_MANIFEST.jsonl`
- `SCORER_ORACLE_MANIFEST.jsonl`
- `TASK_PROVENANCE_MANIFEST.jsonl`
- `TASK_SPLIT_AUDIT.json`

Representative fields:

- `task_id`
- `family`
- `difficulty`
- model-visible segment fields;
- scorer-only oracle fields;
- generation/provenance metadata;
- split-audit status.

`rs_admission_smoke_rows`

Source:

- `artifact/protocol/main_matrix/admission/benchmark_smoke_20260626/*/CONTROLLED_ROWS.confirmatory.jsonl`
- `artifact/protocol/main_matrix/admission/benchmark_smoke_20260626/*/scores.confirmatory.jsonl`
- corresponding budget-300 diagnostic admission files.

Boundary: admission-only, not primary aggregation.

`rs_scoped_evidence_rows`

Source:

- scoped SSR downgrade controlled rows;
- score rows;
- H5 row manifests;
- released raw-output references.

Boundary: supports method-disposition evidence, not completed primary
main-matrix results.

`rs_clean_v2_execution_closure`

Source:

- `artifact/results/main_matrix/record_mode_20260627/CLEAN_V2_MATRIX_EXECUTION_CLOSURE_20260629.md`
- `artifact/results/main_matrix/record_mode_20260627/CLEAN_V2_MATRIX_MODEL_STATUS_20260629.csv`
- five clean-v2 model-condition slice directories under
  `artifact/results/main_matrix/record_mode_20260627/ALL_MODEL_DIRECT_CLEAN_V2_FROM_ZERO_20260628/`

Boundary: row-level execution and VCR audit closure only. This record set does
not contain final paper aggregation tables, mixed-effects model outputs, method
rankings, or headline claims.

`rs_budget300_diagnostic_summary`

Source:

- `artifact/results/evidence/budget_300_diagnostic_20260625/budget_300_summary.json`
- `artifact/results/evidence/budget_300_diagnostic_20260625/budget_300_by_method_budget.csv`

Boundary: descriptive diagnostic only.

## RAI Mapping

The RAI fields in `croissant.json` should point to:

- intended use: `artifact/BENCHMARK_CARD.md`
- limitations: `docs/RAI_ETHICS_LIMITATIONS.md`
- closed-model drift boundary: `REPRODUCIBILITY.md`
- hosting/access plan: `docs/HOSTING_AND_RELEASE_PLAN.md`
- anonymity boundary: `ANONYMITY.md`

The submission-time RAI/provenance fields include:

- `rai:intendedUse`
- `rai:limitations`
- `rai:dataLimitations`
- `rai:dataBiases`
- `rai:personalSensitiveInformation`
- `rai:dataUseCases`
- `rai:dataSocialImpact`
- `rai:hasSyntheticData`
- `prov:wasDerivedFrom`
- `prov:wasGeneratedBy`

`prov:wasDerivedFrom` points to the frozen task/oracle manifests, row
manifests, and scoped saved-output evidence packet. `prov:wasGeneratedBy`
points to the freeze, verification, replay, and diagnostic-summary scripts.

## Placeholders To Resolve Before Public Hosting

Replace these after the final host is chosen:

- `url`;
- `sameAs`;
- `contentUrl` for each file object;
- archive-level checksum and size;
- DOI or persistent identifier;
- public license URL;
- `datePublished`;
- release `version`;
- final citation text;
- creator/publisher identity policy after anonymity is no longer needed.
