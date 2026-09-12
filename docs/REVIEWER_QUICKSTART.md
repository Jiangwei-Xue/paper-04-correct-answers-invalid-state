# Reviewer Quickstart

This is the 10-minute offline path. It does not require API keys, provider
accounts, network access, or live model calls.

## Read First

1. `STATUS.md`: confirms what is complete and what is still gated.
2. `artifact/BENCHMARK_CARD.md`: explains what the benchmark measures and does
   not measure.
3. `artifact/README.md`: maps the artifact directory.
4. `docs/RAI_ETHICS_LIMITATIONS.md`: records responsible-use boundaries.
5. `artifact/metadata/CROISSANT_MAPPING.md`: explains the Croissant draft.

Current gate:

```text
CLEAN_V2_EXECUTION_CLOSURE_COMPLETE
```

The five primary model conditions have completed the clean-v2 7,200-row
record-mode execution closure under
`artifact/results/main_matrix/record_mode_20260627/`. This closes the row-level
execution and VCR audit layer. The submission aggregate result tables are frozen
under `paper/submission_tables/`.

## Offline Verification

From the repository root:

```bash
./scripts/verify_all.sh
```

The wrapper performs the full offline check path. To run the main pieces
manually:

```bash
python3 artifact/verification/replay_main_matrix_from_cassettes.py
python3 artifact/verification/verify_excluded_history_first_pass.py
python3 artifact/verification/replay_ssr_downgrade_from_saved_outputs.py
python3 artifact/verification/summarize_budget_300_diagnostic.py --check
python3 artifact/verification/run_minimal_baseline_validity_suite.py --check
python3 artifact/verification/run_deepseek_v4pro_api_sanity.py --check
python3 artifact/verification/summarize_submission_tables.py --check
python3 -m json.tool artifact/metadata/croissant.json >/dev/null
```

Expected primary cassette replay result:

- `passed: true`
- `primary_rows_recomputed: 7200`
- `cassette_entries_checked: 7200`
- `api_calls_performed: 0`
- `failure_count: 0`

Expected excluded-history first-pass replay result:

- `passed: true`
- `observed_rows_checked: 4843`
- `cassette_entries_checked: 4843`
- `api_calls_performed: 0`
- `failure_count: 0`

Expected saved-output replay result:

- `passed: true`
- `score_rows_recomputed: 650`
- `api_calls_performed: 0`
- `failure_count: 0`
- legacy internal canonical row/response hash mismatches may be reported as
  informational because the anonymous release layout redacts provider headers
  and uses `released_raw_outputs/`.

Expected budget-300 diagnostic check:

- `passed: true`
- checked files under
  `artifact/results/evidence/budget_300_diagnostic_20260625/`

Expected deterministic validity-suite check:

- `passed: true`
- `source_rows: 7200`
- `baseline_score_rows_recomputed: 36000`
- `api_calls_performed: 0`
- `failure_count: 0`

Expected DeepSeek V4-Pro API sanity replay:

- `passed: true`
- `rows_replayed: 40`
- `api_calls_performed: 0`
- `failure_count: 0`

Expected Croissant check:

- no JSON parse error.

Expected submission table check:

- `passed: true`
- `primary_rows: 7200`
- `budget300_rows: 800`
- `qwen3_coder_rows: 1440`

## Scoped Evidence Hash Checks

From the repository root:

```bash
cd artifact/results/evidence/ssr_downgrade_20260623
python3 verify_public_hash_locks.py
python3 verify_e5_interlock.py
```

Expected public-hash result:

- `passed: true`
- raw-output references verified as `644`, `2`, and `4`
- skipped raw-output references all `0`

Expected E5 result:

- `passed: true`
- `evidence_level: E5`
- `failure_count: 0`

From an anonymous Git clone, the verifier also checks repository cleanliness.
From the generated review archive, `.git` metadata are absent by design; the
verifier checks hash closure and marks Git cleanliness as not applicable to
the extracted archive.

The saved-output replay command is the reviewer-facing release-layout verifier.
Its optional `--strict-legacy-internal-canonical` mode audits the older
pre-release private canonical hash contract and is not required for the
anonymous review package.

## What Not To Do

- Do not rerun closed-model APIs to verify the reported saved-output evidence.
- Do not mix admission smoke rows, provider live-refresh rows, sentinel drift
  rows, excluded first-pass history, historical evidence, or budget-`300`
  diagnostic rows into primary aggregation.
- Do not treat budget `300` as part of primary confirmatory ranking.
- Do not treat Qwen3-Coder-480B as a sixth primary model.
- Do not treat deterministic validity-suite rows or DeepSeek sanity rows as
  primary model conditions.
- Do not install provider SDKs or read `.env` files for this offline path.

## Claim Map

Use `docs/CLAIM_TO_ARTIFACT_MAP.md` to connect paper claims to files. The
scorer construct-validity entry explains why `reliable_composite_success` is
primary and standalone governance is diagnostic only.

The current package verifies saved evidence from released outputs, manifests,
scorer code, Croissant metadata, and hash locks. It is not a live closed-model
API rerun package.
