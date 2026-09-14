---
layout: default
title: "Intraday Market Monitor"
grand_parent: 中文
parent: 技能指南
nav_order: 37
lang_peer: /en/skills/intraday-market-monitor/
permalink: /zh/skills/intraday-market-monitor/
generated: true
---

# Intraday Market Monitor
{: .no_toc }

Run an hourly, deterministic intraday market read on 15-minute-delayed Polygon data (breadth from one all-tickers snapshot, SPY/QQQ vs VWAP and prior-day range, sector relative strength, hourly-close watchlist signals) and emit an exposure posture (NEW_ENTRY_ALLOWED / REDUCE_ONLY / CASH_PRIORITY) with Discord notification and optional Claude narrative. Use during the US session at :20 past the hour, or to replay a past session.
{: .fs-6 .fw-300 }

<span class="badge badge-free">无需API</span>

[下载技能包 (.skill)](https://github.com/tradermonty/claude-trading-skills/raw/main/skill-packages/intraday-market-monitor.skill){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
[在GitHub上查看源码](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/intraday-market-monitor){: .btn .fs-5 .mb-4 .mb-md-0 }

> **注意：** 本页面尚未翻译为中文。
> 请参阅[英文版]({{ '/en/skills/intraday-market-monitor/' | relative_url }})获取完整指南。
{: .warning }

---

[查看英文版指南]({{ '/en/skills/intraday-market-monitor/' | relative_url }}){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
