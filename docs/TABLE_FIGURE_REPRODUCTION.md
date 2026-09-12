# Table And Figure Reproduction

The current repository contains protocol documentation, the SSR downgrade
evidence packet, the clean-v2 five-model 7,200-row execution closure, and the
submission aggregate result tables under `paper/submission_tables/`.

## Currently Reproducible

Reviewers can reproduce the included evidence checks:

```bash
python3 artifact/verification/replay_ssr_downgrade_from_saved_outputs.py

cd artifact/results/evidence/ssr_downgrade_20260623
python3 verify_public_hash_locks.py
python3 verify_e5_interlock.py
```

These commands verify the saved output rows, raw-output hashes, recomputed score
fields, and hash chain for the downgrade evidence packet.  They do not call live
model APIs.

## submission Tables

The submission table freeze is:

```text
paper/submission_tables/tables/
```

The table builder is:

```text
artifact/verification/summarize_submission_tables.py
```

Run:

```bash
python3 artifact/verification/summarize_submission_tables.py --check
```

It reads only tracked score CSV files under `artifact/results/main_matrix/` and
does not call model APIs.

Primary tables must rank or compare methods on `reliable_composite_success`.
`answer_success` and strict `state_governance_success` should be shown together
as decomposition columns. A standalone governance table, if included, must be
labeled diagnostic and must not be used as a primary success ranking.

Result captions should use scope-bound co-success language. The preferred
interpretation is that marginal answer success and marginal governance success
can overstate reliable co-success when they occur on different rows. Avoid
phrases such as "mutual exclusion", "SSR fails", or "no method can achieve
both" unless a later, explicitly broader result supports that claim.

The manuscript and repository-hosting metadata remain separate from this
scientific reproduction package.
