# Hash Interlock Report

## Summary

Hash status is `NO_GO`. Current chain strength is H2 max for OpenRouter preflight rows and H1 for legacy processed results. Only H4/H5 can enter the main matrix.

## Candidate Inventory

- Non-git candidate files hashed: 149.
- Candidate HEAD: `582acefbe1afb21ead789e3aa64da98c1514c452`.
- Generated current hash files: `CANDIDATE_CURRENT_FILE_HASHES.csv`, `CANDIDATE_CURRENT_HASH_MANIFEST.jsonl`.

## Key Current Hashes

| Artifact | SHA-256 |
|---|---|
| `agents/run_long_experiment.py` | `7e8088f1c3e4a9275f75a9a5278aa7cfeca0cdb741a56d1214521454f967929f` |
| `configs/openrouter_gpt55_runner_preflight_1task_1method_1budget_1run.json` | `cb06b46ef1e414962ec4ec609608d7f5afff557418f4d1f4ea92b69a24df446b` |
| `configs/openrouter_claude48_runner_preflight_1task_1method_1budget_1run.json` | `453580e60c19e4fa17a54961801e9403f4cf183e0871410536f1d29ef42097da` |
| `data/main_v1/openrouter_runner_preflight_1task_subset.jsonl` | `3e5ee486a5f894405b378e5481b8044b844137d579bce2c0388bd00dc39a3d83` |
| GPT `scores.csv` | `643449781525ab9ba71d1d3a52116141d02391b460fc677d883a292253749d9e` |
| Claude `scores.csv` | `f86b34fba61e9e9b0818f0cb1ef3b455d33468f8c715bb6c2e46fe2949057fe4` |
| `public_release_file_manifest.json` | `e5f1216726e3dff797a7e12f83b50941ceaccae25fb015d8697e1afd8a31ef5e` |

## Broken Links

- Required `HASH_MANIFEST.jsonl` is absent.
- Release manifest is stale: 4 hash mismatches, 2 missing-current entries, 13 extra-current entries.
- OpenRouter configs declare `manifest_sha256=6ab8fa6b...`, but the shipped one-task subset is `3e5ee486a5f894405b378e5481b8044b844137d579bce2c0388bd00dc39a3d83`.
- OpenRouter configs declare `runner_sha256=82417cd4...`, but public runner hash is `7e8088f1c3e4a9275f75a9a5278aa7cfeca0cdb741a56d1214521454f967929f`.
- Score rows refer to private raw paths absent from candidate.
- Score rows record private/source commit `e5f3c84c...`, not current public HEAD `582acefbe1afb21ead789e3aa64da98c1514c452`.
- Scalar `run_id=1` is reused and not globally unique.

## Manifest Comparison

See `RELEASE_MANIFEST_COMPARISON.csv` for row-level details. Mismatches: `README.md`, `ARTIFACT_MANIFEST.md`, GPT config, Claude config.

## Chain Strength

| Family | Strength | Matrix decision |
|---|---:|---|
| Legacy processed CSVs | H1 | exclude/rerun |
| OpenRouter GPT preflight | H2 | pilot only |
| OpenRouter Claude preflight | H2 | pilot only; task failed |
| v4 control docs | H1 | planning only |
| Main matrix candidate rows | below H4 | no-go |
