# RAI, Ethics, and Limitations

This document records the responsible-use boundary for the PCG dynamic-state v2
benchmark artifact. It is a reviewer-facing companion to the benchmark card and
Croissant metadata.

## Data Sensitivity

The benchmark does not use human-subject data, personal records, private
documents, demographic labels, medical records, financial records, or scraped
social-media data.

The task data are synthetic benchmark tasks with separated model-visible task
surfaces and scorer-only oracle fields. Provider outputs are model-generated
responses to those synthetic tasks.

## Intended Use

Use this artifact to:

- auditing reliable co-success under bounded state transfer;
- separating exact-answer success from governed state success;
- checking whether answer success and strict governance success co-occur in
  the same row;
- verifying saved-output evidence, hash locks, scorer behavior, and replay
  cassettes without API keys.

Do not use it to:

- ranking general model quality;
- claiming broad model safety;
- evaluating human preference or open-ended helpfulness;
- training or fine-tuning models;
- proving that current live APIs reproduce historical saved outputs;
- claiming that SSR-style methods universally fail.

## Main Responsible-AI Risks

### Evaluation Claim Overreach

The main risk is overinterpreting a bounded evaluation as a general model
ranking. The benchmark measures reliable co-success in a specific task family,
with fixed methods, budgets, prompts, scorer rules, and provider routes.

The paper and artifact keep the language narrow. The primary claim is a
measurement claim about reliable co-success and answer-governance non-overlap
under the tested conditions.

### Closed-Model Drift

Closed-model providers can change model weights, routing, decoding behavior,
and server-side defaults. A later live rerun may not reproduce the original
outputs.

The reproducibility target is saved-output replay. Replay verifies recorded
model outputs and their scores; it does not claim live API
bit-reproducibility.

### Provider Routing And OpenRouter

OpenRouter is used as the fixed access path for GPT and Claude model
conditions. This creates routing and metadata risks if provider fallback,
returned-model mismatch, or hidden reasoning payloads appear.

The control surface is frozen in the artifact: fallback is disabled, returned
model strings must match the expected strings, tools and web access are
disabled, `reasoning.effort` is `none`, response metadata are hashed, and
replay must close without cache misses.

Read the provider data-governance table below as an audit record, not as a new
legal claim:

| model condition | route | data-use evidence status |
| --- | --- | --- |
| `openrouter_gpt55` | OpenRouter to OpenAI | route and request controls recorded; provider data-use terms are external to this artifact |
| `openrouter_claude48` | OpenRouter to Anthropic | route and request controls recorded; admission smoke passed |
| `deepseek_v4pro` | direct DeepSeek-compatible endpoint | direct-provider route recorded; public/provider policy may change |
| `kimi_k26` | direct Moonshot-compatible endpoint | direct-provider route recorded; Kimi K2.7 Code excluded because reasoning could not be disabled under official docs |
| `qwen37max` | direct DashScope-compatible endpoint | direct-provider route recorded; public/provider policy may change |

If the submission needs a no-training or data-processing guarantee, that claim
must come from provider terms or a contract. The artifact itself records the
request route and replay evidence; it does not certify provider-side retention
or training behavior.

### Benchmark Overfitting And Contamination

The 40-task substrate is a controlled benchmark after protocol calibration. It
should not be described as a completely untouched public held-out test set.

The artifact addresses this by separating model-visible task content from
scorer-only oracles, hash-locking the split, and describing the substrate as
calibration-conditioned rather than untouched.

### Diagnostic Rows Entering Primary Claims

Admission rows, provider live-refresh rows, budget-`300` diagnostic rows,
sentinel drift probes, and historical evidence packets can be mistaken for
primary matrix rows.

The protocol marks these rows as ineligible for primary aggregation. Budget
`300` is descriptive diagnostic evidence only.

### Empty-State Governance Loophole

A method can appear governed under a weak no-conflict-only metric if it carries
little or no output-bearing state.

Strict `state_governance_success` requires an output-bearing carry surface.
Standalone governance is diagnostic only and cannot override answer failure.

## Known Limitations

- The repository contains the clean-v2 five-model 7,200-row row-level
  execution closure and the submission aggregate result tables.
- Statistical interpretation, final venue-facing claim wording, and final
  public hosting metadata remain separate manuscript/release layers.
- Closed-model outputs are not independently reproducible through provider
  reruns.
- Provider metadata surfaces vary across endpoints and may include unavailable
  fields.
- The benchmark focuses on bounded state transfer, not broad open-domain
  reasoning.
- The task substrate is synthetic and calibration-conditioned.
- Budget `300` is a stress diagnostic, not a confirmatory budget level.

## Release And Access Boundary

Reviewer access should not require a private request to the authors. During
anonymous review, the artifact should be distributed as an anonymized archive
or anonymous repository. For public release, the dataset-like surfaces should
be hosted through a durable platform and accompanied by Croissant metadata.

The release should not include private notes, credentials, raw chats,
non-anonymized logs, or local-only directories.

## Related Artifact Files

- `artifact/BENCHMARK_CARD.md`
- `artifact/metadata/croissant.json`
- `artifact/metadata/CROISSANT_MAPPING.md`
- `docs/HOSTING_AND_RELEASE_PLAN.md`
- `REPRODUCIBILITY.md`
- `ANONYMITY.md`
