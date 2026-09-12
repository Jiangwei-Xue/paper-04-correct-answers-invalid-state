# V3 Revision-Level Analysis Plan

Status: frozen before full V3 rescoring.

## Primary estimands

The primary answer metric is the frozen final-answer surface metric:

```text
final_answer_success_v2
```

The primary state metrics are:

```text
intrinsic_state_validity_v3
carried_state_validity_v3
joint_final_answer_state_success_v3
```

The main answer denominator is all 7,200 primary rows. The conditional answer-aligned state estimate uses only rows with `final_answer_success_v2=1`. Legacy raw-scan answer labels are sensitivity-only.

## Representation and method control

Method/representation is a blocking variable. Report every method separately. Estimate executor criterion validity only within methods containing both `V3=1` and `V3=0` among final-answer-success rows. If either stratum is empty, report positivity unavailable and do not calculate a within-method risk difference.

The pooled contrast is not a primary estimand. If a standardized summary is needed, standardize to the predeclared equal-method target distribution and report it as secondary.

## Executor analysis

The executor consumes canonical positive state plus the frozen task action environment. It does not consume final-answer text or scorer labels. For each eligible method, report:

```text
P(E | final_answer_success_v2=1, V3=1, method=m)
P(E | final_answer_success_v2=1, V3=0, method=m)
RD_m = first - second
```

Use task-cluster bootstrap with 10,000 replicates and seed `20260813`. Report the four cells `V3 × E` within the answer-correct stratum.

## Required validation gates

Before V3 aggregate inspection:

1. All ten representation-invariance cases must agree across rolling-summary, visible-carry, and SSR serialization on canonical validity classification.
2. Adapter source inspection must show no hidden oracle-status input.
3. V3 spec and hash manifest must be frozen only after gate 1 passes.
4. V3 replay must preserve every row and keep the six evidence tiers separate.

## Reporting boundary

Do not call this preregistration. Use: “We froze and hash-committed the final-answer surface, representation adapters, V3 contract, and revision analysis plan before full V3 rescoring and aggregate inspection.”
