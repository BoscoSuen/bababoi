# Weekly Trade Strategy Blog Generator

自动生成美股每周交易策略博客的AI代理系统

[English](#english) | [中文](#chinese)

---

## <a name="chinese"></a>中文

### 概述

本项目利用Claude Agents自动生成美股市场每周交易策略博客。依次执行图表分析、市场环境评估和新闻分析，为兼职交易者生成实用的策略报告。

### 主要功能

- **技术分析**: VIX、利率、Breadth指标、主要指数、商品的周线图表分析
- **市场环境评估**: 泡沫风险检测、情绪分析、板块轮动分析
- **新闻与事件分析**: 过去10天新闻影响评估、未来7天经济指标和财报预测
- **每周策略博客生成**: 整合3份分析报告，以200-300行Markdown格式输出实用交易策略
- **中长期策略报告**（可选）: Druckenmiller风格的18个月投资策略，4种情景（Base/Bull/Bear/Tail Risk）

### 前提条件

- **Claude Code CLI** 或 **Claude Desktop**
- 以下Claude技能可用：
  - `technical-analyst`
  - `breadth-chart-analyst`
  - `sector-analyst`
  - `market-environment-analysis`
  - `us-market-bubble-detector`
  - `market-news-analyst`
  - `economic-calendar-fetcher`
  - `earnings-calendar`
  - `stanley-druckenmiller-investment`（中长期策略用）

### 设置

1. **克隆仓库**

```bash
git clone <repository-url>
cd weekly-trade-strategy
```

2. **设置环境变量**

创建`.env`文件并设置所需的API密钥：

```bash
# Financial Modeling Prep API（用于获取财报和经济日历）
FMP_API_KEY=your_api_key_here
```

3. **确认文件夹结构**

```
weekly-trade-strategy/
├── charts/              # 图表图像存放文件夹
├── reports/             # 分析报告存放文件夹
├── blogs/               # 最终博客文章存放文件夹
├── skills/              # Claude技能定义
└── .claude/
    └── agents/          # Claude代理定义
```

### 使用方法

#### 快速开始

1. **准备图表图像**（推荐18张）

```bash
# 创建日期文件夹
mkdir -p charts/2025-11-03

# 放置图表图像（推荐以下图像）
# - VIX（周线）
# - 美国10年期国债收益率（周线）
# - S&P 500 Breadth Index
# - Nasdaq 100, S&P 500, Russell 2000, Dow（周线）
# - 黄金、铜、原油、天然气、铀（周线）
# - Uptrend Stock Ratio
# - 板块和行业表现
# - 财报日历、热力图
```

2. **创建报告文件夹**

```bash
mkdir -p reports/2025-11-03
```

3. **批量执行提示**（在Claude Code/Desktop中执行）

```
请创建2025-11-03周的交易策略博客。

1. 用technical-market-analyst分析charts/2025-11-03/的所有图表
   → reports/2025-11-03/technical-market-analysis.md

2. 用us-market-analyst进行市场环境综合评估
   → reports/2025-11-03/us-market-analysis.md

3. 用market-news-analyzer进行新闻/事件分析
   → reports/2025-11-03/market-news-analysis.md

4. 用weekly-trade-blog-writer生成最终博客文章
   → blogs/2025-11-03-weekly-strategy.md

请依次执行各步骤，确认报告后再进入下一步。
```

4. **可选：中长期策略报告生成**

除每周博客外，还可生成18个月的中长期投资策略报告（推荐每季度执行）。

```
请用druckenmiller-strategy-planner代理制定截至2025年11月3日的18个月策略。

综合分析reports/2025-11-03/下的3份报告，
应用Druckenmiller风格的策略框架，
保存到reports/2025-11-03/druckenmiller-strategy.md。
```

**特点**:
- 18个月前瞻的中长期宏观分析
- 4种情景（Base/Bull/Bear/Tail Risk）及概率评估
- 基于确信度的仓位管理建议
- 宏观转折点（货币政策、经济周期）的识别
- 各情景明确的失效条件

#### 分步执行

更详细的步骤请参阅`CLAUDE.md`。

### 项目结构

```
weekly-trade-strategy/
│
├── charts/                          # 图表图像
│   └── YYYY-MM-DD/
│       ├── vix.jpeg
│       ├── 10year_yield.jpeg
│       └── ...
│
├── reports/                         # 分析报告
│   └── YYYY-MM-DD/
│       ├── technical-market-analysis.md
│       ├── us-market-analysis.md
│       ├── market-news-analysis.md
│       └── druckenmiller-strategy.md  #（可选：中长期策略）
│
├── blogs/                           # 最终博客文章
│   └── YYYY-MM-DD-weekly-strategy.md
│
├── skills/                          # Claude技能定义
│   ├── technical-analyst/
│   ├── breadth-chart-analyst/
│   ├── sector-analyst/
│   ├── market-news-analyst/
│   ├── us-market-bubble-detector/
│   └── ...
│
├── .claude/
│   └── agents/                      # Claude代理定义
│       ├── technical-market-analyst.md
│       ├── us-market-analyst.md
│       ├── market-news-analyzer.md
│       ├── weekly-trade-blog-writer.md
│       └── druckenmiller-strategy-planner.md  #（可选：中长期策略）
│
├── CLAUDE.md                        # 详细执行步骤指南
├── README.md                        # 本文件
├── .env                             # 环境变量（需创建）
└── .gitignore
```

### 代理列表

| 代理 | 职责 | 输出 |
|---------|------|------|
| `technical-market-analyst` | 从图表图像执行技术分析 | `technical-market-analysis.md` |
| `us-market-analyst` | 评估市场环境和泡沫风险 | `us-market-analysis.md` |
| `market-news-analyzer` | 分析新闻影响和事件预测 | `market-news-analysis.md` |
| `weekly-trade-blog-writer` | 整合3份报告生成博客文章 | `YYYY-MM-DD-weekly-strategy.md` |
| `druckenmiller-strategy-planner`（可选） | 中长期（18个月）策略规划（4情景分析） | `druckenmiller-strategy.md` |

### 故障排除

**Q: 代理找不到图表**
- 确认`charts/YYYY-MM-DD/`文件夹存在
- 确认图像格式为`.jpeg`或`.png`

**Q: 报告未生成**
- 确认`reports/YYYY-MM-DD/`文件夹已创建
- 确认上一步的报告已正常生成

**Q: 博客文章的板块配分急剧变化**
- 确认上周的博客文章存在于`blogs/`目录
- 代理设计为进行渐进式调整（±10-15%）

**Q: FMP API报错**
- 确认`.env`文件中`FMP_API_KEY`设置正确
- 确认API密钥有效（[Financial Modeling Prep](https://site.financialmodelingprep.com/)）

### 许可证

本项目基于MIT许可证发布。

### 贡献

欢迎提交Pull Request。如有重大变更，请先创建issue讨论变更内容。

---

## <a name="english"></a>English

### Overview

An AI agent system that automatically generates weekly trading strategy blog posts for US stock markets using Claude Agents. The system performs step-by-step chart analysis, market environment evaluation, and news analysis to produce actionable strategy reports for part-time traders.

### Key Features

- **Technical Analysis**: Weekly chart analysis of VIX, yields, breadth indicators, major indices, and commodities
- **Market Environment Assessment**: Bubble risk detection, sentiment analysis, sector rotation analysis
- **News & Event Analysis**: Past 10 days news impact evaluation, upcoming 7 days economic indicators and earnings forecasts
- **Weekly Strategy Blog Generation**: Integrates three analysis reports into a 200-300 line Markdown format trading strategy
- **Medium-Term Strategy Report** (Optional): 18-month Druckenmiller-style investment strategy with 4 scenarios (Base/Bull/Bear/Tail Risk)

### Prerequisites

- **Claude Code CLI** or **Claude Desktop**
- The following Claude skills must be available:
  - `technical-analyst`
  - `breadth-chart-analyst`
  - `sector-analyst`
  - `market-environment-analysis`
  - `us-market-bubble-detector`
  - `market-news-analyst`
  - `economic-calendar-fetcher`
  - `earnings-calendar`
  - `stanley-druckenmiller-investment` (for medium-term strategy)

### Quick Start

1. Clone the repository
2. Create `.env` file with your `FMP_API_KEY`
3. Create date folders: `mkdir -p charts/2025-11-03 reports/2025-11-03`
4. Place chart images in `charts/2025-11-03/`
5. Run the complete workflow via Claude Code/Desktop (see Chinese section for detailed prompt)

### Project Structure

See the Chinese section above for detailed structure.

### Agents

- **technical-market-analyst**: Chart-based technical analysis
- **us-market-analyst**: Market environment and bubble risk evaluation
- **market-news-analyzer**: News impact and event forecasting
- **weekly-trade-blog-writer**: Final blog post generation
- **druckenmiller-strategy-planner** (Optional): Medium-term (18-month) strategy planning with 4-scenario analysis

### Documentation

For detailed workflow instructions, see `CLAUDE.md`.

### License

This project is licensed under the MIT License.

### Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## Acknowledgments

This project leverages Claude's advanced AI capabilities for financial market analysis. All trading strategies generated are for educational purposes only and should not be considered as financial advice.

---

**Version**: 1.0
**Last Updated**: 2025-11-02
