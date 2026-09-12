# Results

`results/metric_v2/` retains the normalized row inputs, production/reference score outputs, and V2 audit surfaces used to establish the scorer transition.

`results/metric_v3/` retains six V3 evidence tiers:

- `primary`: 7,200 claim-bearing rows;
- `primary_budget300`: 800 diagnostic rows;
- `qwen`: 1,440 supplement rows;
- `qwen_budget300`: 160 diagnostic supplement rows;
- `deepseek_sanity`: 40 saved sanity rows;
- `deterministic_validity_suite`: 36,000 local control rows.

Within each metric version:

- `raw_inputs/` or `inputs/` contains normalized scorer inputs derived from released evidence;
- `scores_v2/` or `scores_v3/` contains deterministic row-level scores;
- `executor/` contains the separately implemented next-step execution rows;
- `oracles_*` contains frozen, task-derived evaluation material.

Aggregate reports are under `reports/metric_v2/` and `reports/metric_v3/`. Frozen legacy submission tables are under `paper/submission_tables/tables/`. The one-command replay regenerates temporary outputs and compares them with these references; it does not overwrite the released files.

