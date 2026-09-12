# _probe_ecvs_deepseek_v4pro_frontier5_realswe5_rolling_visible_carry_forward_baseline_10task_1method_3budget_1run Post-Run Audit

Positioning: calibration only; not primary evidence.

Rows expected: 30
Rows observed: 30
Clean rows: 30
Excluded rows: 0
Rerun-required rows: 0

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
- Baseline protocol: `rolling_visible_identifier_carry_forward_v1_ecvs_safe_visible_only` with deterministic model-visible identifier carry-forward and budget fitting.

Gate policy:

- backend error -> rerun_required
- positive reasoning tokens -> excluded
- returned reasoning content -> excluded
- parse/exact-token failure without control violation remains a measured outcome

