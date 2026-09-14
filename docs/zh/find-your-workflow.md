---
layout: default
title: 选择工作流
parent: 中文
nav_order: 6
lang_peer: /en/find-your-workflow/
permalink: /zh/find-your-workflow/
---

# 选择工作流
{: .no_toc }

Solo Trader OS 的静态"从哪里开始"指南。在查看[技能目录](skill-catalog.md)
和[工作流](workflows.md)页面之前，通过本页面一次找到适合自己情况的入口工作流。

如果下表中没有匹配项，请用自然语言告诉
[**`trading-skills-navigator`**](skills/trading-skills-navigator.md)
你的目的。它会以确定性方式返回相同的推荐结果。

---

## 按日常节奏选择

| 你的情况 | 起始工作流 |
|---|---|
| 想在开盘前 15 分钟做行情检查 | [`market-regime-daily`](https://github.com/tradermonty/claude-trading-skills/blob/main/workflows/market-regime-daily.yaml) |
| 只在行情环境允许时做波段交易 | [`market-regime-daily`](https://github.com/tradermonty/claude-trading-skills/blob/main/workflows/market-regime-daily.yaml) → [`swing-opportunity-daily`](https://github.com/tradermonty/claude-trading-skills/blob/main/workflows/swing-opportunity-daily.yaml) |
| 想每周审查长期投资组合 | [`core-portfolio-weekly`](https://github.com/tradermonty/claude-trading-skills/blob/main/workflows/core-portfolio-weekly.yaml) |
| 想从已成交的交易中学习 | [`trade-memory-loop`](https://github.com/tradermonty/claude-trading-skills/blob/main/workflows/trade-memory-loop.yaml) |
| 想每月回顾业绩并检视规则 | [`monthly-performance-review`](https://github.com/tradermonty/claude-trading-skills/blob/main/workflows/monthly-performance-review.yaml) |

> 如果犹豫不决，请用自然语言向 [`trading-skills-navigator`](skills/trading-skills-navigator.md)
> 描述你的日常节奏。

---

## 按目的选择

| 你的目的 | 技能集 | 驱动工作流 |
|---|---|---|
| 首先想知道今天是 risk-on 还是 risk-off | [`market-regime`](https://github.com/tradermonty/claude-trading-skills/blob/main/skillsets/market-regime.yaml) | `market-regime-daily` |
| 运营 Core（股息/ETF/长期持有）长期投资组合 | [`core-portfolio`](https://github.com/tradermonty/claude-trading-skills/blob/main/skillsets/core-portfolio.yaml) | `core-portfolio-weekly` |
| 只在行情允许时寻找有纪律的卫星波段候选 | [`swing-opportunity`](https://github.com/tradermonty/claude-trading-skills/blob/main/skillsets/swing-opportunity.yaml) | `swing-opportunity-daily` |
| 记录全部交易、生成事后分析，将经验存入日志 | [`trade-memory`](https://github.com/tradermonty/claude-trading-skills/blob/main/skillsets/trade-memory.yaml) | `trade-memory-loop`, `monthly-performance-review` |

> 如果不确定自己的目的属于哪一类，请向 [`trading-skills-navigator`](skills/trading-skills-navigator.md)
> 用自由文本描述目的，它会对应到技能集和工作流。

---

## 没有现成工作流匹配时

### 无需 API 密钥的入口

如果还没有 FMP / FINVIZ / Alpaca 的付费订阅，可以先手动运行以下 5 个技能。
同样的最小循环可以在无付费数据的情况下支撑
[`market-regime-daily`](https://github.com/tradermonty/claude-trading-skills/blob/main/workflows/market-regime-daily.yaml)
和
[`trade-memory-loop`](https://github.com/tradermonty/claude-trading-skills/blob/main/workflows/trade-memory-loop.yaml)。

1. [`market-breadth-analyzer`](skills/market-breadth-analyzer.md) — 基于公开 CSV 的 breadth 评分
2. [`uptrend-analyzer`](skills/uptrend-analyzer.md) — 公开 CSV 的 uptrend 参与比率
3. [`position-sizer`](skills/position-sizer.md) — 纯计算
4. [`trader-memory-core`](skills/trader-memory-core.md) — 基于本地 YAML 的日志
5. [`signal-postmortem`](skills/signal-postmortem.md) — 复盘框架

"无需 API"不等于"无需外部数据"。这些技能需要公开 CSV、图表截图或本地文件。
准确的输入要求请查看各技能在
[`skills-index.yaml`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills-index.yaml)
中的 `integrations:` 字段。

### 已知的空白

部分用例尚未有打包好的工作流。这些空白在
[`PROJECT_VISION.md`](https://github.com/tradermonty/claude-trading-skills/blob/main/PROJECT_VISION.md)
中作为后续工作候选明确跟踪。

- **做空专用/risk-off 日内** — `parabolic-short-trade-planner` 部分覆盖，
  但端到端的做空工作流尚未提供
- **财报周日内** — `earnings-trade-analyzer` 和 `pead-screener` 部分覆盖，
  但每周编排工作流尚未提供
- **策略研究流水线** — 已有 `edge-pipeline-orchestrator`，但"发现新 edge"
  的标准工作流 manifest 尚未提供

如果你的情况属于这些空白，请以探索方式使用。
从[技能目录](skill-catalog.md)中选择所需的单个技能，
在专用工作流推出前按需运行。

### 自由文本自然语言入口

如果上述表格都不匹配你的情况，请使用
[`trading-skills-navigator`](skills/trading-skills-navigator.md)
技能。传入自由文本描述的目的，它会返回最佳工作流、技能集、API 配置和设置步骤。
推荐基于与本页相同的
[`skills-index.yaml`](https://github.com/tradermonty/claude-trading-skills/blob/main/skills-index.yaml)
这一唯一权威来源。

---

## 相关页面

- [快速入门](getting-started.md) — Claude Code / Claude Web App / CLI 安装步骤
- [术语表]({{ '/zh/glossary/' | relative_url }}) — 工作流中使用的交易术语的通俗解释
- [技能目录](skill-catalog.md) — 全部技能的字母顺序目录
- [工作流](workflows.md) — 全部工作流的自动生成 manifest 参考
- [技能集](skillsets.md) — 按目的划分的安装包
