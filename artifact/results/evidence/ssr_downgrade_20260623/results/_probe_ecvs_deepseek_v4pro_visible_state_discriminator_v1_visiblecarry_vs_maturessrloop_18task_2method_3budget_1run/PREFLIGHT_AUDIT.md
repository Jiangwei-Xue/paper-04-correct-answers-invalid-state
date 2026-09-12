# _probe_ecvs_deepseek_v4pro_visible_state_discriminator_v1_visiblecarry_vs_maturessrloop_18task_2method_3budget_1run Preflight Audit

Positioning: `calibration_only_not_primary_evidence`.

No API call was made. No API key value was read.

Overall status: `PASS_REVIEWED`
Checks passed: 30
Checks failed: 0
Expected rows: 108

## Prompt Leakage Scanner

- Hard-fail metadata hits: `0`
- Lexical review hits: `40`
- Semantic leakage review status: `PASS`
- Review notes: Lexical review terms appeared only as ordinary model-visible task language; no scorer-only answer/label/oracle/scoring metadata was detected.

Hard-fail scanner is restricted to explicit scorer/oracle/metric/internal metadata field names. Lexical terms such as `answer`, `label`, `boundary`, `score`, `required`, and `forbidden` are reviewed in context and do not fail preflight when used as ordinary task language.

## Token Prefix Compatibility

This transition-band discriminator packet uses only required marker prefixes recognized by the existing rolling and mature-SSR runners: `REQ`, `LOCK`, `SCOPE`, `CHECK`, `ANCHOR`, `EDGE`, `FRONTIER`, `MERGE`, and `VERIFY`. Task selection is deterministic and method/outcome blind; it is not selected from model success rates. Preflight fails if any required token prefix falls outside the runner extractor contract.

- MIDSTATE required tokens: `0`
- Incompatible required tokens: `0`
- Prefix counts: `{"ANCHOR": 18, "CHECK": 18, "EDGE": 14, "FRONTIER": 8, "LOCK": 18, "MERGE": 1, "REQ": 18, "SCOPE": 18}`

Lexical hit counts:

- `boundary`: 18
- `label`: 22

## Semantic Leakage Review

| task_id | term | semantic_leakage | context | review_note |
|---|---:|---:|---|---|
| vstdp_v1_high_01_requests_proxy_auth_precedence | `label` | `false` | ...id": "s7"}, {"content": "Cross-component requirement: keep the accepted label aligned across client/session.py and client/auth.py; preserve ANCHOR_01... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_high_01_requests_proxy_auth_precedence | `boundary` | `false` | ...VERIFY_01_297HSL9 is still a decoy.", "segment_id": "s6"}, {"content": "Boundary rule: private proxy header and blocked components private/proxy_trace.h... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_high_02_decoy_boundary_filtering | `label` | `false` | ...d LOCK_02_464QRAL.", "segment_id": "s1"}, {"content": "Early draft: use label orbit-gate and marker MERGE_02_VQQSW6F. This draft is preliminary.", "s... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_high_02_decoy_boundary_filtering | `label` | `false` | ...id": "s2"}, {"content": "Later correction: replace the early draft with label orbit-guard. Keep SCOPE_02_MWJH8XE; do not carry the preliminary marker... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_high_02_decoy_boundary_filtering | `label` | `false` | ... decoy.", "segment_id": "s6"}, {"content": "Boundary rule: private dump label and blocked components private/filter_dump.json, tests/internal_filter_... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_high_02_decoy_boundary_filtering | `label` | `false` | ...id": "s7"}, {"content": "Cross-component requirement: keep the accepted label aligned across src/filter/rules.py and src/filter/contracts.py; preserv... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_high_02_decoy_boundary_filtering | `boundary` | `false` | ...VERIFY_02_XVZ3N6Y is still a decoy.", "segment_id": "s6"}, {"content": "Boundary rule: private dump label and blocked components private/filter_dump.jso... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_high_03_cachetools_key_namespace_boundary | `label` | `false` | ...id": "s7"}, {"content": "Cross-component requirement: keep the accepted label aligned across cachetools/keys.py and cachetools/namespace.py; preserve... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_high_03_cachetools_key_namespace_boundary | `boundary` | `false` | ...VERIFY_03_4T2MZQY is still a decoy.", "segment_id": "s6"}, {"content": "Boundary rule: private cache replay and blocked components private/cache_replay.... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_high_04_django_upload_path_transition | `label` | `false` | ...id": "s7"}, {"content": "Cross-component requirement: keep the accepted label aligned across framework/uploads/path.py and framework/uploads/handler.... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_high_04_django_upload_path_transition | `boundary` | `false` | ...VERIFY_04_6EF4V36 is still a decoy.", "segment_id": "s6"}, {"content": "Boundary rule: private upload path and blocked components private/upload_trace.l... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_high_05_plugin_resolution_boundary | `label` | `false` | ...id": "s7"}, {"content": "Cross-component requirement: keep the accepted label aligned across src/plugins/resolver.py and src/plugins/public_registry.... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_high_05_plugin_resolution_boundary | `boundary` | `false` | ...VERIFY_05_MZAS49H is still a decoy.", "segment_id": "s6"}, {"content": "Boundary rule: internal plugin id and blocked components private/plugin_dump.jso... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_high_06_retry_policy_matrix_update | `label` | `false` | ...id": "s7"}, {"content": "Cross-component requirement: keep the accepted label aligned across src/retry/matrix.py and src/retry/backoff.py; preserve A... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_high_06_retry_policy_matrix_update | `boundary` | `false` | ...VERIFY_06_FD627WH is still a decoy.", "segment_id": "s6"}, {"content": "Boundary rule: private retry case and blocked components private/retry_cases.jso... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_low_07_stale_token_retirement | `label` | `false` | ...coy.", "segment_id": "s6"}, {"content": "Boundary rule: tombstone token label and blocked components private/token_tombstone.txt, tests/internal_toke... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_low_07_stale_token_retirement | `label` | `false` | ...id": "s7"}, {"content": "Cross-component requirement: keep the accepted label aligned across src/tokens/lifecycle.py and src/tokens/registry.py; pres... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_low_07_stale_token_retirement | `boundary` | `false` | ...ONTIER_07_VC5H9E3 is still a decoy.", "segment_id": "s6"}, {"content": "Boundary rule: tombstone token label and blocked components private/token_tombst... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_low_08_fastapi_dependency_scope_override | `label` | `false` | ...id": "s7"}, {"content": "Cross-component requirement: keep the accepted label aligned across framework/deps/resolver.py and framework/routing.py; pre... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_low_08_fastapi_dependency_scope_override | `boundary` | `false` | ...ONTIER_08_SXHBVHH is still a decoy.", "segment_id": "s6"}, {"content": "Boundary rule: private dependency trace and blocked components private/dependenc... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_low_09_conditional_config_activation | `label` | `false` | ...id": "s7"}, {"content": "Cross-component requirement: keep the accepted label aligned across src/config/activation.py and src/config/schema.py; prese... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_low_09_conditional_config_activation | `boundary` | `false` | ...ONTIER_09_HR3J8MU is still a decoy.", "segment_id": "s6"}, {"content": "Boundary rule: internal config key and blocked components private/config_probe.y... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_low_10_auth_claim_scope_filter | `label` | `false` | ...id": "s7"}, {"content": "Cross-component requirement: keep the accepted label aligned across src/auth/claims.py and src/auth/scope.py; preserve ANCHO... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_low_10_auth_claim_scope_filter | `boundary` | `false` | ...ONTIER_10_X3GVK6T is still a decoy.", "segment_id": "s6"}, {"content": "Boundary rule: private auth trace and blocked components private/auth_trace.log,... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_low_11_export_redaction_update | `label` | `false` | ...id": "s6"}, {"content": "Cross-component requirement: keep the accepted label aligned across src/export/redaction.py and src/export/policy.py; preser... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_low_11_export_redaction_update | `boundary` | `false` | ...FRONTIER_11_8NHWJTG stays inactive.", "segment_id": "s5"}, {"content": "Boundary rule: private export field and blocked components private/export_sample... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_low_12_multi_file_contract_consistency | `label` | `false` | ...id": "s6"}, {"content": "Cross-component requirement: keep the accepted label aligned across src/contracts/reader.py and tests/public_contract.py; pr... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_low_12_multi_file_contract_consistency | `boundary` | `false` | ...FRONTIER_12_TTZBNEW stays inactive.", "segment_id": "s5"}, {"content": "Boundary rule: internal replay contract and blocked components tests/internal_co... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_mid_13_alias_overwrite_chain | `label` | `false` | ...id": "s7"}, {"content": "Cross-component requirement: keep the accepted label aligned across src/aliases/registry.py and src/aliases/current.py; pres... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_mid_13_alias_overwrite_chain | `boundary` | `false` | ... MERGE_13_9C2JUSL is still a decoy.", "segment_id": "s6"}, {"content": "Boundary rule: private alias trace and blocked components private/alias_trace.lo... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_mid_14_pytest_nodeid_alias_retirement | `label` | `false` | ...id": "s7"}, {"content": "Cross-component requirement: keep the accepted label aligned across runner/nodeid.py and runner/params.py; preserve ANCHOR_1... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_mid_14_pytest_nodeid_alias_retirement | `boundary` | `false` | ... MERGE_14_E8UGKKW is still a decoy.", "segment_id": "s6"}, {"content": "Boundary rule: private node id alias and blocked components private/nodeid_dump.... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_mid_15_schema_migration_gate | `label` | `false` | ...id": "s7"}, {"content": "Cross-component requirement: keep the accepted label aligned across src/schema/migrate.py and src/schema/public_contract.py;... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_mid_15_schema_migration_gate | `boundary` | `false` | ... MERGE_15_SE45XKE is still a decoy.", "segment_id": "s6"}, {"content": "Boundary rule: private schema probe and blocked components private/schema_probe.... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_mid_16_telemetry_field_retirement | `label` | `false` | ...id": "s7"}, {"content": "Cross-component requirement: keep the accepted label aligned across src/telemetry/fields.py and src/telemetry/events.py; pre... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_mid_16_telemetry_field_retirement | `boundary` | `false` | ... MERGE_16_HCLSSHN is still a decoy.", "segment_id": "s6"}, {"content": "Boundary rule: private telemetry field and blocked components private/telemetry_... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_mid_17_route_precedence_shift | `label` | `false` | ...id": "s7"}, {"content": "Cross-component requirement: keep the accepted label aligned across src/router/precedence.py and src/router/table.py; preser... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_mid_17_route_precedence_shift | `boundary` | `false` | ... MERGE_17_G4R6L65 is still a decoy.", "segment_id": "s6"}, {"content": "Boundary rule: internal route replay and blocked components private/route_replay... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_mid_18_pandas_timezone_schema_update | `label` | `false` | ...id": "s7"}, {"content": "Cross-component requirement: keep the accepted label aligned across lib/io/csv_writer.py and lib/timezones/schema.py; preser... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |
| vstdp_v1_mid_18_pandas_timezone_schema_update | `boundary` | `false` | ... MERGE_18_TSQEWME is still a decoy.", "segment_id": "s6"}, {"content": "Boundary rule: private timezone fixture and blocked components private/timezone_... | lexical occurrence reviewed; no explicit scorer/oracle/metric metadata marker |

## Frozen Run Controls

- Provider: `deepseek`
- Base URL: `https://api.deepseek.com`
- Requested model: `deepseek-v4-pro`
- Fallback: disabled
- Tools/web: disabled
- Thinking: `thinking.type=disabled`
- Temperature: explicit `0`
- max_tokens: `4096`
- top_p/top_k/min_p/top_a/penalties/stop/seed: omitted
- stream: false
- Retry policy: max attempts 2; failed attempts retained; no post-hoc failed-row deletion
- max_workers default: `2`
- User-confirmed calibration override may use up to `100` workers; the actual value is recorded in `RUN_MANIFEST.json`.

## Methods

- `rolling_visible_carry_forward`: ordinary rolling natural-language state plus deterministic visible-candidate carry-forward from model-visible text only.
- `mature_ssr_loop`: protocol-level mature SSR loop using the existing SSR loop implementation with deterministic priority compaction; scorer-only metadata is not read during state construction.

## Checks

| check | status | detail |
|---|---:|---|
| MODEL_VISIBLE_TASK_MANIFEST.jsonl sha256 | `PASS` | `{"expected": "3e55ca0d13b98e22312e2409149f678b77ec9aef1850bb20a2b4dd3b9ddb0b1a", "observed": "3e55ca0d13b98e22312e2409149f678b77ec9aef1850bb20a2b4dd3b9ddb0b1a"}` |
| SCORER_ORACLE_MANIFEST.jsonl sha256 | `PASS` | `{"expected": "cff0bce020b88a9a2d3d196f5042a127e5ac1ea6714929d2bf3c0f4bcf5107e5", "observed": "cff0bce020b88a9a2d3d196f5042a127e5ac1ea6714929d2bf3c0f4bcf5107e5"}` |
| TASK_PROVENANCE_MANIFEST.jsonl sha256 | `PASS` | `{"expected": "8d9db20ce97efe30f85c852e25677be982049e6573365705fe9691ec9b104e37", "observed": "8d9db20ce97efe30f85c852e25677be982049e6573365705fe9691ec9b104e37"}` |
| TASK_SELECTION.csv sha256 | `PASS` | `{"expected": "e83e5f36720943793cd894d750a4e149b87149e8afc1f3ba9f39379580fbad40", "observed": "e83e5f36720943793cd894d750a4e149b87149e8afc1f3ba9f39379580fbad40"}` |
| 18 model-visible task rows | `PASS` | `18` |
| 18 scorer-oracle rows | `PASS` | `18` |
| 18 provenance rows | `PASS` | `18` |
| 72 candidate task-selection rows | `PASS` | `72` |
| TASK_SPLIT_AUDIT PASS | `PASS` | `"PASS"` |
| duplicate_task_ids empty | `PASS` | `{"split": [], "visible": []}` |
| required token prefixes compatible with runner extractor | `PASS` | `{"incompatible_required_tokens": [], "midstate_required_tokens": [], "prefix_counts": {"ANCHOR": 18, "CHECK": 18, "EDGE": 14, "FRONTIER": 8, "LOCK": 18, "MERGE": 1, "REQ": 18, "SCOPE": 18}, "safe_required_token_prefixes": ["ANCHOR", "CHECK", "EDGE", "FRONTIER", "LOCK", "MERGE", "REQ", "SCOPE", "V...` |
| MIDSTATE required tokens absent | `PASS` | `[]` |
| model_visible_forbidden_metadata_key_hits empty | `PASS` | `null` |
| model-visible hard-fail metadata scan | `PASS` | `[]` |
| model-visible lexical semantic leakage review | `PASS` | `{"lexical_review_hit_count": 40, "notes": "Lexical review terms appeared only as ordinary model-visible task language; no scorer-only answer/label/oracle/scoring metadata was detected.", "semantic_leakage_count": 0}` |
| BLOCKER.md exists | `PASS` | `"data/main_v1/visible_state_transfer_discriminator_probe_v1/BLOCKER.md"` |
| BLOCKER.md real-SWE limitation disclosed | `PASS` | `"real_swe_style_controlled_transition and non-executable limitation"` |
| result_dir no old row outputs | `PASS` | `{"conflicts": [], "status": "exists_without_row_outputs"}` |
| raw_dir absent or empty | `PASS` | `{"conflicts": [], "status": "absent"}` |
| expected rows 108 | `PASS` | `108` |
| method list strict | `PASS` | `["rolling_visible_carry_forward", "mature_ssr_loop"]` |
| budgets strict | `PASS` | `[300, 600, 1200]` |
| runs strict | `PASS` | `1` |
| max_workers default 1 or 2 | `PASS` | `2` |
| API key value not read during preflight | `PASS` | `{"api_key_env_name": "DEEPSEEK_API_KEY", "value_read": false}` |
| max_tokens 4096 | `PASS` | `4096` |
| temperature explicit zero | `PASS` | `{"send_mode": "explicit", "value": 0}` |
| thinking disabled | `PASS` | `{"thinking": {"type": "disabled"}}` |
| sampling nuisance parameters omitted | `PASS` | `{"frequency_penalty": {"send_mode": "omitted", "value": null}, "min_p": {"send_mode": "omitted", "value": null}, "presence_penalty": {"send_mode": "omitted", "value": null}, "repetition_penalty": {"send_mode": "omitted", "value": null}, "seed": {"send_mode": "omitted", "value": null}, "stop": {"s...` |
| PREFLIGHT_SHA256SUMS internal verification | `PASS` | `["OK tools/run_ecvs_deepseek_visible_state_transfer_discriminator_v1_visiblecarry_vs_maturessrloop.py", "OK configs/_probe_ecvs_deepseek_v4pro_visible_state_discriminator_v1_visiblecarry_vs_maturessrloop_18task_2method_3budget_1run.json", "OK data/main_v1/visible_state_transfer_discriminator_prob...` |

## Blocker

The packet contains `real_swe_style_controlled_transition` rows. They are calibration anchors and must not be claimed as true executable SWE anchors.

## Run Gate

Run the API only after explicit user confirmation. The default script mode is preflight-only.
