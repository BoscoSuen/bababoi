# Claude Trading Skills 项目愿景

Version: 0.2
Last updated: 2026-07-01

English version: [PROJECT_VISION.md](PROJECT_VISION.md)

Claude Trading Skills 是一套基于 Claude Skills 的决策流程操作系统，面向时间有限的个人投资者，帮助他们以长期投资为基础，根据市场环境进行有纪律的波段交易，并通过风险管理和记录复盘实现持续成长。

## 1. 宣言

**Empower solo traders, growing together.**

本项目旨在让个人交易者不再仅依赖孤独的主观判断，而是拥有可复现的流程、明确的风险管理、记录与复盘、以及持续改善的循环。这是一个 Claude Skills 项目。

这里的 **solo** 不意味着孤立。本项目面向独立判断、独立承担风险的交易者，同时致力于通过共享实践推动工作流、复盘和改善经验的共同成长。

## 2. 重要提示与免责声明

本仓库提供的是以教育、研究和流程改善为目的的 Claude Skills 及相关资料。不提供金融建议、投资顾问、买卖信号分发、经纪商订单执行、税务或法律建议。

投资和交易存在包括本金损失在内的风险。过往数据、回测、筛选结果、示例报告和 AI 生成的分析不能保证未来收益。最终的买卖决策、仓位大小、风险管理、税务/法规合规及经纪商使用决定均由用户自行负责。

本项目基于 MIT License 提供。软件和资料按照许可证所述 **"AS IS, WITHOUT WARRANTY"**（即不提供任何明示或暗示的保证）提供。

## 3. 项目起源与公开理由

本项目源于作者希望利用 AI 将自己的交易流程提升一个层次。

对于个人交易者，特别是有主业和生活、同时从事投资交易的人来说，时间、信息量、情绪管理和风险管理都是重大约束。Claude Trading Skills 正是为了在这些约束下，让市场确认、候选标的筛选、交易计划、风险管理、记录和复盘更容易持续进行而创建的。

本项目首先作为作者自己每天、每周使用的实用工具来培育。目的是提升自己的交易水平，建立不易出局的决策流程，从记录中持续学习。同时，考虑到这可能对有相同约束和困惑的人有所帮助，因此以开源形式公开。

这个定位是 **first for self, open for others**。第一个用户就是作者本人，即使外部反馈较少的时期，也会作为自己真正使用的工具持续改善。在此基础上，追求工作流、复盘和改善经验的共享，使个人交易者的实践知识逐步积累。

Claude Trading Skills 不是分发成熟获利方法的项目。作者本人也是仍在学习中的个人交易者。本仓库不是提供"答案"的地方，而是一个分享有用机制的平台，帮助个人交易者锻炼判断力、管理风险、从记录中学习、逐步成长。

## 4. 核心理念

本项目的目的不是比任何人都更好地预测市场。

目的是让个人交易者能够做出更加结构化、风险意识更强、可复盘、可改善的决策。

本项目的核心不是以下流程：

```text
Ask -> Signal -> Trade
```

核心是以下学习循环：

```text
Plan -> Trade -> Record -> Review -> Improve
```

Claude Trading Skills 不是输出买卖信号的引擎。它致力于成为个人交易者利用 AI 建立不易出局的决策流程、一致地运营自己的判断、风险、记录和改善的 **决策流程操作系统**。

## 5. 项目目标

Claude Trading Skills 是一个以美股、ETF、股息投资、波段交易、宏观分析和策略研究为核心，并根据需要涵盖期权和事件策略的 Claude 技能仓库。

各技能支持以下决策：

- 把握市场环境
- 筛选候选标的
- 制定交易计划
- 计算仓位大小
- 确认投资组合风险
- 记录交易假设
- 复盘结果，发现改善点
- 验证新的策略想法

本项目追求的不仅仅是"便利的分析工具集"，而是面向个人交易者的 **决策支持系统**。

特别面向以长期投资为基础、在有限时间内根据市场环境进行波段交易的个人投资者，帮助他们高效决策、避免过度冒险、从记录中改善。

## 6. 本项目是什么 / 不是什么

| 本项目是 | 本项目不是 |
| --- | --- |
| 决策支持系统 | 金融建议/投资顾问 |
| 交易工作流工具箱 | 买卖信号分发服务 |
| 风险管理和复盘框架 | 收益保证系统 |
| Claude Skills 仓库 | 经纪商订单执行平台 |
| 支撑交易者学习循环的机制 | 全自动交易机器人 |

本项目不会替代交易者的判断。它是将交易者的决策流程明确化、可复现化、可复盘化、可改善化的机制。

最终决策和风险责任始终在用户一方。免责详情集中在"重要提示与免责声明"中，这个定位即使项目规模扩大也不会改变。

## 7. 目标用户

本项目的核心对象是 **兼职或时间有限的个人投资者/波段交易者**。

具体来说，面向以长期投资和股息投资为资产积累基础、在市场环境允许时通过中短期波段交易追求额外回报的人。他们有主业和生活，可用于投资的时间有限，因此希望将每日决策高效化、将风险管理和记录系统化。

### Primary Users

最优先关注的用户如下：

| 用户画像 | 主要目的 | 需要的引导 |
| --- | --- | --- |
| 兼职波段交易者 | 每日行情确认、候选筛选、交易计划 | `market-regime-daily` / `swing-opportunity-daily` |
| 希望强化风险管理的成长股投资者 | 区分进攻行情和防守行情 | `market-regime` / `exposure` workflow |
| 股息/长期投资者 | 发掘股息股、检视持仓、确认投资组合 | `core-portfolio` / `dividend-income` |

### Secondary / Advanced Users

扩展对象还包括以下用户：

| 用户画像 | 主要目的 | 需要的引导 |
| --- | --- | --- |
| 事件/财报交易者 | 寻找财报、新闻、经济事件后的机会 | `advanced-satellite` / `earnings-event` |
| 做空策略交易者 | 在 risk-off 环境中监控弱势或过热标的 | `advanced-satellite` / `risk-off-short` |
| 策略研究者/开发者 | 验证假设，改善策略 | `strategy-research` |
| 高级用户 | 扩展自定义 workflow、YAML manifest、CLI | manifests / scripts / API matrix |

另一方面，以下用户不是主要对象：

- 期望全自动交易的人
- 寻求收益保证或买卖信号外包的人
- 不想进行风险管理或记录的人
- 仅以短线超短线交易为主要目的的人

## 8. Core + Satellite 运营理念

本项目的主要目标用户以如下 **Core + Satellite** 结构进行投资和交易：

- **Core**: 长期投资、股息股、ETF、投资组合管理
- **Satellite**: 波段交易、主题股、突破、财报后动量
- **Advanced Satellite**: 按需使用的做空策略、事件策略、期权策略
- **Shared Layer**: 市场环境、风险管理、仓位大小、记录、复盘

重要的是，不要混淆 Core 和 Satellite 的目的、时间框架和风险。

本项目为个人投资者提供运营流程：以长期资产积累为基础，仅在市场环境允许时通过有纪律的中短期交易追求额外回报。

Advanced Satellite 是比主引导路径风险更高、前提更复杂、或需要更多执行确认的领域。例如做空策略、事件策略、期权策略，仅在具备充足经验、明确的亏损上限、手动确认、理解必需 API 和经纪商约束、经过预验证的 workflow 的情况下才使用。即使是实现量大的技能，也不一定是首先推荐给主要目标用户的引导路径。

## 9. 现状

本仓库已包含大量技能。大致覆盖以下领域：

- **市场分析**: 市场环境、广度、板块、宏观、新闻、泡沫风险
- **筛选**: CANSLIM、VCP、股息股、财报后动量、主题、机构资金流
- **交易计划**: 突破、Parabolic Short、仓位大小、敞口管理
- **投资组合与记录**: 投资组合管理、假设管理、交易记录、事后分析
- **策略研究**: 回测、策略创意生成、Edge 研究管道
- **质量管理与元技能**: 技能设计、评审、集成测试、改善循环

个别技能已相当充实。另一方面，从用户角度来看，以下课题仍然存在：

- 不清楚应该使用哪个技能
- 难以看清多个技能的使用顺序
- 交易前后的一系列工作流尚未整理
- 对不熟悉 GitHub 或 `.skill` 文件的人来说入口较难
- 技能使用结果尚未完全连接到持续学习循环

下一阶段的重点不是增加技能，而是 **整合成可用的形式**、**根据用户需求进行引导**、**使运营工作流得以固化**。

## 10. 战略方向：从技能集到运营操作系统

本项目的下一个方向可以用一句话概括：

> 从技能集到个人交易者的运营操作系统。

这里的运营操作系统是指：个人交易者进行每日/每周投资决策所需的市场确认、风险预算、策略选择、候选生成、交易计划、手动执行确认、记录、复盘、改善等一系列串联起来的机制。

这个运营操作系统的目标不是让个人交易者轻松获利。而是在有限时间内，创造一个不出局、管理风险、从记录中学习、逐步改善自己决策流程的状态。

理想的体验如下：

1. 用户用自然语言表达"我想做这样的交易"
2. 系统理解该用户的目的、经验、时间、风险承受度、API 环境
3. 推荐合适的技能集和工作流
4. 用户可以按顺序确认市场环境、风险、候选标的、交易计划
5. 交易后记录假设和结果，连接到下次改善

如果这个流程能够实现，即使不熟悉 GitHub 或工具配置的用户也能逐步获取本项目的价值。

## 11. 项目结构

今后按以下层次整理项目：

```text
1. Individual Skills
    ↓
2. Skill Inventory / API Matrix
    ↓
3. Skillsets
    ↓
4. Workflows
    ↓
5. Trading Skills Navigator
    ↓
6. User Entry Points
    ↓
7. Journal / Postmortem / Learning Loop
```

各层的职责如下：

| 层次 | 职责 |
| --- | --- |
| Skills | 小型专业功能。负责各项分析、计算、计划、记录 |
| Skill Inventory / API Matrix | 整理技能的用途、所需 API、难度、输入输出的单一信息源 |
| Skillsets | 按目的组织的技能束。定义哪些技能组合使用 |
| Workflows | 定义实际运营的顺序、决策门控、产出物的传递 |
| Navigator | 根据用户目的推荐合适 skillset / workflow 的引导者 |
| User Entry Points | docs、starter prompts、CLI、未来的 Web UI 等开始使用的入口 |
| Learning Loop | 通过记录、复盘、改善来培养技能和交易者的机制 |

通过这种结构，避免技能本体、文档、推荐逻辑和工作流的信息过度分散。Navigator 以对话方式向用户推荐合适的引导路径，User Entry Points 以静态文档、starter prompts、CLI、未来的 Web UI 等形式提供入口。

## 12. 路线图

### Phase 0: Vision and Metadata — ✅ metadata / SSoT 层已完成 (2026-05-17)

> **状态:** 引入 `skills-index.yaml` 作为 SSoT (PR #84)。为当前 index 中注册的全部技能赋予了 id / display_name / category / status / summary / integrations[] / timeframe / difficulty / inputs / outputs，`--strict-metadata` 已在 CI 和 pre-push hook 中强制执行。功能性的 metadata/SSoT 工作已完成。后续为常规 docs 维护。

首先整理现有技能群，使项目整体更易于说明。

主要工作:

- 明文化项目愿景和路线图
- 创建 `skills-index.yaml` 或 `skills-inventory.yaml`
- 更新技能列表、类别和 API 要求
- 将各技能的用途、时间框架、难度、所需 API 结构化
- 整理过时的描述和重复表述

完成条件:

- `PROJECT_VISION.md` 和 `PROJECT_VISION.zh.md` 已存在
- `skills-index.yaml` 或 `skills-inventory.yaml` 已存在
- 全部技能具有 category、use case、required API、difficulty、timeframe 的初始分类
- API requirements matrix 已更新
- docs 的技能数、类别、描述与现状无矛盾

### Phase 1: Trading Skills Navigator v0 — ✅ v0 已实现 (2026-05-17)

> **状态:** 在 `skills/trading-skills-navigator/` 中实现了确定性 recommender (`recommend.py`)。读取仓库根的 SSoT，Claude Web App 中回退到同捆的 `metadata_snapshot.json`，还提供 manifest 驱动的 setup。已有 10 题推荐回归测试套件 (`scripts/tests/test_recommend.py::CONTRACT`)。后续为 UX 调整、实际用户 smoke test 和使用示例的完善。

创建作为本仓库引导者的元技能。

用户问"我想做这样的事"时，Navigator 会引导推荐合适的技能、组合、导入方法和工作流。

Phase 1 的职责范围是 AI 对话式推荐。根据用户的目的、经验、时间和 API 环境，在对话中引导应该从哪个 skillset / workflow 开始。

预期的问题:

- "我想在做长期投资的同时，只在行情好时做波段"
- "我想每天早上用 15 分钟了解今天能否进攻"
- "我想分开长期持仓和短线交易的风险"
- "我想查看本周的持仓和股息股候选"
- "我想做波段交易"
- "我想找股息股"
- "我想使用做空策略"
- "我想知道不需要 API 密钥就能使用的技能"
- "我想了解适合初学者的开始方式"

完成条件:

- `skills/trading-skills-navigator/` 已存在
- 对 10 个代表性用户问题能返回推荐的 skillset 和 workflow
- 能区分引导有 API 密钥和没有 API 密钥的路径
- 能说明 Claude Web App 和 Claude Code 的导入步骤

### Phase 2: Skillsets — ✅ 部分完成：核心 4 个 skillset 已实现 (2026-05-17)

> **状态:** 在 `skillsets/` 中实现了 `market-regime` / `core-portfolio` / `swing-opportunity` / `trade-memory` 的 manifest（以及 `skillsets/README.md`）。通过 `validate-skillsets` + `skillset-docs-drift` 门控保护，Navigator 进行引用。剩余 skillset 候选（`dividend-income` / `strategy-research` / `advanced-satellite`）后续完成。

创建按目的组织技能的 manifest。

初始候选:

- `core-portfolio`
- `market-regime`
- `swing-opportunity`
- `trade-memory-loop`
- `dividend-income`
- `strategy-research`
- `advanced-satellite`

`advanced-satellite` 包含比主引导路径更高级的策略：risk-off short、earnings event、options、thematic momentum 等。

完成条件:

- 主要 7 个 skillset 的 YAML manifest 已存在
- 各 skillset 定义了 required / recommended / optional skills
- 记载了目标用户、时间框架、所需 API 和不宜使用的条件
- Navigator 可引用 skillset manifest 进行推荐

### Phase 3: Workflows — ✅ 部分完成 (2026-05-09)

> **状态:** PR #85 在 `workflows/` 中添加了 5 个 Core + Satellite manifest（`core-portfolio-weekly` / `market-regime-daily` / `swing-opportunity-daily` / `trade-memory-loop` / `monthly-performance-review`），通过 `--strict-workflows` 验证。Advanced 系列（`risk-off-short-daily` / `earnings-weekly` / `strategy-research-pipeline`）后续完成。

仅有 Skillset 不足以支撑实际运营。实际交易需要顺序、决策门控和产出物的传递。

典型工作流：

1. **Market Context**: 确认市场环境
2. **Risk Budget**: 决定承担的风险量
3. **Strategy Selection**: 选择今天使用的策略
4. **Candidate Generation**: 寻找候选标的
5. **Trade Planning**: 决定 entry / stop / target / size
6. **Manual Execution Gate**: 实际下单前的确认
7. **Monitoring**: 监控触发和失效
8. **Journal / Postmortem**: 记录并复盘

初始候选:

- `core-portfolio-weekly`
- `market-regime-daily`
- `swing-opportunity-daily`
- `trade-memory-loop`
- `monthly-performance-review`

Advanced workflow 候选:

- `risk-off-short-daily`
- `earnings-weekly`
- `macro-morning-brief`
- `strategy-research-pipeline`

完成条件:

- 至少 3 个实际运营 workflow 以 YAML 定义
- 各 workflow 具有输入、输出、决策门控、使用技能和手动确认项目
- 有兼职交易者可在 15～60 分钟内执行的每日/每周引导路径
- 各交易 workflow 具有连接到 journal entry 或 postmortem 的路径
- 至少 1 个 workflow 可使用示例数据进行端到端说明

### Phase 4: 对用户友好的入口 — ✅ 部分完成 (2026-05-17)

> **状态:** README（EN/ZH）中整备了以 5 个工作流为起点的"推荐的开始方式"和"无需 API 密钥的入口"。工作流/skillset 的文档页面已自动生成。Navigator 提供自然语言的入口。专门的"找到你的工作流"文档和快速入门的扩充后续完成。

为不熟悉 GitHub 或 `.skill` 文件的用户简化入口。

Phase 4 的职责范围是静态入口和分发路径。文档、quickstart、starter prompts、CLI、未来的 Web UI 等，即使没有 Navigator 也能让初次用户开始使用的路径。

候选:

- Core + Satellite quickstart
- "找到你的工作流"文档
- 15 分钟每日例程
- 60 分钟每周复盘
- starter prompts
- skill 下载清单
- API 设置指南
- `scripts/recommend_skills.py`
- 静态推荐页面

完成条件:

- 初次用户可在 5 分钟内选择自己的开始路线
- 区分不需要 API 密钥的路线和使用 FMP / Alpaca 的路线
- 能够知道应该向 Claude Web App 上传哪些 `.skill` 文件
- 准备好首次粘贴给 Claude 的 starter prompt

### Phase 5: Learning Loop — ✅ 部分完成 (2026-05-17)

> **状态:** 通过 `trader-memory-core` + `signal-postmortem` 和 `trade-memory-loop` / `monthly-performance-review` 工作流关闭了 Plan → Trade → Record → Review → Improve 的循环。可公开的端到端执行示例尚未整备。

强化记录交易结果并连接到改善的机制。

目标循环：

```text
Plan -> Trade -> Record -> Review -> Improve -> Adjust Workflow
```

相关技能:

- `trader-memory-core`
- `signal-postmortem`
- `backtest-expert`
- `edge-signal-aggregator`
- `skill-integration-tester`
- `dual-axis-skill-reviewer`

完成条件:

- 至少有 1 个 Plan -> Trade -> Record -> Review -> Improve 的示例运营案例
- 准备好 trade journal template 和 postmortem template
- 可以记录哪个技能产生的信号有效
- 有将失败案例连接到 workflow 或 skillset 改善的路径

## 13. 成功指标

本项目的成功不仅以盈利率或准确率衡量。应衡量的是流程是否实际被使用、被改善、能够持续。

初始观测指标:

- 作者本人持续使用 `market-regime-daily`、`core-portfolio-weekly`、`trade-memory-loop` 之一达 3 个月以上
- 至少 3 个 workflow 以 YAML 或 Markdown 定义，具有输入、输出、决策门控和记录目标
- 80% 以上的主要技能在 `skills-index.yaml` 或 `skills-inventory.yaml` 中注册，具有 category、use case、required API、difficulty、timeframe
- Trading Skills Navigator v0 对 10 个代表性用户问题，经人工评审返回合理的 skillset / workflow
- `core-portfolio`、`market-regime`、`swing-opportunity`、`trade-memory-loop` 使用的 primary-path skills 中 80% 以上通过初始质量门控
- 至少 1 个 Plan -> Trade -> Record -> Review -> Improve 的示例运营案例以公开文档形式可追踪

未来的外部指标:

- 通过 GitHub issue、PR、discussion、X 等渠道收到实际用户的 workflow 改善反馈
- 初次用户可从 README 或 quickstart 在 5 分钟内选择开始路线
- 无需 API 密钥的路线和使用 FMP / Alpaca 等的路线均经过实际验证

## 14. 设计原则

后续开发中重视以下原则：

1. **流程重于预测**
   - 重视可复现的决策流程，而非预测本身。

2. **风险优先**
   - 在候选标的和信号之前，先确认市场环境和风险预算。

3. **以人的判断为中心**
   - 不是自动交易，而是专注于增强人的判断力。

4. **能够说明理由**
   - 能够说明为什么推荐了该技能、工作流和风险设置。

5. **组合小型技能**
   - 组合小而聚焦的技能，而非制作大而全的万能技能。

6. **初学者给入口，高级者给扩展性**
   - 为不熟悉 GitHub 的人创建可进入的路径，同时为深度使用者保留可扩展的结构。

7. **记录并改善**
   - 交易不是执行完就结束，而是通过记录和复盘来改善。

8. **保持单一信息源**
   - 将技能元数据尽可能集中到单一信息源。目录、API 要求表、Navigator 的推荐、workflow manifest 均从共同的元数据生成或验证。

## 15. 短期优先事项

短期内按以下顺序推进：

- ✅ **已完成 (2026-05-09)**: 项目愿景文档（`PROJECT_VISION.md` / `PROJECT_VISION.zh.md`）
- ✅ **已完成 (2026-05-09)**: `skills-index.yaml` SSoT + validator (PR #84)
- ✅ **已完成 (2026-05-09)**: 在 `workflows/` 中添加 5 个 Core 工作流 manifest (PR #85)
- ✅ **已完成 (2026-05-09)**: 工作流文档页面自动生成 (PR #86)
- ✅ **已完成**: 为当前 index 中注册的全部技能赋予 `timeframe` / `difficulty` / `inputs` / `outputs`，并在 CI + pre-push hook 中强制执行 `--strict-metadata`
- ✅ **已完成**: Trading Skills Navigator v0（确定性 recommender + Web App snapshot fallback + manifest 驱动 setup）
- **部分完成**: 主要 skillsets 的 YAML 定义 — 核心 4 个 skillset 已实现（`market-regime` / `core-portfolio` / `swing-opportunity` / `trade-memory`）。剩余 skillset 候选（`dividend-income` / `strategy-research` / `advanced-satellite`）后续完成
- **Next**: 添加 Advanced 工作流 manifest（`risk-off-short-daily` / `earnings-weekly` / `strategy-research-pipeline`）— 在 [#216](https://github.com/tradermonty/claude-trading-skills/issues/216) 中追踪
- ✅ **已完成 (2026-05-24)**: "找到你的工作流"文档（[EN](docs/en/find-your-workflow.md) / [ZH](docs/zh/find-your-workflow.md)，PR #142）
- ✅ **已完成 (2026-05-24)**: 可公开的端到端执行示例 — 在 `examples/workflows/` 中收录了 `market-regime-daily` 和 `trade-memory-loop` 的 sample-run / sample-run-full-path（PR #141）
- ✅ **已完成 (2026-05-24)**: 从 README 链接配套项目 [Hermes Trading Research Agent Work Package](https://github.com/tradermonty/hermes-trading-research-agent-work-package)（PR #140）
- **Later**: 按需创建 bundle builder 或 recommender CLI
- **Later**: 考虑 Web 应用 POC

与其一开始就着手 Web 应用或 bundle ZIP，不如先创建结构化的知识和引导角色更为安全。

### 2026-07-01 仓库审计后的优先事项

2026-07-01 对整个仓库按照使命进行了审计，创建了以下优先级排序的 backlog。各项以 `roadmap-2026-07` 标签的 GitHub Issue 追踪。

审计得出的方针：分析/筛选层已经足够强大。与使命对照最缺乏的是承担"不大亏的机制"的 Priority A，以及支撑"growing together"的社区基础 Priority B。

**Priority A — 与使命直接相关的功能缺口（最优先开发）：**

- [#194](https://github.com/tradermonty/claude-trading-skills/issues/194) 账户级回撤熔断器（每日最大亏损 / 连败冷却 / 每周回撤停止）
- [#195](https://github.com/tradermonty/claude-trading-skills/issues/195) 交易前纪律门控（手动执行前的检查清单）
- [#196](https://github.com/tradermonty/claude-trading-skills/issues/196) 学习循环技能的 Beta 毕业（`trade-performance-coach` / `stockbee-setup-fluency-trainer`）
- [#197](https://github.com/tradermonty/claude-trading-skills/issues/197) 练习功能的通用化（VCP / CANSLIM / 突破的训练 + 模拟交易练习路径）

**Priority B — "growing together" 的社区基础：**

- [#198](https://github.com/tradermonty/claude-trading-skills/issues/198) 社区健康文件（CONTRIBUTING / CODE_OF_CONDUCT / SECURITY）
- [#199](https://github.com/tradermonty/claude-trading-skills/issues/199) 符合欢迎贡献类型的 Issue / PR 模板
- [#201](https://github.com/tradermonty/claude-trading-skills/issues/201) 带基本规则的 GitHub Discussions 开设
- [#203](https://github.com/tradermonty/claude-trading-skills/issues/203) README 精简化（维护者向内容的迁移）

**Priority C — 初学者引导：**

- [#200](https://github.com/tradermonty/claude-trading-skills/issues/200) 术语表（EN / ZH）
- [#202](https://github.com/tradermonty/claude-trading-skills/issues/202) FAQ 页面
- [#204](https://github.com/tradermonty/claude-trading-skills/issues/204) "第一周"指南
- [#206](https://github.com/tradermonty/claude-trading-skills/issues/206) 实际最低成本的明示
- [#208](https://github.com/tradermonty/claude-trading-skills/issues/208) 剩余核心工作流的执行示例
- [#209](https://github.com/tradermonty/claude-trading-skills/issues/209) 输出截图等视觉材料

**Priority D — 当前整理与质量负债：**

- [#212](https://github.com/tradermonty/claude-trading-skills/issues/212) 过时/未生成的 `.skill` 包的重新生成
- [#205](https://github.com/tradermonty/claude-trading-skills/issues/205) `trading-skills-navigator` 中过时技能数量表述的修正
- [#207](https://github.com/tradermonty/claude-trading-skills/issues/207) 已停止的技能改善循环的重启
- [#214](https://github.com/tradermonty/claude-trading-skills/issues/214) 低分 4 个技能的改善

**Priority E — 中期覆盖：**

- [#210](https://github.com/tradermonty/claude-trading-skills/issues/210) CI 测试矩阵的自动生成
- [#211](https://github.com/tradermonty/claude-trading-skills/issues/211) 为测试未整备的技能添加测试
- [#213](https://github.com/tradermonty/claude-trading-skills/issues/213) 小账户支持（PDT 规则 / 零股大小 / 交易摩擦成本）
- [#215](https://github.com/tradermonty/claude-trading-skills/issues/215) 中国税制技能（个人所得税 / 资本利得 / 外国税额抵免）
- [#216](https://github.com/tradermonty/claude-trading-skills/issues/216) 未着手的 skillset 和 Advanced 工作流 manifest

## 16. 社区与运营方针

本项目以 MIT License 公开。欢迎 Issue 和 PR，但不处理金融建议、个别买卖推荐或收益保证的请求。

欢迎的贡献:

- workflow recipe 的改善
- skill metadata 和 API 要求的修正
- 文档、starter prompt 和 quickstart 的改善
- 测试、fixture 和 runbook 的添加
- 分享实际运营中发现的陷阱和改善方案

当前的联络和讨论场所为 GitHub Issues / Pull Requests。优先保持作者本人能持续使用的质量，积累来自实际使用的改善，而非急于扩大社区规模。

## 17. 长期愿景

长期来看，本项目将培育为以下存在：

- 个人交易者能找到适合自己的策略和工作流
- 能根据市场环境调整风险
- 交易前能制定明确的计划
- 交易后能记录结果，从失败中学习
- 技能和工作流从实践中改善
- 初学者容易入门，高级用户也能深入使用

未来，用户将能够分享自己的 workflow recipe、postmortem template、strategy research note 和 skill improvement proposal，使个人交易者的实践知识转化为整个项目的改善。

本项目的本质不是给交易者"答案"。

而是创造一个交易者能锻炼判断力、管理风险、从记录中学习、持续成长的环境。

**Empower solo traders, growing together.**
