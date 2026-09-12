# Scope And Release Policy

Date: 2026-06-23.

This file blocks four common misreadings of the package.

## Raw Outputs

Raw model outputs for the three H5-locked packets are included under
`released_raw_outputs/model_outputs/`. The schema field names are historical:
the original run manifests used `raw_private_ref`, and the verifier still
reports `verified_private_raw_refs` for compatibility with those lock schemas.
In this anonymous release, those references point to reviewer-visible released
raw outputs and are checked byte-for-byte by `verify_public_hash_locks.py`.

The expected verifier counters are:

- core H5 lock: `verified_private_raw_refs = 644`
- targeted backfill lock: `verified_private_raw_refs = 2`
- static sanity lock: `verified_private_raw_refs = 4`

## Historical Status Strings

Do not treat old release-status strings inside immutable lock files or
hash-locked audit reports as the current package status. Those strings are
kept because the files are part of the byte-level evidence record.

The current status is:

- raw outputs are released in this package and verified byte-for-byte;
- `verify_public_hash_locks.py` reports
  `ANON_REVIEW_READY_WITH_RELEASED_RAW_OUTPUTS` for the three H5 locks;
- `verify_e5_interlock.py` reports `E5` when run from a clean Git clone.

## Historical Runs

The 2026-06-18 and 2026-06-19 materials are not the main effect estimate. They
are retained because they explain the sequence of decisions: older evidence was
blocked from matrix entry, early SSR positives motivated stricter controls,
visible carry-forward emerged as a confound, and harder/static repairs showed
protocol sensitivity.

Those historical files are public in this package and hash-recorded. They are
not represented as a full H5/E5 result lock. Treat them as motivation,
calibration, and confound-discovery evidence.

## Main Matrix

This package does not claim main-matrix GO. It supports the narrower decision
to move mature/schema-heavy SSR from a primary-method candidate to an
ablation/diagnostic arm. A formal main-matrix artifact still needs its own
freeze packet, run packet, and GO decision.

## Review Wording

Safe wording:

> Under PCG dynamic-state v2, mature/schema-heavy SSR did not retain an
> independent advantage over visible carry-forward and was downgraded to an
> ablation/diagnostic arm.

Unsafe wording:

> SSR universally failed.

Unsafe wording:

> This folder is the final main-matrix artifact.
