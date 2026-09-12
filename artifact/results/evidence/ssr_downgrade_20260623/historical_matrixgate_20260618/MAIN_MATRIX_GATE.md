# Main Matrix Gate Report

Generated UTC: 2026-06-18T02:41:07.294472+00:00  
Workspace: `<AUTHOR_LOCAL_WORKSPACE>`  
Candidate for main matrix: `<AUTHOR_LOCAL_WORKSPACE>/artifact-ssr-public`  
Candidate HEAD: `582acefbe1afb21ead789e3aa64da98c1514c452`  
Scope excluded: paper EV / external validity, to be reviewed by Code X.

## Decision

`NO_GO` for direct entry of current `artifact-ssr-public` into the main matrix.

This is not a judgment that the project is unrecoverable. It means the current candidate artifact is a curated public release/control-provenance package and OpenRouter preflight package, not a fresh-admission/main-matrix evidence package. The recoverable path is `HOLD -> fresh freeze packet -> rerun admission -> post-run audit -> new gate`.

## Executive Summary

The historical gate audit concluded that no current run in `artifact-ssr-public` satisfies the hard criteria for main matrix entry. The artifact contains useful forward controls, OpenRouter route/access evidence, historical processed CSVs, and public release manifests. It does not contain a closed E4/E5 reproducibility chain for candidate matrix rows.

The candidate's own readiness document states the project is not ready for formal main matrix execution and lists missing freeze artifacts: fresh admission protocol/configs/task manifest, final model identities, runner/scorer/oracle hashes, endpoint inventory refresh, raw manifest policy, post-run audit template, and pre-result commit/tag.

## Critical Findings

| ID | Finding | Severity | Blocks |
|---|---|---:|---:|
| TF-001 | OpenRouter config/task lineage was not frozen before recorded outputs in the source chronology. | R3 | yes |
| MD-001 | No fresh five-model admission or main-matrix freeze exists in the current candidate. | R4 | yes |
| PVC-002 | OpenRouter configs declare manifest hash `6ab8fa6b...`, while shipped preflight subset hashes to `3e5ee486a5f894405b378e5481b8044b844137d579bce2c0388bd00dc39a3d83`. | R4 | yes |
| HASH-001 | `HASH_MANIFEST.jsonl` is absent; release manifest is stale: 4 mismatches, 2 missing-current entries, 13 extras. | R4 | yes |
| HASH-003 | Claude preflight prose audit conflicts with score row `reliable_success=0`, `failure_type=final_exact_failure`. | R3 | yes |
| OR-001 | OpenRouter route metadata is adequate as preflight evidence only, not matrix evidence. | R3 | yes |
| CL-001 | Raw preflight traces indicate model-visible scoring-boundary/forbidden-label exposure. | R3 | yes |
| CL-002 | Local Qwen32B public result set was operationally repaired by removing 437 backend-error rows. | R3 | yes |

## Safe To Enter Main Matrix

None.

## Safe Only As Provenance / Pilot Evidence

- v4 variable-control registry and model-condition cards.
- OpenRouter GPT-5.5 / Claude 4.8 one-task preflight rows as access/routing/metadata evidence.
- Endpoint inventories and private raw manifest hashes as preflight audit artifacts.
- Historical/local processed CSVs as legacy provenance only, not fresh matrix evidence.

## Must Exclude From Current Main Matrix

- OpenRouter GPT-5.5 one-row preflight as outcome evidence.
- OpenRouter Claude 4.8 one-row preflight as outcome evidence; task failed.
- Old direct-provider GPT/Kimi records as fresh evidence.
- Local Qwen32B repaired/backend-recovery result sets.
- Legacy 30-task DeepSeek/Qwen/Llama public processed CSVs as fresh matrix evidence.

## Must Rerun

Run a fresh admission and later main matrix only after a pre-result freeze packet exists. Required frozen inputs include final model list, task manifest, configs, runner, scorer/oracle, endpoint inventory, retry/backend policy, raw-manifest policy, and post-run audit template.

## Evidence Notes

The candidate inventory hashed 149 non-git candidate files. See `CANDIDATE_CURRENT_FILE_HASHES.csv` and `CANDIDATE_CURRENT_HASH_MANIFEST.jsonl` in this report folder.

Release manifest comparison: `match=132`, `hash_mismatch=4`, `missing_current=2`, `extra_current=13`. The mismatches include `README.md`, `ARTIFACT_MANIFEST.md`, and both OpenRouter configs.

## Machine-Readable Decision

```json
{
  "decision": "NO_GO",
  "candidate": "artifact-ssr-public",
  "candidate_head": "582acefbe1afb21ead789e3aa64da98c1514c452",
  "safe_runs": [],
  "excluded_runs": [
    "openrouter_gpt55_runner_preflight_1task_1method_1budget_1run_as_outcome_evidence",
    "openrouter_claude48_runner_preflight_1task_1method_1budget_1run_as_outcome_evidence",
    "legacy_direct_provider_rows_as_fresh_evidence",
    "local_qwen25_coder32b_repaired_rows",
    "legacy_processed_csvs_as_fresh_matrix_evidence"
  ],
  "rerun_required": ["fresh_five_model_admission", "future_main_matrix"],
  "blocking_findings": [
    "TF-001",
    "MD-001",
    "PVC-001",
    "PVC-002",
    "HASH-001",
    "HASH-002",
    "HASH-003",
    "OR-001",
    "CL-001",
    "CL-002"
  ],
  "out_of_scope": ["paper_ev"],
  "confidence": "high"
}
```
