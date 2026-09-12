# _probe_ecvs_deepseek_v4pro_harder_stress_v1_2mode20_readeraware_vs_schemaaware_attempt3_15task_2method_3budget_1run Preflight Audit

Positioning: `calibration_only_not_primary_evidence`.

No API call was made. No API key value was read.

Overall status: `PASS_REVIEWED`
Checks passed: 28
Checks failed: 0
Expected rows: 90

## Prompt Leakage Scanner

- Hard-fail metadata hits: `0`
- Lexical review hits: `94`
- Semantic leakage review status: `PASS`
- Review notes: Lexical review terms appeared only as ordinary model-visible task language; no scorer-only answer/label/oracle/scoring metadata was detected.

Hard-fail scanner is restricted to explicit scorer/oracle/metric/internal metadata field names. Lexical terms such as `answer`, `label`, `boundary`, `score`, `required`, and `forbidden` are reviewed in context and do not fail preflight when used as ordinary task language.

Lexical hit counts:

- `answer`: 60
- `boundary`: 18
- `label`: 16

## Semantic Leakage Review

| task_id | term | semantic_leakage | context | review_note |
|---|---:|---:|---|---|
| harder_stress_v1_frontierpp_01_parser_error_taxonomy | `answer` | `false` | ...s to public classes without exposing replay-only labels. Keep the final answer focused on the active editable files and preserve CHECK_01_7CERA when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_01_parser_error_taxonomy | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name tests/parser_private_trace_test.py, private... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_01_parser_error_taxonomy | `answer` | `false` | ...plan.", "segment_id": "s8"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_01_parser_error_taxonomy | `answer` | `false` | ...prefix.", "segment_id": "s10"}, {"content": "Late constraint: the final answer must use the accepted branch from the maintainers' update, not the draf... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_01_parser_error_taxonomy | `label` | `false` | ...t_id": "s3"}, {"content": "A compatibility note says the new normalized label is allowed only when class and source component both match. If the cond... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_01_parser_error_taxonomy | `label` | `false` | ...applies only after the late condition has been satisfied. The near-miss label DECOY_01_T7CER remains invalid even though it shares the ticket prefix.... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_01_parser_error_taxonomy | `boundary` | `false` | ...OBSOLETE_01_7CERA remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_01_QGAREC7TT7C and VAULT_01_7CERAG are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_02_staged_schema_migration | `answer` | `false` | ...the old reader path and add a guarded writer transition. Keep the final answer focused on the active editable files and preserve CHECK_02_FR6Y4 when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_02_staged_schema_migration | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name private/schema_patch_notes.md, tests/schema... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_02_staged_schema_migration | `answer` | `false` | ...plan.", "segment_id": "s8"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_02_staged_schema_migration | `answer` | `false` | ...prefix.", "segment_id": "s10"}, {"content": "Late constraint: the final answer must use the accepted branch from the maintainers' update, not the draf... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_02_staged_schema_migration | `label` | `false` | ...applies only after the late condition has been satisfied. The near-miss label DECOY_02_UFR6Y remains invalid even though it shares the ticket prefix.... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_02_staged_schema_migration | `boundary` | `false` | ...OBSOLETE_02_FR6Y4 remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_02_4P4Y6RFUUFR and VAULT_02_FR6Y4P are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_03_policy_alias_cascade | `answer` | `false` | ...ctive alias through the registry without widening scope. Keep the final answer focused on the active editable files and preserve CHECK_03_KX4J4 when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_03_policy_alias_cascade | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name docs/private_policy_notes.md, tests/policy_... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_03_policy_alias_cascade | `answer` | `false` | ...plan.", "segment_id": "s8"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_03_policy_alias_cascade | `answer` | `false` | ...prefix.", "segment_id": "s10"}, {"content": "Late constraint: the final answer must use the accepted branch from the maintainers' update, not the draf... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_03_policy_alias_cascade | `label` | `false` | ...applies only after the late condition has been satisfied. The near-miss label DECOY_03_DKX4J remains invalid even though it shares the ticket prefix.... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_03_policy_alias_cascade | `boundary` | `false` | ...OBSOLETE_03_KX4J4 remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_03_RU4J4XKDDKX and VAULT_03_KX4J4U are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_04_export_retention_window | `answer` | `false` | ...avior while applying the late regional retention window. Keep the final answer focused on the active editable files and preserve CHECK_04_MDM3R when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_04_export_retention_window | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name private/export_trace.csv, tests/export_priv... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_04_export_retention_window | `answer` | `false` | ...plan.", "segment_id": "s8"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_04_export_retention_window | `answer` | `false` | ...prefix.", "segment_id": "s10"}, {"content": "Late constraint: the final answer must use the accepted branch from the maintainers' update, not the draf... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_04_export_retention_window | `label` | `false` | ...applies only after the late condition has been satisfied. The near-miss label DECOY_04_KMDM3 remains invalid even though it shares the ticket prefix.... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_04_export_retention_window | `boundary` | `false` | ...e change plan to plan an export retention change with late regional and boundary constraints. The active editable files are src/export/window.py, src/ex... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_04_export_retention_window | `boundary` | `false` | ...OBSOLETE_04_MDM3R remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_04_JZR3MDMKKMD and VAULT_04_MDM3RZ are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_05_telemetry_redaction_contract | `answer` | `false` | ...nt fields while preserving public aggregate event names. Keep the final answer focused on the active editable files and preserve CHECK_05_9GLLQ when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_05_telemetry_redaction_contract | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name logs/private_telemetry_sample.jsonl, tests/... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_05_telemetry_redaction_contract | `answer` | `false` | ...plan.", "segment_id": "s8"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_05_telemetry_redaction_contract | `answer` | `false` | ...prefix.", "segment_id": "s10"}, {"content": "Late constraint: the final answer must use the accepted branch from the maintainers' update, not the draf... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_05_telemetry_redaction_contract | `label` | `false` | ...applies only after the late condition has been satisfied. The near-miss label DECOY_05_39GLL remains invalid even though it shares the ticket prefix.... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_05_telemetry_redaction_contract | `boundary` | `false` | ...OBSOLETE_05_9GLLQ remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_05_QGQLLG9339G and VAULT_05_9GLLQG are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_06_cache_invalidation_mesh | `answer` | `false` | ...only after both stores acknowledge the active namespace. Keep the final answer focused on the active editable files and preserve CHECK_06_EG3S4 when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_06_cache_invalidation_mesh | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name src/cache/internal_probe.py, private/cache_... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_06_cache_invalidation_mesh | `answer` | `false` | ...plan.", "segment_id": "s8"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_06_cache_invalidation_mesh | `answer` | `false` | ...prefix.", "segment_id": "s10"}, {"content": "Late constraint: the final answer must use the accepted branch from the maintainers' update, not the draf... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_06_cache_invalidation_mesh | `label` | `false` | ...applies only after the late condition has been satisfied. The near-miss label DECOY_06_JEG3S remains invalid even though it shares the ticket prefix.... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_06_cache_invalidation_mesh | `boundary` | `false` | ...OBSOLETE_06_EG3S4 remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_06_KC4S3GEJJEG and VAULT_06_EG3S4C are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_07_plugin_registry_resolution | `answer` | `false` | ...mespace resolver and preserve the public fallback order. Keep the final answer focused on the active editable files and preserve CHECK_07_WSQFL when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_07_plugin_registry_resolution | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name private/plugin_registry_dump.json, tests/pl... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_07_plugin_registry_resolution | `answer` | `false` | ...plan.", "segment_id": "s8"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_07_plugin_registry_resolution | `answer` | `false` | ...prefix.", "segment_id": "s10"}, {"content": "Late constraint: the final answer must use the accepted branch from the maintainers' update, not the draf... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_07_plugin_registry_resolution | `label` | `false` | ...applies only after the late condition has been satisfied. The near-miss label DECOY_07_JWSQF remains invalid even though it shares the ticket prefix.... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_07_plugin_registry_resolution | `boundary` | `false` | ...OBSOLETE_07_WSQFL remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_07_3KLFQSWJJWS and VAULT_07_WSQFLK are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_08_retry_route_matrix | `answer` | `false` | ... operations and preserve the route-local backoff policy. Keep the final answer focused on the active editable files and preserve CHECK_08_YCZRK when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_08_retry_route_matrix | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name tests/retry_private_replay.py, private/retr... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_08_retry_route_matrix | `answer` | `false` | ...plan.", "segment_id": "s8"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_08_retry_route_matrix | `answer` | `false` | ...prefix.", "segment_id": "s10"}, {"content": "Late constraint: the final answer must use the accepted branch from the maintainers' update, not the draf... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_08_retry_route_matrix | `label` | `false` | ...applies only after the late condition has been satisfied. The near-miss label DECOY_08_XYCZR remains invalid even though it shares the ticket prefix.... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_08_retry_route_matrix | `boundary` | `false` | ...OBSOLETE_08_YCZRK remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_08_BRKRZCYXXYC and VAULT_08_YCZRKR are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_09_auth_claim_boundary | `answer` | `false` | ...ience and nullable only in the gated compatibility case. Keep the final answer focused on the active editable files and preserve CHECK_09_MCZ4B when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_09_auth_claim_boundary | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name private/auth_trace.log, tests/auth_claims_p... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_09_auth_claim_boundary | `answer` | `false` | ...plan.", "segment_id": "s8"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_09_auth_claim_boundary | `answer` | `false` | ...prefix.", "segment_id": "s10"}, {"content": "Late constraint: the final answer must use the accepted branch from the maintainers' update, not the draf... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_09_auth_claim_boundary | `label` | `false` | ...applies only after the late condition has been satisfied. The near-miss label DECOY_09_RMCZ4 remains invalid even though it shares the ticket prefix.... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_09_auth_claim_boundary | `boundary` | `false` | ...OBSOLETE_09_MCZ4B remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_09_VDB4ZCMRRMC and VAULT_09_MCZ4BD are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_10_build_matrix_compat | `answer` | `false` | ...ublic build contract and avoid generated lockfile churn. Keep the final answer focused on the active editable files and preserve CHECK_10_D5YAL when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_10_build_matrix_compat | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name private/build_matrix_notes.md, tests/build_... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_10_build_matrix_compat | `answer` | `false` | ...plan.", "segment_id": "s8"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_10_build_matrix_compat | `answer` | `false` | ...prefix.", "segment_id": "s10"}, {"content": "Late constraint: the final answer must use the accepted branch from the maintainers' update, not the draf... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_10_build_matrix_compat | `label` | `false` | ...applies only after the late condition has been satisfied. The near-miss label DECOY_10_BD5YA remains invalid even though it shares the ticket prefix.... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_frontierpp_10_build_matrix_compat | `boundary` | `false` | ...OBSOLETE_10_D5YAL remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_10_M7LAY5DBBD5 and VAULT_10_D5YAL7 are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_realswe_01_django_upload_path_boundary | `answer` | `false` | ...d path without allowing private storage prefix exposure. Keep the final answer focused on the active editable files and preserve CHECK_01_A4SS7 when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_realswe_01_django_upload_path_boundary | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name tests/private_upload_replay.py, private/upl... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_realswe_01_django_upload_path_boundary | `answer` | `false` | ...plan.", "segment_id": "s8"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_realswe_01_django_upload_path_boundary | `answer` | `false` | ...prefix.", "segment_id": "s10"}, {"content": "Late constraint: the final answer must use the accepted branch from the maintainers' update, not the draf... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_realswe_01_django_upload_path_boundary | `label` | `false` | ...applies only after the late condition has been satisfied. The near-miss label DECOY_01_YA4SS remains invalid even though it shares the ticket prefix.... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_realswe_01_django_upload_path_boundary | `boundary` | `false` | ...ge plan to repair a repo-style upload path handling issue with security boundary and config sensitivity. The active editable files are framework/uploads... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_realswe_01_django_upload_path_boundary | `boundary` | `false` | ...OBSOLETE_01_A4SS7 remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_01_ET7SS4AYYA4 and VAULT_01_A4SS7T are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_realswe_02_requests_proxy_redirect_auth | `answer` | `false` | ...der behavior while avoiding private proxy trace leakage. Keep the final answer focused on the active editable files and preserve CHECK_02_YX5B9 when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_realswe_02_requests_proxy_redirect_auth | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name tests/private_proxy_auth_replay.py, private... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_realswe_02_requests_proxy_redirect_auth | `answer` | `false` | ...plan.", "segment_id": "s8"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_realswe_02_requests_proxy_redirect_auth | `answer` | `false` | ...prefix.", "segment_id": "s10"}, {"content": "Late constraint: the final answer must use the accepted branch from the maintainers' update, not the draf... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_realswe_02_requests_proxy_redirect_auth | `label` | `false` | ...applies only after the late condition has been satisfied. The near-miss label DECOY_02_NYX5B remains invalid even though it shares the ticket prefix.... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_realswe_02_requests_proxy_redirect_auth | `boundary` | `false` | ... repo-style change plan to plan a proxy auth redirect fix with security boundary and header retention constraints. The active editable files are client/... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_realswe_02_requests_proxy_redirect_auth | `boundary` | `false` | ...OBSOLETE_02_YX5B9 remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_02_FN9B5XYNNYX and VAULT_02_YX5B9N are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_realswe_03_pandas_tz_csv_roundtrip | `answer` | `false` | ...undtrip behavior without copying private fixture labels. Keep the final answer focused on the active editable files and preserve CHECK_03_LQZ4L when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_realswe_03_pandas_tz_csv_roundtrip | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name tests/private_csv_roundtrip_debug.py, priva... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_realswe_03_pandas_tz_csv_roundtrip | `answer` | `false` | ...plan.", "segment_id": "s8"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_realswe_03_pandas_tz_csv_roundtrip | `answer` | `false` | ...prefix.", "segment_id": "s10"}, {"content": "Late constraint: the final answer must use the accepted branch from the maintainers' update, not the draf... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_realswe_03_pandas_tz_csv_roundtrip | `label` | `false` | ...applies only after the late condition has been satisfied. The near-miss label DECOY_03_XLQZ4 remains invalid even though it shares the ticket prefix.... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_realswe_03_pandas_tz_csv_roundtrip | `boundary` | `false` | ...OBSOLETE_03_LQZ4L remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_03_ARL4ZQLXXLQ and VAULT_03_LQZ4LR are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_realswe_04_pytest_nodeid_stability | `answer` | `false` | ...node ids stable while applying the late escaping branch. Keep the final answer focused on the active editable files and preserve CHECK_04_XN9QH when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_realswe_04_pytest_nodeid_stability | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name tests/private_nodeid_replay.py, private/nod... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_realswe_04_pytest_nodeid_stability | `answer` | `false` | ...plan.", "segment_id": "s8"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_realswe_04_pytest_nodeid_stability | `answer` | `false` | ...prefix.", "segment_id": "s10"}, {"content": "Late constraint: the final answer must use the accepted branch from the maintainers' update, not the draf... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_realswe_04_pytest_nodeid_stability | `label` | `false` | ...applies only after the late condition has been satisfied. The near-miss label DECOY_04_ZXN9Q remains invalid even though it shares the ticket prefix.... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_realswe_04_pytest_nodeid_stability | `boundary` | `false` | ...OBSOLETE_04_XN9QH remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_04_JWHQ9NXZZXN and VAULT_04_XN9QHW are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_realswe_05_fastapi_dependency_precedence | `answer` | `false` | ...l override precedence while keeping app defaults intact. Keep the final answer focused on the active editable files and preserve CHECK_05_2P4S7 when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_realswe_05_fastapi_dependency_precedence | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name tests/private_dependency_replay.py, private... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_realswe_05_fastapi_dependency_precedence | `answer` | `false` | ...plan.", "segment_id": "s8"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_realswe_05_fastapi_dependency_precedence | `answer` | `false` | ...prefix.", "segment_id": "s10"}, {"content": "Late constraint: the final answer must use the accepted branch from the maintainers' update, not the draf... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_realswe_05_fastapi_dependency_precedence | `label` | `false` | ...applies only after the late condition has been satisfied. The near-miss label DECOY_05_K2P4S remains invalid even though it shares the ticket prefix.... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_realswe_05_fastapi_dependency_precedence | `boundary` | `false` | ...OBSOLETE_05_2P4S7 remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_05_7S7S4P2KK2P and VAULT_05_2P4S7S are private diagnostic... | ordinary task wording, not scorer-only metadata |

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

- `rolling_visible_carry_forward2.0(reader_aware)`: rolling visible carry-forward with a deterministic reader-aware state compiler over model-visible text only.
- `mature_ssr_loop2.0(schema_aware)`: mature SSR loop 2.0 with a deterministic format-aware state compiler over model-visible text only.

## Checks

| check | status | detail |
|---|---:|---|
| MODEL_VISIBLE_TASK_MANIFEST.jsonl sha256 | `PASS` | `{"expected": "33146312feffa160a32e762c32a2b0a3b61464eaaeb147e93bec4f257a858730", "observed": "33146312feffa160a32e762c32a2b0a3b61464eaaeb147e93bec4f257a858730"}` |
| SCORER_ORACLE_MANIFEST.jsonl sha256 | `PASS` | `{"expected": "24c2aa4fdaf72321ee311eeeb023714d65b6477b681b763519a40c830f2f1974", "observed": "24c2aa4fdaf72321ee311eeeb023714d65b6477b681b763519a40c830f2f1974"}` |
| TASK_PROVENANCE_MANIFEST.jsonl sha256 | `PASS` | `{"expected": "d239781121d1d6a6cd4cbcab5e859463831be69b2bcfc1a1884a2ada2c1ef299", "observed": "d239781121d1d6a6cd4cbcab5e859463831be69b2bcfc1a1884a2ada2c1ef299"}` |
| TASK_SELECTION.csv sha256 | `PASS` | `{"expected": "649fa93b196242a19e144bd5297cf90abac45ad4aab2596921bacaa4f809894a", "observed": "649fa93b196242a19e144bd5297cf90abac45ad4aab2596921bacaa4f809894a"}` |
| 15 model-visible task rows | `PASS` | `15` |
| 15 scorer-oracle rows | `PASS` | `15` |
| 15 provenance rows | `PASS` | `15` |
| 15 task-selection rows | `PASS` | `15` |
| TASK_SPLIT_AUDIT PASS | `PASS` | `"PASS"` |
| duplicate_task_ids empty | `PASS` | `{"split": [], "visible": []}` |
| model_visible_forbidden_metadata_key_hits empty | `PASS` | `[]` |
| model-visible hard-fail metadata scan | `PASS` | `[]` |
| model-visible lexical semantic leakage review | `PASS` | `{"lexical_review_hit_count": 94, "notes": "Lexical review terms appeared only as ordinary model-visible task language; no scorer-only answer/label/oracle/scoring metadata was detected.", "semantic_leakage_count": 0}` |
| BLOCKER.md exists | `PASS` | `"data/main_v1/harder_visible_state_transfer_stress_v1/BLOCKER.md"` |
| BLOCKER.md real-SWE limitation disclosed | `PASS` | `"real_swe_style_controlled_plus and non-executable limitation"` |
| result_dir no old row outputs | `PASS` | `{"conflicts": [], "status": "exists_without_row_outputs"}` |
| raw_dir absent or empty | `PASS` | `{"conflicts": [], "status": "absent"}` |
| expected rows 90 | `PASS` | `90` |
| method list strict | `PASS` | `["rolling_visible_carry_forward2.0(reader_aware)", "mature_ssr_loop2.0(schema_aware)"]` |
| budgets strict | `PASS` | `[300, 600, 1200]` |
| runs strict | `PASS` | `1` |
| max_workers default 1 or 2 | `PASS` | `2` |
| API key value not read during preflight | `PASS` | `{"api_key_env_name": "DEEPSEEK_API_KEY", "value_read": false}` |
| max_tokens 4096 | `PASS` | `4096` |
| temperature explicit zero | `PASS` | `{"send_mode": "explicit", "value": 0}` |
| thinking disabled | `PASS` | `{"thinking": {"type": "disabled"}}` |
| sampling nuisance parameters omitted | `PASS` | `{"frequency_penalty": {"send_mode": "omitted", "value": null}, "min_p": {"send_mode": "omitted", "value": null}, "presence_penalty": {"send_mode": "omitted", "value": null}, "repetition_penalty": {"send_mode": "omitted", "value": null}, "seed": {"send_mode": "omitted", "value": null}, "stop": {"s...` |
| PREFLIGHT_SHA256SUMS internal verification | `PASS` | `["OK tools/run_ecvs_deepseek_harder_stress_v1_2mode20_readeraware_vs_schemaaware_attempt3.py", "OK configs/_probe_ecvs_deepseek_v4pro_harder_stress_v1_2mode20_readeraware_vs_schemaaware_attempt3_15task_2method_3budget_1run.json", "OK data/main_v1/harder_visible_state_transfer_stress_v1/MODEL_VISI...` |

## Blocker

The packet contains `real_swe_style_controlled_plus` rows. They are calibration anchors and must not be claimed as true executable SWE anchors.

## Run Gate

Run the API only after explicit user confirmation. The default script mode is preflight-only.
