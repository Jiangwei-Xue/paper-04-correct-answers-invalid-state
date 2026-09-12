# Carried-State Validity v3 Construct Decision Memo

Status: decision record before V3 replay; revision gate remains closed until the representation-invariance suite passes.

## Decisions

1. `SUMMARY` is a formal carried-state surface, but only through a deterministic representation adapter. A non-empty summary is not sufficient for positive-state presence.
2. Native representations are converted to a canonical claimed state before validation. The common validator never parses `SUMMARY`, `OUT`, `ALW`, or visible-carry syntax directly.
3. Adapters receive only the native state surface and a task-visible identifier universe. They do not read hidden oracle statuses, final answers, executor results, or scorer labels. Ambiguous polarity fails closed.
4. `required_state_completeness_v2` is not edited. V2 remains frozen as the first complete-contract implementation and is retained as a rejected representation-neutrality candidate.
5. V3 replaces completeness with action-relevant sufficiency. A task is intrinsically sufficient when all mandatory current facts are positively carried and at least one admissible action option is positively supported.
6. An answer-selected path must be supported by the canonical state. This is answer-state consistency, not a global requirement to carry every admissible alternative.
7. Representation is a blocking/stratification variable. Pooled executor contrasts are descriptive only; the primary criterion estimand is within-method.
8. `final_answer_success_v2` is frozen as the revision answer metric. `answer_success_legacy_rawscan` is retained only as metric-history sensitivity.

## Canonical state

```text
positive_operational_items
negative_or_excluded_items
ambiguous_items
annotation_items
parseable
```

The oracle is consulted only after canonicalization to evaluate mandatory facts, admissible action options, disallowed items, and answer alignment.

## Denominator and timing boundary

The underlying provider outputs predate this revised construct. The final-answer surface decision and V3 revision analysis plan are frozen before full V3 replay and aggregate inspection. This is a transparent post hoc reanalysis, not a preregistration.

No model calls, outcome-dependent refill, or paper edits are authorized by this memo.
