# Minimal Baseline Validity Suite Interlock Report

## Summary

- suite_id: `minimal_baseline_validity_suite_20260706`
- generated_at_utc: `2026-07-07T16:53:34Z`
- source_rows: `7200`
- baseline_score_rows: `36000`
- api_calls_performed: `0`
- evidence_level: `E5` for the deterministic saved-output baseline chain

## Baseline Rates

| policy | kind | n | answer | governance | co-success |
| --- | --- | ---: | ---: | ---: | ---: |
| carry_all_visible_v1 | visible_only | 7200 | 0.00% | 0.00% | 0.00% |
| copy_initial_visible_v1 | visible_only | 7200 | 15.00% | 100.00% | 15.00% |
| oracle_ceiling_control_v1 | oracle_upper_control | 7200 | 100.00% | 100.00% | 100.00% |
| random_visible_v1 | visible_only | 7200 | 0.53% | 18.33% | 0.53% |
| rule_visible_transition_v1 | visible_only | 7200 | 15.00% | 15.00% | 15.00% |

## Chain

- row_manifest_sha256: `10ace9463c960c35bbfa501e23e554924c6ef2f1f5fd904e7e18324e872938e0`
- visible_task_manifest_sha256: `f26636d5c6f01b13e659d9162a2e5b366d8c448d2c03190dfbe137a392d3b1a1`
- oracle_manifest_sha256: `670c47db3b1a873eba10045fc4e8e656d464128a225850854cceb3fbd4f85280`
- scorer_sha256: `67c18a606d50760990ef28054b059058c69e758d8439b1caa1ed2e8f1dc6417b`
- generator_script_sha256: `e7db02d15088777b078f2a9b2cbe57309ebedfab5a5f73a4bbecdf8da7dda552`

Each output row stores the source primary row hash, visible-task hash, oracle-entry hash used by the scorer, run-input hash, generated output hash, metric hash, and score-record hash.

## Boundary

The visible-only baselines are local deterministic policies. They do not call a model and do not read the oracle while generating answers. The oracle ceiling control is included only to confirm that the scorer can produce the expected upper bound.
