# Engineering Workflow Guide

三层工程栈使用指南。Superpowers 提供纪律底线，9 个自定义 skill 提供流程和工具。

## 快速参考

| 我想... | 说什么 | 触发的 skill |
|---------|-------|-------------|
| 探索一个新功能想法 | "我想做一个 XX 功能" | SP brainstorming |
| 把设计变成计划 | "写个实施计划" | SP writing-plans |
| 检查计划是否靠谱 | "review 一下这个计划" | plan-review-personas |
| 开始写代码 | "开始执行计划" | SP subagent-driven-dev |
| 修一个 bug | "这里有个 bug" | SP systematic-debugging |
| 提交前审查代码 | "review 代码" | structured-review |
| 安全检查 | "安全审计" | security-audit |
| 提交并开 PR | "ship it" | ship-and-pr |
| 端到端浏览器测试 | "测试页面" / "e2e test" | e2e-browser-test |
| 记录经验教训 | "compound" / "记录一下" | knowledge-compound |
| 周复盘 | "retro" | engineering-retro |
| 同步文档 | "update docs" / "同步文档" | document-sync |
| 处理 PR 反馈 | "resolve PR comments" | resolve-pr-feedback |

## 完整工作流

### 场景 1: 开发新功能（完整流程）

```
第 1 步: 构思
─────────────
你: "我想给用户加一个通知中心"
→ SP brainstorming 自动触发
→ 苏格拉底式对话，逐步澄清需求
→ 产出: docs/superpowers/specs/YYYY-MM-DD-notification-center-design.md

第 2 步: 计划
─────────────
你: "写个实施计划"
→ SP writing-plans 自动触发
→ 产出: 2-5 分钟粒度的任务列表

第 3 步: 审查计划
─────────────────
你: "review 一下这个计划" (或自动触发)
→ plan-review-personas 派遣 2-3 个 persona:
   - feasibility: 技术上能做吗？
   - scope-guardian: 做多了吗？
   - adversarial: 哪里会崩？(仅复杂计划)
→ 产出: Plan Review Report (APPROVE / REVISE / RETHINK)

第 4 步: 执行
─────────────
你: "开始执行" 或 "go"
→ SP subagent-driven-dev 自动触发
→ 每个任务: 派遣 implementer subagent → spec review → quality review
→ SP TDD 纪律贯穿全程 (先写测试, 看它失败, 再写代码)

第 4.5 步: 端到端测试 (涉及 UI 时)
──────────────────────────────────────
如果变更涉及前端页面:
→ e2e-browser-test 触发:
   - 自动映射 diff 中的文件到可测试的 URL
   - 三级深度: Quick (烟雾) / Standard (功能) / Exhaustive (全状态)
   - 使用 agent-browser CLI 打开页面、点击、填表、截图
→ 产出: E2E Test Report (PASS / FAIL)
→ 需要: agent-browser CLI (`npm install -g agent-browser`)

第 5 步: 代码审查
─────────────────
你: "review 代码" (或任务全部完成后)
→ structured-review 触发:
   1. 搜索 docs/learnings/ 查找相关先验知识
   2. 两轮审查 (CRITICAL → INFORMATIONAL)
   3. 并行派遣 reviewer agents (correctness, testing, +条件触发 security, maintainability)
   4. 合并去重 → fix-first 修复 → 报告
→ 产出: Review Summary (PASS / PASS WITH NOTES / BLOCK)

第 6 步: 安全审计 (仅安全敏感变更)
────────────────────────────────────
当变更涉及 auth/用户输入/API/密钥时:
→ security-audit 触发:
   - 依赖扫描
   - OWASP Top 10 代码审计
   - 配置和密钥检查
   - STRIDE 威胁模型
→ 产出: Security Audit Report (PASS / FAIL)

第 7 步: 发布
─────────────
你: "ship it" 或 "提交开 PR"
→ ship-and-pr 触发:
   1. Pre-flight 检查 (分支, 测试, 冲突)
   2. 暂存和提交 (价值导向的 commit message)
   3. 推送
   4. 创建 PR (描述按变更复杂度缩放)
→ 产出: PR URL

第 7.5 步: 文档同步
──────────────────────
ship-and-pr 完成后:
→ document-sync 触发:
   - 扫描所有 .md 文件, 交叉比对 diff
   - 自动更新事实性变更 (路径、数量、命令名)
   - 主观变更需确认 (叙述、架构理念)
→ 产出: Document Sync Report

第 8 步: 记录经验
─────────────────
ship-and-pr 完成后会提示:
→ "这次开发有什么值得记录的经验吗？"
→ 如果有: knowledge-compound 触发
   - Bug track: 根因 + 修复 + 预防
   - Knowledge track: 模式 + 什么时候用 + 什么时候不用
   - Decision track: 选项 + 决策 + 理由
→ 产出: docs/learnings/YYYY-MM-DD-<topic>.md
```

### 场景 2: 修复一个 Bug（简化流程）

```
你: "登录页面报 500 错误"
→ SP systematic-debugging 触发:
   Phase 1: 根因调查 (读错误 → 复现 → 查改动 → 收集证据)
   Phase 2: 假设验证
   Phase 3: 修复 (最小化变更)
   Phase 4: 验证

→ 修复后, 你: "review 一下"
→ structured-review (搜索先验知识 → 审查 → 报告)

→ 如果修复了 UI: "测试一下页面"
→ e2e-browser-test (Quick tier, 验证修复可见)

→ 你: "ship it"
→ ship-and-pr (pre-flight → commit → push → PR)
→ document-sync (自动检查文档是否需要更新)

→ 收到 review comments?
→ resolve-pr-feedback (批量处理反馈 → 修复 → 回复)

→ "这个 bug 值得记录吗？"
→ knowledge-compound (Bug track)
```

### 场景 3: 周五复盘

```
你: "retro"
→ engineering-retro 触发:
   1. 分析过去 7 天的 git 提交
   2. 按类别分类 (features, bugs, tests, refactor...)
   3. 计算健康指标 (test ratio, bug rate, churn)
   4. 对比上次 retro 的 action items
   5. 定性分析 (做得好的 + 需改进的)
→ 产出: Engineering Retro Report

→ "这段时间有什么经验值得记录？"
→ knowledge-compound (如果有)
```

### 场景 4: 处理 PR 反馈

```
你: "resolve PR comments" (或提供 PR 编号)
→ resolve-pr-feedback 触发:
   1. 获取所有未解决的 review threads
   2. 分类: 新的 / 已处理的 / 不可操作的
   3. 并行派遣 agent 修复每个 valid comment
   4. 提交、推送、回复 thread 并标记 resolved
→ 产出: PR Feedback Resolution Summary
```

### 场景 5: 只做代码审查

```
你: "review 当前分支的代码"
→ structured-review 触发
→ 直接从 Step 0 开始 (diff scope → prior knowledge → checklist → reviewers)
→ 不需要前面的 brainstorm/plan 步骤
```

## 关键纪律（来自 Superpowers）

这些是不可跳过的底线:

| 纪律 | Iron Law | 意味着 |
|------|----------|-------|
| **TDD** | 没有失败的测试就没有生产代码 | 先写测试 → 看它失败 → 再写代码 |
| **系统化调试** | 没有根因调查就没有修复 | 不猜测, 不随便改, 先查清楚 |
| **验证先于声明** | 没有新鲜的验证证据就没有完成声明 | 跑命令 → 看输出 → 然后才能说"好了" |
| **计划审查限制** | 最多 2 轮 RETHINK | 2 轮后需要人工思考, 不是更多 agent 循环 |

## 知识系统

### 知识从哪里来

| Skill | 什么时候产生知识 |
|-------|----------------|
| structured-review | 发现新模式、安全问题、与旧决策矛盾 |
| security-audit | 漏洞模式、安全决策、假阳性模式 |
| plan-review-personas | 计划缺陷被捕获、persona 分歧揭示权衡 |
| ship-and-pr | PR 完成后提示 |
| e2e-browser-test | 浏览器特有的 bug (逻辑通过但 UI 崩溃) |
| document-sync | 文档漂移模式 (同一文件反复过时) |
| resolve-pr-feedback | 反馈中的重复模式 |
| engineering-retro | 周期性反思 |
| SP systematic-debugging | 非显然的根因 |

### 知识被谁消费

| Skill | 怎么用先验知识 |
|-------|--------------|
| structured-review | Bug learning → 提升审查重点; Decision → 验证一致性 |
| plan-review-personas | Bug → adversarial 已知失败模式; Decision → feasibility 约束 |
| security-audit | 安全类 Bug → 升高风险; 旧审计 → 检查延迟项 |
| ship-and-pr | Pitfall → PR 描述注意事项 |
| engineering-retro | 上次 action items → 追踪改善; 重复 bug → 系统性问题 |

### 知识文件格式

每条 learning 存储为 `docs/learnings/YYYY-MM-DD-<category>-<slug>.md`。

v1.1 起 frontmatter 必须包含 `track` 和 `status`；`category` / `last-verified` 等可选。INDEX.md 是路由层（v1.1 手写，v1.2 起 `learnings-refresh` skill 自动生成）。

三种最小模板:

**Bug (最小):**
```markdown
# 登录 500 错误: session token 过期未处理

**Track:** Bug | **Date:** 2026-04-02 | **Severity:** P1

**Symptom:** 登录页面返回 500
**Root Cause:** session middleware 未检查 token 过期时间
**Fix:** 添加过期检查, 过期时重定向到登录页
**Prevention:** 添加 session token 过期的单元测试
```

**Knowledge (最小):**
```markdown
# 数据库迁移前先备份

**Track:** Knowledge | **Date:** 2026-04-02

**When:** 涉及 ALTER TABLE 或 DROP COLUMN 的迁移
**Do:** 迁移脚本中包含回滚步骤, 生产环境先在副本上测试
**Don't:** 直接在生产库上跑未测试的迁移
```

**Decision (最小):**
```markdown
# 选择 JWT 而非 session cookie

**Track:** Decision | **Date:** 2026-04-02 | **Status:** Active

**Context:** 需要跨域认证
**Chose:** JWT **because** 无需服务端存储 session, 天然支持跨域
**Trade-off:** token 无法在服务端主动失效, 需要额外的 blacklist 机制
```

## 目录结构

```
your-project/
├── CLAUDE.md                    ← 项目指令 (包含 skill routing 规则)
├── docs/
│   ├── learnings/               ← knowledge-compound 写入
│   │   ├── INDEX.md             ← 路由层（v1.1 手写，v1.2 起自动生成）
│   │   ├── 2026-04-02-bug-session-token-expiry.md
│   │   ├── 2026-04-02-pattern-retry-with-backoff.md
│   │   ├── 2026-04-02-architecture-jwt-over-sessions.md
│   │   └── archive/             ← 已归档的 learnings
│   └── superpowers/
│       ├── specs/               ← brainstorming 写入
│       │   └── 2026-04-02-notification-center-design.md
│       └── plans/               ← writing-plans 写入
│           └── 2026-04-02-notification-center-plan.md
└── src/                         ← 你的代码
```

## 常见问题

### Q: 改 3 行 CSS 也要走全流程吗？

不需要。Superpowers 的 brainstorming 会自动识别简单任务并 short-circuit。plan-review-personas 对 trivial 计划会跳过审查。你可以直接 TDD → commit。

### Q: 如果我赶时间，可以跳过审查吗？

TDD 和 verification 是不可跳过的纪律。structured-review 和 security-audit 可以在时间紧迫时跳过——但要有意识地做这个决定，而不是让 agent 帮你合理化跳过。

### Q: docs/learnings/ 会不会越来越多？

会。v1.1 提供了基础设施：
- session-start hook 在 30+/50+ 阈值发出软信号（`LEARNINGS_THRESHOLD_INDEX` / `LEARNINGS_THRESHOLD_REFRESH` 可调）
- 协议（`learnings-protocol.md`）定义了 archive / supersede / synthesize 的判断规则

**v1.2 将 ship `learnings-refresh` skill** 来自动检测：cited 代码路径已删 / 同 category ≥3 条（可合并）/ 长期未碰 —— 但所有动作仍需用户逐行确认。在 v1.2 之前，参考协议手工 curate。

### Q: 安全审计什么时候触发？

仅当代码变更涉及安全敏感文件时（auth, user input, API endpoints, secrets, config）。纯 UI/文档变更不触发。你也可以随时手动触发: "安全审计"。

### Q: 我可以只用其中一部分 skill 吗？

完全可以。每个 skill 都是独立的。最有价值的单独使用组合:
- **只用 structured-review**: 比普通 code review 更结构化
- **只用 knowledge-compound**: 积累经验教训
- **只用 engineering-retro**: 周复盘
- **只用 e2e-browser-test**: 快速验证页面是否能用
- **只用 resolve-pr-feedback**: 批量处理 PR comments

### Q: e2e-browser-test 需要什么环境？

需要安装 `agent-browser` CLI: `npm install -g agent-browser && agent-browser install`。同时需要本地开发服务器运行（如 `npm run dev`）。

### Q: resolve-pr-feedback 会自动提交代码吗？

会。它对每个 valid 的 review comment 做修复后，统一 commit 并 push。但 `needs-human` 类型的反馈会呈现给你决定，不会自动处理。

### Q: document-sync 会重写我的 CHANGELOG 吗？

绝对不会。它只做措辞润色（voice polish），永远不会删除、重排或重新生成 CHANGELOG 条目。如果发现条目可能有误，会问你而不是自动修复。

### Q: Learnings Protocol 是什么？

`skills/using-engineering-workflow/references/learnings-protocol.md` 是版本化的契约，定义所有 learning-touching skill 必须遵守的 READ / WRITE / MAINTAIN 三阶段。9 个 skill 都引用它（meta + 7 consumer + document-sync），不重复散文。修改契约是 plugin 的破坏性变更。
