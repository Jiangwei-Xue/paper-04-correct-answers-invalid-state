# OpenRouter Normalization Report

## Summary

OpenRouter status is `HOLD / OR_RERUN_REQUIRED`. The current GPT-5.5 and Claude 4.8 rows are usable as provider-pinned preflight metadata only.

## Entry Boundary

First public successful access evidence appears in the GPT and Claude access audits from 2026-06-16. First public runner rows are one-row preflights on 2026-06-17.

## Controls Present For Preflight

- `provider=openrouter`.
- `base_url=https://openrouter.ai/api/v1`.
- Provider order pinned to `OpenAI` or `Anthropic`.
- `allow_fallbacks=false`.
- `require_parameters=true`.
- OpenRouter metadata header enabled.
- Selected provider/model, generation IDs, timestamps, and raw response hashes in `scores.csv`.

## Open Issues

- Endpoint inventory must be refreshed for the actual admission window.
- GPT/Claude rows are one-task preflights, not admission/main-matrix rows.
- Configs have retry ambiguity: top-level `max_retries=1`, model-level `max_retries=3`.
- Temperature is omitted in request mode but config also carries `temperature=0`; freeze semantics explicitly.
- Route reproducibility is partial because OpenRouter aliases can expose multiple providers over time.
- Current config hashes do not match old public release manifest entries.

## Classification

| Run | Classification | Matrix status |
|---|---|---|
| `openrouter_gpt55_runner_preflight_1task_1method_1budget_1run` | OR_SAFE_WITH_METADATA | pilot only |
| `openrouter_claude48_runner_preflight_1task_1method_1budget_1run` | OR_SAFE_WITH_METADATA for route; task failed | pilot only |
| future admission | OR_RERUN_REQUIRED | blocked until fresh freeze |
