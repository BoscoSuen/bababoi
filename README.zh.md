# Claude Trading Skills

Claude Trading Skills 起源于作者希望利用AI改善自身交易流程的个人项目。

Claude Trading Skills 是一套基于 Claude Skills 的交易工作流工具包，面向时间有限的个人投资者。

主要面向以长期投资、ETF和股息股为核心（Core），在市场条件有利时以纪律性波段交易作为卫星策略（Satellite）追求额外收益的投资者。

目标不是将买卖决策外包给AI，而是将市场确认、风险管理、交易计划、记录和持续改进结构化为可重复的流程。由于支撑更好交易决策的工作流程、检查清单和复盘习惯可以通过共享实践来改进，因此作为开源项目发布。

这不是信号服务或盈利承诺项目，而是为想要建立更好决策流程的交易者提供的工具箱。

本项目的定位是 **first for self, open for others**：首先作为作者实际使用的实践工作流来构建，然后作为对有类似需求的人可能有用的工具开放共享。

📖 **文档网站:** <https://tradermonty.github.io/claude-trading-skills/>

**项目愿景:** [`PROJECT_VISION.zh.md`](PROJECT_VISION.zh.md)

English README is available at [`README.md`](README.md).

## 免责声明

本仓库仅用于教育、研究和流程改进目的。不提供金融建议、投资咨询、税务/法律建议、交易信号服务或经纪商订单执行。投资和交易存在风险，包括本金损失。过往业绩、回测、筛选结果、报告和AI生成的分析不保证未来收益。所有交易决策、仓位管理、税务/合规遵守和经纪商使用均由用户自行负责。

本项目基于 MIT License 提供，**按原样提供，不含任何担保**。

## 适用人群

本仓库适合以下人群：

- 投资时间有限的个人投资者
- 以长期投资为基础，仅在市场条件好时进行波段交易的投资者
- 希望定期检查股息股、ETF和持仓的投资者
- 在寻找交易标的之前先确认市场环境和风险的投资者
- 希望记录交易并从复盘中改进的投资者

不适合以全自动交易、信号外包或短线剥头皮为主要目的的用户。

## 推荐起步路径

新用户请从以下运营工作流之一开始。各链接指向 [`workflows/`](workflows/) 下的机器可读清单，按顺序描述所用技能、判断门和产出物。

| 目标 | 工作流 | 核心技能 | API配置 |
| --- | --- | --- | --- |
| 每天15分钟市场检查 | [`market-regime-daily`](workflows/market-regime-daily.yaml) | market-breadth-analyzer, uptrend-analyzer, exposure-coach | 无需API |
| 每周长期投资组合审查 | [`core-portfolio-weekly`](workflows/core-portfolio-weekly.yaml)（[示例](examples/workflows/core-portfolio-weekly/sample-run/)） | portfolio-manager, kanchi-dividend-review-monitor, trader-memory-core | 需要Alpaca；手动CSV为降级备选 |
| 仅在风险允许时寻找波段候选 | [`swing-opportunity-daily`](workflows/swing-opportunity-daily.yaml)（[示例](examples/workflows/swing-opportunity-daily/sample-run/)） | vcp-screener, drawdown-circuit-breaker, technical-analyst, position-sizer, trader-memory-core, pre-trade-discipline-gate | 需要FMP；风险/纪律门使用本地状态 |
| 成交后记录和学习交易 | [`trade-memory-loop`](workflows/trade-memory-loop.yaml) | trader-memory-core, signal-postmortem | 无需API |
| 月度绩效和规则审查 | [`monthly-performance-review`](workflows/monthly-performance-review.yaml)（[示例](examples/workflows/monthly-performance-review/sample-run/)） | trader-memory-core, signal-postmortem, backtest-expert | 无需API |

清单的阅读方式和手动执行步骤请参阅 [`workflows/README.md`](workflows/README.md)。如需一页式"哪个工作流适合我"指南，请参阅 [Find Your Workflow](docs/en/find-your-workflow.md)（[中文](docs/zh/find-your-workflow.md)）。

新用户请参阅 [Your First Week](docs/en/your-first-week.md)（[中文](docs/zh/your-first-week.md)），从安装到无付费数据API的市场检查、首次日志登记和首次周度审查。

### 实际费用

Claude Web的Skills目前可在Free、Pro、Max、Team和Enterprise账户上使用。
使用条件可能会变化，请查看Anthropic的
[最新Skills帮助](https://support.claude.com/en/articles/12512180-use-skills-in-claude)。
Claude Code有单独的账户要求，不包含在Claude.ai的Free计划中。详情请查看
[Claude Code设置指南](https://code.claude.com/docs/en/getting-started)。
FMP、FINVIZ Elite、Alpaca等数据/API和经纪商集成是可选的或仅特定工作流需要。
以下5个技能的入口使用公开CSV、图表图像和本地文件，无需付费市场数据API。

### 无需API密钥的入口

如果您还没有FMP/FINVIZ/Alpaca付费订阅，请先手动运行这5个技能：

1. `market-breadth-analyzer` — 公开CSV的市场宽度评分，无需API密钥
2. `uptrend-analyzer` — 公开CSV的上升趋势比率，无需API密钥
3. `position-sizer` — 纯计算，无I/O
4. `trader-memory-core` — 本地YAML日志记录
5. `signal-postmortem` — 复盘框架

仅此路径即可**无需付费数据API**完成"市场确认→仓位管理→交易记录→复盘"最小循环。注意"无需API"不等于"无需外部数据"，公开CSV、图表图像和本地文件仍然需要。各技能的精确输入要求请参阅 [`skills-index.yaml`](skills-index.yaml) 的 `integrations:` 字段。

> **权威来源:** [`skills-index.yaml`](skills-index.yaml) 是所有技能元数据的权威来源。如本README、`CLAUDE.md`或文档与index内容不一致，以index为准。多技能工作流同理，[`workflows/*.yaml`](workflows/) 为权威来源。

## 仓库结构
- `skills/<skill-name>/` – 各技能源文件夹。包含 `SKILL.md`、参考资料和辅助脚本。
- `skills-index.yaml` – 所有技能元数据的权威来源（id、类别、integrations、workflows引用）。
- `workflows/` – Core + Satellite 运营工作流清单集（权威来源，通过 `--strict-workflows` 验证）。
- `skill-packages/` – 可直接上传到Claude Web应用 **Skills** 标签页的 `.skill` 包。
- `docs/` – 文档网站内容、生成的技能页面、`docs/dev/metadata-and-workflow-schema.md`（模式规范）。
- `scripts/` – 仓库级自动化和维护脚本，包含验证器和引导辅助工具。
- `skillsets/` – 按目的分组的安装单元。为每个主要目标定义 required/recommended/optional 技能（已实现4个核心skillset: market-regime, core-portfolio, swing-opportunity, trade-memory。Navigator引用）。

## 快速开始

首次使用请先查看涵盖计划、费用、安全性和功能范围的
[常见问题](docs/zh/faq.md)。

### 在Claude Web应用中使用
1. 从 `skill-packages/` 下载所需技能对应的 `.skill` 文件。
2. 个人账户请在 **Settings > Capabilities** 中启用 **Code execution and file creation**。Team/Enterprise可能需要组织管理员启用。
3. 在 **Customize > Skills** 中上传ZIP，确认列表中显示并按需启用（另请参阅Anthropic的[最新Skills帮助](https://support.claude.com/en/articles/12512180-use-skills-in-claude)）。

### 在Claude Code（桌面/CLI）中使用
1. 克隆或下载本仓库。
2. 将所需技能文件夹（如 `backtest-expert`）复制到个人使用的 `~/.claude/skills/` 或项目级的 `.claude/skills/`（另请参阅[Claude Code设置指南](https://code.claude.com/docs/en/getting-started)）。
3. 现有skills目录内的变更会自动检测。仅在会话启动后新建顶层skills目录时需要重启。

> 提示：`.skill` 包从源文件夹生成，排除测试和本地构建产物。自定义技能请编辑源文件夹，分发到Web应用时请运行 `python3 scripts/package_skills.py --skill <skill-name>`。

## 支持平台

本项目支持 **Python 3.9-3.13**，适用于 Linux / Windows / macOS。
仅CI实际验证过的组合视为 *supported*。此范围内未验证的组合为尽力支持。
精确的支持矩阵和强制方法请参阅 [docs/dev/compatibility-matrix.md](docs/dev/compatibility-matrix.md)。

## 配套工作包

如需即用的代理型工作流，请参阅配套仓库
[Hermes Trading Research Agent Work Package](https://github.com/tradermonty/hermes-trading-research-agent-work-package)。

将本仓库的技能集整合到Hermes配置文件中，可作为 `/pre-market-routine`、`/after-close-review`、
`/trade-journal`、`/weekly-portfolio-review`、`/monthly-performance-review` 等目的型斜杠命令投入实际使用。

这是支持研究、日志记录和风险审查的助手，**不是自动交易系统**。
不执行下单，不是信号服务，不运行隐藏的定时任务。

**最终决策始终由人类做出。**

## 主要技能领域

本仓库包含以下领域的技能：

| 领域 | 代表技能 |
| --- | --- |
| Market Regime | `market-breadth-analyzer`, `uptrend-analyzer`, `exposure-coach` |
| Core Portfolio | `portfolio-manager`, `value-dividend-screener`, `kanchi-dividend-sop` |
| Swing Opportunities | `vcp-screener`, `canslim-screener`, `breakout-trade-planner` |
| Trade Planning | `position-sizer`, `technical-analyst`, `pre-trade-discipline-gate` |
| Trade Memory | `trader-memory-core`, `signal-postmortem` |
| Strategy Research | `backtest-expert`, `edge-pipeline-orchestrator` |
| Advanced Satellite | `parabolic-short-trade-planner`, `earnings-trade-analyzer`, `options-strategy-advisor` |

以下详细目录由 `skills-index.yaml` 通过 `scripts/generate_catalog_from_index.py` **自动生成**。如需更新技能描述，请编辑 `skills-index.yaml` 后重新运行生成器（`python3 scripts/generate_catalog_from_index.py`）。更直观的列表请参阅文档网站。技能的生命周期、测试覆盖率和运行时健康状况的自动生成列表请参阅[质量仪表板](https://tradermonty.github.io/claude-trading-skills/zh/quality-dashboard/)。

## 详细技能目录

> **说明:** 本目录的技能描述直接显示 `skills-index.yaml` 中的英文原文。

<!-- skills-index:start name="catalog-zh" -->
<!-- 本部分由 skills-index.yaml 通过 scripts/generate_catalog_from_index.py 自动生成。请勿手动编辑，请更新 index 并重新运行生成器。 -->

### 市场体制（Market Regime）

| 技能 | 摘要 | 依赖 | 运营角色 | 状态 |
|---|---|---|---|---|
| **Breadth Chart Analyst** (`breadth-chart-analyst`) | This skill should be used when analyzing market breadth charts, specifically the S&P 500 Breadth Index (200-Day MA based) and the US Stock Market Uptrend Stock Ratio charts. | `chart_image` **required** | standalone | production |
| **COT Contrarian Detector** (`cot-contrarian-detector`) | Detects crowded speculative (large-speculator) positioning in CFTC futures markets using Commitment of Traders data, implementing step 1 of Jason Shapiro's contrarian methodology. | `fmp` **required** | workflow_step | production |
| **Crypto Regime Analyzer** (`crypto-regime-analyzer`) | Quantifies crypto market regime health (0-100 composite, 100 = risk-on) from six components using free keyless public data. | `coingecko` **required**, `binance_funding` _recommended_, `prices_json` optional | standalone | beta |
| **Downtrend Duration Analyzer** (`downtrend-duration-analyzer`) | Analyze historical downtrend durations and generate interactive HTML histograms showing typical correction lengths by sector and market cap. | `local_calculation` — | research_only | production |
| **Exposure Coach** (`exposure-coach`) | Generate a one-page Market Posture summary with net exposure ceiling, growth-vs-value bias, participation breadth, and new-entry-allowed vs cash-priority recommendation by integrating signals from breadth, regime, and flow analysis skills. | `local_calculation` — | workflow_step | production |
| **FTD Detector** (`ftd-detector`) | Detects Follow-Through Day (FTD) signals for market bottom confirmation using William O'Neil's methodology. | `polygon` **required** | standalone | production |
| **IBD Distribution Day Monitor** (`ibd-distribution-day-monitor`) | Detect IBD-style Distribution Days for QQQ/SPY (close down at least 0.2% on higher volume), track 25-session expiration and 5% invalidation, count d5/d15/d25 clusters, classify market risk (NORMAL/CAUTION/HIGH/SEVERE), and emit TQQQ/QQQ... | `polygon` **required** | standalone | production |
| **Intraday Market Monitor** (`intraday-market-monitor`) | Hourly, deterministic intraday market read on 15-minute-delayed Polygon data (all-tickers breadth snapshot, SPY/QQQ vs VWAP and prior-day range, sector relative strength, hourly-close watchlist signals) emitting NEW_ENTRY_ALLOWED / REDUCE_ONLY / CASH_PRIORITY with Discord notification and optional Claude narrative. | `polygon` **required**, `discord_webhook` optional, `claude_cli` optional | standalone | beta |
| **Macro Regime Detector** (`macro-regime-detector`) | Detect structural macro regime transitions (1-2 year horizon) using cross-asset ratio analysis. | `polygon` **required** | workflow_step | production |
| **Market Breadth Analyzer** (`market-breadth-analyzer`) | Quantifies market breadth health using TraderMonty's public CSV data. | `public_csv` **required** | workflow_step | production |
| **Market Environment Analysis** (`market-environment-analysis`) | Comprehensive market environment analysis and reporting tool. | `websearch` **required**, `chart_image` optional | workflow_step | production |
| **Market News Analyst** (`market-news-analyst`) | This skill should be used when analyzing recent market-moving news events and their impact on equity markets and commodities. | `websearch` **required** | workflow_step | production |
| **Market Top Detector** (`market-top-detector`) | Detects market top probability using O'Neil Distribution Days, Minervini Leading Stock Deterioration, and Monty Defensive Sector Rotation. | `polygon` **required**, `public_csv` **required** | workflow_step | production |
| **News Reaction Failure Analyzer** (`news-reaction-failure-analyzer`) | Judges whether a market failed to react to news favorable to a crowded speculative position, implementing step 2 of Jason Shapiro's contrarian methodology with a Monte-Carlo-verified drift-significance verdict test. | `fmp` **required**, `websearch` **required** | workflow_step | production |
| **Sector Analyst** (`sector-analyst`) | This skill should be used when analyzing sector rotation patterns and market cycle positioning. | `chart_image` **required** | workflow_step | production |
| **Uptrend Analyzer** (`uptrend-analyzer`) | Analyzes market breadth using Monty's Uptrend Ratio Dashboard data to diagnose the current market environment. | `public_csv` **required** | workflow_step | production |
| **US Market Bubble Detector** (`us-market-bubble-detector`) | Evaluates market bubble risk through quantitative data-driven analysis using the revised Minsky/Kindleberger framework v2.1. | `user_input` **required** | standalone | production |

### 核心投资组合（Core Portfolio）

| 技能 | 摘要 | 依赖 | 运营角色 | 状态 |
|---|---|---|---|---|
| **Dividend Growth Pullback Screener** (`dividend-growth-pullback-screener`) | Use this skill to find high-quality dividend growth stocks (12%+ annual dividend growth, 1.5%+ yield) that are experiencing temporary pullbacks, identified by RSI oversold conditions (RSI ≤40). | `fmp` **required**, `finviz` _recommended_ | workflow_step | production |
| **Kanchi Dividend Review Monitor** (`kanchi-dividend-review-monitor`) | Monitor dividend portfolios with Kanchi-style forced-review triggers (T1-T5) and convert anomalies into OK/WARN/REVIEW states without auto-selling. | `fmp` _recommended_ | workflow_step | production |
| **Kanchi Dividend SOP** (`kanchi-dividend-sop`) | Convert Kanchi-style dividend investing into a repeatable US-stock operating procedure. | `fmp` _recommended_ | workflow_step | production |
| **Kanchi Dividend US Tax Accounting** (`kanchi-dividend-us-tax-accounting`) | Provide US dividend tax and account-location workflow for Kanchi-style income portfolios. | `local_calculation` — | workflow_step | production |
| **Portfolio Manager** (`portfolio-manager`) | Comprehensive portfolio analysis using Alpaca MCP Server integration to fetch holdings and positions, then analyze asset allocation, risk metrics, individual stock positions, diversification, and generate rebalancing recommendations. | `alpaca` **required** | workflow_step | production |
| **US Undervalued Growth Screener** (`us-undervalued-growth-screener`) | Screen and rank US-listed small- and mid-cap undervalued-growth stocks with a generated stable-first FMP client, persistent SQLite cache, adaptive listing enumeration, FY1 estimate normalization, verified 20-day liquidity, deterministic four-lane discovery, forward same-basis valuation, standard and SBC-adjusted FCF, dilution, peer, cycle and LOE controls, strict final evaluation, prepublication audit, and a self-contained evidence bundle. | `fmp` _recommended_, `alternate_market_data` optional, `sec_edgar` **required**, `company_ir` **required**, `official_macro` **required**, `local_calculation` — | standalone | beta |
| **Value Dividend Screener** (`value-dividend-screener`) | Screen US stocks for high-quality dividend opportunities combining value characteristics (P/E ratio under 20, P/B ratio under 2), attractive yields (3% or higher), and consistent growth (dividend/revenue/EPS trending up over 3 years). | `fmp` **required**, `finviz` _recommended_ | workflow_step | production |

### 波段机会（Swing Opportunity）

| 技能 | 摘要 | 依赖 | 运营角色 | 状态 |
|---|---|---|---|---|
| **Breakout Trade Planner** (`breakout-trade-planner`) | Generate Minervini-style breakout trade plans from VCP screener output with worst-case risk calculation, portfolio heat management, and Alpaca-compatible order templates (stop-limit bracket for pre-placement, limit bracket for post-confi... | `local_calculation` — | workflow_step | production |
| **CANSLIM Screener** (`canslim-screener`) | Screen US stocks using William O'Neil's CANSLIM growth stock methodology. | `fmp` **required** | workflow_step | production |
| **Finviz Screener** (`finviz-screener`) | Build and open FinViz screener URLs from natural language requests. | `finviz` optional | standalone | production |
| **Stockbee Exhaustion Hammer Screener** (`stockbee-exhaustion-hammer-screener`) | Screen US stocks for Stockbee-style selling-exhaustion hammer candidates using quality/liquidity gates, prior momentum, pullback depth, undercut/reclaim, hammer geometry, volume confirmation, market gate, and risk-distance filters. | `fmp` **required**, `prices_json` optional, `profiles_json` optional, `local_calculation` — | workflow_step | beta |
| **Stockbee Momentum Burst Screener** (`stockbee-momentum-burst-screener`) | Screen US stocks for Stockbee-style 3-5 day momentum burst candidates using 4% breakout, dollar breakout, range expansion, volume expansion, setup quality, and risk-distance filters. | `fmp` **required**, `prices_json` optional, `local_calculation` — | workflow_step | beta |
| **Theme Detector** (`theme-detector`) | Detect and analyze trending market themes across sectors. | `fmp` optional, `finviz` _recommended_ | workflow_step | production |
| **VCP Screener** (`vcp-screener`) | Screen S&P 500 stocks for Mark Minervini's Volatility Contraction Pattern (VCP). | `polygon` **required** | workflow_step | production |

### 交易计划（Trade Planning）

| 技能 | 摘要 | 依赖 | 运营角色 | 状态 |
|---|---|---|---|---|
| **Contrarian Setup Gate** (`contrarian-setup-gate`) | Offline synthesis gate that combines COT crowding, news-reaction failure, and weekly price-action confirmation into one actionable setup_status via a fail-closed precedence state machine, implementing the decision center of Jason Shapiro's contrarian methodology. | `local_calculation` — | workflow_step | beta |
| **Drawdown Circuit Breaker** (`drawdown-circuit-breaker`) | Account-level circuit breaker that reads trader-memory-core state and decides whether new trade risk is allowed today using daily loss limits, losing-streak cooldowns, and weekly/monthly drawdown halts. | `local_calculation` — | workflow_step | beta |
| **Futures Position Sizer** (`futures-position-sizer`) | Calculate contract-based futures position sizes from a direction, entry, and stop-loss, using a verified 23-market contract-spec table (multiplier, tick size, tick value), implementing step 4 of Jason Shapiro's contrarian pipeline. | `local_calculation` — | workflow_step | beta |
| **Position Sizer** (`position-sizer`) | Calculate risk-based position sizes for long stock trades. | `local_calculation` — | workflow_step | production |
| **Pre-Trade Discipline Gate** (`pre-trade-discipline-gate`) | Offline manual-execution checklist gate that blocks planless, oversized, revenge-risk, market-regime-blocked, or circuit-breaker-blocked entries and journals the result. | `local_calculation` — | workflow_step | beta |
| **Technical Analyst** (`technical-analyst`) | This skill should be used when analyzing weekly price charts for stocks, stock indices, cryptocurrencies, or forex pairs. | `chart_image` **required**, `polygon` optional | workflow_step | production |
| **US Stock Analysis** (`us-stock-analysis`) | Comprehensive US stock analysis including fundamental analysis (financial metrics, business quality, valuation), technical analysis (indicators, chart patterns, support/resistance), stock comparisons, and investment report generation. | `user_input` **required** | standalone | production |

### 交易记忆（Trade Memory）

| 技能 | 摘要 | 依赖 | 运营角色 | 状态 |
|---|---|---|---|---|
| **Signal Postmortem** (`signal-postmortem`) | Record and analyze post-trade outcomes for signals generated by edge pipeline and other skills. | `local_calculation` —, `polygon` optional | workflow_step | production |
| **Stockbee Setup Fluency Trainer** (`stockbee-setup-fluency-trainer`) | Build a Stockbee-style setup model book from momentum-burst screener candidates, then update 3-day and 5-day forward outcomes with MFE/MAE, stop-hit status, outcome tags, and cohort statistics. | `prices_json` optional, `fmp` optional, `local_calculation` — | workflow_step | beta |
| **Trade Hypothesis Ideator** (`trade-hypothesis-ideator`) | Generate falsifiable trade strategy hypotheses from market data, trade logs, and journal snippets with ranked hypothesis cards and optional strategy.yaml export. | `local_calculation` — | workflow_step | production |
| **Trade Performance Coach** (`trade-performance-coach`) | Review closed trades, partial exits, and monthly aggregates for process adherence, risk discipline, execution quality, and evidence-based trading behavior patterns, then produce next-session operating rules. | `local_calculation` — | workflow_step | beta |
| **Trader Memory Core** (`trader-memory-core`) | Track investment theses across their lifecycle — from screening idea to closed position with postmortem. | `polygon` optional | workflow_step | production |
| **Weekly Performance Digest** (`weekly-performance-digest`) | Generate a weekly performance summary from closed trades with win rate, expectancy, and pattern analysis. | `local_calculation` — | standalone | production |

### 策略研究（Strategy Research）

| 技能 | 摘要 | 依赖 | 运营角色 | 状态 |
|---|---|---|---|---|
| **Backtest Expert** (`backtest-expert`) | Expert guidance for systematic backtesting of trading strategies. | `user_input` **required** | workflow_step | production |
| **Edge Candidate Agent** (`edge-candidate-agent`) | Generate and prioritize US equity long-side edge research tickets from EOD observations, then export pipeline-ready candidate specs for trade-strategy-pipeline Phase I. | `fmp` optional | workflow_step | production |
| **Edge Concept Synthesizer** (`edge-concept-synthesizer`) | Abstract detector tickets and hints into reusable edge concepts with thesis, invalidation signals, and strategy playbooks before strategy design/export. | `local_calculation` — | internal_component | production |
| **Edge Hint Extractor** (`edge-hint-extractor`) | Extract edge hints from daily market observations and news reactions, with optional LLM ideation, and output canonical hints.yaml for downstream concept synthesis and auto detection. | `local_calculation` — | workflow_step | production |
| **Edge Pipeline Orchestrator** (`edge-pipeline-orchestrator`) | Orchestrate the full edge research pipeline from candidate detection through strategy design, review, revision, and export. | `local_calculation` — | research_only | production |
| **Edge Signal Aggregator** (`edge-signal-aggregator`) | Aggregate and rank signals from multiple edge-finding skills (edge-candidate-agent, theme-detector, sector-analyst, institutional-flow-tracker) into a prioritized conviction dashboard with weighted scoring, deduplication, and contradicti... | `local_calculation` — | standalone | production |
| **Edge Strategy Designer** (`edge-strategy-designer`) | Convert abstract edge concepts into strategy draft variants and optional exportable ticket YAMLs for edge-candidate-agent export/validation. | `local_calculation` — | internal_component | production |
| **Edge Strategy Reviewer** (`edge-strategy-reviewer`) | Critically review strategy drafts from edge-strategy-designer for edge plausibility, overfitting risk, sample size adequacy, and execution realism. | `local_calculation` — | internal_component | production |
| **manifoldbt Backtester** (`manifoldbt-backtester`) | Runs a declarative strategy spec over OHLCV bars with the manifoldbt Rust engine and emits the eight inputs backtest-expert scores. | `manifoldbt` **required**, `ohlcv_file` **required** | research_only | beta |
| **MT5 Robot Tester** (`mt5-robot-tester`) | Batch-test MetaTrader 5 Expert Advisors through a resumable three-round local pipeline, rank results, and retain deterministic parameter and symbol learnings. | `mt5_local_files` **required**, `local_calculation` — | research_only | beta |
| **Residual Edge Analyzer** (`residual-edge-analyzer`) | Separate strategy return performance into declared baseline exposure and residual edge using HAC regression, rolling stability, baseline sensitivity, and regime diagnostics. | `local_calculation` — | research_only | beta |
| **Scenario Analyzer** (`scenario-analyzer`) | Analyze 18-month scenarios from news headlines via scenario-analyst agent with strategy-reviewer second opinion; outputs primary/secondary/tertiary impact analysis and stock picks. | `websearch` **required** | workflow_step | production |
| **Stanley Druckenmiller Investment** (`stanley-druckenmiller-investment`) | Druckenmiller Strategy Synthesizer - Integrates 8 upstream skill outputs (Market Breadth, Uptrend Analysis, Market Top, Macro Regime, FTD Detector, VCP Screener, Theme Detector, CANSLIM Screener) into a unified conviction score (0-100),... | `local_calculation` — | workflow_step | production |
| **Stockbee 20% Study** (`stockbee-20pct-study`) | Build a daily Stockbee-style +20%/-20% mover event study, classify catalysts and setup context, update forward outcomes, and export evidence-backed edge hints without treating movers as buy/sell signals. | `fmp` **required**, `prices_json` optional, `news_events_json` optional, `websearch` optional, `local_calculation` — | workflow_step | beta |
| **Strategy Pivot Designer** (`strategy-pivot-designer`) | Detect backtest iteration stagnation and generate structurally different strategy pivot proposals when parameter tuning reaches a local optimum. | `local_calculation` — | research_only | production |

### 高级卫星（Advanced Satellite）

| 技能 | 摘要 | 依赖 | 运营角色 | 状态 |
|---|---|---|---|---|
| **Earnings Trade Analyzer** (`earnings-trade-analyzer`) | Analyze recent post-earnings stocks using a 5-factor scoring system (Gap Size, Pre-Earnings Trend, Volume Trend, MA200 Position, MA50 Position). | `fmp` **required** | workflow_step | production |
| **Institutional Flow Tracker** (`institutional-flow-tracker`) | Use this skill to track institutional investor ownership changes and portfolio flows using 13F filings data. | `fmp` **required** | standalone | production |
| **Options Strategy Advisor** (`options-strategy-advisor`) | Options trading strategy analysis and simulation tool. | `fmp` optional | standalone | production |
| **Pair Trade Screener** (`pair-trade-screener`) | Statistical arbitrage tool for identifying and analyzing pair trading opportunities. | `fmp` **required** | standalone | production |
| **Parabolic Short Trade Planner** (`parabolic-short-trade-planner`) | Screen US equities for parabolic exhaustion patterns and generate conditional pre-market short plans, then evaluate intraday trigger fires from live 5-min bars. | `fmp` **required**, `alpaca` optional | standalone | production |
| **PEAD Screener** (`pead-screener`) | Screen post-earnings gap-up stocks for PEAD (Post-Earnings Announcement Drift) patterns. | `fmp` **required** | workflow_step | production |
| **Stockbee Episodic Pivot Analyzer** (`stockbee-episodic-pivot-analyzer`) | Analyze Stockbee-style Day 1 Episodic Pivot candidates from earnings, guidance, M&A, FDA, analyst, contract, product, short-squeeze, and story/theme catalysts using catalyst quality, gap/range expansion, volume shock, neglect/revaluation context, liquidity, and EP-day-low risk. | `catalyst_events_json` **required**, `fmp` optional, `local_calculation` — | workflow_step | beta |

### 元 / 开发工具（Meta）

| 技能 | 摘要 | 依赖 | 运营角色 | 状态 |
|---|---|---|---|---|
| **Data Quality Checker** (`data-quality-checker`) | Validate data quality in market analysis documents and blog articles before publication. | `local_calculation` — | standalone | production |
| **Dual Axis Skill Reviewer** (`dual-axis-skill-reviewer`) | Review skills in any project using a dual-axis method: (1) deterministic code-based checks (structure, scripts, tests, execution safety) and (2) LLM deep review findings. | `local_calculation` — | workflow_step | production |
| **Earnings Calendar** (`earnings-calendar`) | This skill retrieves upcoming earnings announcements for US stocks using the Financial Modeling Prep (FMP) API. | `fmp` **required** | standalone | production |
| **Economic Calendar Fetcher** (`economic-calendar-fetcher`) | Fetch upcoming economic events and data releases using FMP API. | `fmp` **required** | standalone | production |
| **FXMacroData Calendar** (`fxmacrodata-calendar`) | Fetch official-source macro release-calendar events using FXMacroData for trade planning and event-risk filters. | `fxmacrodata` optional | standalone | beta |
| **Skill Designer** (`skill-designer`) | Design new Claude skills from structured idea specifications. | `local_calculation` — | internal_component | production |
| **Skill Idea Miner** (`skill-idea-miner`) | Mine Claude Code session logs for skill idea candidates. | `local_calculation` — | internal_component | production |
| **Skill Integration Tester** (`skill-integration-tester`) | Validate multi-skill workflows defined in CLAUDE.md by checking skill existence, inter-skill data contracts (JSON schema compatibility), file naming conventions, and handoff integrity. | `local_calculation` — | standalone | production |
| **Trading Skills Navigator** (`trading-skills-navigator`) | Recommend the right workflow, skillset, API profile, and setup path from a natural-language trading goal. | `local_calculation` — | standalone | production |
<!-- skills-index:end name="catalog-zh" -->

## 补充工作流示例

Core + Satellite 的主要路径已在上文"推荐起步路径"中汇总。以下是包含 Advanced Satellite 和贡献者相关的补充组合示例。

### 每日市场监控
1. **Economic Calendar Fetcher** — 检查今日高影响事件（FOMC、NFP、CPI发布）
2. **Earnings Calendar** — 识别今日发布财报的主要公司
3. **Market News Analyst** — 回顾隔夜动态及市场影响
4. **Breadth Chart Analyst** — 评估整体市场健康度和仓位方向

### 每周策略回顾
1. **Sector Analyst** — 获取CSV数据识别板块轮动模式（可选提供图表图像）
2. **Technical Analyst** — 对主要指数和持仓进行趋势确认
3. **Market Environment Analysis** — 进行全面宏观简报
4. **US Market Bubble Detector** — 评估投机过热和风险水平

### 个股研究
1. **US Stock Analysis** — 进行全面的基本面和技术面分析
2. **Earnings Calendar** — 检查即将到来的财报日期
3. **Market News Analyst** — 回顾近期公司新闻和板块动态
4. **Backtest Expert** — 在仓位管理前验证入场/出场策略

### 策略性仓位配置
1. **Stanley Druckenmiller Investment Advisor** — 识别宏观主题
2. **Economic Calendar Fetcher** — 围绕关键数据发布安排入场时机
3. **Breadth Chart Analyst** + **Technical Analyst** — 获取确认信号
4. **US Market Bubble Detector** — 获取风险管理和止盈指引

### 财报动量交易
1. **Earnings Trade Analyzer** — 对近期财报反应（缺口、趋势、成交量、MA位置）评分
2. **PEAD Screener**（模式B）— 以分析器输出为输入，检测PEAD设置（红K线回调→突破信号）
3. **Technical Analyst** — 确认周线图形态和支撑/阻力位
4. 用PEAD Screener流动性过滤器确认仓位管理可行性
5. 监控SIGNAL_READY标的，以明确止损（红K线低点）和2R目标执行突破入场

### Kanchi股息工作流（美股）
1. **Kanchi Dividend SOP** — 运行5步筛选和买入条件
2. **Kanchi Dividend Review Monitor** — 运行日/周/季度异常检测队列
3. **Kanchi Dividend US Tax Accounting** — 确定账户配置和税务假设
4. `REVIEW`判定返回**Kanchi Dividend SOP**重新评估前提

### 技能质量与自动化

- **Data Quality Checker** (`data-quality-checker`)
  - 在发布前验证市场分析文档和博客文章的数据质量。
  - 5个检查类别：价格刻度不一致（ETF vs 期货位数提示）、商品表记一致性、日期星期不匹配、分配合计错误（按段落限定）、单位不一致。
  - 咨询模式 — 以警告形式显示问题，即使检测到问题也返回exit 0。最终判断由人类做出。
  - 支持全角字符（％、〜）、范围表记（50-55%）和无年份日期的年份推断。
  - 无需API密钥 — 使用本地Markdown文件离线运行。

- **Skill Designer** (`skill-designer`)
  - 从结构化的创意规范生成用于设计新技能的Claude CLI提示。
  - 将仓库规范（结构指南、质量检查清单、SKILL.md模板）嵌入提示中。
  - 包含现有技能列表以防止重复。用于技能自动生成管道的每日流程。
  - 无需API密钥。

- **Dual Axis Skill Reviewer** (`dual-axis-skill-reviewer`)
  - 使用双轴方法评审技能质量：确定性自动评分（结构、工作流、执行安全性、产出物、测试健康度）和可选LLM深度评审。
  - 5类自动轴（0-100）：元数据与用例(20)、工作流覆盖(25)、执行安全性与可复现性(25)、支持产出物(10)、测试健康度(20)。
  - 检测`knowledge_only`技能（无脚本，仅参考资料）并调整评分标准以避免不公平惩罚。
  - 可选LLM轴进行定性评审（准确性、风险、缺失逻辑、可维护性），支持加权混合。
  - `--all`批量评审所有技能，`--skip-tests`快速分类，`--project-root`评审其他项目。
  - 无需API密钥。

- **Skill Idea Miner** (`skill-idea-miner`)
  - 从Claude Code会话日志中挖掘技能创意候选，按新颖性、可行性和交易价值评分，管理优先级排序的待办列表。
  - 用于每周技能自动生成管道。也支持手动执行。
  - 无需API密钥。

## 贡献者自动化

自我改进和技能自动生成管道是面向维护者的工作流，
不是面向新手的交易操作指南。行为、副作用、手动命令和macOS定期执行请参阅
[技能自动化快速入门](docs/dev/skill-automation.zh.md)（[English](docs/dev/skill-automation.md)）。

## 自定义与贡献
- 如需调整触发描述或功能说明，请更新各文件夹内的`SKILL.md`。打包为ZIP时请确认frontmatter中的`name`与文件夹名一致。
- 可通过添加参考资料或新脚本来扩展工作流。
- 分发变更时，请重新生成反映最新内容的`.skill`文件到`skill-packages/`。
  ```bash
  python3 scripts/package_skills.py --skill <skill-name>
  ```

## API要求

部分技能需要API密钥来访问数据：

- **Intraday Market Monitor**、**VCP Screener**、**FTD Detector**、**Macro Regime Detector**、**IBD Distribution Day Monitor**、**Market Top Detector**、**Technical Analyst（价格回退）**: 需要[Polygon.io](https://polygon.io/)（Stocks Starter以上，15分钟延迟）密钥
  - 设置环境变量：`export POLYGON_API_KEY=your_key_here`（记录在已gitignore的`.envrc`中）
  - 共享客户端：`scripts/market_data/`（缓存于`.cache/market_data/`，`--provider fixture --fixture-dir DIR`用于离线回放）
  - Intraday Market Monitor通知可选使用`DISCORD_WEBHOOK_URL`
- **Economic Calendar Fetcher**、**Earnings Calendar**、**CANSLIM Screener**: 需要[Financial Modeling Prep (FMP) API](https://financialmodelingprep.com)密钥
  - 免费层：250请求/天（足够大多数技能使用）
  - 设置环境变量：`export FMP_API_KEY=your_key_here`
  - 或在运行时通过命令行参数提供密钥
- **Market Breadth Analyzer**、**Uptrend Analyzer**、**Sector Analyst**: 无需API密钥（使用GitHub公开CSV数据；Sector Analyst可选使用图表图像）
- **Theme Detector**: 核心功能无需API密钥（FINVIZ公开 + yfinance）。FMP API用于增强选股（可选），FINVIZ Elite用于获取股票列表（可选）
- **FinViz Screener**: 无需API密钥（公开FinViz筛选器）。FINVIZ Elite从`$FINVIZ_API_KEY`环境变量自动检测（可选）
- **Kanchi Dividend 3技能**（`kanchi-dividend-sop` / `kanchi-dividend-review-monitor` / `kanchi-dividend-us-tax-accounting`）: 无需API密钥（上游数据使用其他技能输出或手动输入）
- **Edge Candidate Agent** (`edge-candidate-agent`): 无需API密钥（本地YAML生成，对本地管道仓库验证）
- **Trade Hypothesis Ideator** (`trade-hypothesis-ideator`): 无需API密钥（本地JSON假设管道，可选策略导出）
- **Edge Strategy Reviewer** (`edge-strategy-reviewer`): 无需API密钥（本地YAML草稿的确定性评分）
- **Edge Pipeline Orchestrator** (`edge-pipeline-orchestrator`): 无需API密钥（通过subprocess编排本地edge技能）
- **Edge Signal Aggregator** (`edge-signal-aggregator`): 无需API密钥（整合本地JSON/YAML输出生成加权排名）
- **Trader Memory Core** (`trader-memory-core`): 🟡 可选 — Polygon仅用于`postmortem --with-prices`的MAE/MFE。核心功能离线运行
- **Exposure Coach** (`exposure-coach`): 🟡 可选 — FMP仅在使用institutional-flow-tracker数据时需要
- **Signal Postmortem** (`signal-postmortem`): 🟡 可选 — Polygon用于获取实现收益。也支持手动价格输入

## 参考链接
- Claude Skills发布概述: https://www.anthropic.com/news/skills
- Claude Code Skills指南: https://docs.claude.com/en/docs/claude-code/skills
- Financial Modeling Prep API: https://financialmodelingprep.com/developer/docs

如有问题或改进建议，请创建issue或在各技能文件夹中留下备注，便于后续用户参考。

## 许可证

本仓库所有技能和参考资料均以教育和研究为目的提供。
