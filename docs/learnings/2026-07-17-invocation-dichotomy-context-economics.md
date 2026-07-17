---
track: knowledge
status: active
category: pattern
last-verified: 2026-07-17
---
# Invocation 二分法：每个 skill 在 context load 与 cognitive load 之间二选一

**Track:** Knowledge
**Date:** 2026-07-17
**Applies to:** general（skill/插件/agent 工具设计）

## Context

一个 skill 是 model-invoked（agent 可自主触发）还是 user-invoked（仅人可触发，`disable-model-invocation: true`），不是实现细节，而是一笔显式账：model-invoked 付 **context load**（description 常驻每个会话的上下文，一次写下永久收费）；user-invoked 付 **cognitive load**（人必须记得它存在——这是「人类能动性的价格」，不是要最小化的成本）。源自 mattpocock/skills 的 writing-great-skills/invocation.md，v1.8 落地。

## Guidance

- 判据只有一条：**agent 必须能在流程中自主够到它，或被其他 skill 调用，才值得付 context load。** 其余（人工节律的仪式：复盘、知识库维护、一次性 setup）一律 user-invoked。
- 自然语言触发依赖 model-invocation：路由表写「用户说 X → 调 skill Y」的前提是 Y 可被模型调用。翻转一个 skill 时必须同步扫掉所有教模型「自动调用它」的路由面，否则路由器在说谎。
- 翻转后 description 从模型可见面消失——description 携带的语义（阈值、触发时机）必须迁移到仍可见的载体（hook 信号、meta 表行），否则静默丢失。
- user-invoked skill 的 description 改写为「给人读的一行」（无触发词列表）；触发时机改用「建议用户运行 /x」措辞。

## When to Apply

- 新建 skill 时（先决定 invocation 再写 frontmatter）；审计现有 skill 清单的 token 成本时。

## When NOT to Apply

- 需要被其他 skill 内嵌调用的原语（如 grilling 类内核）不能翻转——判据第二条。
- 团队 UX 以自然语言短语为主且该短语高频时，翻转省下的 token 可能不值交互摩擦——按频率权衡。

## Examples

- v1.8：`engineering-retro`、`learnings-refresh` 翻转为 user-invoked（周/月度仪式，从不被 mid-flow 调用）；30+/50+ 阈值语义从 description 迁入 session-start 信号串。其余 11 个因自然语言路由依赖保持 model-invoked。

## Related

- [[2026-07-06-scaffolding-vs-invariant]] — 同一「为每条常驻指令付费」的经济学视角。
- `CONTRIBUTING.md` — Skill Writing Standards → Invocation（判据的权威家）。
