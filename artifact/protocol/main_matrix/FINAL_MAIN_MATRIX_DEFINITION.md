# Final Main Matrix Definition

The current confirmatory primary matrix is:

```text
40 tasks x 5 models x 6 methods x 2 budgets x 3 runs = 7,200 rows
```

The confirmatory budget levels are `600` and `1200`.

A separate preregistered low-budget diagnostic probe is retained for the
`300`-character regime:

```text
40 tasks x 5 models x 4 core methods x 1 budget x 1 run = 800 rows
```

The diagnostic probe uses only the 2-by-2 core methods:
`rolling_summary`, `ssr_no_visible_carry`,
`rolling_visible_carry_forward`, and `mature_ssr_loop`.

## Axes

Tasks:

- 40 PCG dynamic-state v2 tasks.

Models:

- 5 closed-model endpoints, fixed before the main run.
- Candidate endpoints that were discussed but not admitted into this fixed
  axis are handled in `MODEL_AXIS_DISPOSITION.md`.

Methods:

- 6 method conditions:
  `loop_only`, `rolling_summary`, `rolling_visible_carry_forward`,
  `rolling_visible_fields_only`, `ssr_no_visible_carry`, and
  `mature_ssr_loop`.

Budgets:

- 2 confirmatory token or context-budget levels: `600` and `1200`.
- `300` is excluded from the confirmatory budget axis and is retained only as
  the separate low-budget diagnostic probe.

Runs:

- 3 independent repeats per cell.

## Primary Row Definition

One confirmatory primary row is one task, one model, one method condition, one
confirmatory budget level, and one repeat. Each row should include:

- task id and task-manifest hash;
- model/provider route metadata available at request time;
- method condition id;
- prompt/config hashes;
- request payload hash;
- raw response hash;
- parsed score record hash;
- verifier/scorer version hash;
- row-level H5 packet hash.

## Outcome Discipline

The primary metric is `reliable_composite_success`, defined as
`answer_success AND state_governance_success`. The two component metrics are
reported together as decomposition signals. Standalone `state_governance_success`
is diagnostic only: because no-conflict-only governance can be inflated by empty
or non-bearing carried state, it must not be used for primary method ranking or
as evidence of successful governance when answer recovery fails.

The main empirical target is reliable co-success: whether answer success and
strict state-governance success occur on the same row. Marginal answer success
or marginal governance success must not be reported as a substitute for the
composite.

## Scope Boundary

Admission probes, historical probes, backfills, static sanity checks, and
sentinel drift probes are not primary rows unless explicitly included in this
matrix definition before execution. The `300`-budget diagnostic probe is also
not a primary row set: it is reported descriptively for floor-effect,
truncation, and carry-failure analysis, and is excluded from confirmatory
mixed-effects models, method ranking, and overall method averages. The current
SSR downgrade packet is an evidence packet and does not populate this matrix.
