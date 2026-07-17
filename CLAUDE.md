# engineering-workflow-plugin 维护规则

本文件是同步不变量清单（机制，不是文档）。方法论 → `docs/skill-authoring.md`；机械清单 → `CONTRIBUTING.md`。

## 同步不变量（skill 增 / 删 / 改名 / 行为变化时，一次全扫）

以下表面必须同步更新，缺一处即为漂移：

1. `skills/using-engineering-workflow/SKILL.md` — Rule 1 路由表 + Available Skills 表（计数与行数）
2. `README.md` — 头条计数（`N process skills`）、`### Skills (N)` 表、三层架构图中的计数
3. `ARCHITECTURE.md` — 三层架构图计数与 skill 名单
4. `CONTRIBUTING.md` — Directory Layout 树
5. `docs/engineering-workflow-guide.md` — 场景路由表 + 头部描述（不写具体计数）
6. `CHANGELOG.md` — 用户可读的叙事条目（动机 + 语义变化，不只罗列文件）
7. 版本号 ×3：`.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json`（metadata.version、plugins[0].version）
8. 若 skill 触碰 `docs/learnings/` → `references/learnings-protocol.md` 参与表加行

**计数规则：** 能不写具体数字就不写（用「见参与表」替代「All 10 skills」）；必须写的数字要能被 `skills/*/SKILL.md` 目录数直接核对。历史记录（`docs/plans/`、`docs/specs/`、`CHANGELOG.md` 旧条目、`tests/eval-*.md`）是快照，**永不回改**。

## 说谎的路由器规则

`using-engineering-workflow` 是路由器：任何 skill 增删改名、invocation 翻转或触发方式变化后，必须重读其 Rule 1 表与 Available Skills 表并更新——漏掉新 skill、或仍指向旧行为的路由器是在说谎。routing 行必须与该 skill 的 frontmatter 实际状态一致（user-invoked 的行要写「建议用户运行 /x」而非直接调用）。

## Invocation 二分法

判据、流程与当前 user-invoked 清单的唯一权威家是 `CONTRIBUTING.md` — Skill Writing Standards → Invocation（其余 skill 全部 model-invoked）。

## 版本化契约

`references/learnings-protocol.md` 与 `references/scenario-protocol.md` 是版本化契约（当前版本见各文件头，不在此处复述）：任何语义修改必须 bump 版本号并在头部记 changelog 行；破坏性变更需迁移说明。`references/domain-glossary.md` 是 advisory 约定，非契约。

## 验证纪律

- 判断类产物（分类 rubric、路由规则、门禁）上线前跑盲评：`skills/using-engineering-workflow/tests/README.md`。
- manifest 改动后跑 `claude plugin validate . --strict`（只校验 marketplace manifest，不校验 SKILL.md frontmatter——frontmatter 靠人工/脚本核对）。
- 对本仓库自身的改动同样受插件流程治理（Rule 0 分档、conservative-wins、手动提交）。
