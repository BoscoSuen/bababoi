---
layout: default
title: "Intraday Market Monitor"
grand_parent: 日本語
parent: スキルガイド
nav_order: 37
lang_peer: /en/skills/intraday-market-monitor/
permalink: /ja/skills/intraday-market-monitor/
generated: true
---

# Intraday Market Monitor
{: .no_toc }

Run an hourly, deterministic intraday market read on 15-minute-delayed Polygon data (breadth from one all-tickers snapshot, SPY/QQQ vs VWAP and prior-day range, sector relative strength, hourly-close watchlist signals) and emit an exposure posture (NEW_ENTRY_ALLOWED / REDUCE_ONLY / CASH_PRIORITY) with Discord notification and optional Claude narrative. Use during the US session at :20 past the hour, or to replay a past session.
{: .fs-6 .fw-300 }

<span class="badge badge-free">API不要</span>

[スキルパッケージをダウンロード (.skill)](https://github.com/tradermonty/claude-trading-skills/raw/main/skill-packages/intraday-market-monitor.skill){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
[GitHubでソースを見る](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/intraday-market-monitor){: .btn .fs-5 .mb-4 .mb-md-0 }

> **Note:** This page has not yet been translated into Japanese.
> Please refer to the [English version]({{ '/en/skills/intraday-market-monitor/' | relative_url }}) for the full guide.
{: .warning }

---

[English版ガイドを見る]({{ '/en/skills/intraday-market-monitor/' | relative_url }}){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
