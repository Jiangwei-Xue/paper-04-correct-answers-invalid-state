# PCG Dynamic-State v2 Backfill Execution Queue

Date: 2026-06-23

Status: queue plus execution record. This document records pending API
backfills and the DeepSeek targeted rerun completed after explicit
authorization on 2026-06-23.

## Zero-Compute Items Completed In This Patch

- Replace legacy `ssr_loop` / `ssr_only` alias wording with the 2026-06-22
  canonical six-method slot-compiler contract.
- Mark `rolling_visible_fields_only` as a mechanical visible-field negative
  control, not a competitive method arm.
- Require both `answer_success` and `reliable_composite_success` for the crux
  carry-vs-schema interpretation.
- Treat budget direction as exploratory while retaining `300`, `600`, and
  `1200` character budgets.
- Add provider-purity rules: direct-provider or otherwise single-provider rows
  only in main effect tables; OpenRouter rows are robustness/appendix unless a
  paired packet is separately preregistered.
- Keep real-SWE execution assets out of the PCG v2 main claim until a separate
  execution-layer protocol reaches its own GO gate.

## Pending API Backfills

### Q1: Claude Direct Provider Backfill

Status: `PENDING_USER_API_AUTHORIZATION`.

Provider route: official Anthropic API only, not OpenRouter.

Rows: `75` total.

Full missing-task rows: `4 tasks x 6 methods x 3 budgets x 1 run = 72`.

Missing task ids:

- `pcgds_v2_00004_api_migration_state_transition_medium`
- `pcgds_v2_00013_permission_boundary_with_attractive_blocked_path_medium`
- `pcgds_v2_00036_protected_information_redaction_under_task_pressure_medium`
- `pcgds_v2_00021_requirement_overwrite_cumulative_active_medium`

Targeted direct rerun rows:

- `method=ssr_no_visible_carry`, `task_id=pcgds_v2_00019_requirement_overwrite_cumulative_active_medium`, `budget=1200`, `run_id=1`
- `method=mature_ssr_loop`, `task_id=pcgds_v2_00035_protected_information_redaction_under_task_pressure_medium`, `budget=300`, `run_id=1`
- `method=rolling_summary`, `task_id=pcgds_v2_00035_protected_information_redaction_under_task_pressure_medium`, `budget=600`, `run_id=1`

Existing OpenRouter Claude gap-fill rows cover these units as a local
calibration aid only. They must remain robustness/appendix rows and must not be
pooled with direct Anthropic rows.

Recommended execution control: reuse the official Claude runner with
`max_workers=10` and the `45` requests/minute throttle that eliminated the
prior 429 failure mode.

### Q2: OpenAI GPT Direct Targeted Rerun

Status: `PENDING_USER_API_AUTHORIZATION`.

Provider route: official OpenAI API only, not OpenRouter.

Rows: `5` targeted reruns.

- `method=loop_only`, `task_id=pcgds_v2_00001_api_migration_state_transition_easy`, `budget=600`, `run_id=1`
- `method=loop_only`, `task_id=pcgds_v2_00008_api_migration_state_transition_hard`, `budget=300`, `run_id=1`
- `method=rolling_summary`, `task_id=pcgds_v2_00008_api_migration_state_transition_hard`, `budget=1200`, `run_id=1`
- `method=rolling_visible_carry_forward`, `task_id=pcgds_v2_00012_permission_boundary_with_attractive_blocked_path_medium`, `budget=600`, `run_id=1`
- `method=rolling_visible_carry_forward`, `task_id=pcgds_v2_00019_requirement_overwrite_cumulative_active_medium`, `budget=1200`, `run_id=1`

The separate OpenAI missing-4 packet has `72/72` rows and no rerun-required
rows, so it does not need a gap-fill rerun.

### Q3: DeepSeek Direct Targeted Reruns

Status: `COMPLETED_20260623_APPEND_ONLY_BACKFILL`.

Provider route: direct DeepSeek route used by the original decisive and
2026-06-22 random-10 packets.

Rows: `2` targeted reruns.

- `method=mature_ssr_loop`, `task_id=pcgds_v2_00026_decoy_heavy_same_prefix_config_easy`, `budget=600`, `run_id=1`
- `method=loop_only`, `task_id=pcgds_v2_00032_decoy_heavy_same_prefix_config_hard`, `budget=300`, `run_id=1`

Execution packet:

- `results/pcg_dynamic_state_v2_targeted_missing_rows_backfill_20260623/`
- `released_raw_outputs/model_outputs/pcg_dynamic_state_v2_targeted_missing_rows_backfill_20260623/`
- `data/pcg_dynamic_state_v2/h5_targeted_backfill_lock_20260623/`

Result:

- `gate_status=measured`, `gate_reason=ok`
- `answer_success=False`
- `state_governance_success=False`
- `reliable_composite_success=False`
- addendum H5 verifier: `passed=true`, `row_manifest_rows=2`,
  `h5_private_raw_lock_rows=2`, `failures=[]`

The original 100-worker rerun packet remains append-only as observed; this
addendum closes the reviewer-facing missingness gap without overwriting it.

### Q4: Direct-vs-OpenRouter Paired Robustness Packet

Status: optional. This is not a blocker for direct-provider main tables.

If executed, pair the same tasks, methods, budgets, and run ids across direct
provider and OpenRouter-mediated routes. Report it as a route-normalization
robustness analysis. Do not pool route layers.

## Required Before Any API Backfill

- Static sanity gate disposition recorded.
- Canonical runner hash lock present in the freeze packet.
- Provider/model snapshot captured without reading or storing secrets.
- Raw responses, parsed rows, scores, preflight, and hash manifests retained.
- User explicitly authorizes `--run-api` and accepts API cost.
