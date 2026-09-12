# E5 Interlock Report

Date: 2026-06-23.

Scope: the SSR downgrade evidence packet in this folder. The claim is narrow.
Under the PCG dynamic-state v2 probes, the tested mature/schema-heavy SSR arm
does not carry an independent advantage over visible carry-forward, so it is
treated as an ablation and diagnostic condition. This report does not claim a
universal failure of all SSR variants.

## Status

The package satisfies E5 when it is committed in the anonymous review
repository and verified from a clean tree.

Use `verify_e5_interlock.py` for the strict check. In staging, the same script
may be run with `--allow-dirty`; that mode is only a pre-commit diagnostic and
does not satisfy the code-commit part of E5.

## Effective E5 Scope

The original core PCG v2 lock is an immutable 644-row snapshot. Two rows in that
snapshot were known missingness rows and are superseded by the targeted
2026-06-23 backfill. The effective downgrade evidence chain is:

| component | rows in manifest | effective E5 result rows | role |
|---|---:|---:|---|
| core PCG v2 lock | 644 | 642 | main downgrade evidence after excluding two superseded gaps |
| targeted backfill lock | 2 | 2 | closes the two missing rows append-only |
| static sanity lock | 4 | 4 | checks that the canonical mature SSR runner is not trivially broken |

The historical 2026-06-18 and 2026-06-19 files remain calibration and confound
discovery evidence. They are public-hash referenced in this package, but they
are not promoted into the effective E5 result chain and should not be used as a
pooled effect estimate.

## E5 Checklist

| E5 item | reviewer-facing evidence | verifier check |
|---|---|---|
| code commit | the clean Git commit containing this folder | `git.rev-parse HEAD` and no dirty release files |
| environment hash | each `ENVIRONMENT_LOCK.json` plus package `requirements.txt` | recomputes `environment_lock_sha256` and requirements SHA-256 |
| dataset hash | task and oracle manifests under `data/pcg_dynamic_state_v2/` | joins `dataset_hash` to controlled `task_manifest_sha256` and public file source |
| prompt hash | row-level prompt hashes in `CONTROLLED_ROWS.jsonl` and H5 manifests | joins H5 `prompt_hash` to the controlled row |
| config hash | copied configs and redaction-map original/public SHA-256 pairs | joins `config_file_byte_sha256` to controlled `config_sha256` and public/redacted source |
| run log | controlled rows, scores, audits, and H5 manifests under `results/` and `data/` | requires a controlled row for every H5 row |
| output hash | released raw output files under `released_raw_outputs/model_outputs/` | recomputes raw file byte SHA-256 for every raw reference |
| manifest linkage | H5 row hashes, chain hashes, score hashes, metric hashes, and artifact manifests | recomputes release row H5 and verifies parent hash linkage |

The H5 schemas retain historical field names such as `raw_private_ref`. In this
review packet, those references point to released raw output files under
`released_raw_outputs/model_outputs/`. The files are included and byte-verified;
they are not hidden reviewer dependencies.

Some older `H5_LOCK_SUMMARY.json` files still contain the release-status text
that was true before this anonymous package was assembled. Those summary files
are kept byte-stable because they are part of the historical lock. The current
review status is derived by `verify_public_hash_locks.py` from the files
actually present in this package.

The same rule applies to hash-locked audit reports. Older phrases about raw
release policy or public readiness are historical metadata, not the current
review status. Current status is given by this report, the package README, and
the two verifier outputs.

## Redaction Boundary

Some original configs, runner files, or preflight notes contained author-local
absolute paths. Those strings were removed from the public copy. `REDACTION_MAP.json`
records both the original SHA-256 and the public-copy SHA-256, so the verifier
can distinguish an anonymization rewrite from an unaccounted hash mismatch.

This means a config or runner hash may be satisfied by one of two public
sources:

- the released public file, when the row hash already matches the public copy;
- the redaction-map original digest, when the historical row recorded the
  pre-redaction byte hash.

## Expected Verification

From this folder:

```bash
python3 verify_public_hash_locks.py
python3 verify_e5_interlock.py
```

Expected strict result after the folder is committed:

```text
verify_public_hash_locks.py: passed true
verify_e5_interlock.py: evidence_level E5, failure_count 0
```

If `verify_e5_interlock.py` reports `release artifact files are not committed`,
the package is still a staging packet, not strict E5.

If it reports that `git HEAD` is unavailable, the files were probably unpacked
from a source archive or zip. That copy can still verify the public H5 locks,
but the strict E5 code-commit check requires a Git clone of the anonymous
review repository.

## Claim Language

Safe:

> The PCG dynamic-state v2 SSR downgrade packet is E5-verifiable after commit:
> code state, environment, datasets, prompts, configs, run logs, released raw
> outputs, metrics, and H5 manifests are linked in a clean anonymous review
> repository.

Not safe:

> Every historical 2026-06-18/2026-06-19 calibration run is itself E5-locked.

Not safe:

> SSR as a broad family is proven to fail.

## Machine-Readable Summary

```json
{
  "schema_version": "ssr_downgrade_e5_interlock_report.v1",
  "date": "2026-06-23",
  "scope": "PCG dynamic-state v2 SSR downgrade evidence packet",
  "claim": "tested mature/schema-heavy SSR is downgraded to ablation/diagnostic status under PCG dynamic-state v2",
  "effective_e5_rows": {
    "core_pcg_v2": 642,
    "targeted_backfill": 2,
    "static_sanity": 4
  },
  "historical_20260618_20260619_role": "calibration_and_confound_discovery_only",
  "strict_e5_verifier": "verify_e5_interlock.py",
  "public_hash_verifier": "verify_public_hash_locks.py",
  "requires_clean_git_commit": true,
  "raw_outputs_released_for_byte_verification": true
}
```
