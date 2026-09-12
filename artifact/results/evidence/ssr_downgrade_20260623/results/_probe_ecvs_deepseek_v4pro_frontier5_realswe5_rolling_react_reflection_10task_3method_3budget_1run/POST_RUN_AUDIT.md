# _probe_ecvs_deepseek_v4pro_frontier5_realswe5_rolling_react_reflection_10task_3method_3budget_1run Post-Run Audit

Positioning: calibration only; not primary evidence.

Rows expected: 90
Rows observed: 90
Clean rows: 84
Excluded rows: 0
Rerun-required rows: 6

Controls:

- Provider: `deepseek` direct endpoint `https://api.deepseek.com`.
- Model: `deepseek-v4-pro`.
- Fallback: disabled.
- Temperature: explicit 0.
- max_tokens: 4096.
- top_p/top_k/min_p/top_a/penalties/stop/seed: omitted.
- stream: false.
- thinking control: `thinking.type=disabled`.
- tools/web: disabled.
- Prompt/oracle split: model-visible manifest is used for prompts; scorer oracle manifest is used only for scoring.

Gate policy:

- backend error -> rerun_required
- positive reasoning tokens -> excluded
- returned reasoning content -> excluded
- parse/exact-token failure without control violation remains a measured outcome

## Rerun-Required Reason Counts

- `backend_error`: 6

