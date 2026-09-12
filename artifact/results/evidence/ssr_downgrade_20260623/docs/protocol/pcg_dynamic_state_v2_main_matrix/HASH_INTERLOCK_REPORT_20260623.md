# Hash Interlock Report: SSR-Downgrade Evidence

Date: 2026-06-23

Scope: evidence used for the scoped claim that tested mature/schema-heavy SSR
does not show independent advantage in PCG dynamic-state probes. Paper external
validity is out of scope.

## Summary

Status: `H5_PRIVATE_RAW_LOCK` for the core non-Claude/GPT SSR-downgrade
evidence plus the 2026-06-23 targeted missing-row backfill addendum; not yet
`H5_PUBLIC_RELEASE_LOCK`.

The PCG v2 result rows contain strong row-level hash fields, including
`h5_chain_hash`, `manifest_entry_hash`, `config_sha256`, `runner_sha256`,
`task_manifest_sha256`, `scorer_oracle_sha256`, `prompt_hash`,
`request_hash`, `raw_response_sha256`, `parsed_output_sha256`, and
`metric_record_sha256`.

This report was written before the anonymous review package was assembled. It
is retained as a historical hash-interlock audit, not as the current submission
disposition. The current release status is governed by the package README,
`E5_INTERLOCK_REPORT_20260623.md`, `verify_public_hash_locks.py`,
`verify_e5_interlock.py`, and `scripts/check_anonymity.sh`.

At the time of this historical audit, the local working copy still had these
release-preparation blockers:

- `parser_sha256` and `eval_harness_sha256` are missing in inspected
  `CONTROLLED_ROWS.jsonl` rows.
- `environment_hash_or_commit` is `git_not_invoked_by_policy`, not a code
  commit, lockfile hash, or reproducible environment hash.
- `scores.jsonl` and `scores.csv` do not carry the row-level H5 fields.
- `raw_response_sha256` is an internal canonical JSON hash, not a byte hash of
  the public raw file artifact.
- result preflight manifests contained local-path placeholders that required
  release redaction and explicit original/public SHA-256 mapping.
- the local working copy contained ignored local-only materials that should
  never be included in a reviewer archive.
- Git metadata and reviewer-visible paths still needed a submission-time
  anonymity check.

Conclusion: the core non-Claude/GPT evidence and the targeted two-row backfill
were locked to raw artifacts with verifiers. At this historical checkpoint they
were usable as internal H5 evidence locks and for scoped paper drafting, while
anonymous release packaging still remained to be done. Later reviewer-facing
package files supersede this paragraph for current submission readiness.

## H5 Private Raw Lock Added

The following lock packet has been generated:

- `data/pcg_dynamic_state_v2/h5_release_lock_20260623/H5_LOCK_SUMMARY.json`
- `data/pcg_dynamic_state_v2/h5_release_lock_20260623/ROW_H5_MANIFEST.jsonl`
- `data/pcg_dynamic_state_v2/h5_release_lock_20260623/ARTIFACT_HASH_MANIFEST.jsonl`
- `data/pcg_dynamic_state_v2/h5_release_lock_20260623/ENVIRONMENT_LOCK.json`
- `data/pcg_dynamic_state_v2/h5_release_lock_20260623/scores_with_h5_hashes.csv`

Generation and verification scripts:

- `tools/pcg_dynamic_state_v2/build_pcg_dynamic_state_v2_h5_release_lock.py`
- `tools/pcg_dynamic_state_v2/verify_pcg_dynamic_state_v2_h5_release_lock.py`

Verification result:

```text
passed: true
row_manifest_rows: 644
h5_private_raw_lock_rows: 644
failures: []
```

Targeted backfill addendum generated after the API backfill:

- `data/pcg_dynamic_state_v2/h5_targeted_backfill_lock_20260623/H5_LOCK_SUMMARY.json`
- `data/pcg_dynamic_state_v2/h5_targeted_backfill_lock_20260623/ROW_H5_MANIFEST.jsonl`
- `data/pcg_dynamic_state_v2/h5_targeted_backfill_lock_20260623/ARTIFACT_HASH_MANIFEST.jsonl`
- `data/pcg_dynamic_state_v2/h5_targeted_backfill_lock_20260623/ENVIRONMENT_LOCK.json`
- `data/pcg_dynamic_state_v2/h5_targeted_backfill_lock_20260623/backfill_scores_with_h5_hashes.csv`

Backfill verification result:

```text
passed: true
row_manifest_rows: 2
h5_private_raw_lock_rows: 2
artifact_manifest_rows: 23
failures: []
```

Canonical static sanity addendum generated after the API sanity run:

- `data/pcg_dynamic_state_v2/h5_static_sanity_lock_20260623/H5_LOCK_SUMMARY.json`
- `data/pcg_dynamic_state_v2/h5_static_sanity_lock_20260623/ROW_H5_MANIFEST.jsonl`
- `data/pcg_dynamic_state_v2/h5_static_sanity_lock_20260623/ARTIFACT_HASH_MANIFEST.jsonl`
- `data/pcg_dynamic_state_v2/h5_static_sanity_lock_20260623/ENVIRONMENT_LOCK.json`
- `data/pcg_dynamic_state_v2/h5_static_sanity_lock_20260623/static_sanity_scores_with_h5_hashes.csv`

Static sanity verification result:

```text
passed: true
row_manifest_rows: 4
h5_private_raw_lock_rows: 4
artifact_manifest_rows: 30
failures: []
```

## Evidence Reviewed

- `results/_probe_ecvs_deepseek_v4pro_pcg_dynamic_state_v2_e10_h3_decisive_13task_4method_2budget_1run/CONTROLLED_ROWS.jsonl`
- `results/_probe_deepseek_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_rerun100/CONTROLLED_ROWS.jsonl`
- `results/_probe_qwen37max_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_50workers/CONTROLLED_ROWS.jsonl`
- `results/_probe_kimi_k26_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_50workers/CONTROLLED_ROWS.jsonl`
- `results/pcg_dynamic_state_v2_targeted_missing_rows_backfill_20260623/BACKFILL_CONTROLLED_ROWS.jsonl`
- `results/pcg_dynamic_state_v2_static_sanity_deepseek_1task_4method_budget600_1run_20260623/CONTROLLED_ROWS.jsonl`
- matching `scores.jsonl`, `scores.csv`, `PREFLIGHT_HASH_MANIFEST.jsonl`, and
  `PREFLIGHT_SHA256SUMS.txt` files for the same packets.
- targeted backfill `BACKFILL_SCORES.*`, `BACKFILL_AUDIT.*`,
  `MISSINGNESS_SENSITIVITY_AUDIT.md`, and private raw refs.
- static sanity `STATIC_SANITY_GATE_REPORT.md`, `STATIC_SANITY_SUMMARY.json`,
  and private raw refs.
- repository `.gitignore`, root file inventory, and `git remote -v`.

## Interlock Strength Table

| evidence packet | rows | row h5 present | row manifest present | effective parser/eval hash | env lock status | release grade |
|---|---:|---:|---:|---:|---|---|
| DeepSeek decisive 104-row PCG v2 | 104 | 104/104 | 104/104 | release manifest | environment lock | H5 private raw |
| DeepSeek random10 rerun100 | 180 | 180/180 | 180/180 | release manifest | environment lock | H5 private raw |
| Qwen random10 | 180 | 180/180 | 180/180 | release manifest | environment lock | H5 private raw |
| Kimi random10 | 180 | 180/180 | 180/180 | release manifest | environment lock | H5 private raw |
| Targeted missing-row backfill | 2 | 2/2 | 2/2 | addendum manifest | environment lock | H5 private raw |
| Canonical static sanity gate | 4 | 4/4 | 4/4 | addendum manifest | environment lock | H5 private raw |
| GPT official 7-task | 126 | 126/126 | 126/126 | 126/126 | placeholder | H4 internal, incomplete rows |
| GPT official missing-four | 72 | 72/72 | 72/72 | 72/72 | placeholder | H4 internal |

The H5 private raw classification means the manifest closes each core row
through dataset/oracle, config, runner, effective scorer/parser, environment
lock, prompt, request, private raw byte hash, parsed output, score row, metric,
and release row hash. It is still not H5 public release because raw artifacts
are private and the anonymous release repository has not been assembled.

## What Is Already Good

- Every inspected `CONTROLLED_ROWS.jsonl` row has unique `h5_chain_hash` and
  `manifest_entry_hash`.
- Rows include task, oracle, config, runner, prompt, request, raw-response,
  parsed-output, and metric hashes.
- Provider route, requested model, selected/returned model, fallback status,
  reasoning-content status, temperature, and max token metadata are recorded in
  inspected rows.
- The current PCG v2 freeze packet hashes task manifests, protocol docs, strict
  scorer, configs, and canonical six-method runners.

## What Blocks H5 Public Release

| blocker | severity | action |
|---|---|---|
| Missing parser/eval harness hashes in result rows | R3 | Add explicit parser/scorer/eval harness SHA-256 fields or publish a release manifest mapping rows to scorer files. |
| Placeholder environment field | R3 | Record Python version, dependency lock/hash, OS/container hash, and code commit or source tarball hash. |
| Raw hash is canonical-object hash, not public file byte hash | R2 | Publish sanitized raw artifacts or a verifiable raw-byte manifest; define canonical raw hashing. |
| Scores files omit H5 linkage | R2 | Generate reviewer-facing `scores_with_hashes.jsonl/csv` or a join manifest keyed by `global_artifact_id`. |
| Local paths in preflight manifests | R3 | Rewrite release manifests to relative anonymized paths and record original/public SHA-256 mappings. |
| Local-only artifacts not yet excluded | R4 | Build reviewer archives only from the curated tracked release boundary. |
| Git metadata anonymity not yet checked | R3 | Run submission-time identity, remote, branch, and path-name checks before release. |

## Historical Anonymous GitHub Readiness Note

This section records the 2026-06-23 working-copy state. It is not the current
reviewer-package decision.

At that time, the release work still needed to:

- exclude ignored local-only files from any reviewer archive;
- map local-path redactions to original/public SHA-256 values;
- publish reviewer-visible raw-output files or a reviewer-facing hash
  commitment policy;
- run a final anonymity scan over git metadata, content, and path names.

The current anonymous review package implements those checks through
`REDACTION_MAP.json`, `verify_public_hash_locks.py`,
`verify_e5_interlock.py`, `scripts/check_anonymity.sh`, and
`scripts/build_review_archive.sh`.

Recommended release shape from this historical audit:

- create a fresh anonymous artifact repository;
- copy only curated PCG v2 docs, scorer code, task manifests, configs,
  post-run audits, scores, and sanitized hash manifests;
- exclude `.env`, `.venv`, ignored local-only directories, raw provider smoke
  files outside the release boundary, and local path provenance;
- add `ARTIFACT_HASH_MANIFEST.jsonl` with byte hashes for every released file;
- add `ROW_HASH_MANIFEST.jsonl` linking each result row to task/config/runner/
  prompt/raw/parsed/metric hashes;
- add one verification script that recomputes all release-file hashes and
  re-scores from released parsed outputs or released raw outputs.

## Safe Claim Level

Safe now:

> The core non-Claude/GPT PCG v2 evidence and the targeted two-row backfill
> addendum have H5 private-raw locks; the canonical static sanity gate also has
> an H5 private-raw lock and passed as a runner-discrimination check.

Not established by this historical report alone:

> The full historical SSR-downgrade evidence chain is public-H5 locked and the
> current working repo is ready for anonymous GitHub review.

## Required Fixes Before Anonymous Submission Artifact

1. Publish reviewer-visible raw outputs or a reviewer-facing raw-hash
   commitment policy.
2. Build a clean anonymous release archive from git-tracked files only.
3. Map any redacted local paths to original/public SHA-256 values.
4. Add source archive or commit hash for the clean release artifact.
5. Run the verifier and anonymity scripts inside the release artifact before
   upload.

## Machine-Readable Findings

```json
[
  {
    "finding_id": "HASH-SSR-20260623-001",
    "agent": "hash-interlock-agent",
    "severity": "R2",
    "status": "pass",
    "claim": "Core non-Claude/GPT PCG v2 evidence plus targeted backfill has H5 private-raw locks.",
    "evidence_refs": [
      {"type": "output", "ref": "results/_probe_deepseek_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_rerun100/CONTROLLED_ROWS.jsonl", "hash": null},
      {"type": "output", "ref": "results/_probe_qwen37max_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_50workers/CONTROLLED_ROWS.jsonl", "hash": null},
      {"type": "output", "ref": "results/_probe_kimi_k26_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_50workers/CONTROLLED_ROWS.jsonl", "hash": null},
      {"type": "output", "ref": "results/pcg_dynamic_state_v2_targeted_missing_rows_backfill_20260623/BACKFILL_CONTROLLED_ROWS.jsonl", "hash": null}
    ],
    "affected_runs": ["DeepSeek decisive", "DeepSeek random10", "Qwen random10", "Kimi random10", "targeted two-row backfill"],
    "affected_artifacts": ["ROW_H5_MANIFEST.jsonl", "ARTIFACT_HASH_MANIFEST.jsonl", "ENVIRONMENT_LOCK.json", "scores_with_h5_hashes.csv", "backfill_scores_with_h5_hashes.csv"],
    "recommended_action": "Use as internal H5 evidence; do not call it public H5 until raw-output policy and anonymous release repo are complete.",
    "blocks_main_matrix": false
  },
  {
    "finding_id": "HASH-SSR-20260623-002",
    "agent": "hash-interlock-agent",
    "severity": "R3",
    "status": "fail",
    "claim": "The full historical evidence bundle and current working repo are public-H5 ready for anonymous GitHub review.",
    "evidence_refs": [
      {"type": "file", "ref": ".gitignore", "hash": null},
      {"type": "file", "ref": ".env", "hash": null},
      {"type": "file", "ref": ".env.save", "hash": null},
      {"type": "file", "ref": "private/", "hash": null},
      {"type": "run_log", "ref": "PREFLIGHT_HASH_MANIFEST.jsonl files containing local absolute paths", "hash": null}
    ],
    "affected_runs": ["all current local PCG evidence packets"],
    "affected_artifacts": ["working repository", "preflight manifests", "private raw artifacts"],
    "recommended_action": "Create a clean anonymized artifact repo with release-level manifests and verifier script.",
    "blocks_main_matrix": true
  }
]
```
