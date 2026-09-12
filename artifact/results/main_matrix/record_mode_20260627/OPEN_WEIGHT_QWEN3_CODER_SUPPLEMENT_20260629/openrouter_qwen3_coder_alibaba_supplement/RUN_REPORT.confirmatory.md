# Qwen3-Coder Open-Weight Supplement - confirmatory

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
| expected rows | 1440 |
| score rows | 1440 |
| preexisting rows reused | 0 |
| new rows recorded now | 1440 |
| backend_error | 0 (0.0%) |
| final_json_parse_success | 1439 (99.9%) |
| parse_and_score_success | 1439 (99.9%) |
| answer_success | 280 (19.4%) |
| final_exact_success | 280 (19.4%) |
| state_governance_success | 298 (20.7%) |
| reliable_composite_success | 113 (7.8%) |
| returned_model_match | 1440 (100.0%) |
| reasoning_content_present | 0 (0.0%) |
| nonzero_reasoning_tokens | 0 (0.0%) |
| hard_failure | 0 (0.0%) |
| api_calls_performed | 8760 |

HTTP status distribution: `{"200": 1440}`

Finish reason distribution: `{"stop": 1440}`

Reasoning tokens observed distribution: `{"0": 1440}`
