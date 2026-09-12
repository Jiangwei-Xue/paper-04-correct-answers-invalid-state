# Targeted Missing-Row Backfill Audit

Backfill id: `pcg_dynamic_state_v2_targeted_missing_rows_backfill_20260623`

Status: `PASS`

This packet is append-only. It does not overwrite the original result packets.
API key values are never printed or written.

## Targets

| packet | row | original gate | original reason | preflight |
|---|---|---|---|---|
| `deepseek_decisive_104` | `_probe_ecvs_deepseek_v4pro_pcg_dynamic_state_v2_e10_h3_decisive_13task_4method_2budget_1run::pcgds_v2_00026_decoy_heavy_same_prefix_config_easy::mature_ssr_loop::budget600::run1` | `rerun_required` | `backend_or_empty_output` | `PASS` |
| `deepseek_random10_rerun100` | `_probe_deepseek_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_rerun100::pcgds_v2_00032_decoy_heavy_same_prefix_config_hard::loop_only::budget300::run1` | `rerun_required` | `backend_or_empty_output` | `PASS` |

## Backfill Results

| packet | task | method | budget | gate | answer | governance | reliable | raw ref |
|---|---|---|---:|---|---:|---:|---:|---|
| `deepseek_decisive_104` | `pcgds_v2_00026_decoy_heavy_same_prefix_config_easy` | `mature_ssr_loop` | `600` | `measured` | `False` | `False` | `False` | `released_raw_outputs/model_outputs/pcg_dynamic_state_v2_targeted_missing_rows_backfill_20260623/deepseek_decisive_104/deepseek/mature_ssr_loop__pcgds_v2_00026_decoy_heavy_same_prefix_config_easy__run_1__budget_600.jsonl` |
| `deepseek_random10_rerun100` | `pcgds_v2_00032_decoy_heavy_same_prefix_config_hard` | `loop_only` | `300` | `measured` | `False` | `False` | `False` | `released_raw_outputs/model_outputs/pcg_dynamic_state_v2_targeted_missing_rows_backfill_20260623/deepseek_random10_rerun100/deepseek/loop_only__pcgds_v2_00032_decoy_heavy_same_prefix_config_hard__run_1__budget_300.jsonl` |

## Variable Control

- Provider: direct DeepSeek.
- Requested model: `deepseek-v4-pro`.
- Temperature: explicit `0`.
- Max tokens: `4096`.
- Thinking control: `thinking.type=disabled`.
- Tools/web/cache: disabled or not requested.
- Fallback: disabled.
- Original configs, task manifests, method protocols, runners, and scorers are reused.

## Non-Pooling Rule

These rows are targeted technical backfill rows. Use them to close missingness
only; do not treat them as a new protocol version or as a new matrix.
