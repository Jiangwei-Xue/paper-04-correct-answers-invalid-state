# _probe_kimi_k26_pcg_dynamic_state_v2_random10_6method_3budget_1run_20260622_50workers Preflight Audit

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
| provider direct kimi_k26 | `PASS` | `{"access_path": "direct_provider", "api_key_env": "MOONSHOT_API_KEY", "api_key_env_alternates_recorded_not_printed": ["KIMI_API_KEY"], "base_url": "https://api.moonshot.cn/v1", "condition_id": "kimi_k26", "fallback_enabl` |
| temperature explicit Kimi provider setting | `PASS` | `{"send_mode": "explicit", "value": 0.6}` |
| Kimi thinking disabled | `PASS` | `{"send_mode": "explicit", "value": {"thinking": {"type": "disabled"}}}` |
| tools/web disabled | `PASS` | `{"tools": "disabled", "web": "disabled"}` |
| task split audit PASS | `PASS` | `"PASS"` |
| no prior row output files in result dir | `PASS` | `[]` |
| raw output dir absent or empty | `PASS` | `[]` |
| variable control doc exists | `PASS` | `"<AUTHOR_LOCAL_PROTOCOL_DIR>/LATEST_EXPERIMENT_VARIABLE_REQUIREMENTS_GOVERNANCE_MAIN_MATRIX_v1_20260621.md"` |
| method protocol doc exists | `PASS` | `"<AUTHOR_LOCAL_PROTOCOL_DIR>/METHOD_CONDITION_PROTOCOLS_GOVERNANCE_MAIN_MATRIX_v1_20260621.md"` |
| strict scorer exists | `PASS` | `"tools/pcg_dynamic_state_v2/score_pcg_dynamic_state_v2_main_matrix.py"` |

## Hashes

- runner_sha256: `e16b09d0226b95b8330b6deab9fe2eff1bbc4923bcc17453440b03afbf7bf372`
- base_runner_sha256: `5694e404cc1660614c37dd4293b4c311e0899409a07fbfefb4acdc37e80168e6`
- config_sha256: `a4b968977b528a9d7210aafc222b9b4c74b4a871c8bed95d550a666b678817d5`
- subset_model_visible_manifest_sha256: `f2c73bcfe956933dcefbb9746511ea34162899fbc5e0237e19a4d902f57299b0`
- subset_oracle_manifest_sha256: `71c107feefafdc3cad49aa66ed7392343b0f8932e29a2d1ea674c935890dd4fe`
- scorer_sha256: `67c18a606d50760990ef28054b059058c69e758d8439b1caa1ed2e8f1dc6417b`
