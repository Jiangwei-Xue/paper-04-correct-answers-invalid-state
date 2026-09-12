# PreMatrix Variable Control Report: 2026-06-19 Alignment

Date: 2026-06-23

Scope: variable-control status for 2026-06-19 ECVS harder/static probes and
nearby PCG v2 evidence. Paper external validity is out of scope.

## Summary

Variable-control status for the 2026-06-19 harder/static sequence is
`SAFE_ONLY_AS_CALIBRATION`. It is not aligned enough for main-matrix effect
estimation. The later PCG v2 direct-provider random10 packets are better
controlled but still local pilots, not the frozen 5-model main matrix.

## Intended Matrix Axes

For the future PCG v2 main matrix, intended axes are:

- task;
- model/provider condition;
- method;
- state budget;
- run id.

Everything else should be frozen or explicitly recorded.

## Controlled Variables Observed

| variable | observed control |
|---|---|
| provider route in newer direct probes | direct provider, fallback disabled where recorded |
| state budgets | generally `300`, `600`, `1200` for ECVS harder/static and random10 PCG |
| methods within each 2026-06-19 harder/static packet | usually `rolling_visible_carry_forward` and `mature_ssr_loop` |
| DeepSeek model in 2026-06-19 harder/static configs | `deepseek-v4-pro` direct |
| reasoning mode in newer configs | `thinking.type=disabled` where recorded |

## Uncontrolled Or Drifted Variables

| variable | drift | affected runs | risk |
|---|---|---|---|
| task substrate | harder, mid, mid_fixed, 65, 65_pressure, static65/82/90 use different manifests and hashes | 2026-06-19 harder/static series | R3 |
| runner wrapper | wrapper file changes per substrate | 2026-06-19 harder/static series | R2 |
| internal method mapping | ECVS `mature_ssr_loop` maps to old `ssr_loop`, not 2026-06-22 canonical PCG v2 slot compiler | 2026-06-19 harder/static series | R3 |
| metric definition | bundled `reliable_success` versus PCG v2 split metrics | ECVS vs PCG v2 | R3 |
| run status | some directories are preflight-only or blocked attempts | 2026-06-19 `65` and blocked attempts | R3 |
| difficulty/profile | early/mid near-floor, mid_fixed/static near-ceiling, 65_pressure mixed | 2026-06-19 harder/static series | R3 |

## Variable Drift Table

| run family | task hash status | runner status | metric status | inclusion |
|---|---|---|---|---|
| harder v1 | distinct substrate hashes | distinct wrapper | bundled ECVS reliable | SAFE_ONLY_AS_CALIBRATION |
| harder v1 mid | distinct substrate hashes | distinct wrapper | bundled ECVS reliable | SAFE_ONLY_AS_CALIBRATION |
| harder v1 mid_fixed | distinct substrate hashes | distinct wrapper | bundled ECVS reliable | SAFE_ONLY_AS_CALIBRATION |
| harder v1 65 | preflight-only in inspected result directory | distinct wrapper | no result scores in inspected dir | EXCLUDE_FROM_RESULTS |
| harder v1 65_pressure | distinct substrate hashes | distinct wrapper | bundled ECVS reliable | SAFE_ONLY_AS_CALIBRATION |
| static65/static82/static90 | distinct static substrates | old ECVS wrapper | bundled ECVS reliable | CANDIDATE_STATIC_SANITY_EVIDENCE_ONLY |
| PCG v2 random10 direct | PCG v2 substrate | 2026-06-22 six-method runner | strict/split PCG metrics | SAFE_AS_LOCAL_PILOT |

## Hidden Confounders

- Model-provider alias/revision is not enough for main-matrix GO unless exact
  provider metadata and supported-parameter snapshots are recorded in the run
  window.
- Old ECVS wrappers do not provide the same `compile_state` /
  `build_final_prompt` contract as the canonical 2026-06-22 PCG v2 runner.
- `reliable_success` in old ECVS summaries is not equivalent to PCG v2
  `reliable_composite_success`.

## Runs Safe For Matrix

None of the 2026-06-19 harder/static runs are safe for the future main matrix.
They are safe as calibration/history only.

## Runs Requiring Rerun Or Exclusion

- Rerun required for primary claims: any 2026-06-19 harder/static result if it
  is to be used under PCG v2 metrics.
- Exclude as result evidence: `*_sandbox_network_blocked_attempt`,
  `*_failed_latin1_*`, and preflight-only result directories.
- Use only as static sanity candidate evidence: static65/static82/static90.

## Freeze Spec Recommendation

- Freeze the 2026-06-22 PCG v2 six-method runner.
- Freeze strict scorer with `answer_success` and `reliable_composite_success`.
- Freeze provider-purity policy: direct rows and OpenRouter rows never pooled.
- Canonical static sanity packet has been run and passed; retain it as a
  non-pooled gate appendix.
- Keep 2026-06-19 ECVS harder/static results out of primary aggregation.

## Confidence

High that the 2026-06-19 sequence has protocol/variable drift. Medium that all
run timestamps are exact, because file timestamps were treated as lower-trust
than configs and result artifacts.

## Machine-Readable Findings

```json
[
  {
    "finding_id": "PVC-20260623-001",
    "agent": "prematrix-variable-control-agent",
    "severity": "R3",
    "status": "fail",
    "claim": "2026-06-19 harder/static runs are aligned enough for one main effect estimate.",
    "evidence_refs": [
      {"type": "config", "ref": "configs/_probe_ecvs_deepseek_v4pro_harder_stress_v1_visiblecarry_vs_maturessrloop_15task_2method_3budget_1run.json", "hash": null},
      {"type": "config", "ref": "configs/_probe_ecvs_deepseek_v4pro_harder_stress_v1_mid_fixed_visiblecarry_vs_maturessrloop_15task_2method_3budget_1run.json", "hash": null},
      {"type": "config", "ref": "configs/_probe_ecvs_deepseek_v4pro_harder_stress_v1_static90_visiblecarry_vs_maturessrloop_15task_2method_3budget_1run.json", "hash": null}
    ],
    "affected_runs": ["2026-06-19 harder/mid/static stress series"],
    "affected_artifacts": ["configs", "summary_by_method_budget.csv"],
    "recommended_action": "Keep these runs as calibration/history; rerun under the frozen PCG v2 protocol for primary claims.",
    "blocks_main_matrix": true
  },
  {
    "finding_id": "PVC-20260623-002",
    "agent": "prematrix-variable-control-agent",
    "severity": "R2",
    "status": "pass",
    "claim": "Static65/static82/static90 can serve as candidate evidence for a static sanity control.",
    "evidence_refs": [
      {"type": "output", "ref": "results/_probe_ecvs_deepseek_v4pro_harder_stress_v1_static65_visiblecarry_vs_maturessrloop_15task_2method_3budget_1run/summary_by_method_budget.csv", "hash": null},
      {"type": "output", "ref": "results/_probe_ecvs_deepseek_v4pro_harder_stress_v1_static82_visiblecarry_vs_maturessrloop_15task_2method_3budget_1run/summary_by_method_budget.csv", "hash": null},
      {"type": "output", "ref": "results/_probe_ecvs_deepseek_v4pro_harder_stress_v1_static90_visiblecarry_vs_maturessrloop_15task_2method_3budget_1run/summary_by_method_budget.csv", "hash": null}
    ],
    "affected_runs": ["static65", "static82", "static90"],
    "affected_artifacts": ["summary_by_method_budget.csv"],
    "recommended_action": "Use only to justify why a canonical PCG v2 static sanity control was needed; the separate 2026-06-23 canonical static sanity packet is the actual gate result.",
    "blocks_main_matrix": false
  }
]
```
