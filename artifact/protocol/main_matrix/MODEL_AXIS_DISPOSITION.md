# Model Axis Disposition

This note records why candidate closed-model endpoints that appeared in earlier
planning discussions are not part of the current primary model axis. The issue
is admission control, not post-hoc performance selection.

The current primary model axis is defined only by the frozen five endpoints used
for the 7,200-row PCG dynamic-state v2 confirmatory matrix. Candidate endpoints
discussed before that freeze do not contribute primary rows and should not be
interpreted as omitted unfavorable results.

## Disposition Summary

| Candidate endpoint | Primary-matrix status | Reason | Allowed future use |
| --- | --- | --- | --- |
| GLM-family endpoint | Excluded before primary execution | The reviewed ordinary access path did not provide a frozen no-training, DPA-style, or equivalent data-governance control for unpublished benchmark content. This was not a performance-based exclusion. | Supplementary or post-freeze rerun only under a documented no-training, enterprise/DPA, or public-timestamp route, with fresh hashes and a separate protocol note. |
| Gemini-family endpoint | Not admitted into the frozen model axis | The frontier/parity condition considered before the freeze did not provide an unambiguous thinking-off control. Lower-tier no-thinking-capable conditions would create a model-tier mismatch. No frozen admission run or primary model execution was completed. | Separate protocol revision only, requiring provider-route freeze, request/config hashes, reasoning/thinking control evidence, validation/admission evidence, and a new matrix freeze before execution. |
| Kimi K2.7 Code endpoint | Not admitted into the frozen model axis | Moonshot's official Kimi K2.7 Code documentation states that the model does not support non-thinking mode and that disabling thinking errors. The current matrix therefore uses `kimi-k2.6`, whose official documentation permits `thinking.type = "disabled"`. This was a reasoning-control decision, not a performance-based exclusion. | Separate protocol revision only, if Moonshot documents a K2.7-class non-thinking route or another exact Kimi endpoint that preserves model-tier comparability while allowing thinking-off control. |

## Official Source Notes

Official documentation was checked on 2026-06-24 and refreshed for the Kimi
K2.7/K2.6 reasoning-control boundary on 2026-06-26. These notes support the
admission boundary. They are not legal findings and do not assert provider
misconduct.

| Endpoint family | Official source | Relevant source statement | Experiment interpretation |
| --- | --- | --- | --- |
| GLM-family | BigModel privacy policy, `https://docs.bigmodel.cn/cn/terms/privacy-policy` | The policy describes the open platform as covering natural-language processing, API calls, and future service types; it also notes that user-provided model inputs may include personal or sensitive personal information. | The ordinary route needed a stronger frozen release record before exposing unpublished benchmark tasks, prompts, and oracle structure. |
| GLM-family | BigModel GLM Coding Plan team agreement, `https://docs.bigmodel.cn/cn/terms/subscription-agreement-team` | The team-plan feature list includes `数据默认不用于模型训练` as a plan-specific benefit. | This supports the control distinction: no-training protection existed as a documented team/enterprise-style property, but the primary matrix did not freeze such a route for GLM. |
| GLM-family | BigModel team-plan benefits page, `https://docs.bigmodel.cn/cn/coding-plan/team` | The team-plan page states that `提交的代码、提示词、对话内容等不会用于模型训练`. | GLM can be reconsidered under that documented route, or under an equivalent DPA/no-training agreement, but not by inheriting the earlier ordinary-route plan. |
| Gemini-family | Google Gemini API thinking documentation, `https://ai.google.dev/gemini-api/docs/thinking` | The API documents thought blocks, signatures, and thought-token accounting when thinking is used. | Thought blocks and thought-token accounting are state/control surfaces. The PCG matrix requires hidden reasoning to be disabled or absent, not merely unreported. |
| Gemini-family | Google Cloud Gemini thinking documentation, `https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/thinking` | The documentation states that thinking cannot be turned off for Gemini 3 Pro and Gemini 3.1 Pro; it also states that Gemini 2.5 Pro cannot turn off thinking. | The intended frontier/parity Gemini condition failed the clean thinking-off gate. |
| Gemini-family | Google Cloud Gemini thinking documentation, `https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/thinking` | The same documentation treats `MINIMAL` thinking as close to zero but still signature-bearing, and notes that Gemini 2.5 Flash/Flash-Lite can suppress thought content while reasoning-style text may still appear. | A lower-tier Flash-class replacement would not be the same model tier as the intended frontier condition, and would still require a separate admission protocol. |
| Kimi K2.7 Code | Kimi K2.7 Code quickstart, `https://platform.kimi.com/docs/guide/kimi-k2-7-code-quickstart.md` | The documentation describes K2.7 Code as supporting thinking mode and states that it does not support non-thinking mode; the parameter table says disabling thinking will error. | A K2.7 Code row would introduce mandatory hidden reasoning into a matrix that treats thinking as a controlled state variable. |
| Kimi K2.7 Code / Kimi K2.6 | Kimi thinking-model guide, `https://platform.kimi.com/docs/guide/use-kimi-k2-thinking-model.md` | The guide distinguishes K2.7 Code, which is always thinking and has preserved thinking always on, from K2.6, whose thinking can be disabled. | The admitted Kimi condition is `kimi-k2.6` with `thinking.type = "disabled"`; K2.7 Code is excluded from the primary axis until a clean thinking-off route exists. |
| Kimi K2.6 | Kimi K2.6 quickstart, `https://platform.kimi.com/docs/guide/kimi-k2-6-quickstart.md` | The documentation lists `thinking.type` as accepting enabled or disabled and provides a disabled-thinking request example for `kimi-k2.6`. | This supports the frozen `kimi_k26` condition used in the current model axis. |

## Reporting Boundary

These endpoints should not be used to estimate primary effects, compute primary
model averages, or support claims about current method superiority. If mentioned
in the paper, they should be described only as model-axis disposition decisions.

Recommended wording:

```text
Candidate endpoints considered before the final freeze were not admitted to the
primary model axis unless their provider route, request configuration, admission
evidence, reasoning/thinking controls, and hash locks were frozen before
execution. GLM-family endpoints were excluded for data-governance reasons, not
performance reasons. Gemini-family endpoints were not admitted because the
frontier/parity condition lacked a clean thinking-off control at freeze time.
Kimi K2.7 Code was not admitted for the same reasoning-control reason:
official Kimi documentation made K2.7 Code a mandatory-thinking condition,
whereas `kimi-k2.6` allowed explicit thinking disablement. No excluded
candidate primary run was executed.
```

## Non-Cherry-Picking Boundary

The GLM-family exclusion should not be described as weak or negative evidence
against that endpoint. Earlier diagnostics were treated as pre-main or
supplementary-only evidence because the final unpublished benchmark exposure
policy required a route-level no-training/DPA control that was not frozen for
GLM before primary execution.

If an ethics-oriented explanation is needed, use this narrower wording:

```text
We could not document a frozen access path establishing that submitted benchmark
content would be excluded from model-training use. As an experiment-ethics and
data-governance safeguard, GLM-family endpoints were not admitted to the primary
matrix.
```

The Gemini-family endpoint and Kimi K2.7 Code should not be described as failed
or removed conditions. They were never admitted into the frozen primary model
axis.

## Reasoning-Control Boundary

Hidden reasoning or provider-side thinking is treated as a state variable in
this benchmark. A model condition with mandatory, preserved, or ambiguous
thinking would add an uncontrolled capability to the method comparison and
weaken attribution. A lower-tier replacement selected only because it supports
thinking-off would introduce a different mismatch. Candidate Gemini endpoints
and Kimi K2.7 Code therefore require a separate protocol revision before any
future use.

## Claim Boundary

The paper should not say that GLM or Gemini was "dropped after poor results."
The defensible claim is narrower:

```text
GLM-family endpoints were excluded before primary execution because the reviewed
access path did not provide a frozen no-training or equivalent data-governance
control for unpublished benchmark content. Gemini-family endpoints and Kimi
K2.7 Code were not admitted because the intended candidate conditions lacked a
clean thinking-off control; Kimi K2.6 was used for the Kimi axis because it
supports explicit thinking disablement under the frozen request policy.
```

## Relationship To Legacy Evidence

Historical calibration, admission, or operational-planning notes may explain
why the model axis was narrowed or frozen, but they do not populate the current
main matrix. They are governed by `LEGACY_RESULT_DISPOSITION.md` and the
current row definition in `FINAL_MAIN_MATRIX_DEFINITION.md`.
