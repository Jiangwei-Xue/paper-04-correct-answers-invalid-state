# Method Delta Report: SSR Failure Claim And 2026-06-19 Runs

Date: 2026-06-23

Scope: PCG dynamic-state v2 and nearby ECVS/PCG calibration runs. Paper
external validity is out of scope.

## Summary

Status: `HOLD_FOR_MAIN_MATRIX`, but `MATURE_SSR_DOWNGRADED_FOR_TESTED_PROBES`.

The current evidence supports a scoped claim that mature SSR / schema-heavy SSR
does not show independent advantage under the tested PCG dynamic-state probes.
It does not support a universal claim that SSR as a family has failed.

The 2026-06-19 harder/static series contains deliberate method and substrate
changes. Those runs are valid as calibration/history, but they are not one
aligned experiment and must not be pooled as main evidence.

## Evidence Reviewed

- `results/_probe_deepseek_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_rerun100/POST_RUN_AUDIT.md`
- `results/_probe_qwen37max_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_50workers/POST_RUN_AUDIT.md`
- `results/_probe_kimi_k26_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_50workers/POST_RUN_AUDIT.md`
- `results/_probe_ecvs_deepseek_v4pro_pcg_dynamic_state_v2_e10_h3_decisive_13task_4method_2budget_1run/POST_RUN_AUDIT.md`
- `results/_probe_ecvs_deepseek_v4pro_harder_stress_v1_*_visiblecarry_vs_maturessrloop_15task_2method_3budget_1run/summary_by_method_budget.csv`
- `configs/_probe_ecvs_deepseek_v4pro_harder_stress_v1_*_visiblecarry_vs_maturessrloop_15task_2method_3budget_1run.json`
- 2026-06-21 DeepSeek five-day protocol-variable audit report
- supporting scorer-evidence audit note from the 2026-06-22 decision audit

## Method Version Table

| version | active window | runs | method status |
|---|---|---|---|
| M0 | early 2026-06-19 and before | legacy strong-positive SSR probes | Historical only. Audit says strong positives used oracle-aware or over-strong compaction and cannot be inherited. |
| M1 | 2026-06-19 afternoon | ECVS frontier5/realswe5 probes | Calibration. Visible carry baseline reached 30/30 reliable, making visible carry a core mechanism variable. |
| M2 | 2026-06-19 evening | harder/mid/mid_fixed/65/static stress series | Calibration. Task substrate and wrappers changed repeatedly; results swing from near-floor to near-ceiling. |
| M3 | 2026-06-20 | PCG v2 decisive DeepSeek probe | Method-triage evidence. Mature SSR downgraded to ablation/diagnostic. |
| M4 | 2026-06-22 | PCG v2 six-method multi-provider random10 pilots | Local direct-provider evidence. Qwen/Kimi clean; DeepSeek originally had one `backend_or_empty_output` row outside SSR methods, now closed by the 2026-06-23 targeted backfill addendum. |
| M5 | 2026-06-23 freeze patch, targeted backfill, and static sanity | PCG v2 main matrix freeze/backfill/sanity | Backfill gate passed for the two known gaps; canonical static sanity passed; future primary matrix still on HOLD until remaining provider/release gates pass. |

## Method Diff Table

| diff | classification | comparability |
|---|---|---|
| M0 to M1 | fundamental method change; oracle-aware compactor removed | Not comparable; legacy positives must be renamed/excluded. |
| M1 to M2 | dataset/substrate and task-difficulty changes | Not poolable; calibration only. |
| M2 harder to mid_fixed/static | substrate/token-prefix/difficulty correction | Not comparable as one effect estimate. |
| M2 to M3 | benchmark and metric change to PCG dynamic-state split metrics | Comparable only as design history, not as pooled rows. |
| M3 to M4 | method set expanded to six methods and providers expanded | Comparable as scoped local probes only with explicit method/provider disclosure. |

## Confounded Changes

- 2026-06-19 harder/static series changes task substrate hashes, wrapper runner,
  difficulty profile, and sometimes preflight/run status.
- `mature_ssr_loop` in those ECVS wrappers maps internally to older `ssr_loop`,
  not the 2026-06-22 canonical PCG v2 slot compiler.
- Old `reliable_success` is bundled; PCG v2 uses `answer_success`,
  `state_governance_success`, and `reliable_composite_success`.
- Some 2026-06-19 directories are preflight-only or blocked attempts, not result
  packets.

## Pass/Fail Table

| claim | status | evidence | risk |
|---|---|---|---|
| Mature SSR should not be sold as the main winning method. | pass | DeepSeek decisive downgrade; Qwen/Kimi/DeepSeek random10 rates. | R0 scoped |
| SSR universally failed. | fail | `ssr_no_visible_carry` sometimes has answer success, and static ECVS rows reach ceiling. | R3 |
| 2026-06-19 harder/static runs are one aligned experiment. | fail | Different task hashes, wrappers, difficulty variants, and near-floor/near-ceiling swings. | R3 |
| 2026-06-19 runs are useful calibration history. | pass | Summary files and 2026-06-21 audit disposition. | R1 |

## Safe To Include

- PCG v2 direct-provider local probes, only as scoped tested-probe evidence.
- DeepSeek 104-row decisive probe as method-triage evidence.
- 2026-06-19 hard/static series as calibration history explaining why PCG v2
  was needed.

## Exclude Or Rerun

- Legacy oracle-compacted SSR positives from primary claims.
- `*_failed_latin1_*`, `*_sandbox_network_blocked_attempt`, and preflight-only
  packets.
- Any pooled effect estimate across 2026-06-19 harder/mid/static variants.

## Required Fixes Before Main Matrix

- Canonical static sanity with the 2026-06-22 PCG v2 runner is complete and
  passed; keep it as a gate appendix, not main evidence.
- Keep direct-provider and OpenRouter rows separate.
- Treat the 2026-06-23 API backfill as an append-only missingness addendum,
  not as a new protocol version or pooled matrix.

## Confidence

High for local artifact interpretation; medium for timeline exactness because
timestamps are secondary evidence and the repo is a working lab tree.

## Machine-Readable Findings

```json
[
  {
    "finding_id": "MD-SSR-20260623-001",
    "agent": "method-delta-agent",
    "severity": "R0",
    "status": "pass",
    "claim": "Mature SSR is downgraded to ablation/diagnostic for tested PCG probes.",
    "evidence_refs": [
      {"type": "run_log", "ref": "results/_probe_ecvs_deepseek_v4pro_pcg_dynamic_state_v2_e10_h3_decisive_13task_4method_2budget_1run/POST_RUN_AUDIT.md", "hash": null},
      {"type": "run_log", "ref": "results/_probe_qwen37max_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_50workers/POST_RUN_AUDIT.md", "hash": null},
      {"type": "run_log", "ref": "results/_probe_kimi_k26_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_50workers/POST_RUN_AUDIT.md", "hash": null}
    ],
    "affected_runs": ["PCG v2 decisive", "PCG v2 random10 direct-provider pilots"],
    "affected_artifacts": ["POST_RUN_AUDIT.md", "scores.csv"],
    "recommended_action": "Use scoped wording: tested mature SSR did not show independent advantage; do not claim universal SSR failure.",
    "blocks_main_matrix": false
  },
  {
    "finding_id": "MD-SSR-20260623-002",
    "agent": "method-delta-agent",
    "severity": "R3",
    "status": "fail",
    "claim": "The 2026-06-19 harder/static sequence is one comparable experiment.",
    "evidence_refs": [
      {"type": "config", "ref": "configs/_probe_ecvs_deepseek_v4pro_harder_stress_v1_visiblecarry_vs_maturessrloop_15task_2method_3budget_1run.json", "hash": null},
      {"type": "config", "ref": "configs/_probe_ecvs_deepseek_v4pro_harder_stress_v1_mid_fixed_visiblecarry_vs_maturessrloop_15task_2method_3budget_1run.json", "hash": null},
      {"type": "config", "ref": "configs/_probe_ecvs_deepseek_v4pro_harder_stress_v1_static90_visiblecarry_vs_maturessrloop_15task_2method_3budget_1run.json", "hash": null}
    ],
    "affected_runs": ["2026-06-19 harder/mid/static ECVS stress runs"],
    "affected_artifacts": ["summary_by_method_budget.csv", "config json files"],
    "recommended_action": "Report as calibration variants only; do not pool or use as main effect evidence.",
    "blocks_main_matrix": true
  }
]
```
