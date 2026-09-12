# SSR Downgrade Evidence

This package is not the full paper artifact and not the final main-matrix
artifact. It serves one role only: to justify downgrading mature/schema-heavy
SSR from a primary method candidate to an ablation/diagnostic condition. For
that scoped decision, the relevant evidence is the PCG dynamic-state v2
decisive packet, the targeted backfill, the static sanity gate, and the H5/E5
verification scripts. Historical files are included only to explain why
stricter controls were introduced.

Date: 2026-06-23.

This package supports one narrow claim. In the PCG dynamic-state v2 protocol,
the tested mature/schema-heavy SSR arm did not keep an independent advantage
over visible carry-forward, so it was downgraded to an ablation and diagnostic
condition. The package does not argue that SSR fails universally.

The decisive comparison is small enough to inspect directly. In the DeepSeek
PCG v2 packet, `mature_ssr_loop` reached `3/26 = 0.115` reliable composite
success; `rolling_visible_carry_forward` reached `13/26 = 0.500`. The 2026-06-23
targeted backfill closed two missing rows without changing that comparison.
The static sanity run then checked the narrower objection that the mature SSR
runner was trivially broken on a clean control.

## Where To Start

Read these four files first:

- `E5_INTERLOCK_REPORT_20260623.md`
- `docs/protocol/pcg_dynamic_state_v2_main_matrix/SSR_DOWNGRADE_EVIDENCE_CHAIN_20260623.md`
- `docs/protocol/pcg_dynamic_state_v2_main_matrix/VARIABLE_METHOD_RESULT_EVIDENCE_CHAIN_20260623.md`
- `docs/protocol/pcg_dynamic_state_v2_main_matrix/HASH_INTERLOCK_REPORT_20260623.md`

The first three files give the current review status and downgrade argument.
`HASH_INTERLOCK_REPORT_20260623.md` is kept as a hash-locked historical audit
record. It may contain release-status wording that was true before this
anonymous package was assembled; the current status is the one reported by the
verifiers below.

## What Is Included

`data/pcg_dynamic_state_v2/h5_release_lock_20260623/` contains the core H5 lock:
644 rows across DeepSeek decisive, DeepSeek random10, Qwen random10, and Kimi
random10 packets.

`data/pcg_dynamic_state_v2/h5_targeted_backfill_lock_20260623/` contains the
append-only lock for the two missing-row backfills.

`data/pcg_dynamic_state_v2/h5_static_sanity_lock_20260623/` contains the
one-task static sanity gate.

`results/`, `configs/`, `tools/`, and `released_raw_outputs/model_outputs/`
contain the copied reviewer-facing materials needed to audit those locks and
the historical calibration summaries. The listed raw-output files are included
for byte-level hash verification.

`historical_matrixgate_20260618/` gives the selected MatrixGate reports behind
the earlier `NO_GO` decision for inheriting old public SSR evidence.
`HISTORICAL_EVIDENCE_PUBLIC_HASH_MANIFEST.jsonl` records hashes for the copied
historical evidence-chain files and labels their role.

Some preflight notes, configs, and runner constants contained author-local
absolute paths. Those strings were removed for double-blind review. The
per-file original SHA-256 and public-copy SHA-256 values are in
`REDACTION_MAP.json`.

`SCOPE_AND_RELEASE_POLICY.md` states the raw-output policy, historical-evidence
scope, and main-matrix boundary in review-facing terms.

## Status Wording

Some immutable lock files and historical audit reports use older field names or
status strings, including `H5_PRIVATE_RAW_LOCK`, `raw_private_ref`,
`verified_private_raw_refs`, and `NOT_PUBLIC_READY_UNTIL_RAW_POLICY_AND_ANONYMIZED_RELEASE_REPO`.
Those strings are preserved because the files are byte-hashed evidence. They
are not the current release status.

Current status for this anonymous review package:

- raw outputs referenced by the H5 locks are included under the release path
  `released_raw_outputs/model_outputs/`;
- `verify_public_hash_locks.py` reports `review_release_status:
  ANON_REVIEW_READY_WITH_RELEASED_RAW_OUTPUTS` for all three H5 locks;
- `verify_e5_interlock.py` reports `evidence_level: E5` from a clean Git clone.

## Verify The Locks

Run this command from the current folder:

```bash
python3 verify_public_hash_locks.py
python3 verify_e5_interlock.py
```

The public-hash verifier checks H5 row hashes, included artifact hashes,
raw-output byte hashes, and the redaction map. The E5 verifier additionally
requires code-commit cleanliness, environment lock recomputation, dataset,
prompt, config, run-log, output, and manifest linkage.

Expected result after this folder is committed: `passed: true` for both
verifiers, with `verify_e5_interlock.py` reporting `evidence_level: E5`. The
word `private` in raw counters reflects the historical manifest field name, not
a hidden reviewer dependency.

The strict E5 verifier reads `git HEAD` and checks cleanliness when it runs
from an anonymous Git clone. In the generated review archive, `.git` metadata
are absent by design; archive-mode verification still checks internal hash
closure and treats the unpacked directory's Git cleanliness check as not
applicable.

Clean-tree verification summary for the current reviewer-facing package:

| command | expected result |
|---|---|
| `python3 verify_public_hash_locks.py` | `passed: true`; raw refs verified as `644`, `2`, and `4`; skipped raw refs `0`, `0`, and `0` |
| `python3 verify_e5_interlock.py` | `passed: true`; `evidence_level: E5`; `failure_count: 0`; effective E5 rows `642 + 2 + 4` |

## Boundary

Use this package to review the SSR downgrade evidence chain. Do not cite it as
a universal SSR failure result or an H5/E5 lock over every historical
calibration run.

The main-matrix freeze state is intentionally not changed by this package. This
folder supports the method downgrade decision; it does not replace a later
main-matrix GO packet.
