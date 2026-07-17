---
track: knowledge
status: active
category: pattern
last-verified: 2026-07-17
---
# 跨 session 大工程规划的三条纪律（wayfinder 精髓，先于实现沉淀）

**Track:** Knowledge
**Date:** 2026-07-17
**Applies to:** general（任何大到一个会话装不下、被未知笼罩的工程的规划期）

## Context

mattpocock/skills 的 wayfinder 把超大工程建模为「决策票地图」。我们决定推迟实现（见 [[2026-07-17-mattpocock-borrowing-tiers]]），但其三条纪律独立于工具形态，值得先沉淀——出现第一个 >1-session 工程时直接用。

## Guidance

1. **Plan, don't do；一次只解一个决策。** 规划期的产出是 decisions 不是 deliverables；想动手实现通常是「该收束规划、交接给实施」的信号。每个规划会话最多解决一个决策（研究类可并行），强制慢而密——防止规划滑向半成品实施。
2. **迷雾的判据是「能否精确陈述问题」，不是「能否回答」。** 能精确陈述 → 立为待解决项；只是隐约感到会来 → 标记为雾，随前沿推进再具体化；超出目标范围 → 显式 out-of-scope，永不回流。先命名 **destination**（终点），它固定 scope 并塑造每个待解决项。
3. **HITL 项不许自答。** 每个工作项标注 HITL（需人在环：拷问、原型评审）或 AFK（agent 独立：调研、机械任务）。HITL 项只能通过与人的真实往返解决——agent 替人回答自己提的问题，就是纪律失效（grill-me v1.8 已落地此规则的单点版）。

另有一条早退规则：开局的广度拷问若发现**没有雾**，说明工程装得进一个会话——不要建没人需要的地图。

## When to Apply

- 工程大到必须跨多个会话、且存在真实未知（技术选型未定、需求成片模糊）时的规划期。

## When NOT to Apply

- 目标清晰的常规 feature（哪怕大）：直接 plan → tickets，不需要决策地图。
- 用作拖延实施的借口——无雾即动手。

## Related

- [[2026-07-17-mattpocock-borrowing-tiers]] — 推迟 wayfinder 实现的决策与触发条件。
