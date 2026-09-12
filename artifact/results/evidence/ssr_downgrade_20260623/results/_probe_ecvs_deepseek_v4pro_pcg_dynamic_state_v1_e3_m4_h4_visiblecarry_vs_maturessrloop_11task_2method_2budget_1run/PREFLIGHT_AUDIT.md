# _probe_ecvs_deepseek_v4pro_pcg_dynamic_state_v1_e3_m4_h4_visiblecarry_vs_maturessrloop_11task_2method_2budget_1run Preflight Audit

Positioning: `calibration_only_not_primary_evidence`.

No API call was made. No API key value was read.

Overall status: `PASS_REVIEWED`
Checks passed: 16
Checks failed: 0
Expected rows: 44

## Matrix

- Tasks: 11 PCG dynamic-state v1 tasks
- Difficulty distribution: easy=3, medium=4, hard=4
- Methods: `rolling_visible_carry_forward`, `mature_ssr_loop`
- Budgets: 600, 1200
- Runs: 1
- Provider/model: DeepSeek direct `deepseek-v4-pro`

## Frozen Controls

- temperature: explicit `0`
- max_tokens: `4096`
- thinking: `thinking.type=disabled`
- top_p/top_k/min_p/top_a/penalties/stop/seed: omitted
- tools/web/fallback/cache: disabled
- retry: max attempts 2; failed attempts retained

## Checks

| check | status | detail |
|---|---:|---|
| PCG task count 11 | `PASS` | `11` |
| difficulty distribution 3/4/4 | `PASS` | `{"easy": 3, "hard": 4, "medium": 4}` |
| method list strict | `PASS` | `["rolling_visible_carry_forward", "mature_ssr_loop"]` |
| budget list strict | `PASS` | `[600, 1200]` |
| expected rows 44 | `PASS` | `44` |
| runs strict | `PASS` | `1` |
| TASK_SPLIT_AUDIT PASS | `PASS` | `"PASS"` |
| model-visible hard metadata hits empty | `PASS` | `[]` |
| result_dir no old row outputs | `PASS` | `{"conflicts": [], "status": "exists_without_row_outputs"}` |
| raw_dir absent or empty | `PASS` | `{"conflicts": [], "status": "absent"}` |
| API key value not read during preflight | `PASS` | `{"api_key_env_name": "DEEPSEEK_API_KEY", "value_read": false}` |
| max_tokens 4096 | `PASS` | `4096` |
| temperature explicit zero | `PASS` | `{"send_mode": "explicit", "value": 0}` |
| thinking disabled | `PASS` | `{"thinking": {"type": "disabled"}}` |
| sampling nuisance parameters omitted | `PASS` | `{"frequency_penalty": {"send_mode": "omitted", "value": null}, "min_p": {"send_mode": "omitted", "value": null}, "presence_penalty": {"send_mode": "omitted", "value": null}, "repetition_penalty": {"send_mode": "omitted", "value": null}, "seed": {"send_mode": "omitted", "value": null}, "stop": {"s...` |
| PREFLIGHT_SHA256SUMS internal verification | `PASS` | `["OK tools/run_ecvs_deepseek_pcg_dynamic_state_v1_visiblecarry_vs_maturessrloop.py", "OK docs/pcg_dynamic_state/GENERATOR_SPEC.md", "OK <AUTHOR_LOCAL_WORKSPACE>/stateful-reasoning-benchmark-release/docs/protocol/fresh_main_matrix_v2/LATEST_EXPERIMENT_VARIABLE_REQUIREMENTS_ROLLING_VISIBLE_CARRY_FORWARD_...` |
