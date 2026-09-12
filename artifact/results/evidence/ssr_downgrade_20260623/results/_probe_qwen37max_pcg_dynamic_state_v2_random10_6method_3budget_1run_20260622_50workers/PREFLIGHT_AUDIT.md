# _probe_qwen37max_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_50workers Preflight Audit

Overall status: `PASS`

This is a local calibration run packet only.

| check | status | detail |
|---|---|---|
| selected task rows = 10 | `PASS` | `10` |
| oracle rows = 10 | `PASS` | `10` |
| family split = 2 each | `PASS` | `{"api_migration_state_transition": 2, "decoy_heavy_same_prefix_config": 2, "permission_boundary_with_attractive_blocked_path": 2, "protected_information_redaction_under_task_pressure": 2, "requirement_overwrite_cumulativ` |
| method list = six-method new matrix | `PASS` | `["loop_only", "rolling_summary", "rolling_visible_carry_forward", "rolling_visible_fields_only", "ssr_no_visible_carry", "mature_ssr_loop"]` |
| state budgets = 300/600/1200 | `PASS` | `[300, 600, 1200]` |
| runs = 1 | `PASS` | `1` |
| expected rows = 180 | `PASS` | `180` |
| provider direct qwen37max | `PASS` | `{"access_path": "direct_provider", "api_key_env": "DASHSCOPE_API_KEY", "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "condition_id": "qwen37max", "fallback_enabled": false, "provider": "dashscope", "re` |
| temperature explicit qwen standard | `PASS` | `{"send_mode": "explicit", "value": 0.7}` |
| DashScope thinking/search disabled | `PASS` | `{"send_mode": "explicit", "value": {"enable_search": false, "enable_thinking": false}}` |
| tools/web disabled | `PASS` | `{"tools": "disabled", "web": "disabled"}` |
| task split audit PASS | `PASS` | `"PASS"` |
| no prior row output files in result dir | `PASS` | `[]` |
| raw output dir absent or empty | `PASS` | `[]` |
| variable control doc exists | `PASS` | `"<AUTHOR_LOCAL_PROTOCOL_DIR>/LATEST_EXPERIMENT_VARIABLE_REQUIREMENTS_GOVERNANCE_MAIN_MATRIX_v1_20260621.md"` |
| method protocol doc exists | `PASS` | `"<AUTHOR_LOCAL_PROTOCOL_DIR>/METHOD_CONDITION_PROTOCOLS_GOVERNANCE_MAIN_MATRIX_v1_20260621.md"` |
| strict scorer exists | `PASS` | `"tools/pcg_dynamic_state_v2/score_pcg_dynamic_state_v2_main_matrix.py"` |

## Hashes

- runner_sha256: `4a82d32cd6632bdd6a8debb98089859f62795d504618a10e1566fe732a27b0d0`
- base_runner_sha256: `5694e404cc1660614c37dd4293b4c311e0899409a07fbfefb4acdc37e80168e6`
- config_sha256: `3ba7e6466ce7e38ba62071508fe2b35df90f9bc6b8476ca7b724b213be4fa64a`
- subset_model_visible_manifest_sha256: `f2c73bcfe956933dcefbb9746511ea34162899fbc5e0237e19a4d902f57299b0`
- subset_oracle_manifest_sha256: `71c107feefafdc3cad49aa66ed7392343b0f8932e29a2d1ea674c935890dd4fe`
- scorer_sha256: `67c18a606d50760990ef28054b059058c69e758d8439b1caa1ed2e8f1dc6417b`
