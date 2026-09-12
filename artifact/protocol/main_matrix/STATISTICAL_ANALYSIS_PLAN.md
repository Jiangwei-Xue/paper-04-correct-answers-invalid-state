# Statistical Analysis Plan

Status: pre-primary-execution analysis protocol

Scope: PCG dynamic-state v2 confirmatory main matrix

This document specifies the statistical analysis plan for the PCG dynamic-state
v2 confirmatory main matrix. It does not redefine experiment variables, method
semantics, model admission rules, request policy, or budget disposition. Those
are controlled by the corresponding hash-locked protocol files.

If this document conflicts with the hash-locked matrix definition,
method-condition protocol, API policy, budget-disposition document,
model-axis disposition, or preregistered decision rules, the corresponding
hash-locked source file controls.

This SAP must be frozen and hash-registered before any primary record-mode rows
are executed. Any change after primary execution is a post-run amendment and
must not alter the primary estimand, contrast hierarchy, failure-coding rule, or
diagnostic-exclusion rule for confirmatory claims.

## Analysis Scope

The primary confirmatory analysis applies only to the frozen PCG dynamic-state
v2 main matrix:

```text
40 tasks x admitted model conditions x 6 methods x 2 confirmatory budgets x 3 runs
```

The confirmatory budgets are `600` and `1200`.

The following rows are excluded from the primary analysis population:

- admission smoke rows;
- provider refresh rows;
- historical calibration rows;
- legacy or old-repo packets;
- static sanity rows;
- targeted backfills;
- sentinel drift probes;
- budget-300 diagnostic rows;
- routed-provider rows without frozen route equivalence;
- rows with audited protocol-level violations.

Budget `300` is diagnostic only and is analyzed separately for floor effects,
truncation behavior, hard-cap behavior, and carry-failure patterns.

## Analysis Population

Let the primary analysis set be:

```text
D_primary = {
  (t, m, k, b, r):
    t in T,
    m in M,
    k in K6,
    b in {600, 1200},
    r in {1, 2, 3}
}
```

where `|T| = 40`, `|K6| = 6`, `|B| = 2`, and `|R| = 3`.

The model set `M` is the set of model conditions admitted before full
record-mode execution. If `openrouter_claude48` does not clear the admission
smoke gate, the model axis must be formally revised before primary execution.
It must not be removed or reinterpreted post hoc after seeing outcome data.

Model condition is treated as a fixed blocking factor. The analysis scope is
the tested model conditions, not a random population of all frontier models.

## Row-Level Outcomes

For each row, define:

```text
A_tmkbr = 1(answer_success)
G_tmkbr = 1(state_governance_success)
R_tmkbr = A_tmkbr * G_tmkbr
        = 1(reliable_composite_success)
```

The primary endpoint is `R`, reliable co-success.

`answer_success` and `state_governance_success` are paired decomposition
metrics. Standalone governance is diagnostic only. Legacy no-conflict-only
governance is appendix diagnostic only and is not used as a primary endpoint.

## Failure Coding And Protocol Exclusions

Execution and parsing failures are row outcomes, not complete-case exclusions.

The following are scored as failure-as-zero in the primary analysis:

- invalid JSON;
- parser failure;
- backend failure after the allowed retry policy;
- timeout;
- provider error;
- unverifiable final answer;
- unverifiable carried state.

If a row cannot be verified as successful, then:

```text
A_tmkbr = 0
G_tmkbr = 0
R_tmkbr = 0
```

Protocol-level violations are not treated as ordinary model failures. They are
excluded only after audit logging with row id, reason, affected hash linkage,
and exclusion status. Examples include:

- wrong returned model;
- provider fallback enabled or observed;
- tools or web enabled;
- oracle leakage into model-visible content;
- wrong method implementation;
- wrong budget;
- wrong prompt template;
- hash linkage broken;
- missing raw output for a claimed row;
- row generated outside the frozen run policy.

No row may be excluded because the answer is wrong, the score is low, the JSON
is unattractive, or the carried state is inconvenient to interpret.

## Design-Based Cell Summaries

For `q in {R, A, G}`, let `Y^(q)_tmkbr` denote the corresponding row-level
binary outcome. The method x model x budget cell mean is:

```text
p_hat^(q)_kmb =
  1 / (|T| * |R|)
  * sum_{t in T} sum_{r in R} Y^(q)_tmkbr
```

Method-level summaries are equal-weighted over frozen model x budget cells:

```text
p_hat^(q)_k =
  1 / (|M| * |B|)
  * sum_{m in M} sum_{b in {600, 1200}} p_hat^(q)_kmb
```

Averages are not weighted by provider success rate, post-hoc row availability,
failure-free subsets, or model-specific row counts.

All main result tables report the following side by side:

- `answer_success`;
- `state_governance_success`;
- `reliable_composite_success`.

`reliable_success` may appear only as a backward-compatible alias of
`reliable_composite_success`.

## Primary Estimand

Primary confirmatory inference is design-based.

For a preregistered contrast `c = (k1, k0)`, define the task-level paired
difference:

```text
d_t^(q)(k1, k0) =
  1 / (|M| * |B| * |R|)
  * sum_{m in M} sum_{b in {600, 1200}} sum_{r in R}
      [Y^(q)_tmk1br - Y^(q)_tmk0br]
```

The paired risk-difference estimand is:

```text
tau_hat^(q)(k1, k0) =
  1 / |T| * sum_{t in T} d_t^(q)(k1, k0)
```

The primary endpoint for confirmatory contrasts is `q = R`. The decomposition
endpoints `q = A` and `q = G` are reported to explain the source of reliable
co-success gains or failures.

## Task-Cluster Bootstrap

The primary uncertainty unit is the task.

Confidence intervals for paired risk differences are computed by task-cluster
bootstrap. Each bootstrap replicate samples 40 task ids with replacement. For
each sampled task, all associated model, budget, run, and method rows are
retained together.

For bootstrap replicate `s`:

```text
T_star_s = {t*_1, ..., t*_40}

tau_hat_star^(s,q)(k1, k0) =
  1 / 40 * sum_{t in T_star_s} d_t^(q)(k1, k0)
```

The primary 95% confidence interval is the percentile interval:

```text
[Q_0.025(tau_hat_star^(s,q)), Q_0.975(tau_hat_star^(s,q))]
```

The planned number of bootstrap replicates is `10,000`.

Rows are not resampled independently because independent row resampling would
break the paired task x model x budget x run design.

## Confirmatory Contrast Hierarchy

### Primary Contrast: Crux Comparison

The primary contrast is:

```text
rolling_visible_carry_forward - ssr_no_visible_carry
```

This compares carry without schema against schema without deterministic visible
carry.

Formally:

```text
tau_hat_crux^(q) =
  tau_hat^(q)(rolling_visible_carry_forward, ssr_no_visible_carry)
```

The primary endpoint is `q = R`. The answer-axis version `q = A` is reported as
a power-bearing decomposition. The governance-axis version `q = G` is reported
as decomposition only.

### Key Secondary Contrast: Schema Added On Top Of Carry

The key secondary contrast is:

```text
mature_ssr_loop - rolling_visible_carry_forward
```

Formally:

```text
tau_hat_schema_given_carry^(q) =
  tau_hat^(q)(mature_ssr_loop, rolling_visible_carry_forward)
```

This contrast tests whether typed SSR schema adds value after deterministic
visible carry is already present.

### Secondary Mechanism Contrasts

The 2-by-2 mechanism analysis is restricted to the four core methods:

- `rolling_summary`;
- `rolling_visible_carry_forward`;
- `ssr_no_visible_carry`;
- `mature_ssr_loop`.

Let:

```text
p00^(q) = p^(q)(rolling_summary)
p10^(q) = p^(q)(rolling_visible_carry_forward)
p01^(q) = p^(q)(ssr_no_visible_carry)
p11^(q) = p^(q)(mature_ssr_loop)
```

where the first index denotes deterministic visible carry and the second index
denotes schema.

The risk-difference-scale carry effect is:

```text
Delta_carry^(q) =
  1/2 * [(p10^(q) - p00^(q)) + (p11^(q) - p01^(q))]
```

The risk-difference-scale schema effect is:

```text
Delta_schema^(q) =
  1/2 * [(p01^(q) - p00^(q)) + (p11^(q) - p10^(q))]
```

The interaction is:

```text
Delta_interaction^(q) =
  p11^(q) - p01^(q) - p10^(q) + p00^(q)
```

`loop_only` and `rolling_visible_fields_only` are excluded from factorial
mechanism coefficient estimation. They are reported as reference/control arms
only.

## Multiple-Comparison Policy

The primary confirmatory contrast family contains only the crux contrast on
`R`. The `schema_given_carry` contrast is key secondary and is reported with
its confidence interval and label.

The secondary mechanism family consists of:

- carry main effect;
- schema main effect;
- carry-by-schema interaction.

These are reported as mechanism decomposition. If formal p-values are reported
for the secondary mechanism family, they are adjusted separately from the
primary contrast using Holm or FDR. Confidence intervals remain the primary
reporting surface.

Model-specific, task-family-specific, pressure-profile, provider-route, and
budget-moderation analyses are exploratory.

## Co-Success Alignment Gap

To quantify answer-governance non-overlap, define:

```text
Gap_kmb = min(p_hat^(A)_kmb, p_hat^(G)_kmb) - p_hat^(R)_kmb
```

Method-level alignment gap is:

```text
Gap_k =
  1 / (|M| * |B|) * sum_{m in M} sum_{b in B} Gap_kmb
```

Interpretation:

```text
min(p_A, p_G) is the maximum possible reliable co-success if answer success
and governance success occurred on the same rows. The gap measures how much
reliable co-success is lost because answer success and governance success do
not align row-wise.
```

The alignment gap is a secondary measurement estimand, not a method-ranking
criterion.

## Budget-300 Diagnostic Analysis

Budget `300` is excluded from:

- primary paired risk differences;
- confirmatory task-cluster bootstrap confidence intervals;
- method ranking;
- overall method averages;
- confirmatory mixed-effects models;
- 2-by-2 confirmatory mechanism effects;
- primary claim tables.

Budget `300` is analyzed descriptively only. Diagnostic summaries may include:

- `answer_success`;
- `state_governance_success`;
- `reliable_composite_success`;
- `state_hard_cap_used`;
- truncation indicators;
- carry-failure patterns;
- parser/provider failure rates.

For each diagnostic method and model:

```text
p_hat^(q,300)_km =
  1 / |T| * sum_{t in T} Y^(q)_tmk,300,1
```

Budget-300 results must be labeled diagnostic and must not be pooled with
confirmatory 600/1200 rows.

## Model-Assisted Sensitivity Analysis

Logistic mixed-effects models are model-assisted sensitivity analyses. They do
not replace the design-based paired risk-difference estimands.

For adjusted six-method summaries:

```text
Y^(q)_tmkbr ~ Bernoulli(p^(q)_tmkbr)

logit(p^(q)_tmkbr) =
  alpha^(q)_kmb + u^(q)_t + rho^(q)_r

u^(q)_t ~ Normal(0, sigma^2_(q,task))
```

Here:

```text
alpha_kmb = saturated method x model x budget fixed cell
u_t       = task random intercept
rho_r     = run fixed block effect
```

For 2-by-2 model-assisted mechanism analysis:

```text
logit(p^(q)_tmkbr) =
  beta_0^(q)
  + beta_C^(q) C_k
  + beta_S^(q) S_k
  + beta_CS^(q) C_k S_k
  + lambda_m^(q)
  + eta_b^(q)
  + u_t^(q)
  + rho_r^(q)
```

where `C_k` denotes deterministic visible carry and `S_k` denotes SSR schema.

If a GLMM fails to converge, has a singular fit, or exhibits complete or
quasi-complete separation, the failure is reported. Such failure does not
affect the primary design-based estimates. Penalized or weakly regularized
logistic models may be reported only as additional sensitivity analyses.

## Exploratory Heterogeneity Analyses

Task-family, pressure-profile, model-specific, and budget-moderation analyses
are exploratory unless separately preregistered before primary execution.

Pressure-profile dimensions include:

- boundary;
- decoy;
- retention;
- suppression;
- update.

Exploratory moderation may be estimated at the task level:

```text
d_t^(q)(k1, k0) = gamma_0 + gamma_j z_tj + epsilon_t
```

Each pressure dimension is analyzed separately. These analyses do not alter the
primary contrast hierarchy or method disposition.

Budget moderation may be summarized as:

```text
Delta_budget^(q) =
  tau_hat_1200^(q)(k1, k0) - tau_hat_600^(q)(k1, k0)
```

Budget moderation is a stability/scope check, not a primary treatment claim.

## Reporting Hierarchy

| Layer | Role | Status |
| --- | --- | --- |
| Six-method cell summaries | Main descriptive table | Primary reporting |
| Paired risk differences | Main method contrasts | Primary inference |
| Task-cluster bootstrap | Primary confidence interval | Primary inference |
| Crux contrast | Primary mechanism contrast | Confirmatory |
| Schema-given-carry contrast | SSR disposition contrast | Key secondary |
| 2-by-2 carry/schema decomposition | Mechanism attribution | Secondary |
| Co-success alignment gap | Answer-governance non-overlap | Secondary measurement |
| GLMM | Adjusted/model-assisted check | Sensitivity |
| Budget 300 | Floor/truncation/carry failure | Diagnostic only |
| Pressure profiles | Scope/heterogeneity | Exploratory |

## Integration With Artifact And Freeze Chain

This SAP must be added to the reviewer-facing protocol map before primary
execution. At minimum, the following surfaces should reference it:

- `README.md`;
- `artifact/protocol/main_matrix/EXPERIMENT_VARIABLE_CONTROL_OVERVIEW.md`;
- `artifact/protocol/main_matrix/README.md`;
- `docs/CLAIM_TO_ARTIFACT_MAP.md`;
- `artifact/BENCHMARK_CARD.md`.

The SAP file hash must be included in the freeze/hash manifest before
record-mode execution. Any change to the SAP after primary execution must be
reported as a post-run amendment and must not alter the primary estimand,
contrast hierarchy, failure-coding rule, or diagnostic-exclusion rule.

