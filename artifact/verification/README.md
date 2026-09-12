# Verification

This directory contains shared verifier and reproduction scripts.

## Saved-Output Replay

The scoped SSR downgrade packet now has an offline saved-output replay:

```bash
python3 artifact/verification/replay_ssr_downgrade_from_saved_outputs.py
```

Expected result:

- `passed: true`
- `api_calls_performed: 0`
- `controlled_rows_checked: 650`
- `score_rows_recomputed: 650`
- `raw_files_checked: 650`
- `failure_count: 0`

This is deliberately an LLM-specific replay cache check, not a live API rerun.
It reloads the released controlled rows and raw-output files, verifies raw byte
hashes and H5 release-layout links, extracts the saved final provider body,
then reruns the hash-locked scorer selected by each H5 manifest row.

Historical raw files in this packet preserve full final-response bodies but
only summary hashes for intermediate state-update calls.  Therefore this script
reproduces reported scores from recorded model outputs; it does not claim that
current live APIs will reproduce identical outputs.

The H5 manifests retain historical internal canonical hashes for pre-release
controlled rows and raw response objects.  In the anonymous review package,
provider headers are redacted and raw outputs live under
`released_raw_outputs/`, so those legacy canonical hashes are informational in
the default release-layout verifier.  Use
`--strict-legacy-internal-canonical` only for auditing the older private layout.

## Scorer Metric Contract

Main-matrix aggregation should treat `reliable_composite_success` as the primary
metric. `answer_success` and strict `state_governance_success` are paired
decomposition metrics. Standalone governance is diagnostic only and must not be
used as a primary ranking signal.

The strict governance score requires an output-bearing carry surface. This keeps
the `loop_only` floor arm from receiving governance credit merely because it
carries little or no state that can conflict.

## Minimal Baseline Validity Suite

The local baseline suite is a diagnostic scale reference, not a model-condition
extension of the primary matrix:

```bash
python3 artifact/verification/run_minimal_baseline_validity_suite.py --check
```

Expected result:

- `passed: true`
- `source_rows: 7200`
- `baseline_score_rows_recomputed: 36000`
- `policy_count: 5`
- `api_calls_performed: 0`

The checked-in outputs live under
`artifact/results/baselines/minimal_validity_suite_20260706/`. The visible-only
policies are local deterministic policies over the frozen model-visible task
text. They do not call a model and do not read the scorer oracle while
generating answers. The oracle-ceiling policy is included only to confirm that
the scorer can reach the expected upper bound.

The suite writes row-level source hashes, generated-output hashes, metric
hashes, an environment record, and a `HASH_MANIFEST.jsonl` linking the primary
row manifest, visible task manifest, scorer oracle, strict scorer, generated
outputs, and scored metrics.

## DeepSeek V4-Pro API Sanity Diagnostic

The DeepSeek v4-pro sanity diagnostic is a small learned-policy reference:
40 tasks, one direct `deepseek-v4-pro` call per task, 10-way concurrency at
record time. It is not part of the primary 7,200-row matrix.

Review-time verification uses saved-output replay only:

```bash
python3 artifact/verification/run_deepseek_v4pro_api_sanity.py --check
```

Expected result:

- `passed: true`
- `rows_replayed: 40`
- `api_calls_performed: 0`

The checked-in outputs live under
`artifact/results/baselines/deepseek_v4pro_api_sanity_20260706/`. The saved
cassette stores redacted provider response bodies, request/output hashes,
provider metadata, scored rows, summary CSVs, and a `HASH_MANIFEST.jsonl`. API
key values are not stored. Live record mode requires an external
`DEEPSEEK_API_KEY` and should not be used as the default reviewer verifier.

## Main-Matrix Freeze And Replay Contract

The new-repo main-matrix freeze packet can be rebuilt and checked with:

```bash
python3 artifact/verification/build_main_matrix_freeze.py
python3 artifact/verification/verify_main_matrix_freeze.py
```

Expected static verification result:

- `passed: true`
- `confirmatory_rows: 7200`
- `diagnostic_rows: 800`
- `api_calls_performed: 0`

The formal VCR-style runner contract is:

```bash
python3 artifact/verification/main_matrix_vcr_runner.py --mode audit \
  --config artifact/protocol/main_matrix/configs/pcg_dynamic_state_v2_confirmatory_40task_5model_6method_2budget_3run_20260625.json
```

It exposes three modes:

- `record`: imports explicit provider-adapter JSONL output into a cassette,
  validates row request hashes, and stores raw-response hashes.
- `replay`: forbids provider calls, reads only a local cassette, and fails on
  any cache miss.
- `audit`: verifies config row counts, duplicate request hashes, cassette
  hashes, and cache coverage.

Replay reproduces scores from recorded model outputs. It does not claim that
current live APIs will reproduce identical outputs.

The freeze/admission verifier remains a protocol-layer check: it verifies the
frozen row counts, provider snapshots, request controls, and benchmark-smoke
admission evidence without making provider calls. The clean-v2 five-model
7,200-row record-mode execution closure is now recorded under
`artifact/results/main_matrix/record_mode_20260627/`; submission descriptive
aggregate tables are frozen under `paper/submission_tables/`. Statistical modeling and
final claim wording remain separate manuscript layers.
OpenRouter GPT/Claude request controls explicitly set
`reasoning: {"effort": "none"}`, and the refreshed provider rows observed
`reasoning_tokens = 0`.

The provider live refresh can be rerun with:

```bash
python3 artifact/verification/refresh_main_matrix_providers.py
```

It uses a non-benchmark prompt, stores sanitized response records under
`artifact/protocol/main_matrix/admission/live_refresh_20260625/`, and does not
populate primary results.

## Replay Key Contract

The replay cache key includes stable experimental identity fields:
`task_id`, `method`, `budget`, `run_id`, `model_name`, `provider`,
`temperature`, `max_tokens`, `prompt_version`, `scorer_version`,
task/prompt hashes, and request-control hashes.

The replay cache key excludes volatile metadata such as timestamps, API
request IDs, latency, and token usage.  These values should still be preserved
as metadata for audit, but they should not decide cassette identity.

## Packet-Local Verifiers

The packet-local hash verifiers remain inside the scoped evidence packet they
verify:

```text
artifact/results/evidence/ssr_downgrade_20260623/verify_public_hash_locks.py
artifact/results/evidence/ssr_downgrade_20260623/verify_e5_interlock.py
```

Future shared verifiers should also avoid API calls by default and should
recompute scores, hashes, and aggregate outputs from released files.
