---
layout: default
title: "News Reaction Failure Analyzer"
grand_parent: 中文
parent: 技能指南
nav_order: 39
lang_peer: /en/skills/news-reaction-failure-analyzer/
permalink: /zh/skills/news-reaction-failure-analyzer/
generated: false
---

# News Reaction Failure Analyzer
{: .no_toc }

Judge whether a market FAILED to react to news favorable to a crowded speculative position — step 2 of Jason Shapiro's COT contrarian process. Consumes a cot-contrarian-detector report (or an explicit direction) plus a Claude-curated events JSON, fetches the underlying price series with a documented fallback chain, and produces a fail-closed CONFIRMED / NOT_CONFIRMED / INSUFFICIENT_EVIDENCE verdict using a statistically validated drift-significance test (not a naive failure-ratio, which false-confirms on pure noise). Generic beyond COT — reusable for PEAD and macro-crowding news-failure checks. Use when the user asks to check news-failure confirmation, whether a crowded market "shrugged off" good/bad news, or wants to run Shapiro step 2 on a CROWDED_LONG/CROWDED_SHORT market.
{: .fs-6 .fw-300 }

<span class="badge badge-api">FMP必需</span>

[下载技能包 (.skill)](https://github.com/tradermonty/claude-trading-skills/raw/main/skill-packages/news-reaction-failure-analyzer.skill){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
[在GitHub上查看源码](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/news-reaction-failure-analyzer){: .btn .fs-5 .mb-4 .mb-md-0 }

> **注意：** 本页面尚未翻译为中文。
> 请参阅[英文版]({{ '/en/skills/news-reaction-failure-analyzer/' | relative_url }})获取完整指南。
{: .warning }

---

[查看英文版指南]({{ '/en/skills/news-reaction-failure-analyzer/' | relative_url }}){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
