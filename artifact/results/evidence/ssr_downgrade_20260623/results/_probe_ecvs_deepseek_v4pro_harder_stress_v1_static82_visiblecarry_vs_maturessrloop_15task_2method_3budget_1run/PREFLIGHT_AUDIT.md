# _probe_ecvs_deepseek_v4pro_harder_stress_v1_static82_visiblecarry_vs_maturessrloop_15task_2method_3budget_1run Preflight Audit

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

This static-82 packet uses only required marker prefixes recognized by the existing rolling and mature-SSR runners: `REQ`, `LOCK`, `SCOPE`, `CHECK`, `ANCHOR`, `EDGE`, `FRONTIER`, `MERGE`, and `VERIFY`. Difficulty is downshifted from the parent v1 design by reducing static task-construction pressure; it is not selected from model success rates. Preflight fails if any required token prefix falls outside the runner extractor contract.

- MIDSTATE required tokens: `0`
- Incompatible required tokens: `0`
- Prefix counts: `{"ANCHOR": 15, "CHECK": 15, "EDGE": 15, "FRONTIER": 15, "LOCK": 30, "MERGE": 15, "REQ": 30, "SCOPE": 17, "VERIFY": 15}`

Lexical hit counts:

- `answer`: 45
- `boundary`: 18
- `label`: 1

## Semantic Leakage Review

| task_id | term | semantic_leakage | context | review_note |
|---|---:|---:|---|---|
| harder_stress_v1_static82_frontierpp_01_parser_error_taxonomy | `answer` | `false` | ...s to public classes without exposing replay-only labels. Keep the final answer focused on the active editable files and preserve CHECK_01_B8GAM when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_01_parser_error_taxonomy | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name tests/parser_private_trace_test.py, private... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_01_parser_error_taxonomy | `answer` | `false` | ...lan.", "segment_id": "s10"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_01_parser_error_taxonomy | `label` | `false` | ...t_id": "s3"}, {"content": "A compatibility note says the new normalized label is allowed only when class and source component both match. If the cond... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_01_parser_error_taxonomy | `boundary` | `false` | ...er DECOY_01_7B8GA remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_01_VRMAG8B77B8 and VAULT_01_B8GAMR are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_02_plugin_registry_resolution | `answer` | `false` | ...mespace resolver and preserve the public fallback order. Keep the final answer focused on the active editable files and preserve CHECK_02_EJFL5 when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_02_plugin_registry_resolution | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name private/plugin_registry_dump.json, tests/pl... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_02_plugin_registry_resolution | `answer` | `false` | ...lan.", "segment_id": "s10"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_02_plugin_registry_resolution | `boundary` | `false` | ...er DECOY_02_FEJFL remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_02_UF5LFJEFFEJ and VAULT_02_EJFL5F are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_03_auth_claim_boundary | `answer` | `false` | ...ience and nullable only in the gated compatibility case. Keep the final answer focused on the active editable files and preserve CHECK_03_AD3HF when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_03_auth_claim_boundary | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name private/auth_trace.log, tests/auth_claims_p... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_03_auth_claim_boundary | `answer` | `false` | ...lan.", "segment_id": "s10"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_03_auth_claim_boundary | `boundary` | `false` | ...er DECOY_03_4AD3H remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_03_QCFH3DA44AD and VAULT_03_AD3HFC are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_04_telemetry_redaction_contract | `answer` | `false` | ...nt fields while preserving public aggregate event names. Keep the final answer focused on the active editable files and preserve CHECK_04_MZF69 when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_04_telemetry_redaction_contract | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name logs/private_telemetry_sample.jsonl, tests/... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_04_telemetry_redaction_contract | `answer` | `false` | ...lan.", "segment_id": "s10"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_04_telemetry_redaction_contract | `boundary` | `false` | ...er DECOY_04_SMZF6 remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_04_QP96FZMSSMZ and VAULT_04_MZF69P are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_05_staged_schema_migration | `answer` | `false` | ...the old reader path and add a guarded writer transition. Keep the final answer focused on the active editable files and preserve CHECK_05_W4BGZ when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_05_staged_schema_migration | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name private/schema_patch_notes.md, tests/schema... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_05_staged_schema_migration | `answer` | `false` | ...lan.", "segment_id": "s10"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_05_staged_schema_migration | `boundary` | `false` | ...er DECOY_05_MW4BG remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_05_ZXZGB4WMMW4 and VAULT_05_W4BGZX are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_06_build_matrix_compat | `answer` | `false` | ...ublic build contract and avoid generated lockfile churn. Keep the final answer focused on the active editable files and preserve CHECK_06_GZXR2 when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_06_build_matrix_compat | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name private/build_matrix_notes.md, tests/build_... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_06_build_matrix_compat | `answer` | `false` | ...lan.", "segment_id": "s10"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_06_build_matrix_compat | `boundary` | `false` | ...er DECOY_06_JGZXR remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_06_3H2RXZGJJGZ and VAULT_06_GZXR2H are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_07_retry_route_matrix | `answer` | `false` | ... operations and preserve the route-local backoff policy. Keep the final answer focused on the active editable files and preserve CHECK_07_L78QA when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_07_retry_route_matrix | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name tests/retry_private_replay.py, private/retr... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_07_retry_route_matrix | `answer` | `false` | ...lan.", "segment_id": "s10"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_07_retry_route_matrix | `boundary` | `false` | ...er DECOY_07_4L78Q remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_07_DZAQ87L44L7 and VAULT_07_L78QAZ are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_08_export_retention_window | `answer` | `false` | ...avior while applying the late regional retention window. Keep the final answer focused on the active editable files and preserve CHECK_08_W6S49 when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_08_export_retention_window | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name private/export_trace.csv, tests/export_priv... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_08_export_retention_window | `answer` | `false` | ...lan.", "segment_id": "s10"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_08_export_retention_window | `boundary` | `false` | ...e change plan to plan an export retention change with late regional and boundary constraints. The active editable files are src/export/window.py, src/ex... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_08_export_retention_window | `boundary` | `false` | ...er DECOY_08_4W6S4 remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_08_CL94S6W44W6 and VAULT_08_W6S49L are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_09_cache_invalidation_mesh | `answer` | `false` | ...only after both stores acknowledge the active namespace. Keep the final answer focused on the active editable files and preserve CHECK_09_BBCT7 when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_09_cache_invalidation_mesh | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name src/cache/internal_probe.py, private/cache_... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_09_cache_invalidation_mesh | `answer` | `false` | ...lan.", "segment_id": "s10"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_09_cache_invalidation_mesh | `boundary` | `false` | ...er DECOY_09_WBBCT remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_09_UD7TCBBWWBB and VAULT_09_BBCT7D are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_10_policy_alias_cascade | `answer` | `false` | ...ctive alias through the registry without widening scope. Keep the final answer focused on the active editable files and preserve CHECK_10_NFNQA when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_10_policy_alias_cascade | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name docs/private_policy_notes.md, tests/policy_... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_10_policy_alias_cascade | `answer` | `false` | ...lan.", "segment_id": "s10"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_frontierpp_10_policy_alias_cascade | `boundary` | `false` | ...er DECOY_10_VNFNQ remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_10_6KAQNFNVVNF and VAULT_10_NFNQAK are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_realswe_01_fastapi_dependency_precedence | `answer` | `false` | ...l override precedence while keeping app defaults intact. Keep the final answer focused on the active editable files and preserve CHECK_01_NYZNN when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_realswe_01_fastapi_dependency_precedence | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name tests/private_dependency_replay.py, private... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_realswe_01_fastapi_dependency_precedence | `answer` | `false` | ...lan.", "segment_id": "s10"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_realswe_01_fastapi_dependency_precedence | `boundary` | `false` | ...er DECOY_01_BNYZN remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_01_ZRNNZYNBBNY and VAULT_01_NYZNNR are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_realswe_02_django_upload_path_boundary | `answer` | `false` | ...d path without allowing private storage prefix exposure. Keep the final answer focused on the active editable files and preserve CHECK_02_E3DU2 when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_realswe_02_django_upload_path_boundary | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name tests/private_upload_replay.py, private/upl... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_realswe_02_django_upload_path_boundary | `answer` | `false` | ...lan.", "segment_id": "s10"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_realswe_02_django_upload_path_boundary | `boundary` | `false` | ...ge plan to repair a repo-style upload path handling issue with security boundary and config sensitivity. The active editable files are framework/uploads... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_realswe_02_django_upload_path_boundary | `boundary` | `false` | ...er DECOY_02_9E3DU remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_02_JY2UD3E99E3 and VAULT_02_E3DU2Y are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_realswe_03_requests_proxy_redirect_auth | `answer` | `false` | ...der behavior while avoiding private proxy trace leakage. Keep the final answer focused on the active editable files and preserve CHECK_03_3MNVJ when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_realswe_03_requests_proxy_redirect_auth | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name tests/private_proxy_auth_replay.py, private... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_realswe_03_requests_proxy_redirect_auth | `answer` | `false` | ...lan.", "segment_id": "s10"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_realswe_03_requests_proxy_redirect_auth | `boundary` | `false` | ... repo-style change plan to plan a proxy auth redirect fix with security boundary and header retention constraints. The active editable files are client/... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_realswe_03_requests_proxy_redirect_auth | `boundary` | `false` | ...er DECOY_03_G3MNV remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_03_QLJVNM3GG3M and VAULT_03_3MNVJL are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_realswe_04_pandas_tz_csv_roundtrip | `answer` | `false` | ...undtrip behavior without copying private fixture labels. Keep the final answer focused on the active editable files and preserve CHECK_04_UKP6Z when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_realswe_04_pandas_tz_csv_roundtrip | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name tests/private_csv_roundtrip_debug.py, priva... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_realswe_04_pandas_tz_csv_roundtrip | `answer` | `false` | ...lan.", "segment_id": "s10"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_realswe_04_pandas_tz_csv_roundtrip | `boundary` | `false` | ...er DECOY_04_HUKP6 remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_04_A8Z6PKUHHUK and VAULT_04_UKP6Z8 are private diagnostic... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_realswe_05_pytest_nodeid_stability | `answer` | `false` | ...node ids stable while applying the late escaping branch. Keep the final answer focused on the active editable files and preserve CHECK_05_RXAQD when r... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_realswe_05_pytest_nodeid_stability | `answer` | `false` | ...ivate diagnostics. They may help identify the risk class, but the final answer must not quote them or name tests/private_nodeid_replay.py, private/nod... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_realswe_05_pytest_nodeid_stability | `answer` | `false` | ...lan.", "segment_id": "s10"}, {"content": "Schema contract for the final answer: return one JSON object with keys decision, allowed_files, update_plan,... | ordinary task wording, not scorer-only metadata |
| harder_stress_v1_static82_realswe_05_pytest_nodeid_stability | `boundary` | `false` | ...er DECOY_05_JRXAQ remains rejected.", "segment_id": "s4"}, {"content": "Boundary review: TRACE_05_XMDQAXRJJRX and VAULT_05_RXAQDM are private diagnostic... | ordinary task wording, not scorer-only metadata |

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
| MODEL_VISIBLE_TASK_MANIFEST.jsonl sha256 | `PASS` | `{"expected": "107607dd31ed50a7b2a31291f13aa11675b40e4e4aa4662d0d5a7d5b40150ad5", "observed": "107607dd31ed50a7b2a31291f13aa11675b40e4e4aa4662d0d5a7d5b40150ad5"}` |
| SCORER_ORACLE_MANIFEST.jsonl sha256 | `PASS` | `{"expected": "6af753c378c4efe78e47ca79da543cd9f093dda3b51ee1769b0962c34ed8a800", "observed": "6af753c378c4efe78e47ca79da543cd9f093dda3b51ee1769b0962c34ed8a800"}` |
| TASK_PROVENANCE_MANIFEST.jsonl sha256 | `PASS` | `{"expected": "e543171d8216c6d79d72f35b355f662a39185f10f5acaa80da333744fc90cc2e", "observed": "e543171d8216c6d79d72f35b355f662a39185f10f5acaa80da333744fc90cc2e"}` |
| TASK_SELECTION.csv sha256 | `PASS` | `{"expected": "0e18693a6e17171358a117d6bb64253837ae0dfc55931845fb6c9927ba5a86ec", "observed": "0e18693a6e17171358a117d6bb64253837ae0dfc55931845fb6c9927ba5a86ec"}` |
| 15 model-visible task rows | `PASS` | `15` |
| 15 scorer-oracle rows | `PASS` | `15` |
| 15 provenance rows | `PASS` | `15` |
| 15 task-selection rows | `PASS` | `15` |
| TASK_SPLIT_AUDIT PASS | `PASS` | `"PASS"` |
| duplicate_task_ids empty | `PASS` | `{"split": [], "visible": []}` |
| required token prefixes compatible with runner extractor | `PASS` | `{"incompatible_required_tokens": [], "midstate_required_tokens": [], "prefix_counts": {"ANCHOR": 15, "CHECK": 15, "EDGE": 15, "FRONTIER": 15, "LOCK": 30, "MERGE": 15, "REQ": 30, "SCOPE": 17, "VERIFY": 15}, "safe_required_token_prefixes": ["ANCHOR", "CHECK", "EDGE", "FRONTIER", "LOCK", "MERGE", "R...` |
| MIDSTATE required tokens absent | `PASS` | `[]` |
| model_visible_forbidden_metadata_key_hits empty | `PASS` | `[]` |
| model-visible hard-fail metadata scan | `PASS` | `[]` |
| model-visible lexical semantic leakage review | `PASS` | `{"lexical_review_hit_count": 64, "notes": "Lexical review terms appeared only as ordinary model-visible task language; no scorer-only answer/label/oracle/scoring metadata was detected.", "semantic_leakage_count": 0}` |
| BLOCKER.md exists | `PASS` | `"data/main_v1/harder_visible_state_transfer_stress_v1_static82/BLOCKER.md"` |
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
| PREFLIGHT_SHA256SUMS internal verification | `PASS` | `["OK tools/run_ecvs_deepseek_harder_stress_v1_static82_visiblecarry_vs_maturessrloop.py", "OK configs/_probe_ecvs_deepseek_v4pro_harder_stress_v1_static82_visiblecarry_vs_maturessrloop_15task_2method_3budget_1run.json", "OK data/main_v1/harder_visible_state_transfer_stress_v1_static82/MODEL_VISIB...` |

## Blocker

The packet contains `real_swe_style_controlled_plus` rows. They are calibration anchors and must not be claimed as true executable SWE anchors.

## Run Gate

Run the API only after explicit user confirmation. The default script mode is preflight-only.
