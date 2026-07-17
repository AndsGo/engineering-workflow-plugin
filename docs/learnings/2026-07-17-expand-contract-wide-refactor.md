---
track: knowledge
status: active
category: pattern
last-verified: 2026-07-17
---
# 宽重构用 expand-contract 切片，保持每步 CI 常绿

**Track:** Knowledge
**Date:** 2026-07-17
**Applies to:** general（跨全库的机械性改动：改名、换 schema、换 API 形态）

## Context

垂直切片（tracer bullet）假设每片可独立落地并保持绿。**宽重构**破坏这个假设：一个机械改动（改列名、换函数签名）的爆炸半径横跨全库，成千个调用点同时红，没有任何垂直切片能独立变绿。源自 mattpocock/skills 的 to-tickets。

## Guidance

三段式：
1. **Expand** — 新形态与旧形态并存上线（新列/新函数/新 API 加进去，旧的不动）。此步自身绿。
2. **Migrate** — 调用点按爆炸半径分批迁移，每批一个可独立合并的工作项，批间 CI 始终绿。
3. **Contract** — 全部迁完后删除旧形态。此步只删死代码，绿。

无法并存时（如硬 schema 约束）：退到共享 integration 分支 + 最后一个 integrate-and-verify 工作项，只在终点要求绿。

## When to Apply

- 任何「一处定义、N 处使用」的全库机械改动，N 大到一个 PR/一次会话装不下或 review 不动。

## When NOT to Apply

- 爆炸半径小（几个调用点）时直接一把改完——三段式此时是纯开销。
- 行为性重构（逻辑真的变了）不适用：那是 feature，走正常切片。

## Examples

- 典型：`fetchUser` → `getUser` 全库改名：expand（新名 re-export 旧实现）→ 分批替换 import → contract（删旧 export）。

## Related

- [[2026-07-17-mattpocock-borrowing-tiers]] — 来源决策；to-tickets 整体形态的采纳条件在该条。
