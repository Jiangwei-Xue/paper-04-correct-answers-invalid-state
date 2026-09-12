# Qwen3-Coder Supplement Timing Audit Note

Date: 2026-06-30

Scope: derived timing audit for the Qwen3-Coder open-weight supplement. This
note does not modify the frozen score rows, cassette rows, replay rows,
summaries, or VCR audit artifacts.

## Issue

The five-model clean-v2 score rows include a row-level
`record_mode_created_at_utc` field. The Qwen3-Coder supplement score rows do
not duplicate that field.

This is a supplement schema consistency gap, not a loss of timing evidence and
not a primary-matrix issue. The Qwen3-Coder supplement is outside the frozen
five-model primary matrix. Its phase summaries preserve phase-level timing, and
the cassettes preserve final-answer provider-attempt timing inside
`raw_response.final_raw.attempts`.

## Derived Crosswalk

To make row-level timing easier to audit without rewriting the frozen score
files, the following derived crosswalk files were generated from cassette
records and score-row joins by `row_id`:

| role | score rows | cassette rows | crosswalk rows | rows with final-attempt timing | phase start | phase complete | final-attempt timing range |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| `admission` | 16 | 16 | 16 | 16 | 2026-06-29T11:24:43Z | 2026-06-29T11:25:04Z | 2026-06-29T11:24:49Z to 2026-06-29T11:25:03Z |
| `confirmatory` | 1,440 | 1,440 | 1,440 | 1,440 | 2026-06-29T11:25:04Z | 2026-06-29T12:11:21Z | 2026-06-29T11:25:09Z to 2026-06-29T12:11:18Z |
| `budget300_diagnostic` | 160 | 160 | 160 | 160 | 2026-06-29T12:11:22Z | 2026-06-29T12:15:54Z | 2026-06-29T12:11:27Z to 2026-06-29T12:15:54Z |

Derived files:

- `qwen3_coder_row_timing_crosswalk.jsonl`
- `qwen3_coder_row_timing_crosswalk.csv`
- `TIMING_CROSSWALK.admission.jsonl`
- `TIMING_CROSSWALK.confirmatory.jsonl`
- `TIMING_CROSSWALK.budget300_diagnostic.jsonl`
- `TIMING_AUDIT_MANIFEST_20260630.json`
- `TIMING_AUDIT_MANIFEST_20260630.sha256`

The combined `qwen3_coder_row_timing_crosswalk.*` files contain `1,616` rows
covering admission, confirmatory, and budget-300 diagnostic phases. They
include `row_id`, `logical_request_hash`, phase, method, budget, run id,
final-answer request start/finish times, final-attempt counts, source score and
cassette hashes, provider route metadata, and reasoning-audit metadata.

## Interpretation Boundary

The crosswalk projects timing from:

```text
cassette.raw_response.final_raw.attempts
```

Its scope is:

```text
final_answer_provider_attempts_only
```

The Qwen3-Coder cassette records do not expose separate
`started_at_utc`/`finished_at_utc` fields for every summarized state-update
call. Therefore, the combined crosswalk includes
`state_call_started_min_utc` and `state_call_finished_max_utc` as explicit
empty fields, with `state_call_timing_available=false`. The derived crosswalk
should be used for final-answer request attempt timing and row-level temporal
audit convenience. It should not be described as a complete per-provider-call
timing trace for every internal state-update call.

The original score files are intentionally left unchanged. This preserves the
frozen supplement artifact while making the timing evidence explicit and easier
to inspect.
