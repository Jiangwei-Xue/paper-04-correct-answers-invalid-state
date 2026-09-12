# _probe_ecvs_deepseek_v4pro_frontier5_realswe5_mature_ssr_10task_2method_3budget_1run Post-Run Audit

Positioning: calibration only; not primary evidence.

Rows expected: 60
Rows observed: 60
Clean rows: 57
Excluded rows: 0
Rerun-required rows: 3

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
- SSR method protocol: `mature_ssr_protocol_v1_ecvs_safe_visible_only` with deterministic field parsing, OUT-priority carry-forward, and budget fitting.

Gate policy:

- backend error -> rerun_required
- positive reasoning tokens -> excluded
- returned reasoning content -> excluded
- parse/exact-token failure without control violation remains a measured outcome

## Rerun-Required Reason Counts

- `backend_error`: 3

