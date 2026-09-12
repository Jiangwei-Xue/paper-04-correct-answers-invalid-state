# Qwen3-Coder Open-Weight Supplement - budget300_diagnostic

Date: 20260629

Scope: open-weight supplement, not a sixth primary model condition.
These counts are supplement QC/result metadata only and are not pooled into the primary five-model tables.

## Controls

- Requested model: `qwen/qwen3-coder`
- Expected returned model: `qwen/qwen3-coder-480b-a35b-07-25`
- Provider: `Alibaba`
- Provider order: `['alibaba']`
- Provider tag: `alibaba/opensource`
- Quantization: `unknown`
- Fallback: disabled
- require_parameters: true
- temperature: `0`
- top_p: `1`
- top_k: not sent
- max_tokens: `4096`
- network execution: `direct_no_system_proxy`
- reasoning: not exposed, not requested
- tools/function calling/web/retrieval/agent mode: not requested
- structured output forcing: not requested

## Summary

| field | value |
| --- | ---: |
| expected rows | 160 |
| score rows | 160 |
| preexisting rows reused | 0 |
| new rows recorded now | 160 |
| backend_error | 0 (0.0%) |
| final_json_parse_success | 160 (100.0%) |
| parse_and_score_success | 160 (100.0%) |
| answer_success | 22 (13.8%) |
| final_exact_success | 22 (13.8%) |
| state_governance_success | 40 (25.0%) |
| reliable_composite_success | 7 (4.4%) |
| returned_model_match | 160 (100.0%) |
| reasoning_content_present | 0 (0.0%) |
| nonzero_reasoning_tokens | 0 (0.0%) |
| hard_failure | 0 (0.0%) |
| api_calls_performed | 960 |

HTTP status distribution: `{"200": 160}`

Finish reason distribution: `{"stop": 160}`

Reasoning tokens observed distribution: `{"0": 160}`
