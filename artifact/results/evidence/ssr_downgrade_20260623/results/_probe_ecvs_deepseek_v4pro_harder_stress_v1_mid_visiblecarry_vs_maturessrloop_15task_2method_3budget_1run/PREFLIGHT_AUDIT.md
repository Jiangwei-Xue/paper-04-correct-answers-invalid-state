# _probe_ecvs_deepseek_v4pro_harder_stress_v1_mid_visiblecarry_vs_maturessrloop_15task_2method_3budget_1run Preflight Audit

Positioning: `calibration_only_not_primary_evidence`.

No API call was made. No API key value was read.

Overall status: `PASS_REVIEWED`
Checks passed: 28
Checks failed: 0
Expected rows: 90

## Prompt Leakage Scanner

- Hard-fail metadata hits: `0`
- Lexical review hits: `64`
- Semantic leakage review status: `PASS`
- Review notes: Lexical review terms appeared only as ordinary model-visible task language; no scorer-only answer/label/oracle/scoring metadata was detected.

Hard-fail scanner is restricted to explicit scorer/oracle/metric/internal metadata field names. Lexical terms such as `answer`, `label`, `boundary`, `score`, `required`, and `forbidden` are reviewed in context and do not fail preflight when used as ordinary task language.

Lexical hit counts:

- `answer`: 45
- `boundary`: 18
- `label`: 1

## Semantic Leakage Review

| task_id | term | semantic_leakage | context | review_note |
|---|---:|---:|---|---|
| harder_stress_v1_mid_frontierpp_01_parser_error_taxonomy | `answer` | `false` | ...s to public classes without exposing replay-only labels. Keep the final answer focused on the active editable files and preserve CHECK_01_EGK9U when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_01_parser_error_taxonomy | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name tests/parser_private_trace_test.py, private... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_01_parser_error_taxonomy | `answer` | `false` | ...plan.", "segment_id": "s8"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_01_parser_error_taxonomy | `label` | `false` | ...t_id": "s3"}, {"content": "A compatibility note says the new normalized label is allowed only when class and source component both match. If the cond... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_01_parser_error_taxonomy | `boundary` | `false` | ...er DECOY_01_KEGK9 remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_01_BJU9KGEKKEG and VAULT_01_EGK9UJ are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_02_build_matrix_compat | `answer` | `false` | ...ublic build contract and avoid generated lockfile churn. Keep the final answer focused on the active editable files and preserve CHECK_02_MKUTA when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_02_build_matrix_compat | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name private/build_matrix_notes.md, tests/build_... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_02_build_matrix_compat | `answer` | `false` | ...plan.", "segment_id": "s9"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_02_build_matrix_compat | `boundary` | `false` | ...er DECOY_02_WMKUT remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_02_XBATUKMWWMK and VAULT_02_MKUTAB are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_03_staged_schema_migration | `answer` | `false` | ...the old reader path and add a guarded writer transition. Keep the final answer focused on the active editable files and preserve CHECK_03_6YPXS when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_03_staged_schema_migration | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name private/schema_patch_notes.md, tests/schema... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_03_staged_schema_migration | `answer` | `false` | ...lan.", "segment_id": "s10"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_03_staged_schema_migration | `boundary` | `false` | ...er DECOY_03_76YPX remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_03_QPSXPY6776Y and VAULT_03_6YPXSP are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_04_policy_alias_cascade | `answer` | `false` | ...ctive alias through the registry without widening scope. Keep the final answer focused on the active editable files and preserve CHECK_04_65HW7 when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_04_policy_alias_cascade | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name docs/private_policy_notes.md, tests/policy_... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_04_policy_alias_cascade | `answer` | `false` | ...plan.", "segment_id": "s9"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_04_policy_alias_cascade | `boundary` | `false` | ...er DECOY_04_D65HW remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_04_RY7WH56DD65 and VAULT_04_65HW7Y are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_05_telemetry_redaction_contract | `answer` | `false` | ...nt fields while preserving public aggregate event names. Keep the final answer focused on the active editable files and preserve CHECK_05_8MPT4 when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_05_telemetry_redaction_contract | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name logs/private_telemetry_sample.jsonl, tests/... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_05_telemetry_redaction_contract | `answer` | `false` | ...lan.", "segment_id": "s10"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_05_telemetry_redaction_contract | `boundary` | `false` | ...er DECOY_05_S8MPT remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_05_RX4TPM8SS8M and VAULT_05_8MPT4X are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_06_auth_claim_boundary | `answer` | `false` | ...ience and nullable only in the gated compatibility case. Keep the final answer focused on the active editable files and preserve CHECK_06_8XMLM when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_06_auth_claim_boundary | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name private/auth_trace.log, tests/auth_claims_p... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_06_auth_claim_boundary | `answer` | `false` | ...plan.", "segment_id": "s8"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_06_auth_claim_boundary | `boundary` | `false` | ...er DECOY_06_N8XML remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_06_H3MLMX8NN8X and VAULT_06_8XMLM3 are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_07_cache_invalidation_mesh | `answer` | `false` | ...only after both stores acknowledge the active namespace. Keep the final answer focused on the active editable files and preserve CHECK_07_22FZW when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_07_cache_invalidation_mesh | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name src/cache/internal_probe.py, private/cache_... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_07_cache_invalidation_mesh | `answer` | `false` | ...lan.", "segment_id": "s10"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_07_cache_invalidation_mesh | `boundary` | `false` | ...er DECOY_07_C22FZ remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_07_CMWZF22CC22 and VAULT_07_22FZWM are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_08_retry_route_matrix | `answer` | `false` | ... operations and preserve the route-local backoff policy. Keep the final answer focused on the active editable files and preserve CHECK_08_5VTGU when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_08_retry_route_matrix | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name tests/retry_private_replay.py, private/retr... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_08_retry_route_matrix | `answer` | `false` | ...plan.", "segment_id": "s8"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_08_retry_route_matrix | `boundary` | `false` | ...er DECOY_08_35VTG remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_08_QNUGTV5335V and VAULT_08_5VTGUN are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_09_export_retention_window | `answer` | `false` | ...avior while applying the late regional retention window. Keep the final answer focused on the active editable files and preserve CHECK_09_XJDMV when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_09_export_retention_window | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name private/export_trace.csv, tests/export_priv... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_09_export_retention_window | `answer` | `false` | ...plan.", "segment_id": "s9"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_09_export_retention_window | `boundary` | `false` | ...e change plan to plan an export retention change with late regional and boundary constraints. The active editable files are src/export/window.py, src/ex... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_09_export_retention_window | `boundary` | `false` | ...er DECOY_09_CXJDM remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_09_CCVMDJXCCXJ and VAULT_09_XJDMVC are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_10_plugin_registry_resolution | `answer` | `false` | ...mespace resolver and preserve the public fallback order. Keep the final answer focused on the active editable files and preserve CHECK_10_JJZE5 when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_10_plugin_registry_resolution | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name private/plugin_registry_dump.json, tests/pl... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_10_plugin_registry_resolution | `answer` | `false` | ...plan.", "segment_id": "s9"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_frontierpp_10_plugin_registry_resolution | `boundary` | `false` | ...er DECOY_10_JJJZE remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_10_BN5EZJJJJJJ and VAULT_10_JJZE5N are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_realswe_01_fastapi_dependency_precedence | `answer` | `false` | ...l override precedence while keeping app defaults intact. Keep the final answer focused on the active editable files and preserve CHECK_01_PMD7W when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_realswe_01_fastapi_dependency_precedence | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name tests/private_dependency_replay.py, private... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_realswe_01_fastapi_dependency_precedence | `answer` | `false` | ...lan.", "segment_id": "s10"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_realswe_01_fastapi_dependency_precedence | `boundary` | `false` | ...er DECOY_01_4PMD7 remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_01_P9W7DMP44PM and VAULT_01_PMD7W9 are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_realswe_02_pandas_tz_csv_roundtrip | `answer` | `false` | ...undtrip behavior without copying private fixture labels. Keep the final answer focused on the active editable files and preserve CHECK_02_3LZQU when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_realswe_02_pandas_tz_csv_roundtrip | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name tests/private_csv_roundtrip_debug.py, priva... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_realswe_02_pandas_tz_csv_roundtrip | `answer` | `false` | ...lan.", "segment_id": "s10"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_realswe_02_pandas_tz_csv_roundtrip | `boundary` | `false` | ...er DECOY_02_B3LZQ remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_02_QSUQZL3BB3L and VAULT_02_3LZQUS are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_realswe_03_requests_proxy_redirect_auth | `answer` | `false` | ...der behavior while avoiding private proxy trace leakage. Keep the final answer focused on the active editable files and preserve CHECK_03_8K9RZ when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_realswe_03_requests_proxy_redirect_auth | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name tests/private_proxy_auth_replay.py, private... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_realswe_03_requests_proxy_redirect_auth | `answer` | `false` | ...plan.", "segment_id": "s9"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_realswe_03_requests_proxy_redirect_auth | `boundary` | `false` | ... repo-style change plan to plan a proxy auth redirect fix with security boundary and header retention constraints. The active editable files are client/... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_realswe_03_requests_proxy_redirect_auth | `boundary` | `false` | ...er DECOY_03_58K9R remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_03_ZGZR9K8558K and VAULT_03_8K9RZG are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_realswe_04_pytest_nodeid_stability | `answer` | `false` | ...node ids stable while applying the late escaping branch. Keep the final answer focused on the active editable files and preserve CHECK_04_SBD96 when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_realswe_04_pytest_nodeid_stability | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name tests/private_nodeid_replay.py, private/nod... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_realswe_04_pytest_nodeid_stability | `answer` | `false` | ...plan.", "segment_id": "s8"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_realswe_04_pytest_nodeid_stability | `boundary` | `false` | ...er DECOY_04_8SBD9 remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_04_8H69DBS88SB and VAULT_04_SBD96H are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_realswe_05_django_upload_path_boundary | `answer` | `false` | ...d path without allowing private storage prefix exposure. Keep the final answer focused on the active editable files and preserve CHECK_05_TBDRQ when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_realswe_05_django_upload_path_boundary | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name tests/private_upload_replay.py, private/upl... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_realswe_05_django_upload_path_boundary | `answer` | `false` | ...plan.", "segment_id": "s8"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_realswe_05_django_upload_path_boundary | `boundary` | `false` | ...ge plan to repair a repo-style upload path handling issue with security boundary and config sensitivity. The active editable files are framework/uploads... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_mid_realswe_05_django_upload_path_boundary | `boundary` | `false` | ...er DECOY_05_4TBDR remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_05_TLQRDBT44TB and VAULT_05_TBDRQL are private diagnostic... | ordinary task wording, not scorer-only metadata |

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
| MODEL_VISIBLE_TASK_MANIFEST.jsonl sha256 | `PASS` | `{"expected": "1f90a7bec70b172076d48bb50ba556ee191801820ea572b14d3064a0a7156c6d", "observed": "1f90a7bec70b172076d48bb50ba556ee191801820ea572b14d3064a0a7156c6d"}` |
| SCORER_ORACLE_MANIFEST.jsonl sha256 | `PASS` | `{"expected": "e3c3ba0ab2fae271be329286e90e109a5ac10b8f10b5d24fc52eb3ff1c08d93c", "observed": "e3c3ba0ab2fae271be329286e90e109a5ac10b8f10b5d24fc52eb3ff1c08d93c"}` |
| TASK_PROVENANCE_MANIFEST.jsonl sha256 | `PASS` | `{"expected": "92bc3d0180ab3633ccd48c55d4826f4aa165e74694df4e81c6eadc3d3ad30852", "observed": "92bc3d0180ab3633ccd48c55d4826f4aa165e74694df4e81c6eadc3d3ad30852"}` |
| TASK_SELECTION.csv sha256 | `PASS` | `{"expected": "55e4ef15ba1235e8919d141f7efab90c0e8ebb3c99a5dd2ba791a8af13ab61d3", "observed": "55e4ef15ba1235e8919d141f7efab90c0e8ebb3c99a5dd2ba791a8af13ab61d3"}` |
| 15 model-visible task rows | `PASS` | `15` |
| 15 scorer-oracle rows | `PASS` | `15` |
| 15 provenance rows | `PASS` | `15` |
| 15 task-selection rows | `PASS` | `15` |
| TASK_SPLIT_AUDIT PASS | `PASS` | `"PASS"` |
| duplicate_task_ids empty | `PASS` | `{"split": [], "visible": []}` |
| model_visible_forbidden_metadata_key_hits empty | `PASS` | `[]` |
| model-visible hard-fail metadata scan | `PASS` | `[]` |
| model-visible lexical semantic leakage review | `PASS` | `{"lexical_review_hit_count": 64, "notes": "Lexical review terms appeared only as ordinary model-visible task language; no scorer-only answer/label/oracle/scoring metadata was detected.", "semantic_leakage_count": 0}` |
| BLOCKER.md exists | `PASS` | `"data/main_v1/harder_visible_state_transfer_stress_v1_mid/BLOCKER.md"` |
| BLOCKER.md real-SWE limitation disclosed | `PASS` | `"real_swe_style_controlled_plus and non-executable limitation"` |
| result_dir no old row outputs | `PASS` | `{"conflicts": [], "status": "exists_without_row_outputs"}` |
| raw_dir absent or empty | `PASS` | `{"conflicts": [], "status": "absent"}` |
| expected rows 90 | `PASS` | `90` |
| method list strict | `PASS` | `["rolling_visible_carry_forward", "mature_ssr_loop"]` |
| budgets strict | `PASS` | `[300, 600, 1200]` |
| runs strict | `PASS` | `1` |
| max_workers default 1 or 2 | `PASS` | `2` |
| API key value not read during preflight | `PASS` | `{"api_key_env_name": "DEEPSEEK_API_KEY", "value_read": false}` |
| max_tokens 4096 | `PASS` | `4096` |
| temperature explicit zero | `PASS` | `{"send_mode": "explicit", "value": 0}` |
| thinking disabled | `PASS` | `{"thinking": {"type": "disabled"}}` |
| sampling nuisance parameters omitted | `PASS` | `{"frequency_penalty": {"send_mode": "omitted", "value": null}, "min_p": {"send_mode": "omitted", "value": null}, "presence_penalty": {"send_mode": "omitted", "value": null}, "repetition_penalty": {"send_mode": "omitted", "value": null}, "seed": {"send_mode": "omitted", "value": null}, "stop": {"s...` |
| PREFLIGHT_SHA256SUMS internal verification | `PASS` | `["OK tools/run_ecvs_deepseek_harder_stress_v1_mid_visiblecarry_vs_maturessrloop.py", "OK configs/_probe_ecvs_deepseek_v4pro_harder_stress_v1_mid_visiblecarry_vs_maturessrloop_15task_2method_3budget_1run.json", "OK data/main_v1/harder_visible_state_transfer_stress_v1_mid/MODEL_VISIBLE_TASK_MANIFES...` |

## Blocker

The packet contains `real_swe_style_controlled_plus` rows. They are calibration anchors and must not be claimed as true executable SWE anchors.

## Run Gate

Run the API only after explicit user confirmation. The default script mode is preflight-only.
