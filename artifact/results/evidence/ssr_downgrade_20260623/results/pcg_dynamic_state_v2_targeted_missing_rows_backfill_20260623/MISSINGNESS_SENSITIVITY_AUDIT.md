# Missingness Sensitivity Audit

Backfill id: `pcg_dynamic_state_v2_targeted_missing_rows_backfill_20260623`

## Scope

This is a targeted technical backfill for two `backend_or_empty_output` rows.
It does not change the original protocol, prompts, task manifests, provider,
sampling controls, scorer, or original result packets.

## Backfilled Rows

| packet | task | method | budget | gate | answer | governance | reliable |
|---|---|---|---:|---|---:|---:|---:|
| `deepseek_decisive_104` | `pcgds_v2_00026_decoy_heavy_same_prefix_config_easy` | `mature_ssr_loop` | `600` | `measured` | `False` | `False` | `False` |
| `deepseek_random10_rerun100` | `pcgds_v2_00032_decoy_heavy_same_prefix_config_hard` | `loop_only` | `300` | `measured` | `False` | `False` | `False` |

## Decision Sensitivity

- Original decisive mature SSR reliable count was `3/26 = 0.115`.
- With this targeted backfill row counted as observed, mature SSR reliable is
  `3/26 = 0.115`.
- The decisive visible-carry comparator remains `13/26 = 0.500`.
- Therefore the preregistered downgrade conclusion is unchanged.
- The random10 backfill target is `loop_only`; its reliable value is
  `0` and it is not part of the SSR-vs-visible comparison.

## Interpretation

The backfill closes a reviewer-facing missingness gap. It does not rescue
tested mature/schema-heavy SSR as a primary method.
