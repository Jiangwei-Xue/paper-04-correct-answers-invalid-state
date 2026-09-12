# PreMatrix Variable Control Report

## Summary

Variable control status is `RERUN_REQUIRED`. The registry is useful and detailed, but it is explicitly a forward standard. It does not certify current rows for main matrix entry.

## Intended Matrix Axes

Historical intended matrix: 5 models x 50 tasks x 4 methods x 3 budgets x 5 runs. Primary axes include method and state budget, with model/provider and task as blocking factors.

## Controlled For Preflight Only

- OpenRouter provider path and base URL.
- Provider pinning via `provider.order`.
- `allow_fallbacks=false` and `require_parameters=true`.
- `max_tokens=4096` and omitted temperature send mode.
- Selected provider/model metadata in preflight `scores.csv`.

## Uncontrolled Or Missing For Main Matrix

- Final five-model list.
- Fresh admission protocol and configs.
- Fresh task manifest and pre-result manifest hash.
- Row-level config/task/runner/scorer/oracle/prompt hashes.
- Fresh endpoint inventory for actual admission window.
- Single authoritative retry policy; configs include top-level `max_retries=1` and model-level `max_retries=3`.
- Complete raw body accountability for public candidate.

## Run Classes

| Class | Decision |
|---|---|
| OpenRouter GPT preflight | SAFE_ONLY_AS_PILOT |
| OpenRouter Claude preflight | SAFE_ONLY_AS_PILOT; task failed |
| Local Qwen32B derived tables | RERUN_REQUIRED |
| Local backend-recovery slice | EXCLUDE |
| Legacy 30-task public CSVs | SAFE_ONLY_AS_PILOT |
| Current candidate as main matrix | RERUN_REQUIRED / NO_GO as-is |
