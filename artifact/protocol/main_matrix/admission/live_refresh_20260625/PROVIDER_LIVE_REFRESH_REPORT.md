# Provider Live Refresh Report

Created: `2026-06-25T10:54:49Z`

This is an admission-only live refresh. It uses a non-benchmark prompt
and does not populate primary main-matrix results.

## Results

| condition | provider | route | status | http | returned model | content OK | reasoning tokens | reasoning payload | generation metadata |
| --- | --- | --- | --- | ---: | --- | --- | ---: | --- | --- |
| openrouter_gpt55 | openrouter | OpenRouter | pass | 200 | openai/gpt-5.5-20260423 | True | 0 | False | unavailable_error |
| openrouter_claude48 | openrouter | OpenRouter | pass | 200 | anthropic/claude-4.8-opus-20260528 | True | 0 | False | unavailable_error |
| deepseek_v4pro | deepseek | direct | pass | 200 | deepseek-v4-pro | True | None | False | not_applicable |
| kimi_k26 | moonshot | direct | pass | 200 | kimi-k2.6 | True | None | False | not_applicable |
| qwen37max | dashscope | direct | pass | 200 | qwen3.7-max | True | None | False | not_applicable |

OpenRouter `/generation` error bodies are retained only in redacted form,
and reviewer-visible hashes now track the redacted payloads instead of provider-issued IDs.

## VCR Adapter Source

- Source JSONL: `artifact/protocol/main_matrix/admission/live_refresh_20260625/provider_adapter_record_source.jsonl`
- Rows available for record mode: `5`
- Smoke config: `artifact/protocol/main_matrix/admission/live_refresh_20260625/provider_live_refresh_smoke_config.json`

Replay/record closure is checked separately by `main_matrix_vcr_runner.py`.
