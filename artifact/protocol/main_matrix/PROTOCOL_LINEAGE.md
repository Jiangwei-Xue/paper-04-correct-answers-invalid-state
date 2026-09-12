# Protocol Lineage

This file records the main-matrix design lineage so reviewers can distinguish
method development from outcome-driven selection.

## Historical Planning State

Earlier planning notes referred to larger or different row counts, including a
15,000-row-style matrix. Those references are historical planning language and
are not the current primary matrix definition.

## Fresh v2 Planning State

A later Fresh v2 planning state used a 50-task, 5-method, 3-budget, 3-repeat,
4-model-style design, yielding 9,000 planned rows. That state was a pre-run
design candidate, not a completed primary evidence table.

## PCG v2 Transition

The current substrate moved to PCG dynamic-state v2. This changed the task set
and protocol target. The move from 50 tasks to 40 tasks should be described as
a substrate/protocol transition, not as dropping failed rows from a completed
matrix.

The resulting 40-task set is the frozen controlled substrate after protocol
calibration. It should not be described as a completely untouched held-out test
set. Pilot rows, calibration checks, provider-admission rows, and any tiny smoke
rows remain outside primary aggregation.

## Current Freeze

The current confirmatory main matrix is:

```text
40 tasks x 5 models x 6 methods x 2 budgets x 3 runs = 7,200 rows
```

It uses `600` and `1200` as the confirmatory budget levels. Budget `300` is
retained only as a preregistered low-budget diagnostic probe:

```text
40 tasks x 5 models x 4 core methods x 1 budget x 1 run = 800 rows
```

The sixth method is retained to preserve a diagnostic SSR condition after the
2026-06-23 downgrade evidence. A brief PCG v2 candidate plan kept all three
budgets in the confirmatory matrix, yielding 10,800 planned rows, but the later
budget-disposition decision moved `300` out of confirmatory inference because
pilot evidence showed floor and truncation effects in that regime.

The supporting summary is `artifact/results/evidence/budget_300_diagnostic_20260625/`.
In the released random10 pilot rows, the state hard-cap rate is `154/180` at
budget `300`, `72/180` at budget `600`, and `18/180` at budget `1200`.  For
`rolling_visible_carry_forward`, answer success is `4/30` at `300`, compared
with `22/30` at `600` and `20/30` at `1200`.

## V2 Direct-Network Execution State

The matrix shape remains `7,200` confirmatory rows. The execution environment
changed after v1 record-mode logs showed proxy/transport-like backend evidence
that had not been exposed during admission smoke checks. Because proxy-mediated
execution was not preregistered as a controlled variable in v1, the final
primary execution plan is now all-model v2 direct-network from row zero:

```text
artifact/protocol/main_matrix/V2_DIRECT_NETWORK_EXECUTION_PROTOCOL_20260628.md
```

The v1 outputs remain append-only audit evidence and may be used to explain the
execution transition. They are not pooled with v2 direct-network rows in the
primary result table.

## Reporting Rule

Report protocol transitions that affect the research question, task substrate,
primary methods, or final row count. Do not report every local scratch plan,
failed command, or draft-only count unless it changed what reviewers need to
interpret the released primary matrix.
