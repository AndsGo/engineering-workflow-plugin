# Skill 写作方法论

维护者文档：写新 skill、改旧 skill、诊断「skill 不触发 / 不听话 / 太长」时查阅。机械清单（frontmatter 字段、invocation 判据、必备章节）在 `CONTRIBUTING.md` — Skill Writing Standards，本文只讲方法论。

**来源：** 核心概念改编自 Matt Pocock 的 `writing-great-skills`（MIT，https://github.com/mattpocock/skills ），叠加本仓库自己的验证纪律。为独立撰写的适配版，非逐字翻译。

## 根本命题：predictability（可预测性）

> A skill exists to wrangle determinism out of a stochastic system.

skill 的存在意义是从随机系统里拧出确定性。**可预测 = 每次跑走同一个「过程」**，不是产出同一个结果（brainstorming 类 skill 应当可预测地发散）。下面每个杠杆都服务于它；token 成本、可维护性只是它的症状。

## 两种负载（invocation 的经济学）

- **Model-invoked** 付 **context load**：description 常驻每个会话的上下文，一次写下、永久收费。
- **User-invoked** 付 **cognitive load**：人必须记得它存在。这不是要最小化的成本，而是「人类能动性的价格」——该花在人类判断重要的地方（复盘节奏、维护节奏由人掌控，正是合理开销）。
- 判据与流程见 CONTRIBUTING（唯一权威家）。本仓库的路由架构以自然语言触发为主，所以默认 model-invoked；翻转是显式决策。

## Description 写法

- **领头词前置**：description 是干「触发」活的地方，最关键的触发词放最前面。
- **一个分支一条触发**：同一场景的同义改写是 duplication，合并。
- 身份描述（「本 skill 是什么」）如果正文已有，从 description 里砍掉——只留触发条件。这条即 **CSO 规则**（Claude Search Optimization，源自 obra/superpowers 的 writing-skills）：description 只写触发条件，绝不概括工作流。

## 信息层级（一把梯子）

内容只有两类：**steps**（有序动作）和 **reference**（按需查阅的规则/事实）。按「agent 多急需」排：

1. **In-skill step** — 每个 step 以 **completion criterion（完成判据）** 结束。判据有两个正交属性：**clarity**（能否分辨「完成了没有」——抗过早收尾）和 **demand**（要求多少——驱动 agent 在 step 内部自己跑腿查证）。判据要可检验、在关键处穷尽（「每个改动的文件都交代到」优于「产出一份清单」）。
2. **In-skill reference** — 扁平同级集合常是好安排（一次 review 的所有规则同档平铺），不是坏味道。
3. **External reference**（`references/*.md`）— 由 context pointer 按需加载。**pointer 的措辞决定取到的可靠性**：必须取到的材料配了弱措辞（"see also…"），是个 variance bug——先改措辞（"MUST read X before Y"），改不好才 inline。

**Progressive disclosure**：只有部分分支才需要的内容，推到 pointer 后面；每个分支都要的才 inline。**Co-location**：一个概念的定义、规则、注意事项放同一标题下，读一处带出全部。

## Leading words（领头词）

征用模型预训练里已有的紧凑概念做锚——*red*、*seam*、*tracer bullet*、*frontier*、*oracle*、*floor*。一个词反复作为 token 出现，用最少 token 锚定一片行为：body 里锚定执行（每次出现都指向同一动作），description 里锚定触发。范例："fast, deterministic, low-overhead" → *tight*；"a loop you believe in" → *red*（模糊门槛变二元可观测）。自造词没有先验红利——你得花定义 token 去买预训练词免费给的东西，优先用已有词。

## 修剪（防沉积）

- **单一事实源**：每个含义只有一个权威位置，其余用指针。本仓库的教训：计数散文三个版本连烂（9→10→13），复述必漂移。
- **No-op 猎杀（逐句）**：这句话相对模型的默认行为改变了什么？没有 → 删整句（不是删词）。争论一行是不是 no-op，靠跑 skill 解决，不靠辩论。失败的散文大多该删而非重写。
- 对「本就够认真的 agent」说 *be thorough* 是 no-op；修法是更强的领头词（*relentless*），不是加长句子。

## 失败模式诊断表

| 失败模式 | 症状 | 解法 |
|---|---|---|
| **Premature completion** | step 没真做完就收尾 | 先磨锐 completion criterion（便宜、局部）；真观察到赶工才拆分隐藏后续步骤（只有跨真实上下文边界才有效） |
| **Duplication** | 同一含义多处出现 | 单一事实源 + 指针 |
| **Sediment** | 陈旧层堆积（加内容感觉安全、删感觉危险的默认命运） | 定期 no-op 猎杀；document-sync 的 hygiene 检查 |
| **Sprawl** | 单纯太长，每行都还活着 | 梯子：披露 reference、按分支拆 |
| **No-op** | 模型默认就会做的一行 | 删句或换更强领头词 |
| **Negation（大象）** | 「别做 X」把 X 拽进上下文，反而更可得 | 正向表述目标行为；禁令只作硬护栏且必须配「该做什么」 |
| **Negative space（虚空）** | 没写的每个决定都默默交给了模型先验 | 通读草稿的沉默处，逐个决定：填上，或留作真正的开放分支 |

## 本仓库叠加层（不变量，不随上面的手法放松）

- **Iron Law + Red Flags**：一条一行式绝对规则 + 反合理化对照表，是本仓库纪律类 skill 的房型（见 ARCHITECTURE — Pattern 3）。
- **判断类产物必须盲评**：任何让模型「决定」什么的 skill/rubric（分类、路由、门禁），上线前跑盲评——fresh agent、答案键隔离、≥5 次多跑、真实历史场景、分布校准。协议：`skills/using-engineering-workflow/tests/README.md`；教训：`docs/learnings/2026-07-06-blind-eval-not-self-graded.md`。自评 fixture 是循环论证。
- **脚手架 vs 不变量**：加（或保留）任何强制步骤前先问「这是执行编排还是正确性保证？」——前者随模型能力升级要退役，后者要加固。教训：`docs/learnings/2026-07-06-scaffolding-vs-invariant.md`。
- **conservative-wins**：新约定必须对未采纳项目零行为变化。
