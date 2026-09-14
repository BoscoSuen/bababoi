---
layout: default
title: 操作手册
parent: 中文
nav_order: 9
has_children: true
lang_peer: /en/playbooks/
permalink: /zh/playbooks/
---

# 操作手册
{: .no_toc }

本部分不是单个技能的说明，而是跨越多个技能的完整流水线使用指南。每本操作手册从头到尾讲解一条流水线：何时运行、步骤顺序、门控如何判断、仓位如何计算，以及如何将交易登记到 `trader-memory-core`。在单独运行某个技能之前，请先阅读对应的操作手册。

---

## 操作手册列表

| 操作手册 | 时间跨度 | 内容 |
|---|---|---|
| [Cross-Asset Quant Strategy Framework]({{ '/zh/playbooks/quant-strategy-framework/' | relative_url }}) | 跨所有时间维度 | 将所有资产类别的操作手册和技能统一到 Pre / During / Post 框架中 |
| [Stockbee Momentum Burst]({{ '/zh/playbooks/stockbee-momentum-burst/' | relative_url }}) | 2–5 个交易日 | 通过 `stockbee-momentum-burst-screener` 进行突破/区间扩张的短期波段入场 |
| [PEAD（财报后漂移）]({{ '/zh/playbooks/pead/' | relative_url }}) | 2–6 周 | 通过 `pead-screener` 的红周K线回调模式进行财报漂移入场 |
| [Shapiro COT 逆向交易]({{ '/zh/playbooks/shapiro-contrarian/' | relative_url }}) | 每周 | 经过两个独立确认后，反向交易 CFTC 期货的拥挤仓位 |

每本操作手册都是**决策辅助流水线，而非自动下单系统**。所有下单均为手动操作，每个筛选器的输出是待审查的候选列表，而非无条件遵循的信号。支撑这些操作手册的技能（`stockbee-momentum-burst-screener`、`pead-screener`、`earnings-trade-analyzer`、`technical-analyst`、`position-sizer`、`trader-memory-core`、`pre-trade-discipline-gate`、`cot-contrarian-detector` 及 Shapiro 流水线的周边技能）均不执行下单、撤单、券商 API 调用或实时监控。

## 不要混淆两个短期操作手册

Stockbee Momentum Burst 和 PEAD 都会筛选流动性较高的美股波段候选，但它们的持有周期和催化因素不同，属于不同的交易群体。

- **Momentum Burst** 是纯粹的价格/成交量突破策略。不以财报为前提条件，持有期为 2–5 个交易日，以触发日低点破位或缺乏跟进为退出条件。
- **PEAD** 以实际的财报跳空高开和周K线的红K线回调为入场前提，持有期为 2–6 周，以周收盘价触及止损或论点失效为退出条件。

不要仅仅因为某只股票恰好发布了财报，就将 Momentum Burst 的仓位延长到 PEAD 的时间框架。如果要转换，请作为具有不同 `setup_type` 的独立论点重新登记。边界的详细说明请参阅各操作手册的"不要混淆"部分。

## 相关页面

- 单个技能的参考文档请参阅[技能指南]({{ '/zh/skills/' | relative_url }})
- 自动生成的 manifest 列表请参阅[工作流]({{ '/zh/workflows/' | relative_url }})
