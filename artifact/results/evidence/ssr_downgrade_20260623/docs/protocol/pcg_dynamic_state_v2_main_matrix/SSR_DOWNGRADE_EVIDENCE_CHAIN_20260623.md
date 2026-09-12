# SSR Downgrade Evidence Chain

Date: 2026-06-23

Scope: evidence-chain audit for the claim that tested mature/schema-heavy SSR
should be downgraded from primary method to ablation/diagnostic status. This is
not a main-matrix entry audit.

## Bottom Line

The 2026-06-18 to 2026-06-22 artifacts form a coherent SSR-downgrade evidence
chain if each round is assigned the right role:

1. The 2026-06-18 MatrixGate audit shows that older public SSR evidence cannot
   be inherited as clean matrix evidence.
2. The 2026-06-18 late / 2026-06-19 00:24-00:43 early probes show why SSR was
   still plausible: old SSR variants looked strong under favorable/legacy
   compaction.
3. The 2026-06-19 ECVS frontier/realSWE-style probes expose the key confound:
   visible carry-forward can reach the same ceiling as mature SSR.
4. The 2026-06-19 harder/static stress sequence shows repair instability:
   near-floor, mixed, and near-ceiling outcomes appear as task substrate and
   wrapper details change.
5. The 2026-06-20 PCG dynamic-state v2 decisive probe supplies the actual
   downgrade decision under the stricter split-metric protocol.
6. The 2026-06-22 random10 provider pilots confirm that the visible-carry
   pattern is not a single DeepSeek-only accident, while still remaining local
   calibration/provider-probe evidence.

This chain supports the scoped statement:

> In the tested PCG dynamic-state protocol, mature/schema-heavy SSR did not
> retain independent method advantage and was downgraded to an
> ablation/diagnostic arm. The paper should not claim universal SSR failure.

## Round Roles

| round | artifacts | observed result | evidence-chain role | safe use |
|---|---|---:|---|---|
| 2026-06-18 MatrixGate | 2026-06-18 historical MatrixGate gate report | `NO_GO` for old `artifact-ssr-public` direct entry | Blocks inheritance of old public positives | Method-history / evidence-quality preface |
| 2026-06-18 late / 2026-06-19 early probes | `_probe_no_reflexion_*`, `_probe_frontier_hard10_*`, `_probe_frontier_hard10_plus_real_swe_unseen1_*` | `ssr_only` reliable 1.000 in inspected summaries | Shows SSR was a live hypothesis under legacy/favorable conditions | Motivation; do not use as final SSR win |
| 2026-06-19 ECVS frontier/realSWE-style | rolling/ReAct/reflexion, SSR-only/SSR-loop, mature SSR, visible-carry baseline packets | mature SSR and visible carry both reach ceiling in separate packets | Identifies visible carry as the confound that can explain apparent SSR gains | Design rationale for PCG v2 controls |
| 2026-06-19 harder/static stress | harder, mid, mid_fixed, 65_pressure, static65/82/90 | results swing from near-floor to near-ceiling | Shows repair attempts were protocol-sensitive and not a stable SSR rescue | Calibration appendix; not pooled |
| 2026-06-20 PCG v2 decisive | `_probe_ecvs_deepseek_v4pro_pcg_dynamic_state_v2_e10_h3_decisive_13task_4method_2budget_1run` | mature reliable 0.115 vs visible reliable 0.500; bootstrap mature-visible diff -0.385, CI [-0.577, -0.154] | Core downgrade decision | Primary downgrade evidence |
| 2026-06-22 random10 providers | DeepSeek rerun100, Qwen, Kimi | visible-carry reliable exceeds mature SSR in all three direct-provider packets | Provider-robustness support for downgrade pattern | Scoped robustness/provider probes |

## Alignment Check

No fatal contradiction was found once the artifacts are treated as an evidence
chain rather than as one pooled experiment.

Important role constraints:

- The early SSR-positive probes are not contradictory evidence against the
  downgrade. They are the reason the stricter PCG v2 controls were needed.
- The 2026-06-19 harder/static sequence is not one aligned comparison. Its
  value is that repeated rescue/calibration attempts failed to produce a stable
  independent SSR advantage.
- The 2026-06-20 PCG v2 decisive packet is the first inspected packet that can
  carry the downgrade decision itself.
- The 2026-06-22 random10 packets should be described as direct-provider
  robustness/calibration evidence, not as a completed confirmatory main matrix.

## Key Metrics Checked

### Early strong positives

- `_probe_no_reflexion_deepseek_v4pro_thinking_disabled_15task_2method_3budget_1run`:
  `ssr_only` reliable 1.000 vs `rolling_summary` reliable 0.822.
- `_probe_frontier_hard10_no_reflexion_deepseek_v4pro_thinking_disabled_10task_2method_3budget_1run`:
  `ssr_only` reliable 1.000.
- `_probe_frontier_hard10_plus_real_swe_unseen1_no_reflexion_deepseek_v4pro_thinking_disabled_11task_2method_3budget_1run`:
  `ssr_only` reliable 1.000 vs `rolling_summary` reliable 0.788.

These are retained as positive historical motivation, not as final method
evidence.

### 2026-06-19 ECVS confound discovery

- rolling/ReAct/reflexion packet:
  `rolling_summary` reliable 0.333, `react_literature_adapted` 0.100,
  `reflexion_literature_adapted` 0.300.
- SSR-only/SSR-loop packet:
  `ssr_loop` reliable 0.367, `ssr_only` 0.167.
- mature SSR packet:
  `ssr_loop` reliable 1.000, `ssr_only` 0.900.
- visible-carry baseline:
  `rolling_visible_carry_forward` reliable 1.000.

This combination is exactly why the downgrade argument should be framed as
"visible carry explains the useful part of the apparent SSR benefit" rather
than "all SSR-like interventions fail everywhere."

### 2026-06-19 harder/static stress

- harder v1: mature SSR 0.000, visible carry 0.044 reliable.
- mid: mature SSR 0.000, visible carry 0.022.
- mid_fixed: mature SSR 1.000, visible carry 0.978.
- 65_pressure: both mature SSR and visible carry 0.667.
- static65/static82/static90: mature SSR 1.000; visible carry 0.978, 0.933,
  0.956.

This is not a stable effect estimate. It is evidence of sensitivity to task
substrate/wrapper/difficulty and therefore supports the decision to stop using
these variants as final SSR evidence.

### 2026-06-20 PCG v2 decisive

From `POST_RUN_AUDIT.md` and `scores.csv`:

| method | answer | governance | reliable composite |
|---|---:|---:|---:|
| `rolling_summary` | 0.308 | 0.231 | 0.077 |
| `loop_only` | 0.000 | 0.962 | 0.000 |
| `rolling_visible_carry_forward` | 0.808 | 0.654 | 0.500 |
| `mature_ssr_loop` | 0.192 | 0.231 | 0.115 |

Recorded decision:

`DOWNGRADE_MATURE_SSR_TO_ABLATION_DIAGNOSTIC`

The original decisive packet contained one `rerun_required` row in
`mature_ssr_loop` (`backend_or_empty_output`). The 2026-06-23 targeted
backfill closed it as `measured/ok` with `reliable=False`, leaving the observed
gap versus visible carry unchanged.

### 2026-06-22 direct-provider random10

| packet | visible reliable | mature reliable | `ssr_no_visible_carry` reliable | note |
|---|---:|---:|---:|---|
| DeepSeek rerun100 | 0.300 | 0.000 | 0.000 | original one-row `loop_only` gap closed by targeted backfill |
| Qwen3.7-Max | 0.233 | 0.100 | 0.067 | clean 180/180 measured rows |
| Kimi K2.6 | 0.100 | 0.000 | 0.067 | clean 180/180 measured rows |

These packets support the direction of the downgrade, but the wording should
remain provider-probe/local-calibration rather than full confirmatory matrix.

## Targeted Missing-Row Backfill

On 2026-06-23, the two reviewer-facing `backend_or_empty_output` gaps were
closed with an append-only targeted backfill packet:

`results/pcg_dynamic_state_v2_targeted_missing_rows_backfill_20260623/`

The backfill reused the original configs, task manifests, method protocols,
runners, scorers, provider, model, sampling controls, and no-tool/no-fallback
policy. It did not overwrite the original result packets.

| packet | target row | gate after backfill | reliable |
|---|---|---|---:|
| `deepseek_decisive_104` | `pcgds_v2_00026_decoy_heavy_same_prefix_config_easy`, `mature_ssr_loop`, budget 600, run 1 | `measured/ok` | `False` |
| `deepseek_random10_rerun100` | `pcgds_v2_00032_decoy_heavy_same_prefix_config_hard`, `loop_only`, budget 300, run 1 | `measured/ok` | `False` |

The decisive mature SSR count remains `3/26 = 0.115`; visible carry remains
`13/26 = 0.500`. The random10 backfill row is `loop_only`, so it is not part of
the SSR-vs-visible comparison.

No additional API rerun is required for the scoped downgrade claim.

Required paper/appx wording:

- Keep the backfill as a targeted missingness closure, not a new protocol or
  new matrix.
- Say explicitly that early SSR positives are motivation/history, not final
  support for SSR as a primary method.
- Say explicitly that harder/static stress is rescue/calibration history, not a
  pooled effect estimate.
- Keep the downgrade wording scoped to the tested mature/schema-heavy SSR
  operationalization.

## H5 Lock Scope

Current core lock:

`data/pcg_dynamic_state_v2/h5_release_lock_20260623/`

Verifier result:

- `passed: true`
- `row_manifest_rows: 644`
- `h5_private_raw_lock_rows: 644`
- `failures: []`

The core lock covers these four PCG v2 packets as originally observed:

1. DeepSeek decisive 104-row packet.
2. DeepSeek random10 rerun100.
3. Qwen random10.
4. Kimi random10.

A targeted backfill addendum lock was then built:

`data/pcg_dynamic_state_v2/h5_targeted_backfill_lock_20260623/`

Verifier result:

- `passed: true`
- `row_manifest_rows: 2`
- `h5_private_raw_lock_rows: 2`
- `artifact_manifest_rows: 23`
- `failures: []`

The two addendum row hashes are:

- decisive mature SSR row:
  `8e0bcefdf5f94f3b3b11fbd1dde4d98ae758c6839ec40ad6055a08644914ea0e`
- random10 loop-only row:
  `7a542257b3697dd27b07baa4726b5c654a3dde6619185349c129827c4c840091`

The canonical static sanity gate was also executed and locked:

`data/pcg_dynamic_state_v2/h5_static_sanity_lock_20260623/`

Verifier result:

- `passed: true`
- `row_manifest_rows: 4`
- `h5_private_raw_lock_rows: 4`
- `artifact_manifest_rows: 30`
- `failures: []`

This gate is not downgrade evidence. Its role is to close the narrow objection
that the canonical 2026-06-22 `mature_ssr_loop` runner is trivially broken on a
static control.

The combined defensible claim is now:

> the core PCG v2 downgrade evidence is H5-locked, and the two targeted
> missing-row backfills plus the static sanity gate are H5-locked in append-only
> addenda.

This still does not cover all historical evidence-chain rounds. In particular,
it does not lock the 2026-06-18 MatrixGate report, the 2026-06-19 early
strong-positive probes, the 2026-06-19 frontier/realSWE ECVS packets, or the
2026-06-19 harder/static stress packets.

This is acceptable if the H5 claim is phrased as:

> the core PCG v2 downgrade evidence and the targeted missingness backfill have
> H5 private-raw locks; the canonical static sanity gate has a separate H5
> private-raw lock.

It is not acceptable to phrase it as:

> the full 2026-06-18 to 2026-06-22 downgrade evidence chain is H5-locked.

## Remaining Follow-Up Material

No paid model rerun is needed for the scoped downgrade claim. The remaining
material gap is optional provenance hashing for the full historical evidence
chain:

- hash the MatrixGate and read-library reports used as narrative evidence;
- hash the 2026-06-19 configs, scores, summaries, run plans, preflight audits,
  and controlled rows where present;
- mark early/ECVS/harder/static packets as `HISTORICAL_POSITIVE`,
  `CONFOUND_DISCOVERY`, or `REPAIR_CALIBRATION`, not `PRIMARY_DOWNGRADE_RESULT`;
- keep the existing H5 private-raw lock as the core PCG v2 result lock.

## Safe Paper Wording

Safe:

> Early SSR-positive probes motivated the method, but successive controls
> exposed visible carry-forward as a key confound. Under the stricter PCG
> dynamic-state v2 split-metric protocol, mature/schema-heavy SSR failed the
> preregistered decision rule and was downgraded to an ablation/diagnostic arm.

Unsafe:

> SSR universally failed.

Unsafe:

> All 2026-06-18 to 2026-06-22 evidence-chain artifacts are already H5-locked
> for anonymous GitHub review.
