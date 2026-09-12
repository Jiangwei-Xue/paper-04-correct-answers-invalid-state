# Carried-State Validity v2

## Scope

This specification adds a carried-state validity layer to the existing PCG Dynamic-State v2 artifact. It is an offline rescoring protocol. It does not alter the frozen task oracle, raw provider outputs, v1 labels, or any existing primary denominator.

The unit of analysis is one saved output row. Every row remains in its declared tier, including transport, parse, and governance failures. The new labels are reported alongside the legacy labels and are not substituted into the existing tables without an explicit downstream decision.

## Formal fields

For a row with carried state `S`, final answer `A`, and derived task sidecar `O`:

```text
intrinsic_state_validity_v2
  = state_parseable_v2
  AND output_bearing_present_v2
  AND exclusion_safety_v2
  AND required_state_completeness_v2

carried_state_validity_v2
  = intrinsic_state_validity_v2
  AND answer_state_consistency_v2

joint_answer_state_success_v2
  = answer_success_v2
  AND carried_state_validity_v2
```

`answer_success_v2` is an independent reimplementation of the existing answer-correctness rule. It requires all oracle required tokens and prohibits forbidden, protected, revoked, stale, and blocked-path leakage on the operational answer surface. Governance fields such as `state_labels`, `state_transitions`, and `boundary_checks` are retained for diagnostics but are not treated as operational output.

## State roles and fail-closed behavior

Output-bearing fields include `OUT`, `ALW`, `ACTIVE`, `REQUIRED_TOKENS`, `VISIBLE_KEEP`, `OUTPUT`, `FINAL_ACTIVE_SET`, and their explicit path/set variants. `NO`, `B`, `NOTE`, `CK`, labels, transitions, and annotations are not positive carried state. Unknown fields do not make a row invalid by themselves, but they cannot establish presence or completeness. A raw fallback, malformed JSON object, or ambiguous field record fails `state_parseable_v2`.

Required state items are derived from the frozen oracle's `required_exact_tokens`. Allowed paths remain separately tracked as optional operational items because the original oracle distinguishes token requirements from path permissions. They are required for answer-state consistency when the answer emits them. Disallowed items are the oracle's final excluded tokens plus blocked paths. Matching is exact and boundary-aware, so a same-prefix decoy cannot satisfy a required item.

## Evidence and denominator rules

The original oracle and evidence are read-only inputs. A sidecar records the source oracle SHA-256, derivation version, task IDs, status map, required items, optional allowed paths, and disallowed items. Raw output files and VCR material are copied by reference, never rewritten. New scores, tests, and reports live under the versioned `results/metric_v2/` and `reports/metric_v2/` namespaces.

Primary, Qwen supplement, budget-300 diagnostic, DeepSeek sanity, deterministic validity suite, and excluded/admission/smoke/history inventories are separate reporting tiers. No tier is pooled into another merely because it has the same task IDs.

## Interpretation boundary

The metric tests whether the state presented to the final answer is an adequate operational carrier under the frozen task contract. It does not establish model cognition, causal mechanism, or general performance outside this task family. A high answer rate with a lower carried-state rate indicates answer/state disagreement under the contract; a low state parseability rate indicates a representation problem before semantic validity can be assessed.
