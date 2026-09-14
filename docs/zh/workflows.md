---
layout: default
title: 工作流
parent: 中文
nav_order: 4
lang_peer: /en/workflows/
permalink: /zh/workflows/
---

# 工作流
{: .no_toc }

> _本页面由 `scripts/generate_workflow_docs.py` 自动生成。请勿手动编辑。_

个人交易者操作系统的运营工作流定义。每个工作流按顺序描述使用的技能、决策关卡和产出物的流程。[`workflows/`](https://github.com/tradermonty/claude-trading-skills/tree/main/workflows) 下的定义文件为权威来源，本页面由此自动生成。

---

## 工作流一览

| 工作流 | 频率 | 预计（分钟） | API 配置 | 难度 |
|---|---|---|---|---|
| [`core-portfolio-weekly`](#core-portfolio-weekly) — 核心投资组合每周回顾 | 每周 | 60 | mixed | 初级 |
| [`kanchi-dividend-weekly`](#kanchi-dividend-weekly) — Kanchi 式股息选股每周筛选 | 每周 | 60 | mixed | 中级 |
| [`market-regime-daily`](#market-regime-daily) — 市场体制每日确认 | 每日 | 15 | no-api-basic | 初级 |
| [`monthly-performance-review`](#monthly-performance-review) — 月度绩效回顾 | 每月 | 90 | no-api-basic | 中级 |
| [`multi-asset-opportunity-daily`](#multi-asset-opportunity-daily) — 多资产投资机会每日确认 | 每日 | 45 | mixed | 中级 |
| [`shapiro-contrarian`](#shapiro-contrarian) — Shapiro 式 COT 逆向交易 | 每周 | 60 | fmp-required | 高级 |
| [`stockbee-20pct-study-daily`](#stockbee-20pct-study-daily) — Stockbee 20% 波动每日研究 | 每日 | 30 | mixed | 高级 |
| [`stockbee-ep-daily`](#stockbee-ep-daily) — Stockbee EP 每日确认 | 每日 | 40 | mixed | 高级 |
| [`stockbee-fluency-loop`](#stockbee-fluency-loop) — Stockbee 形态熟练度循环 | 每日 | 20 | no-api-basic | 中级 |
| [`swing-opportunity-daily`](#swing-opportunity-daily) — 波段交易机会每日确认 | 每日 | 40 | fmp-required | 中级 |
| [`trade-memory-loop`](#trade-memory-loop) — 交易记忆循环 | 临时 | 30 | no-api-basic | 初级 |

---

## 核心投资组合每周回顾 {#core-portfolio-weekly}

**`core-portfolio-weekly`** · 每周 · 约60分钟 · mixed · 初级

**执行时机:** 每周一次，通常在周六或周日下周开盘前执行。审查长期持仓、股息仓位和整体资产配置。

**不应执行的情况:** 不要作为每日例行任务执行。频繁的日常买卖会破坏本工作流的长期投资框架。

**必需技能:** `portfolio-manager`, `trader-memory-core`

**可选技能:** `kanchi-dividend-review-monitor`, `value-dividend-screener`, `kanchi-dividend-us-tax-accounting`

**产出物一览:**

| 产出物 | 生成步骤 | 必需 | 下游提示 |
|---|---|---|---|
| `holdings_snapshot` | 1 | 是 | `monthly-performance-review` |
| `allocation_report` | 2 | 是 | — |
| `dividend_review_findings` | 3 | 否 | — |
| `rebalance_actions` | 4 | 是 | — |
| `weekly_journal_entry` | 5 | 是 | — |

**步骤:**

**步骤 1: 获取持仓快照** → `portfolio-manager`

- 输出: `holdings_snapshot`

**步骤 2: 审查资产配置与集中度** （决策关卡） → `portfolio-manager`

- 输入: `holdings_snapshot`
- 输出: `allocation_report`
- **决策:** 各板块及个股集中度是否在目标范围内？若超出范围，交易者提议哪些具体的再平衡操作？

**步骤 3: 检查股息健康度（T1-T5 异常检查）** （可选） → `kanchi-dividend-review-monitor`

- 输入: `holdings_snapshot`
- 输出: `dividend_review_findings`

**步骤 4: 决定再平衡操作** （决策关卡） → `portfolio-manager`

- 输入: `allocation_report`, `dividend_review_findings`
- 输出: `rebalance_actions`
- **决策:** 下周是否需要执行再平衡操作？确认包含仓位规模的具体买入/卖出/持有清单。

**步骤 5: 记录每周回顾** → `trader-memory-core`

- 输入: `rebalance_actions`
- 输出: `weekly_journal_entry`

**手动审查:**

- 确认持仓快照反映了实际券商账户（Alpaca 或 CSV）的状态。
- 确认再平衡订单在券商处手动输入，而非自动执行。
- 若 dividend_review_findings 标记了 T1-T5 问题，在解决前暂停加仓。

**记录目标:** `trader-memory-core`

---

## Kanchi 式股息选股每周筛选 {#kanchi-dividend-weekly}

**`kanchi-dividend-weekly`** · 每周 · 约60分钟 · mixed · 中级

**执行时机:** 每周执行，使用 Kanchi 的五步法筛选和审查美国上市的新股息候选标的。按收益率和质量筛选，深入分析最强标的，在入场前登记有完整记录依据的候选投资假设。v1 仅覆盖美国上市的股息股票。

**不应执行的情况:** 不适用于日本股票或美国以外市场上市的股息股票——v1 不覆盖也不暗示支持。并非声称 Kanchi 式筛选是盈利策略——这是纪律性候选筛选流程，不是买入信号。不用于管理现有持仓——那是 core-portfolio-weekly 的职责；本工作流用于发现和审查新候选标的。订单不自动执行，所有买入订单在券商处手动输入。

**必需技能:** `kanchi-dividend-sop`, `trader-memory-core`

**可选技能:** `value-dividend-screener`, `dividend-growth-pullback-screener`, `kanchi-dividend-us-tax-accounting`, `kanchi-dividend-review-monitor`

**前置工作流（参考信息）:**

- `core-portfolio-weekly` 期望的产出物 `holdings_snapshot` — 当需要进行可选的税务或审查监控检查时，使用其实时持仓信息作为输入源。将该快照规范化为每个技能特定的手动输入模式；如果没有适用的输入，则跳过步骤4和5。

**手动输入契约:**

| 输入 | 必需 | 使用步骤 | Schema 参考 | 说明 |
|---|---|---|---|---|
| `tax_holdings_input` | 否 | 4 | `skills/kanchi-dividend-us-tax-accounting/references/input-schema.md` | 包含 holdings[] 的操作员提供的JSON。对于新候选标的，指定预期账户作为假设值，并省略 hold_days_in_window。这样可以确保结果保持为 assumption-required 状态，而不会被错误地标记为已确认。 |
| `review_monitor_input` | 否 | 5 | `skills/kanchi-dividend-review-monitor/references/input-schema.md` | 包含股息和风险证据的标准化现有持仓JSON。无法仅从候选股票代码推导，对于尚未持有且无监控证据的新标的，跳过步骤5。 |

**产出物一览:**

| 产出物 | 生成步骤 | 必需 | 下游提示 |
|---|---|---|---|
| `high_yield_candidates` | 1 | 否 | — |
| `pullback_candidates` | 2 | 否 | — |
| `kanchi_candidates` | 3 | 是 | — |
| `stock_memo` | 3 | 是 | — |
| `account_location_advice` | 4 | 否 | — |
| `review_queue` | 5 | 否 | — |
| `thesis_record` | 6 | 是 | `trade-memory-loop`, `monthly-performance-review` |

**步骤:**

**步骤 1: 筛选高股息候选标的** （可选） → `value-dividend-screener`

- 输出: `high_yield_candidates`

**步骤 2: 筛选股息增长型回调候选标的** （可选） → `dividend-growth-pullback-screener`

- 输出: `pullback_candidates`

**步骤 3: 执行 Kanchi 五步审查** （决策关卡） → `kanchi-dividend-sop`

- 输入: `high_yield_candidates`, `pullback_candidates`
- 输出: `kanchi_candidates`, `stock_memo`
- **决策:** 各候选标的的 Kanchi 判定是否达到可执行级别（CLEAN-PASS / PASS-CAUTION / CONDITIONAL-PASS）？HOLD-REVIEW、STEP1-RECHECK、FAIL 为 fail-closed，在此停止而不进入规模计算或登记。候选标的可使用步骤 1/2 筛选器的输出（如可用），也可使用手动提供的股票代码列表。运行此步骤不强制要求任何筛选器。

**步骤 4: 检查美国税务和账户配置处理** （可选） → `kanchi-dividend-us-tax-accounting`

- 输出: `account_location_advice`

**步骤 5: 检查现有持仓的审查触发条件** （可选） → `kanchi-dividend-review-monitor`

- 输出: `review_queue`

**步骤 6: 登记候选投资假设** （决策关卡） → `trader-memory-core`

- 输入: `kanchi_candidates`, `stock_memo`, `account_location_advice`, `review_queue`
- 输出: `thesis_record`
- **决策:** 对每个可执行的候选标的，将 kanchi_candidates 判定作为 IDEA 投资假设导入，并通过 thesis_store.link_report() 关联已保存的 stock_memo 文件。如可用，还关联税务/账户配置建议和审查监控标记，使有完整记录依据的 Kanchi 备忘录成为可审计记录的一部分，而非仅在文字中引用。下单前确认无未解决的阻碍因素、仓位规模、板块集中度和分批买入计划。在券商实际成交前不将投资假设转为 ACTIVE。此步骤仅到达 IDEA / ENTRY_READY。

**手动审查:**

- 当 Kanchi 判定为 HOLD-REVIEW、STEP1-RECHECK 或 FAIL 时为 fail-closed，不进入规模计算或投资假设登记。
- 步骤 3 的股票备忘录（基于 kanchi-dividend-sop 的 `references/stock-note-template.md` 的手写单页）不嵌入 kanchi_candidates JSON。保存为文件后，在 IDEA 投资假设登记后调用 `thesis_store.link_report(state_dir, thesis_id, "kanchi-dividend-sop", <memo_path>, date)` 进行关联。若未调用，即使已编写备忘录，投资假设的 `linked_reports` 中也不会记录。
- 不自动下单，投资假设不自动转为 ACTIVE。所有成交在券商处手动输入，之后通过 open-position 记录。
- 步骤 1/2 的筛选器为可选；手动提供的股票代码列表同样是步骤 3 的有效输入。
- 步骤 4 的税务和账户配置建议仅供参考，非权威判断。行动前请咨询税务专业人士或参阅实际券商/托管方资料确认。
- 步骤 4 需要符合关联模式的 `tax_holdings_input`，不要将筛选器的原始行直接作为税务持仓信息传入。
- 若步骤 5 的审查监控将现有持仓判定为 WARN 或 REVIEW，仅暂停该标的的加仓，不触发自动卖出。
- 步骤 5 需要符合更详细关联模式的 `review_monitor_input`。仅凭股票代码不够充分，应跳过可选步骤而非伪造缺失证据。
- 筛选器输出保存在各技能专属的 `logs/` 目录下，而非共享的 `reports/`。在步骤间连接时，将产出物 ID 视为逻辑引用而非实际文件名。
- dividend-growth-pullback-screener 的命令示例应使用 `screen_dividend_growth_rsi.py`。`screen_dividend_growth.py` 在本仓库中不存在。

**记录目标:** `trader-memory-core`

---

## 市场体制每日确认 {#market-regime-daily}

**`market-regime-daily`** · 每日 · 约15分钟 · no-api-basic · 初级

**执行时机:** 在考虑当日新的波段交易风险之前执行。在开盘前或开盘后30分钟内运行。

**不应执行的情况:** 不要将此输出用作独立的买卖信号。exposure_decision 是一种态势（allow / restrict / cash-priority），而非买卖指令。

**必需技能:** `market-breadth-analyzer`, `uptrend-analyzer`, `exposure-coach`

**可选技能:** `market-top-detector`, `macro-regime-detector`

**产出物一览:**

| 产出物 | 生成步骤 | 必需 | 下游提示 |
|---|---|---|---|
| `market_breadth_report` | 1 | 是 | `swing-opportunity-daily`, `monthly-performance-review` |
| `uptrend_report` | 2 | 是 | — |
| `top_risk_report` | 3 | 否 | — |
| `exposure_decision` | 4 | 是 | `swing-opportunity-daily` |

**步骤:**

**步骤 1: 分析市场涨跌状况** → `market-breadth-analyzer`

- 输出: `market_breadth_report`

**步骤 2: 分析上升趋势参与状况** → `uptrend-analyzer`

- 输出: `uptrend_report`

**步骤 3: 检查市场见顶风险** （可选） → `market-top-detector`

- 输出: `top_risk_report`

**步骤 4: 决定敞口策略** （决策关卡） → `exposure-coach`

- 输入: `market_breadth_report`, `uptrend_report`, `top_risk_report`
- 输出: `exposure_decision`
- **决策:** 根据今日的涨跌状况、上升趋势参与度和市场见顶风险，新的波段交易风险应设为 allow、restrict 还是 cash-priority？

**手动审查:**

- 确认输出未被用作买卖信号。
- 确认敞口应减少、维持还是增加。
- 若 exposure_decision 为 restrictive，则推迟执行 swing-opportunity-daily。

**记录目标:** `trader-memory-core`

---

## 月度绩效回顾 {#monthly-performance-review}

**`monthly-performance-review`** · 每月 · 约90分钟 · no-api-basic · 中级

**执行时机:** 每月第一个周末，审查上月已平仓头寸、未平仓投资假设的健康度及流程改进。完成计划 -> 交易 -> 记录 -> 回顾 -> 改进的闭环。

**不应执行的情况:** 即使是亏损月份也不要跳过——这恰恰是回顾最重要的时候。为过滤噪音特意设为月度频率，不要按周执行。

**必需技能:** `trader-memory-core`, `signal-postmortem`

**可选技能:** `trade-performance-coach`, `backtest-expert`, `dual-axis-skill-reviewer`

**产出物一览:**

| 产出物 | 生成步骤 | 必需 | 下游提示 |
|---|---|---|---|
| `monthly_aggregate` | 1 | 是 | — |
| `aggregate_postmortem` | 2 | 是 | — |
| `monthly_performance_coach_report` | 3 | 否 | — |
| `monthly_behavior_patterns` | 3 | 否 | — |
| `next_month_operating_rules` | 3 | 否 | — |
| `hypothesis_revalidation` | 4 | 否 | — |
| `skill_review_findings` | 5 | 否 | — |
| `monthly_decision_log` | 6 | 是 | — |
| `rule_changes_for_next_month` | 6 | 是 | — |
| `skill_improvement_backlog` | 6 | 否 | — |

**步骤:**

**步骤 1: 汇总当月交易和投资假设** → `trader-memory-core`

- 输出: `monthly_aggregate`

**步骤 2: 按月度模式进行复盘分析** （决策关卡） → `signal-postmortem`

- 输入: `monthly_aggregate`
- 输出: `aggregate_postmortem`
- **决策:** 当月结果中出现了哪些重复模式？按投资假设质量、执行、市场环境和随机性分类。

**步骤 3: 月度回顾流程、风险和行为模式** （可选） （决策关卡） → `trade-performance-coach`

- 输入: `monthly_aggregate`, `aggregate_postmortem`
- 输出: `monthly_performance_coach_report`, `monthly_behavior_patterns`, `next_month_operating_rules`
- **决策:** 下月操作规则中，哪些应采纳、修改、推迟或仅作记录？

**步骤 4: 通过回测重新验证假设** （可选） → `backtest-expert`

- 输入: `aggregate_postmortem`
- 输出: `hypothesis_revalidation`

**步骤 5: 审查哪些技能有效、哪些适得其反** （可选） → `dual-axis-skill-reviewer`

- 输入: `aggregate_postmortem`
- 输出: `skill_review_findings`

**步骤 6: 生成决策记录和规则变更** （决策关卡） → `trader-memory-core`

- 输入: `aggregate_postmortem`, `hypothesis_revalidation`, `skill_review_findings`
- 输出: `monthly_decision_log`, `rule_changes_for_next_month`, `skill_improvement_backlog`
- **决策:** 基于当月证据，下月需要变更哪些具体规则？交易侧规则与仓库侧改进应分别处理。

**手动审查:**

- 区分流程改进（规则变更）与偶然导致的结果。
- 交易侧的规则变更适用于交易者下月的行为。
- 技能侧的改进是仓库改进候选项，不一定会实施。
- 不仅要添加新规则，还要考虑删除或降级无效的规则。

**最终输出:**

- `monthly_decision_log` — 按类别整理的成功交易与失败交易
- `rule_changes_for_next_month` — 仓位规模、入场规则和体制关卡的调整
- `skill_improvement_backlog` — 反馈至仓库改进循环的可选建议（技能/工作流）

**记录目标:** `trader-memory-core`

---

## 多资产投资机会每日确认 {#multi-asset-opportunity-daily}

**`multi-asset-opportunity-daily`** · 每日 · 约45分钟 · mixed · 中级

**执行时机:** 仅在 market-regime-daily 给出非限制性 exposure_decision 后执行。横跨宏观、主题和新闻，提取股票、通过股票代理的商品以及期权表达的投资想法，汇总为排序后的假设卡片。

**不应执行的情况:** 当最新的 market-regime-daily 的 exposure_decision 为 cash-priority 时不执行。不将假设卡片视为买卖信号——卡片带有 manual_review_required，在动用资金前须经人工审批。外汇输出仅供研究使用，绝不接入券商。

**必需技能:** `macro-regime-detector`, `theme-detector`, `trade-hypothesis-ideator`, `position-sizer`, `trader-memory-core`

**可选技能:** `market-news-analyst`, `market-environment-analysis`, `sector-analyst`, `scenario-analyzer`, `stanley-druckenmiller-investment`

**前置工作流（参考信息）:**

- `market-regime-daily` 期望的产出物 `exposure_decision` — 探索多资产投资机会需要非限制性的敞口策略。 cash-priority 日跳过执行，restrict 日缩小范围。

**产出物一览:**

| 产出物 | 生成步骤 | 必需 | 下游提示 |
|---|---|---|---|
| `macro_regime_brief` | 1 | 是 | `swing-opportunity-daily`, `monthly-performance-review` |
| `hot_themes` | 2 | 是 | `swing-opportunity-daily` |
| `catalyst_news_brief` | 3 | 否 | — |
| `hypothesis_cards` | 4 | 是 | `swing-opportunity-daily`, `trade-memory-loop` |
| `sized_hypotheses` | 5 | 是 | — |
| `opportunity_journal_entries` | 6 | 是 | `trade-memory-loop`, `monthly-performance-review` |

**步骤:**

**步骤 1: 更新宏观体制状况** → `macro-regime-detector`

- 输出: `macro_regime_brief`

**步骤 2: 检测热门主题与板块轮动** → `theme-detector`

- 输入: `macro_regime_brief`
- 输出: `hot_themes`

**步骤 3: 调查新闻与催化剂动态** （可选） → `market-news-analyst`

- 输入: `hot_themes`
- 输出: `catalyst_news_brief`

**步骤 4: 生成排序后的假设卡片** （决策关卡） → `trade-hypothesis-ideator`

- 输入: `macro_regime_brief`, `hot_themes`, `catalyst_news_brief`
- 输出: `hypothesis_cards`
- **决策:** 每个假设中，第一层（宏观）是否与第二层（主题）一致，且市场定价状况仍有利？拒绝与共识差距不明确或已消失的卡片。

**步骤 5: 对假设卡片应用基于风险的仓位规模** → `position-sizer`

- 输入: `hypothesis_cards`
- 输出: `sized_hypotheses`

**步骤 6: 保存为 IDEA / ENTRY_READY 记录** （决策关卡） → `trader-memory-core`

- 输入: `hypothesis_cards`, `sized_hypotheses`
- 输出: `opportunity_journal_entries`
- **决策:** 哪些假设应从 IDEA 推进至 ENTRY_READY，哪些保持为待进一步确认的 IDEA，哪些应拒绝？

**手动审查:**

- 确认宏观体制概述不与 market-regime-daily 的 exposure_decision 矛盾。
- 确认每个假设都有书面投资依据和退出条件。
- 确认仓位规模遵守个股和板块的投资组合风险上限。
- 确认外汇相关输出的 research_only=true，绝不接入券商。
- 确认 IDEA 到 ENTRY_READY 的转换已明确且经过审查。

**记录目标:** `trader-memory-core`

---

## Shapiro 式 COT 逆向交易 {#shapiro-contrarian}

**`shapiro-contrarian`** · 每周 · 约60分钟 · fmp-required · 高级

**执行时机:** 在 CFTC 交易者持仓报告发布后（每周五美东时间下午 3:30 左右，反映周二的持仓）按周执行。从约 65 个期货市场中筛选投机头寸的极端拥挤，仅在新闻反应失败和周线价格反转均得到确认时，才生成带合约数量的逆向交易计划。

**不应执行的情况:** 不在盘中或超过每周一次的频率执行。COT 数据按周更新，优势来源于持仓状况而非盘中价格波动。不要仅凭拥挤极端值交易。在计算仓位规模之前，拥挤、新闻反应失败和价格走势必须全部为 CONFIRMED，关卡须达到 READY_FOR_PLAN。 COT 仅覆盖 CFTC 期货市场，不适用于股票。

**必需技能:** `cot-contrarian-detector`, `news-reaction-failure-analyzer`, `technical-analyst`, `contrarian-setup-gate`, `futures-position-sizer`, `trader-memory-core`

**可选技能:** （无）

**产出物一览:**

| 产出物 | 生成步骤 | 必需 | 下游提示 |
|---|---|---|---|
| `cot_crowding_report` | 1 | 是 | — |
| `news_failure_verdict` | 2 | 是 | — |
| `price_action_confirmation_report` | 3 | 是 | — |
| `contrarian_setup_gate_report` | 4 | 是 | — |
| `futures_position_size` | 5 | 是 | — |
| `contrarian_thesis_entry` | 6 | 是 | `trade-memory-loop`, `monthly-performance-review` |

**步骤:**

**步骤 1: 筛选 COT 拥挤度** （决策关卡） → `cot-contrarian-detector`

- 输出: `cot_crowding_report`
- **决策:** 本周有哪些期货市场处于 3 年 COT 指数的拥挤极端值（CROWDED_LONG / CROWDED_SHORT）？拥挤本身不构成信号，仅将极端值推进至下一步。

**步骤 2: 检查新闻反应失败** （决策关卡） → `news-reaction-failure-analyzer`

- 输入: `cot_crowding_report`
- 输出: `news_failure_verdict`
- **决策:** 对于每个拥挤市场，价格是否未能对有利于多数方向的新闻做出反应（判定为 CONFIRMED）？使用通过 WebSearch 整理的一手来源/通讯社事件文件，排除 NOT_CONFIRMED / INSUFFICIENT_EVIDENCE 的市场。

**步骤 3: 确认周线价格反转** （决策关卡） → `technical-analyst`

- 输入: `cot_crowding_report`
- 输出: `price_action_confirmation_report`
- **决策:** 在周线图上是否存在与多数方向相反的反转（关键反转、突破失败或极端值失败）且被判定为 CONFIRMED，并有明确的波段止损？拒绝 NOT_CONFIRMED / INSUFFICIENT_DATA。

**步骤 4: 综合逆向交易形态关卡判定** （决策关卡） → `contrarian-setup-gate`

- 输入: `cot_crowding_report`, `news_failure_verdict`, `price_action_confirmation_report`
- 输出: `contrarian_setup_gate_report`
- **决策:** 关卡是否达到 fail-closed 的 READY_FOR_PLAN（拥挤、新闻反应失败和价格走势全部为 CONFIRMED）？仅将 READY_FOR_PLAN 的市场推进至仓位规模计算；CROWDED / WATCHING_PRICE / REJECTED / INSUFFICIENT_EVIDENCE 在此停止。

**步骤 5: 计算期货仓位规模** → `futures-position-sizer`

- 输入: `contrarian_setup_gate_report`
- 输出: `futures_position_size`

**步骤 6: 登记逆向交易投资假设** （决策关卡） → `trader-memory-core`

- 输入: `futures_position_size`, `contrarian_setup_gate_report`
- 输出: `contrarian_thesis_entry`
- **决策:** 仅登记 sizer 输出 sizing_status 为 SIZED 的逆向交易，排除 NO_TRADE 结果，按以下顺序操作：(1) 先创建 IDEA 投资假设（手动导入或 register()； attach-futures-position 仅附加到现有假设，不创建新假设）。 (2) 通过 attach-futures-position 附加 SIZED 报告，将合约数、方向、乘数、 USD 货币和风险保存到仓位。(3) 通过 thesis_store.link_report() 将 cot_crowding_report、news_failure_verdict、price_action_confirmation_report 和 contrarian_setup_gate_report 关联到投资假设，使证据链可审计。 (4) 仅在券商实际成交后通过 open-position 转为 ACTIVE。确认每笔交易风险与 sizer 输出一致，且投资组合整体风险敞口在预算范围内。

**手动审查:**

- COT 数据有 3 天延迟（周二快照，周五发布）。将拥挤判定视为周二收盘时的状态，而非实时数据。
- 拥挤是前提条件，不是交易信号。在计算仓位规模之前须确认新闻反应失败和价格走势。
- 新闻反应失败事件须从带有真实 URL 的一手来源/通讯社信息中筛选，不得捏造。INSUFFICIENT_EVIDENCE 不得推进。
- 计算仓位规模之前确认关卡的 setup_status 为 READY_FOR_PLAN。sizer 会拒绝非 READY 的关卡，若拒绝则确认原因。
- 步骤 5 除 contrarian_setup_gate_report 外，还始终需要操作员指定的 --entry、--account-size 和 --risk-pct。关卡和 sizer 均不推导这些值，须在执行 futures-position-sizer 前准备好。
- 下单前验证 sizer 的合约数和每合约风险，确认投资组合整体风险敞口在预算范围内。
- 期货保证金取决于券商和时点，本流程不计算。交易前在券商处确认初始保证金和维持保证金。
- 所有订单在券商处手动输入，不自动执行。在 contrarian-position-monitor 上线前，COT 归一化、止损和投资假设失效的监控也需手动完成。
- 关卡的 entry_trigger 和 sizer 的计划入场价不是实际成交价。保存包含计划入场价的 SIZED 报告本身。手动导入来源也将 entry_price 保存在 origin.raw_provenance.entry_price 中。实际成交前不写入 entry.actual_price。
- 在券商实际成交前不将投资假设转为 ACTIVE（open-position）。步骤 6 仅到达附加了期货仓位的 IDEA / ENTRY_READY，不自动下单。

**记录目标:** `trader-memory-core`

---

## Stockbee 20% 波动每日研究 {#stockbee-20pct-study-daily}

**`stockbee-20pct-study-daily`** · 每日 · 约30分钟 · mixed · 高级

**执行时机:** 在美股收盘后或历史数据补充研究时执行。检测 +20% / -20% 的价格波动，分类事件背景，更新已到期的观察结果，积累极端市场波动的模型手册。

**不应执行的情况:** 不用作买卖信号或自动执行工作流。不从少量样本、仅限当前标的集合的分析或缺少生存偏差和数据质量注记的事件中采纳新规则。

**必需技能:** `stockbee-20pct-study`

**可选技能:** `trader-memory-core`, `edge-candidate-agent`, `edge-hint-extractor`, `stockbee-episodic-pivot-analyzer`, `theme-detector`, `backtest-expert`

**产出物一览:**

| 产出物 | 生成步骤 | 必需 | 下游提示 |
|---|---|---|---|
| `twenty_pct_mover_events` | 1 | 是 | — |
| `classified_event_study` | 2 | 是 | — |
| `matured_event_outcomes` | 3 | 是 | — |
| `twenty_pct_cohort_summary` | 4 | 是 | `monthly-performance-review` |
| `edge_hints_yaml` | 4 | 否 | `monthly-performance-review` |
| `accepted_lessons_log` | 5 | 否 | `monthly-performance-review` |

**步骤:**

**步骤 1: 每日筛选 +20% / -20% 波动标的** → `stockbee-20pct-study`

- 输出: `twenty_pct_mover_events`

**步骤 2: 分类催化剂、图表状况、主题集群和风险标记** → `stockbee-20pct-study`

- 输入: `twenty_pct_mover_events`
- 输出: `classified_event_study`

**步骤 3: 更新历史 20% 研究记录的到期后结果** → `stockbee-20pct-study`

- 输入: `classified_event_study`
- 输出: `matured_event_outcomes`

**步骤 4: 汇总队列并输出优势候选** （决策关卡） → `stockbee-20pct-study`

- 输入: `matured_event_outcomes`
- 输出: `twenty_pct_cohort_summary`, `edge_hints_yaml`
- **决策:** 20% 波动模式中，哪些具有足够的样本量、稳定的结果趋势和现实的可执行性，可从纯观察记录推进至优势研究？

**步骤 5: 记录已采纳的经验教训** （可选） （决策关卡） → `trader-memory-core`

- 输入: `twenty_pct_cohort_summary`, `edge_hints_yaml`
- 输出: `accepted_lessons_log`
- **决策:** 哪些发现应作为操作规则候选采纳，哪些拒绝，哪些待更多案例？

**手动审查:**

- 采纳模式之前，审查代表性的成功和失败图表。
- 区分观察、研究假设和可执行的交易计划。
- 不含退市标的的当前集合的历史分析须标注存在生存偏差。
- 采纳队列规则之前，须满足明确的样本量阈值。
- 不临时更改规则，将已采纳的经验教训传递至 monthly-performance-review。

**记录目标:** `trader-memory-core`

---

## Stockbee EP 每日确认 {#stockbee-ep-daily}

**`stockbee-ep-daily`** · 每日 · 约40分钟 · mixed · 高级

**执行时机:** 在财报/新闻密集日且市场体制工作流允许新风险后执行，或在出现改变格局的重大催化剂时临时执行。对 Day 1 的 Episodic Pivot 候选标的进行分类，判断其今日可执行、列入延迟 EP 观察名单还是移交给 PEAD。

**不应执行的情况:** 不在无催化剂输入的情况下作为机械式筛选器运行。不用于绕过市场体制关卡、图表验证、仓位规模计算或催化剂手动确认。

**必需技能:** `drawdown-circuit-breaker`, `stockbee-episodic-pivot-analyzer`, `technical-analyst`, `position-sizer`, `trader-memory-core`, `pre-trade-discipline-gate`

**可选技能:** `earnings-trade-analyzer`, `stockbee-momentum-burst-screener`, `pead-screener`, `theme-detector`, `breakout-trade-planner`

**前置工作流（参考信息）:**

- `market-regime-daily` 期望的产出物 `exposure_decision` — 新的 EP 交易仍须遵守市场体制的敞口关卡。

**产出物一览:**

| 产出物 | 生成步骤 | 必需 | 下游提示 |
|---|---|---|---|
| `circuit_breaker_decision` | 1 | 是 | — |
| `earnings_candidates` | 2 | 否 | — |
| `momentum_burst_candidates` | 3 | 否 | — |
| `episodic_pivot_candidates` | 4 | 是 | — |
| `pead_handoff_candidates` | 4 | 否 | `swing-opportunity-daily` |
| `delayed_ep_watchlist` | 4 | 否 | — |
| `validated_ep_setups` | 5 | 是 | — |
| `ep_position_sizing` | 6 | 是 | — |
| `ep_trade_plan` | 7 | 否 | — |
| `ep_journal_entry` | 8 | 是 | `trade-memory-loop` |
| `pre_trade_discipline_decision` | 9 | 是 | — |

**步骤:**

**步骤 1: 检查账户熔断机制** （决策关卡） → `drawdown-circuit-breaker`

- 输出: `circuit_breaker_decision`
- **决策:** 对于今日的新 EP 交易风险，账户熔断机制是否处于 TRADING_ALLOWED 状态？

**步骤 2: 可选：筛选财报候选标的** （可选） → `earnings-trade-analyzer`

- 输出: `earnings_candidates`

**步骤 3: 可选：运行动量确认扫描** （可选） → `stockbee-momentum-burst-screener`

- 输出: `momentum_burst_candidates`

**步骤 4: 分析 Day 1 Episodic Pivot 候选标的** （决策关卡） → `stockbee-episodic-pivot-analyzer`

- 输入: `earnings_candidates`, `momentum_burst_candidates`
- 输出: `episodic_pivot_candidates`, `pead_handoff_candidates`, `delayed_ep_watchlist`
- **决策:** 哪些候选标的具有真正改变格局的催化剂且有价量确认？区分 ACTIONABLE_DAY1 和 DELAYED_EP_WATCH，拒绝仅因标题反应的低质量价格波动。

**步骤 5: 验证 EP 图表质量** （决策关卡） → `technical-analyst`

- 输入: `episodic_pivot_candidates`
- 输出: `validated_ep_setups`
- **决策:** 图表是否显示清晰的 EP 反应，且收盘质量、流动性和至 EP 当日低点的风险可接受？

**步骤 6: 计算 EP 仓位规模** → `position-sizer`

- 输入: `validated_ep_setups`
- 输出: `ep_position_sizing`

**步骤 7: 可选：制定 EP 交易计划** （可选） → `breakout-trade-planner`

- 输入: `validated_ep_setups`, `ep_position_sizing`
- 输出: `ep_trade_plan`

**步骤 8: 登记 EP 投资假设或观察名单条目** （决策关卡） → `trader-memory-core`

- 输入: `validated_ep_setups`, `ep_position_sizing`, `ep_trade_plan`
- 输出: `ep_journal_entry`
- **决策:** 哪些候选标的应建立有效投资假设，哪些列入延迟 EP / PEAD 观察，哪些即使初始评分较高也应忽略？

**步骤 9: 执行 EP 手动交易纪律关卡** （决策关卡） → `pre-trade-discipline-gate`

- 输入: `circuit_breaker_decision`, `ep_journal_entry`, `ep_position_sizing`, `ep_trade_plan`
- 输出: `pre_trade_discipline_decision`
- **决策:** 在向券商提交手动订单之前，ACTIONABLE_DAY1 或 ENTRY_READY 的 EP 候选标的是否通过了书面计划、预设止损、仓位规模、近期亏损、市场体制和熔断机制的纪律检查？延迟 EP、PEAD 移交、忽略或拒绝的候选标的视为无交易日志记录，而非订单批准。

**手动审查:**

- 执行前确认 market-regime-daily 允许承担新风险。
- 在分析新 EP 交易风险之前，确认 circuit_breaker_decision 为 TRADING_ALLOWED。
- 手动验证催化剂。本工作流本身不发现或验证新闻真实性。
- 仅有分析师评级或故事驱动的 EP 除非价量确认特别强劲，否则视为低质量。
- 仅在该距离可设置合理仓位规模时，才将 EP 当日低点作为默认止损参考。
- 过度延伸的财报/业绩指引 EP 不在 Day 1 追入，转入 PEAD 监控。
- 向券商提交手动订单前确认 pre_trade_discipline_decision 为 GO；观察名单和 PEAD 移交候选标的不视为订单批准。
- 所有订单在券商处手动输入，不自动执行。

**记录目标:** `trader-memory-core`

---

## Stockbee 形态熟练度循环 {#stockbee-fluency-loop}

**`stockbee-fluency-loop`** · 每日 · 约20分钟 · no-api-basic · 中级

**执行时机:** 在 stockbee-momentum-burst-screener 生成候选报告后执行，以及在 3/5 个交易日观察窗口到期后再次执行。构建 Stockbee Momentum Burst 的模型手册，提升交易者的形态识别能力。

**不应执行的情况:** 不用作执行工作流或信号服务。不从少量样本中更改交易规则。在采用或过滤形态标签之前，须有足够的已观察案例和手动图表审查。

**必需技能:** `stockbee-setup-fluency-trainer`

**可选技能:** `trader-memory-core`, `signal-postmortem`, `backtest-expert`

**产出物一览:**

| 产出物 | 生成步骤 | 必需 | 下游提示 |
|---|---|---|---|
| `model_book_ingest` | 1 | 是 | — |
| `matured_setup_outcomes` | 2 | 是 | — |
| `setup_fluency_summary` | 3 | 是 | `monthly-performance-review` |
| `rule_candidates` | 3 | 否 | `monthly-performance-review` |
| `accepted_lessons_log` | 4 | 否 | `monthly-performance-review` |

**步骤:**

**步骤 1: 导入最新的 Stockbee 动量爆发候选标的** → `stockbee-setup-fluency-trainer`

- 输出: `model_book_ingest`

**步骤 2: 更新已到期的 3 日和 5 日观察结果** → `stockbee-setup-fluency-trainer`

- 输入: `model_book_ingest`
- 输出: `matured_setup_outcomes`

**步骤 3: 汇总形态队列和规则候选** （决策关卡） → `stockbee-setup-fluency-trainer`

- 输入: `matured_setup_outcomes`
- 输出: `setup_fluency_summary`, `rule_candidates`
- **决策:** 哪些形态标签有足够的已观察案例来决定采用、降级或继续监控？更改交易规则之前须审查代表性图表。

**步骤 4: 记录已采纳的经验教训** （可选） （决策关卡） → `trader-memory-core`

- 输入: `setup_fluency_summary`, `rule_candidates`
- 输出: `accepted_lessons_log`
- **决策:** 哪些发现应作为操作规则变更采纳，哪些仍为待更多案例的纯观察记录？

**手动审查:**

- 采纳规则变更前，审查代表性的成功和失败图表。
- 区分证据与执行决策。本工作流记录形态行为趋势，不处理实际盈亏。
- 特别是在市场体制变化时，须明确样本量阈值。
- 不每日临时添加规则，将已采纳的经验教训传递至 monthly-performance-review。

**记录目标:** `trader-memory-core`

---

## 波段交易机会每日确认 {#swing-opportunity-daily}

**`swing-opportunity-daily`** · 每日 · 约40分钟 · fmp-required · 中级

**执行时机:** 仅在 market-regime-daily 给出非限制性敞口决策后执行。筛选波段交易候选标的并制定入场计划。

**不应执行的情况:** 当最新的 market-regime-daily exposure_decision 为 cash-priority 或 restrictive 时不执行。不要绕过体制关卡将其作为独立筛选器使用。

**必需技能:** `vcp-screener`, `drawdown-circuit-breaker`, `technical-analyst`, `position-sizer`, `trader-memory-core`, `pre-trade-discipline-gate`

**可选技能:** `stockbee-momentum-burst-screener`, `stockbee-exhaustion-hammer-screener`, `canslim-screener`, `breakout-trade-planner`, `theme-detector`

**前置工作流（参考信息）:**

- `market-regime-daily` 期望的产出物 `exposure_decision` — 承担新的波段交易风险需要非限制性的敞口决策。在 cash-priority 或 restrictive 的日子跳过此工作流。

**产出物一览:**

| 产出物 | 生成步骤 | 必需 | 下游提示 |
|---|---|---|---|
| `circuit_breaker_decision` | 1 | 是 | — |
| `vcp_candidates` | 2 | 是 | — |
| `momentum_burst_candidates` | 3 | 否 | — |
| `exhaustion_hammer_candidates` | 4 | 否 | — |
| `canslim_candidates` | 5 | 否 | — |
| `theme_candidates` | 6 | 否 | — |
| `validated_setups` | 7 | 是 | — |
| `position_sizing` | 8 | 是 | — |
| `trade_plans` | 9 | 否 | `trade-memory-loop` |
| `candidate_journal_entry` | 10 | 是 | `trade-memory-loop` |
| `pre_trade_discipline_decision` | 11 | 是 | — |

**步骤:**

**步骤 1: 检查账户熔断机制** （决策关卡） → `drawdown-circuit-breaker`

- 输出: `circuit_breaker_decision`
- **决策:** 对于今日的新交易风险，账户熔断机制是否处于 TRADING_ALLOWED 状态？

**步骤 2: 运行 VCP 筛选器** → `vcp-screener`

- 输出: `vcp_candidates`

**步骤 3: 运行 Stockbee 动量爆发筛选器** （可选） → `stockbee-momentum-burst-screener`

- 输出: `momentum_burst_candidates`

**步骤 4: 运行 Stockbee 衰竭锤筛选器** （可选） → `stockbee-exhaustion-hammer-screener`

- 输出: `exhaustion_hammer_candidates`

**步骤 5: 运行 CANSLIM 筛选器** （可选） → `canslim-screener`

- 输出: `canslim_candidates`

**步骤 6: 主题检测交叉验证** （可选） → `theme-detector`

- 输出: `theme_candidates`

**步骤 7: 在周线图上验证形态** （决策关卡） → `technical-analyst`

- 输入: `vcp_candidates`, `momentum_burst_candidates`, `exhaustion_hammer_candidates`, `canslim_candidates`, `theme_candidates`
- 输出: `validated_setups`
- **决策:** 哪些候选标的具有清晰的周线形态（Stage 2 上升趋势、紧凑底部、或从受控底部的 Stockbee 式区间扩张）并通过手动图表审核？对于衰竭锤形态，确认回调未破坏投资假设且至当日低点的风险可接受。拒绝未通过的候选标的。

**步骤 8: 计算仓位规模** → `position-sizer`

- 输入: `validated_setups`
- 输出: `position_sizing`

**步骤 9: 制定入场计划** （可选） → `breakout-trade-planner`

- 输入: `validated_setups`, `position_sizing`
- 输出: `trade_plans`

**步骤 10: 在日志中登记投资假设** （决策关卡） → `trader-memory-core`

- 输入: `position_sizing`, `trade_plans`
- 输出: `candidate_journal_entry`
- **决策:** 为每个通过验证的候选标的登记包含入场价、止损价和目标价的投资假设。确认每笔交易的风险与 position-sizer 输出一致，且投资组合整体风险敞口在预算范围内。

**步骤 11: 执行手动交易纪律关卡** （决策关卡） → `pre-trade-discipline-gate`

- 输入: `candidate_journal_entry`, `position_sizing`, `trade_plans`, `circuit_breaker_decision`
- 输出: `pre_trade_discipline_decision`
- **决策:** 在向券商提交手动订单之前，每个可执行的候选标的是否通过了书面计划、预设止损、仓位规模、近期亏损、市场体制和熔断机制的纪律检查？

**手动审查:**

- 执行前确认 market-regime-daily 的 exposure_decision 允许承担新风险。
- 在筛选或计算新候选标的规模之前，确认 circuit_breaker_decision 为 TRADING_ALLOWED。
- 即使通过了筛选器，周线形态不清晰的候选标的也应拒绝。
- Stockbee 动量爆发输出仅用于候选生成；必须进行图表验证和风险距离审查。
- Stockbee 衰竭锤输出仅用于候选生成；确认回调并非由破坏投资假设的新闻引起，并核实至当日低点的风险。
- 下单前确认投资组合整体风险敞口在预算范围内。
- 向券商提交手动订单前确认 pre_trade_discipline_decision 为 GO。
- 所有订单均在券商处手动输入，不自动执行。

**记录目标:** `trader-memory-core`

---

## 交易记忆循环 {#trade-memory-loop}

**`trade-memory-loop`** · 临时 · 约30分钟 · no-api-basic · 初级

**执行时机:** 每次全部或部分平仓时执行。记录结果并生成复盘分析，可选地回顾流程、风险、执行和行为模式，并通过回测重新验证原始假设。

**不应执行的情况:** 平仓前不执行。如需更新未平仓的投资假设，请直接使用 trader-memory-core。即使是盈利交易，平仓后也不要跳过此循环。

**必需技能:** `trader-memory-core`, `signal-postmortem`

**可选技能:** `trade-performance-coach`, `backtest-expert`

**产出物一览:**

| 产出物 | 生成步骤 | 必需 | 下游提示 |
|---|---|---|---|
| `closed_thesis_record` | 1 | 是 | — |
| `postmortem_findings` | 2 | 是 | `monthly-performance-review` |
| `performance_coach_report` | 3 | 否 | `monthly-performance-review` |
| `next_session_operating_rules` | 3 | 否 | `monthly-performance-review` |
| `backtest_validation` | 4 | 否 | — |
| `lessons_log_entry` | 5 | 是 | `monthly-performance-review` |

**步骤:**

**步骤 1: 记录已平仓交易的结果** → `trader-memory-core`

- 输出: `closed_thesis_record`

**步骤 2: 生成复盘分析** （决策关卡） → `signal-postmortem`

- 输入: `closed_thesis_record`
- 输出: `postmortem_findings`
- **决策:** 结果的根本原因是投资假设质量、执行、市场环境还是随机性？分类并记录。

**步骤 3: 回顾流程、风险和行为模式** （可选） （决策关卡） → `trade-performance-coach`

- 输入: `closed_thesis_record`, `postmortem_findings`
- 输出: `performance_coach_report`, `next_session_operating_rules`
- **决策:** 下一交易时段的操作规则中，哪些应采纳、修改、推迟或仅作记录？

**步骤 4: 通过回测重新验证假设** （可选） → `backtest-expert`

- 输入: `postmortem_findings`
- 输出: `backtest_validation`

**步骤 5: 将经验教训追记到日志** → `trader-memory-core`

- 输入: `postmortem_findings`, `backtest_validation`
- 输出: `lessons_log_entry`

**手动审查:**

- 诚实评估盈利是源于投资假设还是纯粹的运气。
- 诚实评估亏损是源于投资假设的缺陷还是执行不当。
- 不要将随机事件合理化为技能或失败。

**记录目标:** `trader-memory-core`

---
