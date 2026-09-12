# Pre-Matrix Variable Control Report — Carried-State Validity v2 Gate

## 1. Intended matrix axes

- state-transfer method: six named method conditions;
- model/provider condition;
- state budget;
- run index.

The task set, hidden oracle, raw provider output, and saved-output identity are not intended to vary within a declared cell.

## 2. Variable inventory

| Variable | Role | Expected | Observed | Risk | Action |
|---|---|---|---|---|---|
| task identity/oracle | controlled | frozen | frozen sidecar source hash | R0 | retain |
| method | independent/blocking | varied | six balanced conditions | R1 | stratify |
| model/provider | independent/blocking | varied | recorded in row identity and metadata | R1 | stratify |
| budget | independent/blocking | varied | recorded in row identity | R1 | stratify |
| run index | nuisance/replication | recorded | recorded in row identity | R1 | retain |
| state field representation | method-linked confounder | controlled within method | differs by method | R3 | freeze role map or adapter |
| v2 parser/field-role map | evaluation variable | frozen | current map is fixed but not representation-neutral | R3 | revise decision then replay |
| executor allowed-path requirement | downstream criterion variable | explicit | stricter than v2 optional-path rule | R2 | document or align |
| model API calls | controlled | zero for replay | zero | R0 | retain |
| legacy answer denominator | derived comparison variable | separately named | retained as `A_legacy_rawscan` | R1 | crosswalk |

## 3. Evidence reviewed

- `results/metric_v2/raw_inputs/primary.jsonl` — 7,200 saved rows;
- `results/metric_v2/scores_v2/primary.production_with_v1.jsonl` — v1/v2 crosswalk labels;
- `results/metric_v2/oracles_v2/main_matrix_v1.sidecar.jsonl` — 40-task derived oracle sidecar;
- `reports/metric_v2/independent_executor_report.json` — 7,200-row executor surface;
- `reports/metric_v2/gates/representation_control.json` — canonical serialization control;
- `reports/metric_v2/original_evidence_hashes.sha256` — 1,407-file original-evidence lock;
- commit `b3a13fd` — v2 implementation and offline reports.

The v2 source outputs predate the revised metric. The metric was frozen and committed before full v2 aggregate inspection; this is a frozen post hoc reanalysis, not a preregistration.

## 4. Hidden confounders and red flags

The decisive hidden variable is not model routing but state representation. `rolling_summary` stores the final state in `SUMMARY`, while the current v2 spec classifies `SUMMARY` as annotation. `rolling_visible_carry_forward` and `rolling_visible_fields_only` expose candidate universes in positive fields, so exclusion safety is structurally different from typed SSR.

The executor and v2 scorer share task semantics but implement different thresholds: the executor requires allowed paths to be present in the carried state, while the v2 sidecar treats paths as optional unless emitted by the answer. This is a declared criterion difference, not an implementation failure, but it prevents treating either system as a perfect ground truth for the other.

## 5. Safe, pilot-only, and blocked sets

- `SAFE_FOR_MATRIX`: original raw outputs, frozen oracle, v1 scores, and the v2 evidence/hash lineage.
- `SAFE_ONLY_AS_PILOT`: pooled v2 validity rates across all six methods; current figures are diagnostic until the representation decision is frozen.
- `RERUN_REQUIRED`: offline v2 rescoring and executor analysis after any field-role or path-sufficiency change.
- `EXCLUDE_FROM_REVISION_CLAIMS`: method-free pooled executor contrast and any claim that rolling-summary failure establishes model/state failure rather than representation mismatch.

## 6. Required freeze specification

Before revision-level analysis, freeze:

1. the final-answer operational surface (`A_final_v2` candidate) separately from `A_legacy_rawscan`;
2. field-role mapping for `SUMMARY`, `VISIBLE_KEEP`, `VISIBLE_ALLOWED_SCOPE`, and SSR `OUT`/`ALW`;
3. whether allowed paths are required state items or optional carried items;
4. the method-stratified executor estimand and task-cluster bootstrap;
5. the rule that no new model calls or outcome-dependent row replacement are permitted.

## 7. Machine-readable findings

```json
{
  "finding_id": "PVC-V2-REPRESENTATION-001",
  "agent": "prematrix-variable-control-agent",
  "severity": "R3",
  "status": "fail",
  "claim": "A non-axis representation variable differs systematically across methods and affects v2 validity.",
  "evidence_refs": [
    {"type": "file", "ref": "reports/metric_v2/gates/representation_control.json", "hash": null},
    {"type": "file", "ref": "results/metric_v2/raw_inputs/primary.jsonl", "hash": null},
    {"type": "file", "ref": "specs/carried_state_validity_v2.yaml", "hash": null},
    {"type": "commit", "ref": "b3a13fd", "hash": null}
  ],
  "affected_runs": ["primary_7200_all_six_methods"],
  "affected_artifacts": ["results/metric_v2/scores_v2/primary.production.jsonl"],
  "recommended_action": "Freeze a representation-neutral adapter or treat representation as a blocking method variable before revision claims.",
  "blocks_main_matrix": true
}
```
