# PCG Dynamic-State v2 Static Sanity Gate

Date: 2026-06-23

Status: `PASS_EXECUTED_20260623`. This gate defines and records a required
pre-API sanity packet for the PCG dynamic-state v2 main matrix.

## Purpose

The static sanity packet prevents a false negative caused by a broken canonical
runner. Before main-matrix API rows are admissible, the 2026-06-22
`mature_ssr_loop` implementation must recover the answer on a frozen static
control where the historical static SSR-style runner was near ceiling.

This is a runner-discrimination gate, not a main result.

## Executed Packet

The canonical static sanity packet was executed on 2026-06-23:

`results/pcg_dynamic_state_v2_static_sanity_deepseek_1task_4method_budget600_1run_20260623/`

Shape:

- 1 generated frozen static-control task;
- 1 direct-provider model: `deepseek-v4-pro`;
- 4 method arms: `rolling_visible_carry_forward`,
  `rolling_visible_fields_only`, `ssr_no_visible_carry`,
  `mature_ssr_loop`;
- 1 budget: `600`;
- 1 run;
- 4 rows total.

Result:

| method | answer | governance | reliable | note |
|---|---:|---:|---:|---|
| `mature_ssr_loop` | `True` | `True` | `True` | gate pass |
| `rolling_visible_carry_forward` | `True` | `False` | `False` | answer only; governance fails |
| `rolling_visible_fields_only` | `False` | `False` | `False` | negative control leaks forbidden/protected/stale |
| `ssr_no_visible_carry` | `False` | `True` | `False` | blocked-path leakage |

Gate decision: `PASS`.

H5 addendum lock:

`data/pcg_dynamic_state_v2/h5_static_sanity_lock_20260623/`

Verifier result:

- `passed: true`
- `row_manifest_rows: 4`
- `h5_private_raw_lock_rows: 4`
- `artifact_manifest_rows: 30`
- `failures: []`

## Historical Candidate Evidence

The existing ECVS static packets are candidate sources for the control because
they show near-ceiling behavior under direct DeepSeek rows:

- `harder_stress_v1_static65`: `mature_ssr_loop` had `15/15` clean rows and
  `1.0` final-exact/reliable success at each of `300`, `600`, and `1200`.
- `harder_stress_v1_static82`: `mature_ssr_loop` had `15/15` clean rows and
  `1.0` final-exact/reliable success at each of `300`, `600`, and `1200`.
- `harder_stress_v1_static90`: `mature_ssr_loop` had `15/15` clean rows and
  `1.0` final-exact/reliable success at each of `300`, `600`, and `1200`.

These records are evidence that compatible static stress can approach ceiling.
They do not pass this gate by themselves, because their wrappers map
`mature_ssr_loop` to the older ECVS `ssr_loop` implementation rather than the
2026-06-22 canonical PCG v2 slot compiler.

## Required Control

The control must be frozen before execution and must not be selected using model
outcomes from the PCG v2 matrix. The packet must record:

- source task or generated static-control task id;
- model-visible prompt hash;
- oracle hash;
- runner script hash;
- `compile_state` and `build_final_prompt` implementation hash or file hash;
- strict scorer hash;
- provider route, exact model string, fallback status, and supported-parameter
  snapshot for each row.

## Minimal Sanity Arms

The sanity packet must include these arms under matched task, budget, and model
conditions:

- `rolling_visible_carry_forward`
- `rolling_visible_fields_only`
- `ssr_no_visible_carry`
- `mature_ssr_loop`

`rolling_visible_fields_only` remains a negative control. Its expected role is
to show that mechanical visible-field surface alone is insufficient.

## Pass Rule

For a one-task static control, `mature_ssr_loop` must recover all required final
answer tokens without forbidden, revoked, protected, stale, or blocked-path
leakage at the matched admissible budget. For a multi-task static-control
packet, `mature_ssr_loop` must reach at least `0.80` answer success with no
systematic boundary failure.

The pass decision must be made on both:

- `answer_success`
- `reliable_composite_success`

If `mature_ssr_loop` fails this gate, the PCG v2 main matrix stays on HOLD until
the runner is audited or replaced.

## Non-Admission

Static sanity rows are not main-matrix evidence. They must not be pooled with
PCG v2 pilot rows, OpenRouter robustness rows, or the future 5-model main
matrix.

The pass result only closes the narrow runner-validity objection that the
canonical 2026-06-22 `mature_ssr_loop` slot compiler is trivially broken on a
static control. It does not promote mature SSR back to primary-method status.
