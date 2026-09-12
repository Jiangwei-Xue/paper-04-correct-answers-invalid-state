# _probe_ecvs_deepseek_v4pro_harder_stress_v1_static65_visiblecarry_vs_maturessrloop_15task_2method_3budget_1run Preflight Audit

Positioning: `calibration_only_not_primary_evidence`.

No API call was made. No API key value was read.

Overall status: `PASS_REVIEWED`
Checks passed: 30
Checks failed: 0
Expected rows: 90

## Prompt Leakage Scanner

- Hard-fail metadata hits: `0`
- Lexical review hits: `64`
- Semantic leakage review status: `PASS`
- Review notes: Lexical review terms appeared only as ordinary model-visible task language; no scorer-only answer/label/oracle/scoring metadata was detected.

Hard-fail scanner is restricted to explicit scorer/oracle/metric/internal metadata field names. Lexical terms such as `answer`, `label`, `boundary`, `score`, `required`, and `forbidden` are reviewed in context and do not fail preflight when used as ordinary task language.

## Token Prefix Compatibility

This static-65 packet uses only required marker prefixes recognized by the existing rolling and mature-SSR runners: `REQ`, `LOCK`, `SCOPE`, `CHECK`, `ANCHOR`, `EDGE`, `FRONTIER`, `MERGE`, and `VERIFY`. Difficulty is downshifted from the parent v1 design by reducing static task-construction pressure; it is not selected from model success rates. Preflight fails if any required token prefix falls outside the runner extractor contract.

- MIDSTATE required tokens: `0`
- Incompatible required tokens: `0`
- Prefix counts: `{"ANCHOR": 15, "CHECK": 15, "EDGE": 15, "FRONTIER": 15, "LOCK": 27, "MERGE": 15, "REQ": 30, "SCOPE": 15, "VERIFY": 15}`

Lexical hit counts:

- `answer`: 45
- `boundary`: 18
- `label`: 1

## Semantic Leakage Review

| task_id | term | semantic_leakage | context | review_note |
|---|---:|---:|---|---|
| harder_stress_v1_static65_frontierpp_01_retry_route_matrix | `answer` | `false` | ... operations and preserve the route-local backoff policy. Keep the final answer focused on the active editable files and preserve CHECK_01_TNBK2 when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_01_retry_route_matrix | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name tests/retry_private_replay.py, private/retr... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_01_retry_route_matrix | `answer` | `false` | ...lan.", "segment_id": "s10"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_01_retry_route_matrix | `boundary` | `false` | ...er DECOY_01_4TNBK remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_01_Z62KBNT44TN and VAULT_01_TNBK26 are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_02_plugin_registry_resolution | `answer` | `false` | ...mespace resolver and preserve the public fallback order. Keep the final answer focused on the active editable files and preserve CHECK_02_W2TC9 when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_02_plugin_registry_resolution | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name private/plugin_registry_dump.json, tests/pl... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_02_plugin_registry_resolution | `answer` | `false` | ...lan.", "segment_id": "s10"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_02_plugin_registry_resolution | `boundary` | `false` | ...er DECOY_02_AW2TC remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_02_X89CT2WAAW2 and VAULT_02_W2TC98 are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_03_export_retention_window | `answer` | `false` | ...avior while applying the late regional retention window. Keep the final answer focused on the active editable files and preserve CHECK_03_YADX4 when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_03_export_retention_window | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name private/export_trace.csv, tests/export_priv... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_03_export_retention_window | `answer` | `false` | ...lan.", "segment_id": "s10"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_03_export_retention_window | `boundary` | `false` | ...e change plan to plan an export retention change with late regional and boundary constraints. The active editable files are src/export/window.py, src/ex... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_03_export_retention_window | `boundary` | `false` | ...er DECOY_03_XYADX remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_03_LC4XDAYXXYA and VAULT_03_YADX4C are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_04_telemetry_redaction_contract | `answer` | `false` | ...nt fields while preserving public aggregate event names. Keep the final answer focused on the active editable files and preserve CHECK_04_66JVE when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_04_telemetry_redaction_contract | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name logs/private_telemetry_sample.jsonl, tests/... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_04_telemetry_redaction_contract | `answer` | `false` | ...lan.", "segment_id": "s10"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_04_telemetry_redaction_contract | `boundary` | `false` | ...er DECOY_04_566JV remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_04_S9EVJ665566 and VAULT_04_66JVE9 are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_05_auth_claim_boundary | `answer` | `false` | ...ience and nullable only in the gated compatibility case. Keep the final answer focused on the active editable files and preserve CHECK_05_G3RMP when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_05_auth_claim_boundary | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name private/auth_trace.log, tests/auth_claims_p... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_05_auth_claim_boundary | `answer` | `false` | ...lan.", "segment_id": "s10"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_05_auth_claim_boundary | `boundary` | `false` | ...er DECOY_05_XG3RM remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_05_7TPMR3GXXG3 and VAULT_05_G3RMPT are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_06_build_matrix_compat | `answer` | `false` | ...ublic build contract and avoid generated lockfile churn. Keep the final answer focused on the active editable files and preserve CHECK_06_TBEQ7 when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_06_build_matrix_compat | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name private/build_matrix_notes.md, tests/build_... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_06_build_matrix_compat | `answer` | `false` | ...lan.", "segment_id": "s10"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_06_build_matrix_compat | `boundary` | `false` | ...er DECOY_06_YTBEQ remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_06_WE7QEBTYYTB and VAULT_06_TBEQ7E are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_07_staged_schema_migration | `answer` | `false` | ...the old reader path and add a guarded writer transition. Keep the final answer focused on the active editable files and preserve CHECK_07_F7BWC when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_07_staged_schema_migration | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name private/schema_patch_notes.md, tests/schema... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_07_staged_schema_migration | `answer` | `false` | ...lan.", "segment_id": "s10"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_07_staged_schema_migration | `boundary` | `false` | ...er DECOY_07_AF7BW remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_07_6UCWB7FAAF7 and VAULT_07_F7BWCU are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_08_parser_error_taxonomy | `answer` | `false` | ...s to public classes without exposing replay-only labels. Keep the final answer focused on the active editable files and preserve CHECK_08_HACGC when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_08_parser_error_taxonomy | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name tests/parser_private_trace_test.py, private... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_08_parser_error_taxonomy | `answer` | `false` | ...lan.", "segment_id": "s10"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_08_parser_error_taxonomy | `label` | `false` | ...t_id": "s3"}, {"content": "A compatibility note says the new normalized label is allowed only when class and source component both match. If the cond... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_08_parser_error_taxonomy | `boundary` | `false` | ...er DECOY_08_RHACG remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_08_PJCGCAHRRHA and VAULT_08_HACGCJ are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_09_policy_alias_cascade | `answer` | `false` | ...ctive alias through the registry without widening scope. Keep the final answer focused on the active editable files and preserve CHECK_09_U6FBL when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_09_policy_alias_cascade | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name docs/private_policy_notes.md, tests/policy_... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_09_policy_alias_cascade | `answer` | `false` | ...lan.", "segment_id": "s10"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_09_policy_alias_cascade | `boundary` | `false` | ...er DECOY_09_KU6FB remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_09_2SLBF6UKKU6 and VAULT_09_U6FBLS are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_10_cache_invalidation_mesh | `answer` | `false` | ...only after both stores acknowledge the active namespace. Keep the final answer focused on the active editable files and preserve CHECK_10_X9XNE when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_10_cache_invalidation_mesh | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name src/cache/internal_probe.py, private/cache_... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_10_cache_invalidation_mesh | `answer` | `false` | ...lan.", "segment_id": "s10"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_frontierpp_10_cache_invalidation_mesh | `boundary` | `false` | ...er DECOY_10_EX9XN remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_10_EXENX9XEEX9 and VAULT_10_X9XNEX are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_realswe_01_django_upload_path_boundary | `answer` | `false` | ...d path without allowing private storage prefix exposure. Keep the final answer focused on the active editable files and preserve CHECK_01_WBPM3 when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_realswe_01_django_upload_path_boundary | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name tests/private_upload_replay.py, private/upl... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_realswe_01_django_upload_path_boundary | `answer` | `false` | ...lan.", "segment_id": "s10"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_realswe_01_django_upload_path_boundary | `boundary` | `false` | ...ge plan to repair a repo-style upload path handling issue with security boundary and config sensitivity. The active editable files are framework/uploads... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_realswe_01_django_upload_path_boundary | `boundary` | `false` | ...er DECOY_01_DWBPM remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_01_FL3MPBWDDWB and VAULT_01_WBPM3L are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_realswe_02_fastapi_dependency_precedence | `answer` | `false` | ...l override precedence while keeping app defaults intact. Keep the final answer focused on the active editable files and preserve CHECK_02_TERWB when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_realswe_02_fastapi_dependency_precedence | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name tests/private_dependency_replay.py, private... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_realswe_02_fastapi_dependency_precedence | `answer` | `false` | ...lan.", "segment_id": "s10"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_realswe_02_fastapi_dependency_precedence | `boundary` | `false` | ...er DECOY_02_LTERW remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_02_PVBWRETLLTE and VAULT_02_TERWBV are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_realswe_03_pandas_tz_csv_roundtrip | `answer` | `false` | ...undtrip behavior without copying private fixture labels. Keep the final answer focused on the active editable files and preserve CHECK_03_GB5JZ when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_realswe_03_pandas_tz_csv_roundtrip | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name tests/private_csv_roundtrip_debug.py, priva... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_realswe_03_pandas_tz_csv_roundtrip | `answer` | `false` | ...lan.", "segment_id": "s10"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_realswe_03_pandas_tz_csv_roundtrip | `boundary` | `false` | ...er DECOY_03_TGB5J remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_03_QNZJ5BGTTGB and VAULT_03_GB5JZN are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_realswe_04_pytest_nodeid_stability | `answer` | `false` | ...node ids stable while applying the late escaping branch. Keep the final answer focused on the active editable files and preserve CHECK_04_BXL8N when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_realswe_04_pytest_nodeid_stability | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name tests/private_nodeid_replay.py, private/nod... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_realswe_04_pytest_nodeid_stability | `answer` | `false` | ...lan.", "segment_id": "s10"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_realswe_04_pytest_nodeid_stability | `boundary` | `false` | ...er DECOY_04_PBXL8 remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_04_QNN8LXBPPBX and VAULT_04_BXL8NN are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_realswe_05_requests_proxy_redirect_auth | `answer` | `false` | ...der behavior while avoiding private proxy trace leakage. Keep the final answer focused on the active editable files and preserve CHECK_05_YRSEV when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_realswe_05_requests_proxy_redirect_auth | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name tests/private_proxy_auth_replay.py, private... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_realswe_05_requests_proxy_redirect_auth | `answer` | `false` | ...lan.", "segment_id": "s10"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_realswe_05_requests_proxy_redirect_auth | `boundary` | `false` | ... repo-style change plan to plan a proxy auth redirect fix with security boundary and header retention constraints. The active editable files are client/... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static65_realswe_05_requests_proxy_redirect_auth | `boundary` | `false` | ...er DECOY_05_HYRSE remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_05_46VESRYHHYR and VAULT_05_YRSEV6 are private diagnostic... | ordinary task wording, not scorer-only metadata |

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
| MODEL_VISIBLE_TASK_MANIFEST.jsonl sha256 | `PASS` | `{"expected": "b7ef9438f87ec5d28cb020ec08c05051f33e24e1a77982ec060f4cb8e226de63", "observed": "b7ef9438f87ec5d28cb020ec08c05051f33e24e1a77982ec060f4cb8e226de63"}` |
| SCORER_ORACLE_MANIFEST.jsonl sha256 | `PASS` | `{"expected": "f45cccbb686765a79c0669b7346428f5706f89245b537342c218032f27fcad57", "observed": "f45cccbb686765a79c0669b7346428f5706f89245b537342c218032f27fcad57"}` |
| TASK_PROVENANCE_MANIFEST.jsonl sha256 | `PASS` | `{"expected": "669d79b5a2fe01eb5887aaf1f77f841654e9fd487afadc00c39cdea62cc32881", "observed": "669d79b5a2fe01eb5887aaf1f77f841654e9fd487afadc00c39cdea62cc32881"}` |
| TASK_SELECTION.csv sha256 | `PASS` | `{"expected": "7256185a6e9fbc516a2938df0caf3e80ea08a2a3508dd0f3392803a3e24c1c23", "observed": "7256185a6e9fbc516a2938df0caf3e80ea08a2a3508dd0f3392803a3e24c1c23"}` |
| 15 model-visible task rows | `PASS` | `15` |
| 15 scorer-oracle rows | `PASS` | `15` |
| 15 provenance rows | `PASS` | `15` |
| 15 task-selection rows | `PASS` | `15` |
| TASK_SPLIT_AUDIT PASS | `PASS` | `"PASS"` |
| duplicate_task_ids empty | `PASS` | `{"split": [], "visible": []}` |
| required token prefixes compatible with runner extractor | `PASS` | `{"incompatible_required_tokens": [], "midstate_required_tokens": [], "prefix_counts": {"ANCHOR": 15, "CHECK": 15, "EDGE": 15, "FRONTIER": 15, "LOCK": 27, "MERGE": 15, "REQ": 30, "SCOPE": 15, "VERIFY": 15}, "safe_required_token_prefixes": ["ANCHOR", "CHECK", "EDGE", "FRONTIER", "LOCK", "MERGE", "R...` |
| MIDSTATE required tokens absent | `PASS` | `[]` |
| model_visible_forbidden_metadata_key_hits empty | `PASS` | `[]` |
| model-visible hard-fail metadata scan | `PASS` | `[]` |
| model-visible lexical semantic leakage review | `PASS` | `{"lexical_review_hit_count": 64, "notes": "Lexical review terms appeared only as ordinary model-visible task language; no scorer-only answer/label/oracle/scoring metadata was detected.", "semantic_leakage_count": 0}` |
| BLOCKER.md exists | `PASS` | `"data/main_v1/harder_visible_state_transfer_stress_v1_static65/BLOCKER.md"` |
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
| PREFLIGHT_SHA256SUMS internal verification | `PASS` | `["OK tools/run_ecvs_deepseek_harder_stress_v1_static65_visiblecarry_vs_maturessrloop.py", "OK configs/_probe_ecvs_deepseek_v4pro_harder_stress_v1_static65_visiblecarry_vs_maturessrloop_15task_2method_3budget_1run.json", "OK data/main_v1/harder_visible_state_transfer_stress_v1_static65/MODEL_VISIB...` |

## Blocker

The packet contains `real_swe_style_controlled_plus` rows. They are calibration anchors and must not be claimed as true executable SWE anchors.

## Run Gate

Run the API only after explicit user confirmation. The default script mode is preflight-only.
