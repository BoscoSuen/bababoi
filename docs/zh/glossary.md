---
layout: default
title: 术语表
parent: 中文
nav_order: 7
lang_peer: /en/glossary/
permalink: /zh/glossary/
---

# 术语表
{: .no_toc }

面向初次接触者，解释 Claude Trading Skills 中使用的交易术语。此处的定义旨在帮助理解词汇，不构成买卖建议，也不保证未来收益。
{: .fs-6 .fw-300 }

<details open markdown="block">
  <summary>目录</summary>
  {: .text-delta }
- TOC
{:toc}
</details>

---

## 术语列表

### ATR（Average True Range）
{: #atr }

ATR 是一个指标，用于估计在指定周期内（包括跳空），价格通常会波动多大幅度。它衡量的是波动幅度而非方向，用于根据当前波动率调整止损宽度和仓位风险。

**相关技能：** [Position Sizer]({{ '/zh/skills/position-sizer/' | relative_url }})

### 市场广度（Breadth）
{: #breadth }

市场广度反映市场走势中有多少成分股参与其中。由众多股票共同支撑的指数上涨，比仅靠少数大盘股拉动的情况，基础更为广泛。

**相关技能：** [Market Breadth Analyzer]({{ '/zh/skills/market-breadth-analyzer/' | relative_url }})

### 突破（Breakout）
{: #breakout }

突破是指价格越过阻力位或交易区间上限等此前的重要边界。仅仅越过边界并不保证延续，通常还需结合成交量、市场环境以及判定失败的价位来确认。

**相关技能：** [Breakout Trade Planner]({{ '/zh/skills/breakout-trade-planner/' | relative_url }})

### CANSLIM
{: #canslim }

CANSLIM 是一个成长股投资框架，综合评估当季盈利（Current quarterly earnings）、年度盈利增长（Annual earnings growth）、新产品/新高/新管理层（New）、供需关系（Supply and demand）、领涨或落后（Leader or laggard）、机构持仓（Institutional sponsorship）和市场方向（Market direction）。不仅评估企业业绩，还关注价格、成交量和市场环境。

**相关技能：** [CANSLIM Screener]({{ '/zh/skills/canslim-screener/' | relative_url }})

### 催化因素（Catalyst）
{: #catalyst }

催化因素指财报、业绩指引、新产品、监管变化、管理层变动等可能改变市场对个股预期的事件或新信息。它可以触发价格变动，但并不决定市场反应是正面的还是持久的。

**相关技能：** [Stockbee Episodic Pivot Analyzer]({{ '/zh/skills/stockbee-episodic-pivot-analyzer/' | relative_url }})

### 核心+卫星（Core + Satellite）
{: #core-satellite }

核心+卫星是一种投资组合结构，将长期分散持有的核心部分与用于更主动或集中机会的小型卫星配额分开。这有助于防止短期交易在不知不觉中改变长期资产的整体风险特征。

**相关技能：** [Kanchi Dividend SOP]({{ '/zh/skills/kanchi-dividend-sop/' | relative_url }})

### 相关性（Correlation）
{: #correlation }

相关性用 -1 到 +1 的范围概括两个收益序列在历史上共同波动的程度。它反映的是可能随市场环境变化的历史关系，并不证明一方驱动了另一方的因果关系。

**相关技能：** [Pair Trade Screener]({{ '/zh/skills/pair-trade-screener/' | relative_url }})

### COT（Commitments of Traders）
{: #cot }

COT 是美国商品期货交易委员会（CFTC）每周公布的期货持仓报告，按商业套保者、资产管理者等分类。用于分析持仓偏向和拥挤程度，通常不作为单独的交易时机信号，而是结合价格确认使用。

**相关技能：** [COT Contrarian Detector]({{ '/zh/skills/cot-contrarian-detector/' | relative_url }})

### Distribution Day（派发日）
{: #distribution-day }

派发日通常指主要指数在成交量高于前日的情况下明显下跌的交易日。近期多次出现可能暗示机构卖出压力，但仅凭单日无法判断整体市场走向。

**相关技能：** [IBD Distribution Day Monitor]({{ '/zh/skills/ibd-distribution-day-monitor/' | relative_url }})

### 回撤（Drawdown）
{: #drawdown }

回撤是指投资组合或策略从前期高点到随后低点的下跌幅度，通常以百分比表示。除了损失深度外，还需关注持续时间以及恢复到高点所需的涨幅。

**相关技能：** [Drawdown Circuit Breaker]({{ '/zh/skills/drawdown-circuit-breaker/' | relative_url }})

### 边际优势（Edge）
{: #edge }

边际优势是指在大量重复同类决策时，预期产生有利结果的、可复现的信息、行为、分析或执行上的优势。它不保证每笔交易盈利，而是一个可能随市场环境变化而削弱的待验证假设。

**相关技能：** [Edge Concept Synthesizer]({{ '/zh/skills/edge-concept-synthesizer/' | relative_url }})

### 入场（Entry）
{: #entry }

入场是指预先设定的允许开始交易的条件或价格区间。实用的规则还会同时定义所需的证据、可接受的风险以及使该设置失效的条件。

**相关技能：** [Breakout Trade Planner]({{ '/zh/skills/breakout-trade-planner/' | relative_url }})

### Episodic Pivot（事件性枢纽）
{: #episodic-pivot }

Episodic Pivot 是指伴随重大财报意外或业绩指引变化等公司特定重大事件的剧烈价格和成交量变化。预期的重新定价可能开启新趋势，但流动性、后续跟进和风险上限需要单独评估。

**相关技能：** [Stockbee Episodic Pivot Analyzer]({{ '/zh/skills/stockbee-episodic-pivot-analyzer/' | relative_url }})

### 期望值（Expectancy）
{: #expectancy }

期望值表示在足够多的交易中，每笔交易平均预期获得多少利润或亏损。典型的计算方式是胜率乘以平均盈利减去败率乘以平均亏损，但它不预测下一笔交易的结果。

**相关技能：** [Weekly Performance Digest]({{ '/zh/skills/weekly-performance-digest/' | relative_url }})

### 敞口（Exposure）
{: #exposure }

敞口是指暴露于市场波动中的投资组合资本量，通常按净资产比例分为多头、空头、总量和净值。仅看持仓市值可能掩盖杠杆，因此分母和符号的定义很重要。

**相关技能：** [Exposure Coach]({{ '/zh/skills/exposure-coach/' | relative_url }})

### Follow-Through Day（跟进确认日/FTD）
{: #ftd }

跟进确认日是指在市场低点候选之后，主要指数在成交量放大的情况下大幅上涨的交易日。某些成长股投资法将其视为机构资金开始支撑上涨的证据，但它只是确认条件之一，不保证上涨延续。

**相关技能：** [FTD Detector]({{ '/zh/skills/ftd-detector/' | relative_url }})

### 跳空（Gap）
{: #gap }

跳空是指前一个交易时段的价格范围与下一个时段开盘价格之间出现几乎无成交的空白。它通常反映新信息，但实际意义取决于幅度、成交量、出现位置和后续走势。

**相关技能：** [Earnings Trade Analyzer]({{ '/zh/skills/earnings-trade-analyzer/' | relative_url }})

### 对冲比率（Hedge Ratio）
{: #hedge-ratio }

对冲比率指为降低特定风险（如市场风险或价差风险），需要对一方头寸配置多少对手方头寸。配对交易中通常从历史价格推算，但存在估算误差和关系变化带来的残余风险。

**相关技能：** [Pair Trade Screener]({{ '/zh/skills/pair-trade-screener/' | relative_url }})

### 流动性（Liquidity）
{: #liquidity }

流动性反映能否在不显著影响价格的情况下买卖所需数量。成交量、买卖价差和挂单深度是参考指标，但在剧烈波动或盘外时段流动性可能下降。

**相关技能：** [Pair Trade Screener]({{ '/zh/skills/pair-trade-screener/' | relative_url }})

### 最大逆行幅度（Maximum Adverse Excursion / MAE）
{: #mae }

MAE 是持仓期间从入场价向不利方向移动的最大未实现幅度。回顾同类交易的 MAE 可以帮助判断止损是否过窄或者是否放大了亏损，但不应仅根据少量样本优化。

**相关技能：** [Trader Memory Core]({{ '/zh/skills/trader-memory-core/' | relative_url }})

### 最大顺行幅度（Maximum Favorable Excursion / MFE）
{: #mfe }

MFE 是持仓期间从入场价向有利方向移动的最大未实现幅度。与实际结果对比可以回顾出场执行效果，但不应假设持仓中的最佳价位都能实际成交。

**相关技能：** [Trader Memory Core]({{ '/zh/skills/trader-memory-core/' | relative_url }})

### 市场状态（Market Regime）
{: #market-regime }

市场状态是以趋势、波动率、广度、流动性、宏观环境等特征划分的宽泛市场环境。在稳定上升期和高波动下跌期，同一流程可能需要调整敞口和设置规则。

**相关技能：** [Macro Regime Detector]({{ '/zh/skills/macro-regime-detector/' | relative_url }})

### 动量（Momentum）
{: #momentum }

动量是指相对较强或较弱的价格变化在一段时间内持续的趋势。测量周期不同结果也不同，短期动量强的股票在长期可能表现偏弱。

**相关技能：** [Stockbee Momentum Burst Screener]({{ '/zh/skills/stockbee-momentum-burst-screener/' | relative_url }})

### 财报后漂移（Post-Earnings Announcement Drift / PEAD）
{: #pead }

PEAD 是学术研究中记录的一种现象：财报意外后，价格倾向于继续沿初始反应的方向移动。并非所有财报反应都会延续，因此需要明确准入条件、入场规则、流动性标准和失效规则。

**相关技能：** [PEAD Screener]({{ '/zh/skills/pead-screener/' | relative_url }})

### 仓位管理（Position Sizing）
{: #position-sizing }

仓位管理是确定交易中分配的股数、合约数或金额。基于风险的方法不仅凭信心决定数量，而是根据投资组合可承受的亏损额和到失效/止损的距离来计算。

**相关技能：** [Position Sizer]({{ '/zh/skills/position-sizer/' | relative_url }})

### 回调（Pullback）
{: #pullback }

回调是指在主趋势中暂时出现反方向的运动，如上升趋势中的下跌。它可能是有计划的入场机会，但也可能是反转的开始，因此趋势质量和失效价位很重要。

**相关技能：** [Dividend Growth Pullback Screener]({{ '/zh/skills/dividend-growth-pullback-screener/' | relative_url }})

### R 倍数（R-Multiple）
{: #r-multiple }

R 倍数用初始计划风险的比率来表示交易结果：+2R 表示获利为初始风险的 2 倍，-1R 表示亏损为计划风险的全额。一致记录初始风险可以方便比较不同规模的交易。

**相关技能：** [Weekly Performance Digest]({{ '/zh/skills/weekly-performance-digest/' | relative_url }})

### 相对强度（Relative Strength）
{: #relative-strength }

相对强度是将个股在选定周期的表现与基准或同业进行比较。它与 Relative Strength Index（RSI）不同：相对强度是比较，RSI 是在固定范围内的动量振荡指标。

**相关技能：** [CANSLIM Screener]({{ '/zh/skills/canslim-screener/' | relative_url }})

### 风险偏好/风险规避（Risk-On / Risk-Off）
{: #risk-on-risk-off }

Risk-On 指投资者广泛偏好对增长和市场风险敏感度较高的资产，Risk-Off 指资金倾向于保本和防御性资产。这是跨市场动态的概括描述，不是非此即彼的预测。

**相关技能：** [Market Environment Analysis]({{ '/zh/skills/market-environment-analysis/' | relative_url }})

### RSI（Relative Strength Index）
{: #rsi }

RSI 根据近期上涨和下跌幅度的比例计算，通常以 0 到 100 表示的动量振荡指标。70 或 30 等水平反映的是近期计算上的极端状态，不是自动的买卖指令。

**相关技能：** [Dividend Growth Pullback Screener]({{ '/zh/skills/dividend-growth-pullback-screener/' | relative_url }})

### 止损（Stop-Loss）
{: #stop-loss }

止损是在交易不再符合计划时退出的、预先设定的价格或条件。它限制了预期的风险，但在跳空、剧烈波动或流动性不足的情况下，不能保证按预期价格退出。

**相关技能：** [Breakout Trade Planner]({{ '/zh/skills/breakout-trade-planner/' | relative_url }})

### 支撑与阻力（Support and Resistance）
{: #support-resistance }

支撑是过去买盘吸收了卖盘的价格区域，阻力是卖盘吸收了买盘的价格区域。它们是从市场行为推断的区间，不是永久阻挡价格的壁垒。

**相关技能：** [Technical Analyst]({{ '/zh/skills/technical-analyst/' | relative_url }})

### 交易论点与失效条件（Thesis and Invalidation）
{: #thesis-invalidation }

交易论点阐述认为机会成立的理由和可观察的依据，失效条件指出什么证据会使该理由不再成立。在入场前同时写下两者，有助于减少事后诸葛和解释偷换。

**相关技能：** [Trader Memory Core]({{ '/zh/skills/trader-memory-core/' | relative_url }})

### 波动率（Volatility）
{: #volatility }

波动率反映价格变化的幅度和离散程度，不指示方向。波动率越高，结果的摆幅越大，因此要维持相近的投资组合风险，可能需要减少数量或放宽风险区间。

**相关技能：** [Position Sizer]({{ '/zh/skills/position-sizer/' | relative_url }})

### VCP（Volatility Contraction Pattern）
{: #vcp }

VCP 是一种价格结构，表现为连续回调幅度逐渐缩小，暗示在潜在的枢纽价位附近供给减少。它是与 Mark Minervini 相关的设置框架，不是突破成功的证明。

**相关技能：** [VCP Screener]({{ '/zh/skills/vcp-screener/' | relative_url }})

### Z 分数（Z-Score）
{: #z-score }

Z 分数表示当前值偏离历史均值多少个标准差。在价差分析中用于衡量异常偏离的程度，但前提是分布足够稳定且参考期间合适。

**相关技能：** [Pair Trade Screener]({{ '/zh/skills/pair-trade-screener/' | relative_url }})
