# Contamination Leakage Report

## Summary

Contamination/leakage status blocks main matrix entry as-is. The strongest issue is prompt-interface contamination in OpenRouter preflight raw traces: scoring-boundary metadata and forbidden labels were model-visible. The public candidate also lacks a fresh frozen main/admission manifest and includes repaired local Qwen32B outputs.

## Findings

| Area | Finding | Severity |
|---|---|---:|
| Prompt leakage | Preflight prompts exposed required/forbidden token and boundary metadata to the model. | C3/R3 |
| Data lineage | OpenRouter rows are `main_experiment=false`, one-task preflights only. | C1/R2 |
| Output reuse | Segment state is generated output reused as later input by design; acceptable only if logged and hashed in raw manifests. | C1/R2 |
| Tool/web | No evidence of enabled web/tools in OpenRouter configs; fallback disabled. | C0/R0 |
| Operational repair | Local Qwen32B removed 437 backend-error rows from 3000. | C2/R3 |

## Decisions

- Exclude OpenRouter one-row preflights as matrix outcome evidence.
- Exclude or rerun local Qwen32B repaired rows.
- Rebuild prompt interface so visible task content is separated from oracle/scoring metadata before admission.
- Freeze train/dev/test or task manifest before any fresh outputs.
