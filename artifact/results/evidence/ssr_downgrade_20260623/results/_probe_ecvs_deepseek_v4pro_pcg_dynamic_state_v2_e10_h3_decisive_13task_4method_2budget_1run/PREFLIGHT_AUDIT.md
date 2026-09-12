# _probe_ecvs_deepseek_v4pro_pcg_dynamic_state_v2_e10_h3_decisive_13task_4method_2budget_1run Preflight Audit

Overall status: `PASS`

This packet is a local calibration probe only. It does not inherit old results,
does not call an API in preflight mode, and does not read API keys in preflight
mode.

| check | status | detail |
|---|---|---|
| selected task rows = 13 | `PASS` | `13` |
| oracle rows = 13 | `PASS` | `13` |
| difficulty split 10 easy / 3 hard | `PASS` | `{"easy": 10, "hard": 3}` |
| method list strict | `PASS` | `["rolling_summary", "loop_only", "rolling_visible_carry_forward", "mature_ssr_loop"]` |
| budgets fixed to 600 and 1200 | `PASS` | `[600, 1200]` |
| runs = 1 | `PASS` | `1` |
| expected rows = 104 | `PASS` | `104` |
| provider direct deepseek | `PASS` | `{"access_path": "direct_provider", "api_key_env": "DEEPSEEK_API_KEY", "base_url": "https://api.deepseek.com", "condition_id": "deepseek_v4pro", "fallback_enabled": false, "provider": "deepseek", "requested_model": "deeps` |
| temperature explicit 0 | `PASS` | `{"send_mode": "explicit", "value": 0}` |
| max_tokens 4096 | `PASS` | `4096` |
| thinking disabled requested | `PASS` | `{"send_mode": "explicit", "value": {"thinking": {"type": "disabled"}}}` |
| top_p omitted | `PASS` | `{"send_mode": "omitted", "value": null}` |
| tools/web disabled | `PASS` | `{"tools": "disabled", "web": "disabled"}` |
| task split audit PASS | `PASS` | `{"audit_type": "pcg_dynamic_state_v2_probe_task_split_audit", "created_at_utc": "2026-06-20T15:10:00Z", "hard_fail_forbidden_metadata_hits": [], "model_visible_forbidden_key_hits": [], "model_visible_rows": 13, "notes": ` |
| no prior row output files in result dir | `PASS` | `[]` |
| raw output dir absent or empty | `PASS` | `[]` |
| variable control doc exists | `PASS` | `"<AUTHOR_LOCAL_WORKSPACE>/stateful-reasoning-benchmark-release/docs/protocol/fresh_main_matrix_v2/LATEST_EXPERIMENT_VARIABLE_REQUIREMENTS_ROLLING_VISIBLE_CARRY_FORWARD_LOCAL.md"` |
| method protocol doc exists | `PASS` | `"<AUTHOR_LOCAL_WORKSPACE>/stateful-reasoning-benchmark-release/docs/protocol/fresh_main_matrix_v2/LATEST_EXPERIMENT_VARIABLE_REQUIREMENTS_ROLLING_VISIBLE_CARRY_FORWARD_LOCAL.md"` |
| scorer exists | `PASS` | `"tools/pcg_dynamic_state_v2/score_pcg_dynamic_state_v2_outputs.py"` |

## Hashes

- runner_sha256: `5694e404cc1660614c37dd4293b4c311e0899409a07fbfefb4acdc37e80168e6`
- config_sha256: `047982d36c9df0f6aff8d882f6b2f45208a5a88eceddde3abec96ec8ae0ef38a`
- subset_model_visible_manifest_sha256: `caea7fdc801c3eb5d5fb6d1f47c0fd747c32b7ec07c93c74bc13e16082fe69e9`
- subset_oracle_manifest_sha256: `bb8843b7ab29ab664460c091721141a9499b8eec8c4a4f4d1b132d98436b708e`
- scorer_sha256: `c47582ff3e85f6d49db089308f94a77e3eabf3a0bda36ec35995676e088be55b`
