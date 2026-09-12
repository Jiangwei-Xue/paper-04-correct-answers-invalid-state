# Method Delta Report — Carried-State Validity v2 Gate

## 1. Summary

The six method conditions are balanced matrix axes in the saved primary set: 1,200 rows per method. They are not interchangeable serialization schemes. The method determines the carried-state representation, which is directly relevant to the v2 construct. The pooled executor association therefore cannot be interpreted as a method-free validity result.

The most consequential finding is a representation gate failure: a canonical oracle-valid state passes when serialized as SSR or visible-carry fields, but fails when serialized in the native rolling-summary `SUMMARY` field because the frozen v2 field-role map does not treat `SUMMARY` as output-bearing.

## 2. Method version table

| Method condition | Observed state surface | v2 carried rows | Assessment |
|---|---|---:|---|
| `loop_only` | no output-bearing state surface in the saved final state | 0/1200 | structurally ineligible under current contract |
| `mature_ssr_loop` | typed `OUT`, `ALW`, `NO`, `B`, plus diagnostics | 93/1200 | typed SSR representation; criterion result conditional |
| `rolling_summary` | free-form `SUMMARY` assignment | 0/1200 | representation mapping not admitted by current spec |
| `rolling_visible_carry_forward` | `VISIBLE_KEEP` plus free-form `NOTE` | 0/1200 | positive surface contains carried/disallowed candidate mixture |
| `rolling_visible_fields_only` | `VISIBLE_KEEP`, `VISIBLE_ALLOWED_SCOPE`, `VISIBLE_BOUNDARY`, `VISIBLE_NOTE` | 0/1200 | positive surface contains visible candidate universe; safety fails |
| `ssr_no_visible_carry` | mostly typed `OUT`/`ALW` JSON or assignments, no visible carry | 36/1200 | typed SSR representation; small positive subset |

## 3. Method diff and confounding assessment

The intended matrix axes are method, model/provider condition, budget, and run. The task set and oracle are shared. Each method has 1,200 rows, so row-count balance does not remove representation confounding: representation is part of the method and is the route through which v2 is observed.

The v2 component table is in `method_component_executor_summary.json`. Current bottlenecks differ by method:

- `rolling_summary`: output-bearing presence is 27/1200 and completeness is 0/1200.
- `rolling_visible_carry_forward`: parseability and presence are 1200/1200, but exclusion safety is 0/1200 because `VISIBLE_KEEP` carries excluded candidates.
- `rolling_visible_fields_only`: completeness reaches 720/1200, but exclusion safety is 0/1200 and answer-state consistency is 0/1200.
- `mature_ssr_loop`: completeness is 161/1200; carried validity is 93/1200.
- `ssr_no_visible_carry`: completeness is 50/1200; carried validity is 36/1200.

These are construct-relevant representation differences, not incidental sampling noise. They must be modeled as method effects or controlled through a representation-neutral adapter before cross-method validity comparisons.

## 4. Comparable and non-comparable sets

- Safe for raw-output preservation and legacy audit: all six method conditions.
- Comparable for the current typed-SSR v2 scorer: `mature_ssr_loop` and `ssr_no_visible_carry`, with method retained as a blocking variable.
- Not comparable for a pooled v2 validity claim under the current role map: rolling-summary and visible-field conditions.
- No model rerun is required at this gate. The required action is an offline scorer/specification decision followed by replay.

## 5. Executor criterion result

Using legacy final-answer success as the answer denominator, the pooled executor contrast is not accepted as a method-free result. Within `mature_ssr_loop`, the point risk difference is −10.43 percentage points with a task-cluster bootstrap interval of approximately [−48.68, 25.40] pp. Within `ssr_no_visible_carry`, the point difference is +66.63 pp with an interval of approximately [27.06, 98.88] pp. The two typed-SSR methods do not support one common pooled direction.

## 6. Required fixes before main-matrix interpretation

1. Decide whether rolling-summary `SUMMARY` is a valid positive state field. If yes, specify and test a structured representation; if no, exclude it from cross-representation v2 validity claims.
2. Decide whether `optional_allowed_items` are required for executor sufficiency. The current v2 contract permits a valid state without an allowed path, while the executor requires it; this explains the non-equivalence cells and must remain explicit.
3. Re-run the offline scorer and executor summaries only after the representation role map is frozen.
4. Keep method-stratified results primary for criterion validation; do not use the pooled 51.64 pp contrast as a standalone causal or method-free claim.

## 7. Machine-readable findings

```json
{
  "finding_id": "MVD-V2-REPRESENTATION-001",
  "agent": "method-delta-agent",
  "severity": "R3",
  "status": "fail",
  "claim": "The current v2 role map is representation-sensitive across matrix methods.",
  "evidence_refs": [
    {"type": "file", "ref": "reports/metric_v2/gates/representation_control.json", "hash": null},
    {"type": "file", "ref": "reports/metric_v2/gates/method_component_executor_summary.json", "hash": null},
    {"type": "commit", "ref": "b3a13fd", "hash": null}
  ],
  "affected_runs": ["primary_7200_all_six_methods"],
  "affected_artifacts": ["results/metric_v2/scores_v2/primary.production_with_v1.jsonl"],
  "recommended_action": "Freeze a representation-neutral state-role decision and replay before paper revision.",
  "blocks_main_matrix": true
}
```
