# Metric v2 changelog

## 2026-08-13 — 2.0.0

- Added the formal Carried-State Validity v2 specification.
- Added an oracle-derived sidecar without modifying the frozen hidden-state oracle.
- Added independent production and reference scorers.
- Added exact, boundary-aware token/path matching to prevent same-prefix false positives.
- Added separate parseability, output-bearing presence, exclusion safety, required-state completeness, answer-state consistency, intrinsic validity, carried validity, and joint success fields.
- Preserved legacy v1 fields and denominators.
- Added deterministic audit, differential, property, mutation, and downstream execution validation outputs under the metric-v2 namespace.
