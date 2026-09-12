# Variable-Method-Result Evidence Chain

Date: 2026-06-23

Scope: PCG dynamic-state v2 SSR-downgrade evidence chain. This report links
variable control, method versioning, and observed results. Paper external
validity remains out of scope.

## Core Finding

The downgrade claim is defensible only after separating three layers that were
previously easy to blur:

1. Variable layer: the 2026-06-19 ECVS harder/static sequence drifted in task
   substrate, wrapper, method mapping, and metric; it is calibration history,
   not a pooled effect estimate.
2. Method layer: the first run that can carry the downgrade decision is the
   stricter PCG dynamic-state v2 line, with split answer/governance metrics and
   canonical method arms.
3. Result layer: under that stricter line, visible carry explains more of the
   usable performance than mature/schema-heavy SSR. The two missing rows were
   backfilled; the static sanity gate passed; the conclusion did not change.

The safe claim is narrow: tested mature/schema-heavy SSR was downgraded to an
ablation/diagnostic arm in PCG dynamic-state v2. The record does not support a
universal statement that all SSR variants fail.

## Evidence Reviewed

| evidence class | artifact | anchor |
|---|---|---|
| variable freeze | `docs/protocol/pcg_dynamic_state_v2_main_matrix/FREEZE_PACKET_INDEX.json` | `model_visible_sha256=f26636d5c6f01b13e659d9162a2e5b366d8c448d2c03190dfbe137a392d3b1a1`; `oracle_sha256=670c47db3b1a873eba10045fc4e8e656d464128a225850854cceb3fbd4f85280`; `strict_scorer_sha256=67c18a606d50760990ef28054b059058c69e758d8439b1caa1ed2e8f1dc6417b` |
| variable audit | `PREMATRIX_VARIABLE_CONTROL_REPORT_20260623.md` | 2026-06-19 harder/static = `SAFE_ONLY_AS_CALIBRATION`; PCG v2 random10 = local pilot |
| method audit | `METHOD_DELTA_REPORT_20260623.md` | M0-M5 method history; mature SSR downgraded for tested probes |
| result chain | `SSR_DOWNGRADE_EVIDENCE_CHAIN_20260623.md` | decisive PCG v2 plus random10/provider probes |
| core H5 lock | `data/pcg_dynamic_state_v2/h5_release_lock_20260623/H5_LOCK_SUMMARY.json` | `row_count=644`, `h5_private_raw_lock_rows=644`, `failures=[]` |
| backfill H5 lock | `data/pcg_dynamic_state_v2/h5_targeted_backfill_lock_20260623/H5_LOCK_SUMMARY.json` | `row_count=2`, `h5_private_raw_lock_rows=2`, `failures=[]` |
| static sanity H5 lock | `data/pcg_dynamic_state_v2/h5_static_sanity_lock_20260623/H5_LOCK_SUMMARY.json` | `row_count=4`, `h5_private_raw_lock_rows=4`, `failures=[]` |

Evidence strength: E5 for the committed PCG v2 downgrade packet and addenda;
public-hash narrative evidence for historical 2026-06-18/2026-06-19 context.

## Variable Layer

The intended matrix axes are task, model/provider condition, method, state
budget, and run id. Everything else must be frozen or explicitly recorded.

| variable | intended role | controlled status | consequence |
|---|---|---|---|
| task substrate | matrix axis in future main matrix; fixed within each pilot | frozen in PCG v2 packets; drifted across 2026-06-19 harder/static variants | 6/19 harder/static cannot be pooled |
| method arm | intended axis | frozen per packet; method semantics changed from ECVS wrappers to PCG v2 canonical runner | old `mature_ssr_loop` rows are not identical to canonical PCG v2 mature SSR |
| state budget | intended axis | `300/600/1200` in random10; `600/1200` in decisive; `600` in static sanity | budget is interpretable only within packet |
| provider route | intended condition only when declared | direct provider rows separated from OpenRouter rows; fallback disabled in inspected direct packets | direct-provider panels can be used locally; OpenRouter is appendix/robustness only |
| sampling | controlled variable | temperature explicit `0`; max tokens `4096`; thinking disabled; tools/web disabled where recorded | reduces hidden decoding drift |
| metric | dependent variable | PCG v2 uses `answer_success`, `state_governance_success`, `reliable_composite_success` | old ECVS bundled `reliable_success` is not a substitute |
| runner implementation | controlled variable | 2026-06-22 six-method runner supplies canonical PCG v2 method contracts | 6/19 wrapper results stay historical |

The 2026-06-19 harder/static series changed several variables at once: task
substrate, wrapper file, difficulty profile, and metric. The observed swing
from near-floor to near-ceiling is therefore evidence of protocol sensitivity,
not a stable SSR effect estimate.

## Method Layer

The method chain has a clean break at PCG dynamic-state v2.

| phase | method status | admissible role |
|---|---|---|
| M0: early SSR-positive probes | legacy/favorable compaction; SSR looked strong | historical motivation only |
| M1: 2026-06-19 ECVS frontier/realSWE-style | visible carry baseline reaches ceiling beside mature SSR | confound discovery |
| M2: 2026-06-19 harder/static stress | substrate and wrappers shift across attempts | calibration/history |
| M3: 2026-06-20 PCG v2 decisive | split metrics; canonical method comparison begins | primary downgrade evidence |
| M4: 2026-06-22 direct-provider random10 | six-method local provider probes | robustness support, not full main matrix |
| M5: 2026-06-23 addenda | targeted backfill and static sanity | missingness closure and runner-validity gate |

The critical method distinction is output-bearing state. `rolling_visible_carry_forward`
can carry visible candidates mechanically. `mature_ssr_loop` must place final
required tokens in `OUT` and allowed paths in `ALW`; the deterministic slot
compiler then produces the final answer from those fields. `rolling_visible_fields_only`
is a negative control, not a competitive method. `ssr_no_visible_carry` tests
schema without deterministic visible carry.

The static sanity packet confirms that the canonical mature SSR runner is not
trivially broken: on a frozen static-control task, `mature_ssr_loop` reached
`answer_success=1.0`, `state_governance_success=1.0`, and
`reliable_composite_success=1.0`. That finding blocks a narrow implementation
objection. It does not promote mature SSR back to primary-method status.

## Result Layer

The decisive PCG v2 result is negative for mature SSR as a primary method.

| packet | method | answer | governance | reliable | interpretation |
|---|---|---:|---:|---:|---|
| DeepSeek decisive 104-row | `rolling_visible_carry_forward` | 0.808 | 0.654 | 0.500 | strongest compared arm |
| DeepSeek decisive 104-row | `mature_ssr_loop` | 0.192 | 0.231 | 0.115 | downgraded |
| DeepSeek decisive 104-row | `rolling_summary` | 0.308 | 0.231 | 0.077 | weak baseline |
| DeepSeek decisive 104-row | `loop_only` | 0.000 | 0.962 | 0.000 | governance alone is insufficient |

The 2026-06-23 backfill closed the decisive mature-SSR missing row as
`measured/ok` with `reliable=False`. The decisive count remains
`3/26 = 0.115` for mature SSR and `13/26 = 0.500` for visible carry.

The direct-provider random10 packets reproduce the direction of the effect:

| packet | visible reliable | mature reliable | `ssr_no_visible_carry` reliable | role |
|---|---:|---:|---:|---|
| DeepSeek random10 rerun100 | 0.300 | 0.000 | 0.000 | local provider probe |
| Qwen random10 | 0.233 | 0.100 | 0.067 | local provider probe |
| Kimi random10 | 0.100 | 0.000 | 0.067 | local provider probe |

These probes do not form the final 5-model main matrix. They do show that the
decisive DeepSeek pattern is not isolated to one failed run.

## Addenda

Two addenda now close likely reviewer objections.

| objection | addendum | result | claim impact |
|---|---|---|---|
| Missing rows might reverse the decision | targeted two-row backfill | both rows `measured/ok`, both `reliable=False` | no reversal |
| Canonical mature SSR runner might be broken | static sanity gate | `mature_ssr_loop` reliable `1.0` on frozen static control | runner-validity objection reduced |

Both addenda are append-only. They do not overwrite original result packets and
must not be pooled as new matrix rows.

## Hash And Release Status

The locked evidence covers the core PCG v2 downgrade packets and the two
addenda:

| lock | rows | H5 private raw rows | failures |
|---|---:|---:|---:|
| core PCG v2 lock | 644 | 644 | 0 |
| targeted backfill lock | 2 | 2 | 0 |
| static sanity lock | 4 | 4 | 0 |

In this anonymous review package, the H5 locks are paired with released raw
outputs and a strict E5 verifier. The strict E5 check must run from a Git clone
so `git HEAD` can supply the code-commit link; source archives can still verify
the public H5 locks.

## Pass/Fail Table

| claim | status | evidence | risk |
|---|---|---|---|
| 2026-06-19 harder/static results are one aligned experiment | fail | variable drift across substrate, wrapper, method mapping, and metric | R3 |
| PCG v2 decisive result supports mature SSR downgrade | pass | mature reliable `3/26`; visible reliable `13/26` | R0 scoped |
| targeted missing rows could rescue mature SSR | fail | backfilled mature SSR row reliable `False` | R0 |
| canonical mature SSR runner is trivially broken | fail | static sanity mature SSR reliable `1.0` | R1 |
| full historical 6/18-6/22 chain is E5 result-locked | fail | core PCG v2/addenda are E5; historical files are public-hash context | R3 |

## Red Flags

- Do not pool 2026-06-19 harder/static variants with PCG v2 rows.
- Do not describe static65/static82/static90 as having passed the canonical
  static sanity gate; they motivated the gate only.
- Do not mix direct-provider rows with OpenRouter rows in a main-effect table.
- Do not treat historical calibration rows as main-effect rows.

## Open Questions

- Full historical narrative evidence remains outside the E5 result lock.
- The main matrix still needs its own GO packet.

## Required Fixes Before Main Matrix

1. Keep provider-purity gates active: direct provider and OpenRouter rows remain
   separate.
2. Use the frozen PCG v2 task/scorer/method contracts for any new main-matrix
   execution.
3. Keep the anonymous release repo curated; exclude `.env`, local scratch data,
   personal paths, and non-review material.
4. Run release-level hash verification inside the clean Git clone.

## Safe To Include

- DeepSeek decisive PCG v2 as primary method-triage evidence.
- DeepSeek/Qwen/Kimi random10 as scoped direct-provider robustness probes.
- Targeted backfill as missingness closure.
- Static sanity as runner-discrimination gate.
- 2026-06-19 harder/static series only as calibration/history explaining why
  PCG v2 controls were introduced.

## Exclude Or Rerun

- Any pooled effect estimate over 2026-06-19 harder/mid/static variants.
- Legacy oracle-compacted SSR positives as primary method evidence.
- Preflight-only, sandbox-blocked, or failed-latin1 directories as result
  evidence.
- Historical calibration rows as main-effect rows.

## Confidence

High for the PCG v2 downgrade evidence chain because the core rows and addenda
have row-level H5 locks, released raw outputs, and E5 verifier coverage. Medium
for the full 6/18-6/19 historical timeline because the older artifacts remain
context rather than result-locked evidence.

## Machine-Readable Findings

```json
[
  {
    "finding_id": "VMR-20260623-001",
    "agent": "variable-method-result-evidence-chain",
    "severity": "R0",
    "status": "pass",
    "claim": "Tested mature/schema-heavy SSR is downgraded to ablation/diagnostic status under PCG dynamic-state v2.",
    "evidence_refs": [
      {"type": "run_log", "ref": "results/_probe_ecvs_deepseek_v4pro_pcg_dynamic_state_v2_e10_h3_decisive_13task_4method_2budget_1run/POST_RUN_AUDIT.md", "hash": null},
      {"type": "manifest", "ref": "data/pcg_dynamic_state_v2/h5_release_lock_20260623/ROW_H5_MANIFEST.jsonl", "hash": null},
      {"type": "metric", "ref": "data/pcg_dynamic_state_v2/h5_release_lock_20260623/scores_with_h5_hashes.csv", "hash": null}
    ],
    "affected_runs": ["DeepSeek decisive PCG v2", "DeepSeek/Qwen/Kimi random10"],
    "affected_artifacts": ["scores.csv", "CONTROLLED_ROWS.jsonl", "ROW_H5_MANIFEST.jsonl"],
    "recommended_action": "Use scoped wording; do not claim universal SSR failure.",
    "blocks_main_matrix": false
  },
  {
    "finding_id": "VMR-20260623-002",
    "agent": "variable-method-result-evidence-chain",
    "severity": "R3",
    "status": "fail",
    "claim": "The 2026-06-19 harder/static sequence is aligned enough for pooled effect estimation.",
    "evidence_refs": [
      {"type": "config", "ref": "configs/_probe_ecvs_deepseek_v4pro_harder_stress_v1_visiblecarry_vs_maturessrloop_15task_2method_3budget_1run.json", "hash": null},
      {"type": "config", "ref": "configs/_probe_ecvs_deepseek_v4pro_harder_stress_v1_static90_visiblecarry_vs_maturessrloop_15task_2method_3budget_1run.json", "hash": null},
      {"type": "run_log", "ref": "docs/protocol/pcg_dynamic_state_v2_main_matrix/PREMATRIX_VARIABLE_CONTROL_REPORT_20260623.md", "hash": null}
    ],
    "affected_runs": ["2026-06-19 harder/static ECVS stress sequence"],
    "affected_artifacts": ["configs", "summary_by_method_budget.csv"],
    "recommended_action": "Keep as calibration/history only.",
    "blocks_main_matrix": true
  },
  {
    "finding_id": "VMR-20260623-003",
    "agent": "variable-method-result-evidence-chain",
    "severity": "R0",
    "status": "pass",
    "claim": "The two backend_or_empty_output gaps were closed without rescuing mature SSR.",
    "evidence_refs": [
      {"type": "run_log", "ref": "results/pcg_dynamic_state_v2_targeted_missing_rows_backfill_20260623/BACKFILL_AUDIT.json", "hash": null},
      {"type": "manifest", "ref": "data/pcg_dynamic_state_v2/h5_targeted_backfill_lock_20260623/ROW_H5_MANIFEST.jsonl", "hash": null}
    ],
    "affected_runs": ["targeted two-row backfill"],
    "affected_artifacts": ["BACKFILL_CONTROLLED_ROWS.jsonl", "backfill_scores_with_h5_hashes.csv"],
    "recommended_action": "Report as append-only missingness closure.",
    "blocks_main_matrix": false
  },
  {
    "finding_id": "VMR-20260623-004",
    "agent": "variable-method-result-evidence-chain",
    "severity": "R1",
    "status": "pass",
    "claim": "The canonical mature SSR runner is not trivially broken on a static control.",
    "evidence_refs": [
      {"type": "run_log", "ref": "results/pcg_dynamic_state_v2_static_sanity_deepseek_1task_4method_budget600_1run_20260623/STATIC_SANITY_GATE_REPORT.md", "hash": null},
      {"type": "manifest", "ref": "data/pcg_dynamic_state_v2/h5_static_sanity_lock_20260623/ROW_H5_MANIFEST.jsonl", "hash": null}
    ],
    "affected_runs": ["canonical static sanity gate"],
    "affected_artifacts": ["STATIC_SANITY_SUMMARY.json", "static_sanity_scores_with_h5_hashes.csv"],
    "recommended_action": "Use as runner-discrimination gate only; do not pool with result evidence.",
    "blocks_main_matrix": false
  }
]
```
