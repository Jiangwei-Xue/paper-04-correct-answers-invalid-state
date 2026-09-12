# pcg_dynamic_state_v2_static_sanity_deepseek_1task_4method_budget600_1run_20260623 Preflight Audit

Overall status: `PASS`

This is a canonical static sanity gate only.

| check | status | detail |
|---|---|---|
| selected task rows = 1 | `PASS` | `1` |
| oracle rows = 1 | `PASS` | `1` |
| task id frozen | `PASS` | `"pcgds_v2_static_sanity_20260623_clear_boundary_v1"` |
| method list = static sanity 4 arms | `PASS` | `["rolling_visible_carry_forward", "rolling_visible_fields_only", "ssr_no_visible_carry", "mature_ssr_loop"]` |
| state budget = 600 | `PASS` | `[600]` |
| runs = 1 | `PASS` | `1` |
| expected rows = 4 | `PASS` | `4` |
| provider direct deepseek | `PASS` | `{"access_path": "direct_provider", "api_key_env": "DEEPSEEK_API_KEY", "base_url": "https://api.deepseek.com", "condition_id": "deepseek_v4pro", "fallback_enabled": false, "provider": "deepseek", "requested_model": "deeps` |
| temperature explicit 0 | `PASS` | `{"send_mode": "explicit", "value": 0}` |
| thinking disabled | `PASS` | `{"send_mode": "explicit", "value": {"thinking": {"type": "disabled"}}}` |
| tools/web disabled | `PASS` | `{"tools": "disabled", "web": "disabled"}` |
| task split audit PASS | `PASS` | `"PASS"` |
| no prior row output files in result dir | `PASS` | `[]` |
| raw output dir absent or empty | `PASS` | `[]` |
| variable control doc exists | `PASS` | `"docs/protocol/pcg_dynamic_state_v2_main_matrix/LATEST_EXPERIMENT_VARIABLE_REQUIREMENTS_v2.md"` |
| method protocol doc exists | `PASS` | `"docs/protocol/pcg_dynamic_state_v2_main_matrix/METHOD_CONDITION_PROTOCOLS_v2.md"` |
| static sanity gate doc exists | `PASS` | `"docs/protocol/pcg_dynamic_state_v2_main_matrix/STATIC_SANITY_GATE_20260623.md"` |
| strict scorer exists | `PASS` | `"tools/pcg_dynamic_state_v2/score_pcg_dynamic_state_v2_main_matrix.py"` |

## Hashes

- runner_sha256: `fa602b1c9117b45456546aa94a7f50e3fe9e8cc76de1db8825e23227df42eb3c`
- random10_runner_sha256: `7ea256c58943c71262ba972d1576eaadaab991ad33dc5fb8d41f90bdbca41179`
- base_runner_sha256: `5694e404cc1660614c37dd4293b4c311e0899409a07fbfefb4acdc37e80168e6`
- config_sha256: `50a8158a47261382f970ad2d9e1654c4a6b7dc367b7977790cc508eac0fba9d0`
- subset_model_visible_manifest_sha256: `103efdf5ec5f75904442dc63c199ffbc9c7a4bec67c0d8413757a3d9ac95dcda`
- subset_oracle_manifest_sha256: `8cb146c6779070475c407d7eda9c40bc5ca2d4b37d3872e2e3540c5ceb1d9730`
- scorer_sha256: `67c18a606d50760990ef28054b059058c69e758d8439b1caa1ed2e8f1dc6417b`
