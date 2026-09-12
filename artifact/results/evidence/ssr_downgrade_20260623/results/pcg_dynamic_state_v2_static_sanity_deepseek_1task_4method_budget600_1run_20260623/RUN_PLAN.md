# Canonical PCG v2 Static Sanity Gate Run Plan

Experiment: `pcg_dynamic_state_v2_static_sanity_deepseek_1task_4method_budget600_1run_20260623`

Status: static sanity gate only. Not main-matrix evidence and not pooled.

Rows:

```text
1 frozen static-control task
x 1 model: direct DeepSeek `deepseek-v4-pro`
x 4 methods
x 1 state budget: 600
x 1 run
= 4 rows
```

Methods:

```text
rolling_visible_carry_forward
rolling_visible_fields_only
ssr_no_visible_carry
mature_ssr_loop
```

Controls:

- Provider: `deepseek`, direct provider route
- Requested model: `deepseek-v4-pro`
- Temperature: explicit `0`
- Max tokens: `4096`
- Thinking: `{"type":"disabled"}`
- Tools/web/cache: disabled or not requested
- Fallback: false
- Concurrency: `1`
- API key: read only at runtime from `DEEPSEEK_API_KEY`; value is never printed or written
- Scorer: `tools/pcg_dynamic_state_v2/score_pcg_dynamic_state_v2_main_matrix.py`

Pass rule:

`mature_ssr_loop` must have `answer_success=True` and
`reliable_composite_success=True` with no forbidden/protected/revoked/stale or
blocked-path leakage.

Preflight checks:

- selected task rows = 1: PASS
- oracle rows = 1: PASS
- task id frozen: PASS
- method list = static sanity 4 arms: PASS
- state budget = 600: PASS
- runs = 1: PASS
- expected rows = 4: PASS
- provider direct deepseek: PASS
- temperature explicit 0: PASS
- thinking disabled: PASS
- tools/web disabled: PASS
- task split audit PASS: PASS
- no prior row output files in result dir: PASS
- raw output dir absent or empty: PASS
- variable control doc exists: PASS
- method protocol doc exists: PASS
- static sanity gate doc exists: PASS
- strict scorer exists: PASS

Command:

```bash
python3 tools/run_deepseek_pcg_dynamic_state_v2_static_sanity_20260623.py --run-api --max-workers 1
```
