---
track: decision
status: active
category: architecture
last-verified: 2026-07-17
---
# 从 mattpocock/skills 借鉴什么、推迟什么、不借什么

**Track:** Decision
**Date:** 2026-07-17
**Applies to:** engineering-workflow-plugin 的演化路线

## Context

2026-07-17 对 mattpocock/skills（commit 9603c1c，CodeWiki 存 `D:\git\mattpocock\skills\.codewiki\`）做了全量精读对比。两个项目哲学趋同（删执行脚手架、留正确性不变量），生命周期覆盖互补：他们强在前段（对齐、词汇、分解、跨 session 规划）与写 skill 的手艺；我们强在后段（审查/安全/验收/知识复利）与机械化验证。

## Decision

- **第一梯队（已落地 v1.8）**：① CONTEXT.md 领域词汇层（决策仍走 Decision track，不引 ADR 系统）② invocation 二分法（retro/learnings-refresh 翻转）③ skill-authoring 方法论 ④ 同步不变量 + 说谎路由器规则 ⑤ grill-me facts/decisions HITL。
- **第二梯队（按序、按触发条件）**：⑦ spec-fidelity 审查轴（v1.9，不变量强化，先做）→ ⑧ setup skill（下次新项目接入摩擦出现时做；硬/软依赖规则：只有缺配置就出错的 skill 才写 setup 指针）→ ⑥ to-tickets（本地形态；触发条件绑死「计划超一个 session 或需并行」）→ ⑨ wayfinder（**推迟**至第一个真实 >1-session 工程出现；先只沉淀纪律见 [[2026-07-17-cross-session-planning-disciplines]]）。
- **不借**：零 hook/纯人工编排哲学（我们的团队场景靠 hook 拿 ~95-100% 可靠性，是比较优势）；skills.sh 式双轨分发（维护两条哲学不值）；每 skill 一份 agents/openai.yaml（无 Codex 受众）。

## Rationale

- 用 scaffolding-vs-invariant 透镜分类：⑦ 是不变量强化（价值随模型能力升），⑥⑨ 是编排脚手架（必须绑触发条件，否则重蹈 v1.4 砍掉的过度流程）。
- 他们自己的演化佐证取舍：tdd 削成 reference-only、wayfinder 定位 situational on-ramp 而非主干道、版本同步规则自身也漂移（人工不变量无机械检查必失守）。

## Trade-offs

- 翻转两个 skill 换来 context 减负，代价是 "retro" 短语不再自动加载（需 /engineering-retro）。
- 推迟 ⑨ 意味着若突然出现超大工程，首次要现场搭简易地图（可接受：本地 markdown 形态半天可起）。

## Revisit When

- 出现第一个 >1-session 工程（→ 启动 ⑨ 本地形态）；新项目接入摩擦再现（→ ⑧）；多 agent 并行需求出现（→ ⑥ tracker 形态，前置 ⑧）。

## Related

- [[2026-07-06-scaffolding-vs-invariant]] — 分类透镜。
- [[2026-07-17-invocation-dichotomy-context-economics]]、[[2026-07-17-expand-contract-wide-refactor]]、[[2026-07-17-cross-session-planning-disciplines]] — 本决策的知识产出。
