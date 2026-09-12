# Metric v3 changelog

## 2026-08-13 — draft construct decision

- Added representation adapters and a canonical claimed-state layer.
- Added action-relevant operational sufficiency in place of global required-state completeness.
- Promoted `SUMMARY` to an adapter input without treating non-empty text as positive state.
- Froze `final_answer_success_v2` as the revision answer metric candidate; legacy raw-scan remains sensitivity-only.
- Added method-blocked executor estimands and a pre-aggregate analysis plan.
- V3 final specification and hash are intentionally not frozen until the representation-invariance suite passes.
