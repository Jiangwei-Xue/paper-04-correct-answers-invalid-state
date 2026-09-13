# Third-party and externally governed material

The repository-level MIT and CC BY 4.0 grants do not relicense model outputs,
saved provider records, benchmark-derived material, public data, third-party
software, or other externally governed content. A file-specific or upstream
notice takes precedence.

The inventory below is based on the paths, model identifiers, request
configurations, manifests, provenance records, and dependency declarations
present in this repository. Where an upstream license or redistribution grant
cannot be established from those materials, no license is inferred.

| Repository path | Material/source | Version or identifier | Upstream URL | Governing license or terms | Redistribution note |
|---|---|---|---|---|---|
| `artifact/results/main_matrix/record_mode_20260627/OPENROUTER_GPT_CLAUDE_CLEAN_V2_FROM_ZERO_20260627/` and the `openrouter_gpt55` / `openrouter_claude48` portions of `artifact/results/main_matrix/record_mode_20260627/BUDGET300_DIAGNOSTIC_DIRECT_V2_20260629/` | Saved OpenRouter requests, responses, cassettes, replay records, provider metadata, and derived scores for OpenAI GPT and Anthropic Claude routes | `openai/gpt-5.5-20260423`; `anthropic/claude-4.8-opus-20260528` | https://openrouter.ai/terms/ | OpenRouter Terms of Service and the applicable upstream model terms | No new license granted; reuse requires consultation of OpenRouter and applicable model-provider terms. |
| `artifact/results/main_matrix/record_mode_20260627/ALL_MODEL_DIRECT_CLEAN_V2_FROM_ZERO_20260628/deepseek_v4pro/`, the matching budget-300 records, `artifact/results/baselines/deepseek_v4pro_api_sanity_20260706/`, and DeepSeek records under `artifact/results/evidence/` | Saved direct-provider requests, responses, cassettes, replay records, and provider metadata | `deepseek-v4-pro` | https://cdn.deepseek.com/policies/en-US/deepseek-open-platform-terms-of-service.html | DeepSeek Open Platform Terms of Service and incorporated DeepSeek terms | No new license granted; reuse requires consultation of the provider terms. |
| `artifact/results/main_matrix/record_mode_20260627/ALL_MODEL_DIRECT_CLEAN_V2_FROM_ZERO_20260628/kimi_k26/`, the matching budget-300 records, and Kimi records under `artifact/results/evidence/` | Saved direct-provider requests, responses, cassettes, replay records, and provider metadata | `kimi-k2.6` | https://platform.kimi.com/ | Kimi/Moonshot platform and model terms applicable to the API service | No new license granted; reuse requires consultation of the upstream source or provider terms. |
| `artifact/results/main_matrix/record_mode_20260627/ALL_MODEL_DIRECT_CLEAN_V2_FROM_ZERO_20260628/qwen37max/` and the matching budget-300 records | Saved Alibaba Cloud Model Studio requests, responses, cassettes, replay records, and provider metadata | `qwen3.7-max` | https://www.alibabacloud.com/help/en/model-studio/related-agreements | Alibaba Cloud Model Studio service and model terms | No new license granted; reuse requires consultation of the provider and model terms. |
| `artifact/results/main_matrix/record_mode_20260627/OPEN_WEIGHT_QWEN3_CODER_SUPPLEMENT_20260629/` | Saved OpenRouter/Alibaba supplemental-model requests, responses, cassettes, replay records, and provider metadata | `qwen/qwen3-coder-480b-a35b-07-25`; upstream model card: `Qwen/Qwen3-Coder-480B-A35B-Instruct` | https://huggingface.co/Qwen/Qwen3-Coder-480B-A35B-Instruct | The upstream model card identifies the model as Apache-2.0; saved API records also remain subject to OpenRouter and provider terms | The upstream model license does not automatically relicense hosted-service records or generated outputs. No new license is granted for those records. |
| `artifact/protocol/`, `artifact/results/evidence/ssr_downgrade_20260623/data/pcg_dynamic_state_v2/`, `results/metric_v2/`, and `results/metric_v3/` | PCG Dynamic-State v2 task manifests, scorer-only oracle material, row manifests, benchmark-derived inputs, labels, scores, and executor records | `pcg_dynamic_state_v2`; frozen manifests and hashes contained in the listed paths | Repository provenance files and manifests in the listed paths | Benchmark/source terms applicable to each underlying record; provider-derived fields retain provider terms | No new license granted for benchmark-derived or provider-derived records; reuse requires consultation of the source and any applicable provider terms. Project-authored code and aggregate summaries remain governed by the path map in `LICENSES/README.md`. |
| `artifact/metadata/croissant.json` and `artifact/metadata/CROISSANT_MAPPING.md` | Project-authored metadata describing the benchmark and its record sets; vocabulary references MLCommons Croissant | Croissant 1.1 vocabulary reference | http://mlcommons.org/croissant/1.1 | Project-authored prose follows the repository documentation license; referenced vocabulary/specification remains under its upstream terms | This repository does not grant rights in the Croissant specification or vocabulary. |
| `artifact/results/evidence/ssr_downgrade_20260623/requirements.txt` | Runtime dependency declarations; dependency source code is not bundled | Unpinned `openai`; unpinned `python-dotenv` | https://github.com/openai/openai-python ; https://github.com/theskumar/python-dotenv | `openai-python`: Apache License 2.0; `python-dotenv`: upstream BSD-style license | Installations are obtained from upstream package channels and remain subject to their upstream licenses. |
| `LICENSES/MIT.txt` and `LICENSES/CC-BY-4.0.txt` | Standard license texts included to state the grants for project-authored material | MIT License; Creative Commons Attribution 4.0 International | https://opensource.org/license/mit ; https://creativecommons.org/licenses/by/4.0/legalcode | Each standard license text and its own applicable terms | Inclusion of these texts defines only the material classes mapped in `LICENSE` and `LICENSES/README.md`; it does not relicense the repository as a whole. |

## Public-data and copied-code check

The repository describes a synthetic 40-task benchmark and the offline replay
does not require an external public-dataset download. No separately sourced
public dataset or transformed public-dataset copy is identified in the current
repository inventory. No copied third-party source-code tree or independently
licensed source component was identified beyond the upstream runtime
dependencies declared above. If either category is added later, this inventory
must be updated before release.

## Operational boundary

The offline replay consumes saved evidence and performs no model-provider API
calls. That operational fact does not change the ownership, license, or terms
applicable to the saved records.

For any material whose upstream redistribution status is not expressly stated:

> No new license granted; reuse requires consultation of the upstream source or
> provider terms.
