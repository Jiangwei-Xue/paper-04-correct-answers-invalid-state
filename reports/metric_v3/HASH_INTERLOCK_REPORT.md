# Manuscript Data-Completeness and Hash-Interlock Audit

**Audit date:** 2026-09-03  
**Manuscript in scope:** `submission/arxiv_revised_v3_20260902/main.tex`  
**Scope:** Local availability, row-level lineage, hash closure, and numerical replay for every empirical result surface cited by the current V3 manuscript. This is an offline audit; it does not make provider calls and is not a public-release verification.

## Summary

The local repository contains the data required for every claim-bearing V3 result, every supporting evidence tier, and the retained V1 sensitivity results. The V3 primary chain is complete from saved V2 raw rows and V2 answer labels through V3 inputs, V3 scores, and the separately implemented executor report. All audited source hashes and row identities passed.

The manuscript is **not yet a clean numerical-reproduction pass** because the legacy V1 bootstrap table contains six confidence-interval endpoints across five paired-contrast rows that do not match the locally replayed, seed-documented historical bootstrap generator. All affected point estimates match. This is confined to a non-claim-bearing legacy sensitivity table, but it should be resolved before submission by either restoring the generator that produced the displayed endpoints or replacing the displayed endpoints with the reproducible replay values.

## Evidence inventory and results

| Surface | Local source and lineage | Result |
|---|---|---|
| V3 primary matrix | 7,200 saved V2 raw rows -> V2 score/answer labels -> V3 inputs -> V3 scores | PASS |
| V3 budget-300 diagnostic | 800 rows with the same four-stage lineage | PASS |
| V3 Qwen supplement | 1,440 rows with the same four-stage lineage | PASS |
| V3 Qwen budget-300 diagnostic | 160 rows with the same four-stage lineage | PASS |
| V3 DeepSeek sanity check | 40 rows with the same four-stage lineage | PASS |
| V3 deterministic validity suite | 36,000 locally generated control rows, with no API raw-response hash expected by design | PASS |
| V3 executor criterion report | 7,200 row ids matched; offline analysis replay was byte-identical to the saved report | PASS |
| Representation-invariance gate | 10 canonical cases x 3 supported formats | PASS |
| New model-by-budget hard-cap table | 7,200 primary rows joined to hash-verified saved provider records | PASS |
| Frozen V1 aggregate tables | Five primary score files (7,200), five budget-300 files (800), and Qwen supplement (1,440) | PASS |
| V1 task/run/family/parse/Qwen/budget/control tables in manuscript | Mechanically reaggregated directly from the local row-level scores | PASS |
| V1 task-cluster bootstrap table | Current displayed paired-contrast intervals versus local deterministic replay | CONDITIONAL -- six endpoints mismatch |
| Figures | Five rendered figure assets are local; Figures 1--4 also have an editable PPTX source | PASS for data availability; R1 for Figure 5 editability |

## Hash and row-identity checks

The V3 manifest records six evidence tiers totaling 45,640 rows. For all six tiers, the audit checked the V3 raw/input/score row-id sets, source output and state values, V2 answer labels, and the manifest SHA-256 values. Fourteen saved provider-source files and six final-answer-label source files were hash-verified. The 36,000 deterministic rows are local policy/control records and correctly carry no API raw-response hash.

The V3 verifier completed offline with these asserted properties:

- `primary_rows = 7200`
- `deterministic_rows = 36000`
- `representation_cases = 10`
- `task_count = 40`
- `network_calls_performed = 0`

The executor analysis was rerun with 10,000 task-cluster bootstrap replicates and seed `20260813`; its regenerated JSON was byte-identical to `reports/metric_v3/independent_executor_v3_report.json`.

The new within-condition budget table was regenerated from the saved V3 scores and provider-source hard-cap flags. It covered all 7,200 primary rows, verified all five source-file hashes, made zero network calls, and produced `173` joint rows and `180` answer-aligned-validity rows, matching the primary V3 report.

## Numerical spot checks against manuscript tables

The following manuscript results were recomputed from local row-level records and match the displayed values:

- V3 primary counts: final-answer success `696`, intrinsic validity `191`, answer-aligned validity `180`, and joint success `173` of 7,200.
- V3 answer/state cross-tabulation, component counts, six protocol profiles, V2-to-V3 transition, answer-denominator crosswalk, and method-blocked executor counts and intervals.
- V3 model-by-budget hard-cap table: all 10 model/budget cells (720 rows each).
- V1 model-by-protocol joint table; four-core-protocol model table; task-family, difficulty, run-level, parse-sensitivity, Qwen overlap, budget-300, deterministic-control, DeepSeek sanity, and product-of-margins tables.
- The frozen aggregate-table checker completed with no discrepancy for its 12 managed summary files.

## Legacy bootstrap discrepancy

The historical generator `historical_inputs/arxiv_source_20260702_working_copy/scripts/generate_statistical_uncertainty.py` was replayed against the active 7,200-row primary score JSONL files and 1,440-row Qwen supplement, using its documented 10,000 task-cluster replicates and seed `20260704`. Headline intervals and all displayed point estimates agree. The following current-manuscript interval endpoints do not agree with that reproducible replay:

| Contrast and outcome | Displayed in current manuscript | Local replay |
|---|---:|---:|
| Visible carry minus SSR no-carry, Answer upper bound | `+50.92` pp | `+51.00` pp |
| Visible carry minus SSR no-carry, Validity bounds | `[-17.75, -7.42]` pp | `[-17.67, -7.50]` pp |
| Visible carry minus SSR no-carry, Joint lower bound | `+12.17` pp | `+12.08` pp |
| SSR+carry minus visible carry, Answer upper bound | `-41.67` pp | `-41.83` pp |
| SSR+carry minus visible carry, Joint upper bound | `-3.83` pp | `-3.75` pp |

This is a reproducibility-binding issue, not missing experimental data: the full row-level data and a documented historical generator are local. Before submission, retain a source-controlled generator for the displayed values or replace the six endpoints with the replayed values. No V3 claim-bearing result is affected.

## Red flags and required fixes

1. **R1 -- bind the legacy bootstrap interval table to a generator.** Resolve the six endpoint differences above; do not leave the table as manually maintained numeric text.
2. **R1 -- Figure 5 source/editability.** `fig06_product_reference.pdf/png` is present and its data are recomputable from local V1 scores, but the current editable PowerPoint contains only Figures 1--4 and no current Figure 5 generator/source is packaged beside the manuscript.
3. **R1 -- executable interface.** The manuscript prints `./scripts/verify_metric_v3.sh`, but the tracked script currently lacks its executable bit. `bash scripts/verify_metric_v3.sh` passes. Restore execute permission or revise the documented invocation before a public release.
4. **R1 -- public-release boundary.** This audit establishes local data completeness only. `experiment-release` has not been run for a clean public submission tree, so no public-release or submission-package PASS is claimed.

## Pass/fail table

| Gate | Status |
|---|---|
| Required local row-level data present | PASS |
| V3 source-to-score hash interlock | PASS |
| V3 primary and executor numerical replay | PASS |
| Legacy V1 aggregate and static-table replay | PASS |
| Legacy V1 bootstrap-interval numerical replay | CONDITIONAL |
| Figure data presence | PASS |
| Full editable/rebuildable figure provenance | CONDITIONAL |
| Public-release verification | NOT RUN |

## Machine-readable finding JSON

```json
{
  "schema": "pcg.manuscript_data_completeness_audit.v1",
  "audit_date": "2026-09-03",
  "manuscript": "submission/arxiv_revised_v3_20260902/main.tex",
  "overall_status": "LOCAL_DATA_COMPLETE_WITH_REPRODUCTION_FIXES_REQUIRED",
  "network_calls_performed": 0,
  "tiers_checked": {
    "primary": 7200,
    "primary_budget300": 800,
    "qwen": 1440,
    "qwen_budget300": 160,
    "deepseek_sanity": 40,
    "deterministic_validity_suite": 36000
  },
  "lineage": {
    "source_provider_files_hash_verified": 14,
    "answer_label_files_hash_verified": 6,
    "executor_rows_checked": 7200,
    "all_v3_tier_row_id_sets_matched": true
  },
  "findings": [
    {
      "id": "MDC_001",
      "severity": "R0",
      "status": "pass",
      "claim": "All claim-bearing V3 data and saved-output lineage are locally present and hash-verifiable."
    },
    {
      "id": "MDC_002",
      "severity": "R1",
      "status": "conditional",
      "claim": "Six endpoints in five non-claim-bearing legacy bootstrap rows do not match the available seed-documented local generator."
    },
    {
      "id": "MDC_003",
      "severity": "R1",
      "status": "conditional",
      "claim": "All figure data/rendered assets are local, but Figure 5 lacks a current editable or regenerating source beside the manuscript."
    },
    {
      "id": "MDC_004",
      "severity": "R1",
      "status": "not_run",
      "claim": "No clean public submission-tree release verification has been performed in this audit."
    }
  ]
}
```
