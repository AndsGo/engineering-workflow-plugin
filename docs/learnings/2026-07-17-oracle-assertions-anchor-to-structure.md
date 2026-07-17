---
track: knowledge
status: active
category: pitfall
last-verified: 2026-07-17
---
# Oracle 断言必须锚定到它声称检查的结构，否则被邻近文本「空真」满足

**Track:** Knowledge
**Date:** 2026-07-17
**Applies to:** general（一致性脚本、验收断言、任何 grep/substring 式检查的设计）

## Context

给「文档/配置一致性」写机械断言时，最省事的写法是全文 substring（`'x' in file`）。v1.8 的一致性 oracle 两次踩中同一坑：断言通过了，但通过的原因不是被检查的结构存在。

## Guidance

- **锚定结构，不锚定出现**：「参与表包含 grill-me」写成全文 `` `grill-me` in proto ``，会被文件头的 changelog 行满足——删掉表格行检查依然绿。正确写法锚定行结构：`^\| `grill-me` \|`（regex + re.M）。
- **字面残留扫描会漏「别的数字」**：只扫 `"10 skills"` 抓不到 `"11 个自定义 skill"`。正确写法是通用模式：任何 `\d+ … skills?` 提取数字与实际值比对——v1.8 升级后立刻抓到第 4 处漂移。
- **每个修复都要被 RED 见证过**：一处修复若从未对应过一条会失败的断言，它的正确性只是断言（v1.8 的 README:143 修复即如此，审查才补上）。新增断言的顺序永远是：先跑出 RED，再修，再 GREEN。
- **完整性检查优先推导而非点名**：「凡 SKILL.md 提及 knowledge-compound 者必须在参与表」这类推导式断言，抓到了点名清单（grill-me、loop-verify）漏掉的 resolve-pr-feedback。

## When to Apply

- 写任何基于 grep/substring 的验收断言时；review 别人的检查脚本时（问：这条断言可能被什么无关文本满足？）。

## When NOT to Apply

- 真正唯一的长字符串（如特定错误码）全文匹配即可，不必过度结构化。

## Examples

- v1.8 oracle 从 12 条升到 36 条的三类升级：表格行锚定、通用计数扫描、成员推导完整性——每类都在升级当轮抓到真问题。

## Related

- [[2026-07-06-blind-eval-not-self-graded]] — 同一母题（「检查必须真的能失败」）在机械断言侧的落地；本条是它的空真变体。
