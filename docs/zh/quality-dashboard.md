---
layout: page
parent: 中文
title: 质量仪表盘
nav_order: 3
permalink: /zh/quality-dashboard/
lang_peer: /en/quality-dashboard/
generated: true
---


# 质量仪表盘

> 本部分由 `scripts/generate_quality_dashboard.py` 自动生成。请勿手动编辑。

快照基准日： `2026-09-12T00:00:00Z`

## 生命周期

| 合计 | 生产 | Beta | 仅知识库 | 可执行 | 有测试 | 无测试 |
|---:|---:|---:|---:|---:|---:|---:|
| 75 | 58 | 17 | 3 | 72 | 72 | 0 |

## 测试覆盖率

- 总体覆盖率目标: 75.0%
- 总体覆盖率下限: 72.0%
- 允许失败数: 0 (目标 0)

## E2E 回放

- E2E 回放覆盖的工作流: 8 / 11

## 依赖关系

| 提供商 | 数量 |
|---|---:|
| FMP | 23 |
| FINVIZ | 4 |
| ALPACA | 2 |
| 其他外部提供商 | 16 |
| 离线（无外部数据） | 34 |

## Beta 管道

| 技能 | Beta 经过天数 |
|---|---:|
| `contrarian-setup-gate` | not yet measured |
| `crypto-regime-analyzer` | not yet measured |
| `drawdown-circuit-breaker` | not yet measured |
| `futures-position-sizer` | not yet measured |
| `fxmacrodata-calendar` | not yet measured |
| `intraday-market-monitor` | not yet measured |
| `manifoldbt-backtester` | not yet measured |
| `mt5-robot-tester` | not yet measured |
| `pre-trade-discipline-gate` | not yet measured |
| `residual-edge-analyzer` | not yet measured |
| `stockbee-20pct-study` | not yet measured |
| `stockbee-episodic-pivot-analyzer` | not yet measured |
| `stockbee-exhaustion-hammer-screener` | not yet measured |
| `stockbee-momentum-burst-screener` | not yet measured |
| `stockbee-setup-fluency-trainer` | not yet measured |
| `trade-performance-coach` | not yet measured |
| `us-undervalued-growth-screener` | not yet measured |

## 技能状态明细

| 技能 | 状态 | 可执行 | 测试 | 覆盖率 |
|---|---|---|---|---|
| **Backtest Expert** (`backtest-expert`) | 生产 | 是 | 是 | not yet measured |
| **Breadth Chart Analyst** (`breadth-chart-analyst`) | 生产 | 是 | 是 | not yet measured |
| **Breakout Trade Planner** (`breakout-trade-planner`) | 生产 | 是 | 是 | not yet measured |
| **CANSLIM Screener** (`canslim-screener`) | 生产 | 是 | 是 | not yet measured |
| **Contrarian Setup Gate** (`contrarian-setup-gate`) | Beta | 是 | 是 | not yet measured |
| **COT Contrarian Detector** (`cot-contrarian-detector`) | 生产 | 是 | 是 | not yet measured |
| **Crypto Regime Analyzer** (`crypto-regime-analyzer`) | Beta | 是 | 是 | not yet measured |
| **Data Quality Checker** (`data-quality-checker`) | 生产 | 是 | 是 | not yet measured |
| **Dividend Growth Pullback Screener** (`dividend-growth-pullback-screener`) | 生产 | 是 | 是 | not yet measured |
| **Downtrend Duration Analyzer** (`downtrend-duration-analyzer`) | 生产 | 是 | 是 | not yet measured |
| **Drawdown Circuit Breaker** (`drawdown-circuit-breaker`) | Beta | 是 | 是 | not yet measured |
| **Dual Axis Skill Reviewer** (`dual-axis-skill-reviewer`) | 生产 | 是 | 是 | not yet measured |
| **Earnings Calendar** (`earnings-calendar`) | 生产 | 是 | 是 | not yet measured |
| **Earnings Trade Analyzer** (`earnings-trade-analyzer`) | 生产 | 是 | 是 | not yet measured |
| **Economic Calendar Fetcher** (`economic-calendar-fetcher`) | 生产 | 是 | 是 | not yet measured |
| **Edge Candidate Agent** (`edge-candidate-agent`) | 生产 | 是 | 是 | not yet measured |
| **Edge Concept Synthesizer** (`edge-concept-synthesizer`) | 生产 | 是 | 是 | not yet measured |
| **Edge Hint Extractor** (`edge-hint-extractor`) | 生产 | 是 | 是 | not yet measured |
| **Edge Pipeline Orchestrator** (`edge-pipeline-orchestrator`) | 生产 | 是 | 是 | not yet measured |
| **Edge Signal Aggregator** (`edge-signal-aggregator`) | 生产 | 是 | 是 | not yet measured |
| **Edge Strategy Designer** (`edge-strategy-designer`) | 生产 | 是 | 是 | not yet measured |
| **Edge Strategy Reviewer** (`edge-strategy-reviewer`) | 生产 | 是 | 是 | not yet measured |
| **Exposure Coach** (`exposure-coach`) | 生产 | 是 | 是 | not yet measured |
| **Finviz Screener** (`finviz-screener`) | 生产 | 是 | 是 | not yet measured |
| **FTD Detector** (`ftd-detector`) | 生产 | 是 | 是 | not yet measured |
| **Futures Position Sizer** (`futures-position-sizer`) | Beta | 是 | 是 | not yet measured |
| **FXMacroData Calendar** (`fxmacrodata-calendar`) | Beta | 是 | 是 | not yet measured |
| **IBD Distribution Day Monitor** (`ibd-distribution-day-monitor`) | 生产 | 是 | 是 | not yet measured |
| **Institutional Flow Tracker** (`institutional-flow-tracker`) | 生产 | 是 | 是 | not yet measured |
| **Intraday Market Monitor** (`intraday-market-monitor`) | Beta | 是 | 是 | not yet measured |
| **Kanchi Dividend Review Monitor** (`kanchi-dividend-review-monitor`) | 生产 | 是 | 是 | not yet measured |
| **Kanchi Dividend SOP** (`kanchi-dividend-sop`) | 生产 | 是 | 是 | not yet measured |
| **Kanchi Dividend US Tax Accounting** (`kanchi-dividend-us-tax-accounting`) | 生产 | 是 | 是 | not yet measured |
| **Macro Regime Detector** (`macro-regime-detector`) | 生产 | 是 | 是 | not yet measured |
| **manifoldbt Backtester** (`manifoldbt-backtester`) | Beta | 是 | 是 | not yet measured |
| **Market Breadth Analyzer** (`market-breadth-analyzer`) | 生产 | 是 | 是 | not yet measured |
| **Market Environment Analysis** (`market-environment-analysis`) | 生产 | 是 | 是 | not yet measured |
| **Market News Analyst** (`market-news-analyst`) | 生产 | 否 | 否 | not yet measured |
| **Market Top Detector** (`market-top-detector`) | 生产 | 是 | 是 | not yet measured |
| **MT5 Robot Tester** (`mt5-robot-tester`) | Beta | 是 | 是 | not yet measured |
| **News Reaction Failure Analyzer** (`news-reaction-failure-analyzer`) | 生产 | 是 | 是 | not yet measured |
| **Options Strategy Advisor** (`options-strategy-advisor`) | 生产 | 是 | 是 | not yet measured |
| **Pair Trade Screener** (`pair-trade-screener`) | 生产 | 是 | 是 | not yet measured |
| **Parabolic Short Trade Planner** (`parabolic-short-trade-planner`) | 生产 | 是 | 是 | not yet measured |
| **PEAD Screener** (`pead-screener`) | 生产 | 是 | 是 | not yet measured |
| **Portfolio Manager** (`portfolio-manager`) | 生产 | 是 | 是 | not yet measured |
| **Position Sizer** (`position-sizer`) | 生产 | 是 | 是 | not yet measured |
| **Pre-Trade Discipline Gate** (`pre-trade-discipline-gate`) | Beta | 是 | 是 | not yet measured |
| **Residual Edge Analyzer** (`residual-edge-analyzer`) | Beta | 是 | 是 | not yet measured |
| **Scenario Analyzer** (`scenario-analyzer`) | 生产 | 否 | 否 | not yet measured |
| **Sector Analyst** (`sector-analyst`) | 生产 | 是 | 是 | not yet measured |
| **Signal Postmortem** (`signal-postmortem`) | 生产 | 是 | 是 | not yet measured |
| **Skill Designer** (`skill-designer`) | 生产 | 是 | 是 | not yet measured |
| **Skill Idea Miner** (`skill-idea-miner`) | 生产 | 是 | 是 | not yet measured |
| **Skill Integration Tester** (`skill-integration-tester`) | 生产 | 是 | 是 | not yet measured |
| **Stanley Druckenmiller Investment** (`stanley-druckenmiller-investment`) | 生产 | 是 | 是 | not yet measured |
| **Stockbee 20% Study** (`stockbee-20pct-study`) | Beta | 是 | 是 | not yet measured |
| **Stockbee Episodic Pivot Analyzer** (`stockbee-episodic-pivot-analyzer`) | Beta | 是 | 是 | not yet measured |
| **Stockbee Exhaustion Hammer Screener** (`stockbee-exhaustion-hammer-screener`) | Beta | 是 | 是 | not yet measured |
| **Stockbee Momentum Burst Screener** (`stockbee-momentum-burst-screener`) | Beta | 是 | 是 | not yet measured |
| **Stockbee Setup Fluency Trainer** (`stockbee-setup-fluency-trainer`) | Beta | 是 | 是 | not yet measured |
| **Strategy Pivot Designer** (`strategy-pivot-designer`) | 生产 | 是 | 是 | not yet measured |
| **Technical Analyst** (`technical-analyst`) | 生产 | 是 | 是 | not yet measured |
| **Theme Detector** (`theme-detector`) | 生产 | 是 | 是 | not yet measured |
| **Trade Hypothesis Ideator** (`trade-hypothesis-ideator`) | 生产 | 是 | 是 | not yet measured |
| **Trade Performance Coach** (`trade-performance-coach`) | Beta | 是 | 是 | not yet measured |
| **Trader Memory Core** (`trader-memory-core`) | 生产 | 是 | 是 | not yet measured |
| **Trading Skills Navigator** (`trading-skills-navigator`) | 生产 | 是 | 是 | not yet measured |
| **Uptrend Analyzer** (`uptrend-analyzer`) | 生产 | 是 | 是 | not yet measured |
| **US Market Bubble Detector** (`us-market-bubble-detector`) | 生产 | 是 | 是 | not yet measured |
| **US Stock Analysis** (`us-stock-analysis`) | 生产 | 否 | 否 | not yet measured |
| **US Undervalued Growth Screener** (`us-undervalued-growth-screener`) | Beta | 是 | 是 | not yet measured |
| **Value Dividend Screener** (`value-dividend-screener`) | 生产 | 是 | 是 | not yet measured |
| **VCP Screener** (`vcp-screener`) | 生产 | 是 | 是 | not yet measured |
| **Weekly Performance Digest** (`weekly-performance-digest`) | 生产 | 是 | 是 | not yet measured |

## 运行时指标（快照）

| 指标 | 值 |
|---|---|
| 快照基准日： | 2026-09-12T00:00:00Z |
| Dual-axis 分数分布 | not-yet-measured |
| 高严重度未解决 Issue | not-yet-measured |
| 最近成功 CI | not-yet-measured |
| 包差异 | not-yet-measured |
| 文档差异 | not-yet-measured |
| 导航器差异 | not-yet-measured |
