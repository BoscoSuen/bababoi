---
layout: default
title: 技能集
parent: 中文
nav_order: 5
lang_peer: /en/skillsets/
permalink: /zh/skillsets/
---

# 技能集
{: .no_toc }

> _本页面由 `scripts/generate_skillset_docs.py` 自动生成。请勿手动编辑。_

个人交易者操作系统的目标导向技能集合。技能集是按类别组织的技能包（必需 / 推荐 / 可选），并关联到将其运营化的工作流（“为这个目标需要安装什么”的层次）。[`skillsets/`](https://github.com/tradermonty/claude-trading-skills/tree/main/skillsets) 下的 manifest 为权威来源，本页面由此自动生成。

**翻译说明：** 本页面仅对标题标签进行了中文化。manifest 正文（`when_to_use` / `when_not_to_use` 等）直接显示英文原文。正文的中文化为后续计划（在 manifest 中添加 `*_zh` 字段，或设置独立的本地化层）。

---

## 技能集一览

| 技能集 | 时间框架 | API 配置 | 难度 | 关联工作流 |
|---|---|---|---|---|
| [`core-portfolio`](#core-portfolio) — Core Portfolio | weekly | mixed | beginner | `core-portfolio-weekly` |
| [`market-regime`](#market-regime) — Market Regime | daily | no-api-basic | beginner | `market-regime-daily` |
| [`swing-opportunity`](#swing-opportunity) — Swing Opportunity | daily | fmp-required | intermediate | `swing-opportunity-daily` |
| [`trade-memory`](#trade-memory) — Trade Memory | event-driven | no-api-basic | beginner | `trade-memory-loop`, `monthly-performance-review` |

---

## Core Portfolio {#core-portfolio}

**`core-portfolio`** · weekly · mixed · beginner

**适用场景:** The long-term core sleeve: review holdings, dividend health, and overall allocation once a week. Use to keep the buy-and-hold / dividend book healthy and decide deliberate rebalance actions. Operationalized weekly by the core-portfolio-weekly workflow.

**不适用场景:** Do not run this as a daily routine — daily portfolio churn defeats the long-term framing. Do not use it to chase short-term swing setups; that is the swing-opportunity sleeve gated by market-regime.

**目标用户:** `long-term-investor`, `dividend-investor`

**必需技能:** `portfolio-manager`, `trader-memory-core`

**推荐技能:** `kanchi-dividend-review-monitor`, `value-dividend-screener`, `kanchi-dividend-us-tax-accounting`

**可选技能:** `dividend-growth-pullback-screener`, `kanchi-dividend-sop`

**关联工作流:** `core-portfolio-weekly`

---

## Market Regime {#market-regime}

**`market-regime`** · daily · no-api-basic · beginner

**适用场景:** The shared risk layer for every trading day. Use before considering new swing-trade risk to decide today's exposure posture (allow / restrict / cash-priority) from breadth, uptrend participation, and top-risk signals. Operationalized daily by the market-regime-daily workflow.

**不适用场景:** Do not treat this bundle's output as a standalone buy/sell signal — the exposure decision is a posture, not a directive. Do not skip it and run swing-opportunity work directly; the regime gate comes first.

**目标用户:** `part-time-swing-trader`, `growth-investor`

**必需技能:** `market-breadth-analyzer`, `uptrend-analyzer`, `exposure-coach`

**推荐技能:** `market-top-detector`, `macro-regime-detector`

**可选技能:** `breadth-chart-analyst`, `sector-analyst`, `market-environment-analysis`, `market-news-analyst`, `downtrend-duration-analyzer`, `us-market-bubble-detector`

**关联工作流:** `market-regime-daily`

---

## Swing Opportunity {#swing-opportunity}

**`swing-opportunity`** · daily · fmp-required · intermediate

**适用场景:** The satellite swing sleeve: generate and validate swing-trade candidates and build risk-sized entry plans. Use only on days the market-regime sleeve has allowed new risk. Operationalized by the swing-opportunity-daily workflow (prerequisite: market-regime-daily exposure decision).

**不适用场景:** Do not run when the latest market-regime exposure decision is cash-priority or restrictive. Do not use the screeners standalone without the regime gate and position sizing.

**目标用户:** `part-time-swing-trader`

**必需技能:** `vcp-screener`, `drawdown-circuit-breaker`, `technical-analyst`, `position-sizer`, `trader-memory-core`, `pre-trade-discipline-gate`

**推荐技能:** `canslim-screener`, `breakout-trade-planner`, `theme-detector`

**可选技能:** `stockbee-momentum-burst-screener`, `stockbee-exhaustion-hammer-screener`, `finviz-screener`

**关联工作流:** `swing-opportunity-daily`

---

## Trade Memory {#trade-memory}

**`trade-memory`** · event-driven · no-api-basic · beginner

**适用场景:** The shared learning loop: record closed-trade outcomes, run postmortems, and feed lessons back into the process. Use after every closed position and for the monthly performance retrospective. Operationalized by the trade-memory-loop (per closed trade) and monthly-performance-review (monthly) workflows.

**不适用场景:** Do not run before a position is closed — update an open thesis with trader-memory-core directly instead. Do not skip the loop after a closed trade, even on winners.

**目标用户:** `part-time-swing-trader`, `long-term-investor`, `growth-investor`

**必需技能:** `trader-memory-core`, `signal-postmortem`

**推荐技能:** `backtest-expert`, `trade-performance-coach`

**可选技能:** `trade-hypothesis-ideator`

**关联工作流:** `trade-memory-loop`, `monthly-performance-review`

---
