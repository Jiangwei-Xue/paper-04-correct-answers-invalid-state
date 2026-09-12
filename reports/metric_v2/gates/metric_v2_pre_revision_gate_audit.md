# Pre-revision v2 gate audit

No model calls or paper edits were performed.

## Gate result

- Answer crosswalk: 1,217 discordant rows classified; 935 legacy raw-scan outside-final-surface cases and 282 v2 final-surface recovery cases.
- Representation-neutral positive control: `False`.
- Revision-ready: `False`; the representation control requires a scorer/spec decision before paper revision.

## Method component results

| method | rows | parseable | output-bearing | safety | completeness | consistency | intrinsic | carried |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| loop_only | 1200 | 1002 | 0 | 1200 | 0 | 0 | 0 | 0 |
| mature_ssr_loop | 1200 | 973 | 973 | 784 | 161 | 492 | 96 | 93 |
| rolling_summary | 1200 | 879 | 27 | 1196 | 0 | 2 | 0 | 0 |
| rolling_visible_carry_forward | 1200 | 1200 | 1200 | 0 | 68 | 16 | 0 | 0 |
| rolling_visible_fields_only | 1200 | 1200 | 1200 | 0 | 720 | 0 | 0 | 0 |
| ssr_no_visible_carry | 1200 | 846 | 842 | 1134 | 50 | 479 | 43 | 36 |

## Executor criterion

The pooled association is not accepted as a method-free causal claim. Within-method conditional results are reported in `method_component_executor_summary.json`.

## Representation control

- `rolling_summary_native`: carried validity `False`; reasons `['ANSWER_UNSUPPORTED:API_01_10BBFA', 'ANSWER_UNSUPPORTED:API_01_C1FFF0', 'ANSWER_UNSUPPORTED:src/api/unit_01_f1c1da.py', 'MISSING_REQUIRED_STATE', 'NO_OUTPUT_BEARING_STATE']`.
- `visible_carry_native`: carried validity `True`; reasons `[]`.
- `ssr_native`: carried validity `True`; reasons `[]`.
