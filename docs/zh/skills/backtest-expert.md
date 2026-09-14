---
layout: default
title: Backtest Expert
grand_parent: 中文
parent: 技能指南
nav_order: 7
lang_peer: /en/skills/backtest-expert/
permalink: /zh/skills/backtest-expert/
---

# Backtest Expert
{: .no_toc }

通过五维评分定量评估回测结果，做出Deploy/Refine/Abandon判定的技能。
{: .fs-6 .fw-300 }

<span class="badge badge-free">无需API</span>

[下载技能包 (.skill)](https://github.com/tradermonty/claude-trading-skills/raw/main/skill-packages/backtest-expert.skill){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
[在GitHub上查看源码](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/backtest-expert){: .btn .fs-5 .mb-4 .mb-md-0 }

<details open markdown="block">
  <summary>目录</summary>
  {: .text-delta }
- TOC
{:toc}
</details>

---

## 1. 概述

Backtest Expert 是一款系统化评估交易策略回测结果的技能，判定策略应当实战部署（Deploy）、改进优化（Refine）还是放弃（Abandon）。

**核心理念：**
> 不是找"最赚钱的策略"，而是找"最不容易崩溃的策略"

**主要特点：**
- 五维评分（每维20分，满分100分）
- 10+项红旗自动检测
- Deploy（70分以上）/ Refine（40-69分）/ Abandon（39分以下）三级判定
- 无需API，不依赖外部数据（指标由用户提供）
- JSON + Markdown报告同步输出

**解决的问题：**
- 消除回测结果的主观解读，实现定量品质评估
- 检测曲线拟合、前视偏差、幸存者偏差等常见陷阱
- 及早发现"结果好得不真实"的回测危险信号

---

## 2. 前提条件

| 项目 | 必要性 | 说明 |
|------|------|------|
| Python 3.9+ | 必需 | 运行评估脚本 |
| API密钥 | 不需要 | 指标由用户输入 |
| 网络连接 | 不需要 | 完全离线运行 |

无需安装额外的Python包（仅使用标准库）。

> 回测的执行本身不在本技能范围内。本技能专注于"回测结果的评估"。回测执行请使用QuantConnect、Backtrader、Amibroker等专用工具。
{: .tip }

---

## 3. 快速开始

只需将回测结果告诉Claude即可评估：

```
请评估回测结果。150笔交易，胜率62%，平均盈利1.8%，
平均亏损1.2%，最大回撤15%，测试8年，3个参数，
滑点已测试。
```

Claude按以下流程处理：
1. 计算五维评分（样本量、期望值、风险管理、稳健性、执行真实性）
2. 自动检测红旗
3. Deploy/Refine/Abandon判定
4. 针对需要改进维度的具体建议

通过CLI直接运行：

```bash
python3 skills/backtest-expert/scripts/evaluate_backtest.py \
  --total-trades 150 \
  --win-rate 62 \
  --avg-win-pct 1.8 \
  --avg-loss-pct 1.2 \
  --max-drawdown-pct 15 \
  --years-tested 8 \
  --num-parameters 3 \
  --slippage-tested \
  --output-dir reports/
```

---

## 4. 工作原理

### 五维评分框架

每个维度0-20分，合计满分100分。

| # | 维度 | 分值 | 评估对象 |
|---|------|------|---------|
| 1 | 样本量 | 20 | 交易笔数（<30=0、100=15、200+=20） |
| 2 | 期望值 | 20 | 胜率 x 平均盈利 vs 败率 x 平均亏损 |
| 3 | 风险管理 | 20 | 最大回撤（12分）+ Profit Factor（8分） |
| 4 | 稳健性 | 20 | 测试期间（15分）+ 参数数量（5分） |
| 5 | 执行真实性 | 20 | 是否已测试滑点/摩擦成本 |

### 评分要点

- **样本量**：<30=0分、100=15分、200+=满分。30笔以下在统计上无意义
- **期望值**：胜率 x 平均盈利 - 败率 x 平均亏损。≤0则0分（不应交易）
- **风险管理**：回撤（12分）+ Profit Factor（8分）。DD>50%则整体覆盖为0分
- **稳健性**：测试期间（15分，<5年=0）+ 参数数量（5分，≤4=5分，≥8=0分）
- **执行真实性**：滑点已测试=20分，未测试=0分（二值判定）

### 判定标准

| 总分 | 判定 | 操作 |
|-----------|------|-----------|
| 70-100 | **Deploy** | 通过所有压力测试，可实战部署 |
| 40-69 | **Refine** | 核心逻辑健全但需调整参数 |
| 0-39 | **Abandon** | 压力测试失败，依赖脆弱前提 |

### 红旗检测

自动检测的主要红旗：交易笔数<30（高）、滑点未测试（高）、回撤>50%（高）、参数≥7（中）、测试期间<5年（中）、负期望值（高）、胜率>90%+DD<5%（中，"结果好得不真实"）。

---

## 5. 使用示例

### 示例1：财报缺口均值回归策略评估

**提示词：**
```
请评估财报缺口+3%日内回归前收盘价的均值回归策略回测。
200笔交易，胜率58%，平均盈利1.5%，平均亏损1.0%，最大回撤12%，
测试10年，4个参数，滑点已测试。
```

**CLI命令：**
```bash
python3 skills/backtest-expert/scripts/evaluate_backtest.py \
  --total-trades 200 \
  --win-rate 58 \
  --avg-win-pct 1.5 \
  --avg-loss-pct 1.0 \
  --max-drawdown-pct 12 \
  --years-tested 10 \
  --num-parameters 4 \
  --slippage-tested \
  --output-dir reports/
```

**预期结果：** Deploy（高分）。充足的样本量、正期望值、适度回撤、长期测试、少量参数。

---

### 示例2：技术形态筛选器评分

**提示词：**
```
杯柄形态筛选器。80笔交易，胜率55%，
平均盈利2.5%，平均亏损1.8%，最大回撤22%，6年，5个参数，
滑点未测试。
```

**CLI命令：**
```bash
python3 skills/backtest-expert/scripts/evaluate_backtest.py \
  --total-trades 80 \
  --win-rate 55 \
  --avg-win-pct 2.5 \
  --avg-loss-pct 1.8 \
  --max-drawdown-pct 22 \
  --years-tested 6 \
  --num-parameters 5 \
  --output-dir reports/
```

**预期结果：** Refine。滑点未测试（执行真实性=0分）严重拉低总分。样本量也略显不足。

**为什么有用：** 明确"首先应改进什么"。本例中，添加滑点模型和扩大样本是最优先事项。

---

### 示例3：红旗检测（识别脆弱回测）

**提示词：**
```
RSI反转策略。20笔交易，胜率92%，平均盈利0.8%，平均亏损0.3%，
最大回撤3%，3年，8个参数，滑点未测试。这可靠吗？
```

**CLI命令：**
```bash
python3 skills/backtest-expert/scripts/evaluate_backtest.py \
  --total-trades 20 \
  --win-rate 92 \
  --avg-win-pct 0.8 \
  --avg-loss-pct 0.3 \
  --max-drawdown-pct 3 \
  --years-tested 3 \
  --num-parameters 8 \
  --output-dir reports/
```

**预期红旗：** 小样本、滑点未测试、过度优化、短测试期间、结果好得不真实——5项同时触发。看似优秀但多个红旗同时出现的结果不可信赖。

---

### 示例4：两个策略的并列比较

**提示词：**
```
策略A（动量）：150笔交易，胜率48%，盈利3.2%，亏损1.5%，DD25%，7年，3个参数
策略B（均值回归）：300笔交易，胜率68%，盈利0.9%，亏损0.7%，DD18%，7年，5个参数
```

**Claude的动作：** 分别评估两个策略，对比五维的优劣势。使用同一框架横向比较，消除主观判断。

---

### 示例5：滑点1.5-2倍压力测试

**提示词：**
```
请模拟滑点增加到1.5倍和2倍的情况。
原始：200笔交易，胜率60%，平均盈利1.6%，平均亏损1.0%。
1.5倍时平均盈利降至1.525%，2倍时降至1.45%。
```

**Claude的动作：** 在3个场景下运行评估脚本，以对比表展示期望值和Profit Factor的变化。判定"滑点2倍后期望值是否仍为正"。

---

### 示例6：参数稳健性评估

**提示词：**
```
止损在2%、2.5%、3%、3.5%、4%下的结果已有。是否存在高原区？
```

**Claude的动作：** 分别评估5种模式，识别评分稳定的区间（高原区）。"2.5-3.5%范围内评分稳定"→稳健性高，"仅3.0%时高分"→可能存在曲线拟合。

---

### 示例7：前推验证

**提示词：**
```
请评估前推验证的结果。
样本内（2014-2019）：胜率65%，平均盈利2.0%，平均亏损1.3%
样本外（2020-2023）：胜率58%，平均盈利1.6%，平均亏损1.4%
```

**Claude的动作：** 分别评估两个区间，计算期望值衰减率。样本外低于样本内50%则"需要注意"，50%以上则"可接受"。

---

## 6. 理解输出

### JSON输出主要字段

| 字段 | 说明 |
|-----------|------|
| `total_score` | 总分（0-100） |
| `verdict` | Deploy / Refine / Abandon |
| `dimensions` | 五维单项评分（各0-20） |
| `red_flags` | 检测到的红旗列表 |
| `metrics.expectancy` | 期望值（%/笔交易） |
| `metrics.profit_factor` | Profit Factor |

### Markdown报告结构

1. **摘要** - 总分、判定、红旗数量
2. **维度表** - 五维单项评分及明细
3. **关键指标** - 期望值、Profit Factor、回撤
4. **红旗详情** - 各红旗的ID、严重程度、说明
5. **推荐操作** - 基于判定的具体下一步

### 评分解读指南

- **70+分（Deploy）**：可实战部署。80+几乎所有维度都获高评价
- **40-69分（Refine）**：核心逻辑健全，但特定维度（通常是执行真实性或样本量）有改进空间
- **0-39分（Abandon）**：存在根本性问题，多个维度不足

---

## 7. 技巧与最佳实践

### 回测的80/20法则

- **20%**：用于生成想法和编写代码
- **80%**：用于压力测试和试图打破想法

遵循这个比例可以防止"寻找好结果"的偏差。

### 寻找"高原区"

- **好策略**：止损1.5%~3.0%范围内利润稳定
- **差策略**：只有止损恰好为2.13%时才盈利

稳定的表现是真实优势的证据。狭窄的最优值是曲线拟合的征兆。

### 常见失败模式

| 模式 | 征兆 | 对策 |
|---------|------|------|
| 参数过敏 | 仅特定值有效 | 高原区分析确认 |
| 体制依赖 | 仅特定年份表现好 | 按年分析确认 |
| 滑点过敏 | 加成本后亏损 | 1.5-2倍测试 |
| 小样本 | 交易不足30笔 | 扩展数据/延长期间 |
| 前视偏差 | 结果不切实际地好 | 时间戳审计 |

> 本技能专门针对**系统化/量化**回测。不一定适用于主观交易者的方法评估。
{: .tip }

---

## 8. 与其他技能组合

### Earnings Trade Analyzer → Backtest Expert

积累财报缺口的统计数据，用于Deploy/Refine/Abandon判定。

### Backtest Expert → Position Sizer

将Deploy判定的胜率和平均盈亏输入Kelly Criterion，计算最优风险分配。

### PEAD Screener → Backtest Expert

对PEAD信号的准确率和盈亏统计进行评分，判定是否可以投入实际运用。

---

## 9. 故障排除

### "avg_loss_pct must be >= 0" 错误

**原因：** `--avg-loss-pct` 输入了负值

**处理：**
- 平均亏损请输入正数值（例：1.2%的亏损输入 `--avg-loss-pct 1.2`）
- 脚本内部会处理符号

### 执行真实性始终为0分

**原因：** 未指定 `--slippage-tested` 标志

**处理：**
- 如果滑点/摩擦成本已测试，请添加 `--slippage-tested` 标志
- 此维度为二值判定（0分或20分），对总分影响很大
- 如果尚未测试滑点，请用1.5-2倍滑点重新运行回测

### 不明白评分低的原因

**处理：**
- 查看Markdown报告中维度表的各维度单项评分
- 最低分的维度是最优先改进项
- 同时查看红旗列表（包含具体问题和改进建议）

### Profit Factor计算不匹配

**原因：** PF 1.0-3.0线性转换为0-8分后，`int()` 向下取整。例如：PF 1.25→1分，PF 1.50→2分。此离散化是有意设计。

---

## 10. 参考

### CLI选项一览

```bash
python3 skills/backtest-expert/scripts/evaluate_backtest.py [OPTIONS]
```

| 选项 | 说明 | 默认值 |
|-----------|------|-----------|
| `--total-trades` | 回测交易笔数（必需） | - |
| `--win-rate` | 胜率（%，例：58）（必需） | - |
| `--avg-win-pct` | 平均盈利交易（%）（必需） | - |
| `--avg-loss-pct` | 平均亏损交易（%，正数值）（必需） | - |
| `--max-drawdown-pct` | 最大回撤（%）（必需） | - |
| `--years-tested` | 回测期间（年数）（必需） | - |
| `--num-parameters` | 策略可调参数数量（必需） | - |
| `--slippage-tested` | 是否已测试滑点/摩擦成本（标志） | false |
| `--output-dir` | 报告输出目录 | `reports/` |

### 评分速查表

| 维度 | 0分 | 10分 | 20分 |
|------|-----|------|------|
| 样本量 | <30笔交易 | ~70笔交易 | 200+笔交易 |
| 期望值 | ≤0% | ~0.5% | 1.5%+ |
| 风险管理 | DD 50%+ 或 PF<1.0 | DD ~25%, PF ~1.5 | DD <20%, PF 3.0+ |
| 稳健性 | <5年, 8+参数 | 7年, 5参数 | 10+年, ≤4参数 |
| 执行真实性 | 未测试 | - | 已测试 |

### 滑点参考值

压力测试使用典型值的1.5-2倍。超大盘：0.01-0.02%（测试时0.02-0.04%），大盘：0.02-0.05%，中盘：0.05-0.10%，小盘：0.10-0.20%，微盘：0.20-0.50%+。

### 相关文件

| 文件 | 说明 |
|----------|------|
| `skills/backtest-expert/SKILL.md` | 技能定义（工作流） |
| `skills/backtest-expert/references/methodology.md` | 测试方法论详细说明（压力测试、偏差防止等） |
| `skills/backtest-expert/references/failed_tests.md` | 失败模式案例集和红旗检查清单 |
| `skills/backtest-expert/scripts/evaluate_backtest.py` | 五维评估脚本 |
