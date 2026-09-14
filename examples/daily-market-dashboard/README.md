# Daily Market Dashboard

A sample agent application that combines 5 trading skills into a unified daily market dashboard, powered by **Streamlit** and **Claude Agent SDK**.

> **[中文版请见下方](#daily-market-dashboard-中文)**

## What It Does

1. **Dashboard Tab** — Auto-generated market overview from 5 skills running in parallel
2. **Chat Tab** — Ask questions about the dashboard data; the market-advisor agent provides context-aware analysis

![Dashboard Tab](assets/dashboard.png)
![Chat Tab](assets/chat.png)

### Skills Used

| Skill | What It Measures |
|-------|-----------------|
| FTD Detector | Follow-Through Day signals for market bottom confirmation |
| Uptrend Analyzer | Market breadth uptrend composite score (0-100) |
| Market Breadth Analyzer | Broad market participation composite score (0-100) |
| Theme Detector | Bullish/bearish sector themes with lifecycle stages |
| VCP Screener | Volatility Contraction Pattern breakout candidates |

> **Note**: Market Top Detector and Economic Calendar are excluded from automated generation because they require interactive execution. Use `/market-top-detector` or `/economic-calendar-fetcher` in the Chat tab instead.

## Prerequisites

- Python 3.11+
- [Claude Agent SDK](https://docs.anthropic.com/en/docs/agent-sdk) (`pip install claude-agent-sdk`)
- Anthropic API key **or** Claude subscription (logged in via `claude` CLI)
- **No API keys required** — 3 of 5 skills (Uptrend, Breadth, Theme) use public data only; FTD Detector and VCP Screener show N/A without `FMP_API_KEY` (optional, free tier sufficient)
- Third-party Python packages (installed via `requirements.txt`): `requests`, `pandas`, `numpy`, `yfinance`, `finvizfinance`, `beautifulsoup4`, `lxml`, `pyyaml`

## Quick Start

```bash
cd examples/daily-market-dashboard

# Install dependencies
pip install -r requirements.txt

# (Optional) Configure API keys
cp .env.example .env
# Edit .env — ANTHROPIC_API_KEY is optional if using Claude subscription

# Generate today's dashboard
python3 generate_dashboard.py --project-root ../..

# Generate in Chinese
python3 generate_dashboard.py --project-root ../.. --lang zh

# Launch the app
streamlit run app.py
```

## Features

- **Language Selection** — Switch between English and Chinese via the sidebar radio button before regenerating the dashboard
- **Dashboard + Chat Tabs** — View the latest dashboard directly, or switch to Chat for interactive Q&A
- **Regenerate Button** — One-click dashboard refresh from the sidebar (runs all 5 skills in ~80s)
- **Knowledge-Aware Chat** — The agent automatically searches `knowledge/` for relevant dashboard data
- **Auto-Cleanup** — Dashboards older than 3 days are automatically removed

## Scheduled Execution (macOS)

```bash
cd examples/daily-market-dashboard

# Ensure logs directory exists
mkdir -p logs

# Install and load launchd agent
sed "s|\$HOME|$HOME|g; s|\$REPO_ROOT|$(cd ../.. && pwd)|g; s|\$PROJECT_DIR|$(pwd)|g" \
  launchd/com.trading.daily-dashboard.plist > ~/Library/LaunchAgents/com.trading.daily-dashboard.plist
launchctl load ~/Library/LaunchAgents/com.trading.daily-dashboard.plist
```

Runs `generate_dashboard.py` daily at 6:30 AM. Logs are written to `logs/`.

## Directory Structure

```
daily-market-dashboard/
├── app.py                         # Streamlit UI (Dashboard + Chat tabs)
├── generate_dashboard.py          # 5-skill parallel runner + markdown generator
├── agent/                         # Claude Agent SDK client (from template)
├── config/                        # App settings (title, icon, model)
├── knowledge/                     # Auto-generated daily_dashboard_YYYY-MM-DD.md
├── assets/                        # Screenshots for README
├── .claude/
│   ├── agents/market-advisor.md   # Market advisor persona
│   ├── settings.json              # Permission configuration
│   └── skills -> ../../../skills/ # Symlink to trading skills
├── scripts/                       # Agent-created user scripts (sandboxed)
├── logs/                          # launchd execution logs
├── .env.example
├── .mcp.json
├── .streamlit/config.toml
├── requirements.txt
├── launchd/                       # macOS scheduled execution
├── CLAUDE.md                      # Agent coding guidelines
└── README.md
```

---

# Daily Market Dashboard (中文)

基于 Streamlit 和 Claude Agent SDK 的示例应用，集成 5 个交易技能生成统一的每日市场仪表板。

## 概述

1. **仪表板标签** — 并行运行 5 个技能，生成市场概览
2. **聊天标签** — 就仪表板数据向 AI 顾问提问交流

### 使用的技能

| 技能 | 测量内容 |
|------|----------|
| FTD Detector | Follow-Through Day 信号（市场底部确认） |
| Uptrend Analyzer | 上升趋势综合分数 (0-100) |
| Market Breadth Analyzer | 市场广度综合分数 (0-100) |
| Theme Detector | 看多/看空板块主题及生命周期分析 |
| VCP Screener | 波动率收缩形态候选标的 |

> **注意**: Market Top Detector 和 Economic Calendar 需要交互式执行，不在自动生成范围内。请在聊天标签中运行 `/market-top-detector` 或 `/economic-calendar-fetcher`。

## 环境要求

- Python 3.11+
- [Claude Agent SDK](https://docs.anthropic.com/en/docs/agent-sdk)
- Anthropic API 密钥 **或** Claude 订阅（已通过 `claude` CLI 登录）
- **无需 API 密钥** — 3 个技能 (Uptrend, Breadth, Theme) 仅使用公开数据。FTD Detector 和 VCP Screener 在没有 `FMP_API_KEY` 时显示 N/A（可选，免费额度即可满足）
- 第三方 Python 包（通过 `requirements.txt` 安装）: `requests`, `pandas`, `numpy`, `yfinance`, `finvizfinance`, `beautifulsoup4`, `lxml`, `pyyaml`

## 快速开始

```bash
cd examples/daily-market-dashboard

# 安装依赖
pip install -r requirements.txt

# （可选）配置 API 密钥
cp .env.example .env
# 使用 Claude 订阅时，ANTHROPIC_API_KEY 可省略

# 生成仪表板（英文）
python3 generate_dashboard.py --project-root ../..

# 生成仪表板（中文）
python3 generate_dashboard.py --project-root ../.. --lang zh

# 启动应用
streamlit run app.py
```

## 主要功能

- **语言切换** — 通过侧栏单选按钮在 English / 中文 之间切换后重新生成仪表板
- **仪表板 + 聊天标签** — 直接查看最新仪表板，或切换到聊天进行交互式问答
- **一键重新生成** — 点击侧栏"重新生成仪表板"按钮运行全部 5 个技能（约 80 秒）
- **知识关联聊天** — Agent 自动搜索 `knowledge/` 中的仪表板数据进行回答
- **自动清理** — 自动删除 3 天前的仪表板

## 定时执行 (macOS)

```bash
cd examples/daily-market-dashboard

# 创建 logs 目录
mkdir -p logs

# 安装 launchd agent
sed "s|\$HOME|$HOME|g; s|\$REPO_ROOT|$(cd ../.. && pwd)|g; s|\$PROJECT_DIR|$(pwd)|g" \
  launchd/com.trading.daily-dashboard.plist > ~/Library/LaunchAgents/com.trading.daily-dashboard.plist
launchctl load ~/Library/LaunchAgents/com.trading.daily-dashboard.plist
```

每天早上 6:30 自动执行 `generate_dashboard.py`。日志输出到 `logs/`。
