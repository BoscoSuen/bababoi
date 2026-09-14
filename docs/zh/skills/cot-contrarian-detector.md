---
layout: default
title: "COT Contrarian Detector"
grand_parent: 中文
parent: 技能指南
nav_order: 13
lang_peer: /en/skills/cot-contrarian-detector/
permalink: /zh/skills/cot-contrarian-detector/
generated: false
---

# COT Contrarian Detector
{: .no_toc }

Detect crowded speculative positioning in CFTC futures markets (COT report analysis) to find contrarian setups using Jason Shapiro's methodology. Screens large-speculator ("non-commercial") net positioning across 65 futures markets (indices, rates, FX, metals, energy, crypto) via the FMP Commitment of Traders API, computes a 3-year and 26-week COT Index per market, and classifies extremes as CROWDED_LONG / CROWDED_SHORT. Use when the user asks about COT report analysis, crowded positioning, "who is trapped", speculative positioning extremes, contrarian futures setups, or wants to run Jason Shapiro-style analysis. This skill automates crowding DETECTION only (step 1 of 5) — it does not generate trade signals by itself.
{: .fs-6 .fw-300 }

<span class="badge badge-api">FMP必需</span>

[下载技能包 (.skill)](https://github.com/tradermonty/claude-trading-skills/raw/main/skill-packages/cot-contrarian-detector.skill){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
[在GitHub上查看源码](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/cot-contrarian-detector){: .btn .fs-5 .mb-4 .mb-md-0 }

> **注意：** 本页面尚未翻译为中文。
> 请参阅[英文版]({{ '/en/skills/cot-contrarian-detector/' | relative_url }})获取完整指南。
{: .warning }

---

[查看英文版指南]({{ '/en/skills/cot-contrarian-detector/' | relative_url }}){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
