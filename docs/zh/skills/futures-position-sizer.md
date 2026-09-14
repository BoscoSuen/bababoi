---
layout: default
title: "Futures Position Sizer"
grand_parent: 中文
parent: 技能指南
nav_order: 32
lang_peer: /en/skills/futures-position-sizer/
permalink: /zh/skills/futures-position-sizer/
generated: false
---

# Futures Position Sizer
{: .no_toc }

Calculate contract-based futures position sizes from a direction, entry, and stop-loss, using verified per-symbol contract specs (multiplier, tick size, tick value). Use when the user asks how many futures contracts to trade, wants to size a futures position (ES, NQ, ZB, GC, CL, 6E/E6, VX, BT, ...), or is handing off a contrarian-setup-gate READY_FOR_PLAN direction/invalidation_level for sizing. Pure, offline calculation -- no API keys, no network.
{: .fs-6 .fw-300 }

<span class="badge badge-free">无需API</span>

[下载技能包 (.skill)](https://github.com/tradermonty/claude-trading-skills/raw/main/skill-packages/futures-position-sizer.skill){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
[在GitHub上查看源码](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/futures-position-sizer){: .btn .fs-5 .mb-4 .mb-md-0 }

> **注意：** 本页面尚未翻译为中文。
> 请参阅[英文版]({{ '/en/skills/futures-position-sizer/' | relative_url }})获取完整指南。
{: .warning }

---

[查看英文版指南]({{ '/en/skills/futures-position-sizer/' | relative_url }}){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
