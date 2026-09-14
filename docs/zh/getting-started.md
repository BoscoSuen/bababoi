---
layout: default
title: 快速入门
parent: 中文
nav_order: 1
lang_peer: /en/getting-started/
permalink: /zh/getting-started/
---

# 快速入门
{: .no_toc }

引导您完成 Claude Trading Skills 的安装、API 密钥配置，以及首次运行技能。
{: .fs-6 .fw-300 }

首次使用前，建议也查阅[常见问题]({{ '/zh/faq/' | relative_url }})，
其中汇总了访问条件、费用、安全性和功能范围。以下出现的交易术语如有不熟悉，
请参阅[术语表]({{ '/zh/glossary/' | relative_url }})中的通俗解释。

<details open markdown="block">
  <summary>目录</summary>
  {: .text-delta }
- TOC
{:toc}
</details>

---

## 前提条件

> **实际费用说明：** Claude Web 的 Skills 当前可在 Free、Pro、Max、Team、
> Enterprise 中使用。Claude Code 有独立的账号要求，不包含在
> Claude.ai 的 Free 计划中。FMP、FINVIZ Elite、Alpaca 均为可选
> 或仅用于特定技能的集成，5 个入门技能无需付费市场数据 API 订阅。
> 最新使用条件请查阅 Anthropic 的
> [Skills 帮助](https://support.claude.com/en/articles/12512180-use-skills-in-claude)
> 和 [Claude Code 设置指南](https://code.claude.com/docs/en/getting-started)。
{: .note }

| 项目 | 必需/可选 | 说明 |
|------|-----------|------|
| Claude 账号 | 必需 | 支持 Skills 的 Claude Web 账号，或满足独立使用条件的 Claude Code 账号 |
| Python 3.9+ | 必需 | 用于执行脚本。多数技能使用 Python 辅助工具 |
| FMP API 密钥 | 可选 | Financial Modeling Prep API。部分技能必需（有免费额度） |
| FINVIZ Elite | 可选 | 推荐用于加速股息筛选器、提高 Theme Detector 精度 |
| Alpaca 账号 | 可选 | Portfolio Manager 技能获取持仓数据时必需 |

---

## 安装方法

### 在 Claude Web App 中使用

1. 从 `skill-packages/` 目录下载所需技能的 `.skill` 文件（ZIP 格式）。
2. 个人账号在 **Settings > Capabilities** 中启用 **Code execution and file creation**。Team/Enterprise 可能需要组织管理员启用 Skills。
3. 打开 **Customize > Skills**，上传下载的 `.skill` 文件。
4. 确认技能出现在 Customize > Skills 列表中，必要时启用。

> 各账号类型的设置和故障排除，请参阅 Anthropic 的[最新 Skills 帮助](https://support.claude.com/en/articles/12512180-use-skills-in-claude)。
{: .note }

### 在 Claude Code（桌面端/CLI）中使用

```bash
# 1. 克隆仓库
git clone https://github.com/tradermonty/claude-trading-skills.git

# 2. 将所需技能文件夹复制到个人 Claude Code skills 目录
mkdir -p ~/.claude/skills
cp -r claude-trading-skills/skills/finviz-screener ~/.claude/skills/

# 3. 仅在新建顶层 skills 目录后需要重启
```

> 仅在项目内使用的技能也可从 `.claude/skills/` 被检测到。
> 账号要求和安装方法请参阅
> [Claude Code 设置指南](https://code.claude.com/docs/en/getting-started)。
{: .note }

> `.skill` 包由源文件夹生成，但会排除测试和本地构建产物。如需定制，请编辑源文件夹，分发前运行 `python3 scripts/package_skills.py --skill <skill-name>`。
{: .tip }

---

## API 密钥配置

### Financial Modeling Prep (FMP)

许多筛选技能使用的基本面数据 API。

| 计划 | 费用 | API 调用上限 | 适用场景 |
|------|------|-------------|----------|
| Free | 免费 | 250 次/天 | 少量个股筛选足够 |
| Starter | $29.99/月 | 750 次/天 | CANSLIM 40 股全量筛选 |
| Professional | $79.99/月 | 2,000 次/天 | 大规模筛选、多技能并用 |

**注册：** [https://site.financialmodelingprep.com/developer/docs](https://site.financialmodelingprep.com/developer/docs)

```bash
# 通过环境变量设置（推荐）
export FMP_API_KEY=your_key_here

# 或在运行脚本时通过参数指定
python3 scripts/screen_canslim.py --api-key YOUR_KEY
```

### FINVIZ Elite

用于加速股息筛选器（执行时间缩短 70-80%）和提高 Theme Detector 精度。

| 计划 | 费用 | 备注 |
|------|------|------|
| Elite 月付 | $39.50/月 | 实时数据、高速 API |
| Elite 年付 | $299.50/年（约 $24.96/月） | 年度折扣 |

**注册：** [https://elite.finviz.com/](https://elite.finviz.com/)

```bash
export FINVIZ_API_KEY=your_key_here
```

### Alpaca Trading

如需在 Portfolio Manager 中获取实时持仓数据并生成分析和再平衡方案，则为必需。
此读取/分析集成不会向券商发送订单。买卖需由人工单独确认和执行。

| 计划 | 费用 | 备注 |
|------|------|------|
| 模拟交易 | 免费 | 模拟环境，全部 API 可用 |
| 实盘交易 | 免费（无佣金） | 可交易股票和 ETF |

**注册：** [https://alpaca.markets/](https://alpaca.markets/)

```bash
export ALPACA_API_KEY="your_api_key_id"
export ALPACA_SECRET_KEY="your_secret_key"
export ALPACA_PAPER="true"  # 模拟交易时使用
```

---

## 试运行第一个技能 - FinViz Screener

FinViz Screener 无需 API 密钥，是最简单的入门技能。只需用自然语言描述筛选条件，即可生成带 FinViz 过滤器的 URL 并在 Chrome 中打开。

### 使用示例

尝试对 Claude 说：

```
找出 EPS 增长率 25% 以上、且在 SMA200 之上的股票
```

### Claude 的执行过程

1. 解析用户的自然语言，转换为 FinViz 过滤器代码
   - `fa_epsqoq_o25` (EPS QoQ 增长率 > 25%)
   - `ta_sma200_pa` (在 SMA200 之上)
2. 以表格形式展示所选过滤器供确认
3. 确认后构建 URL 并在 Chrome 中打开结果页面

### 预期输出

- Chrome 浏览器中显示 FinViz Screener 结果
- 符合条件的股票以表格形式列出
- 可切换 Overview / Valuation / Financial / Technical 等视图查看详情

> FinViz Screener 的详细用法请参阅 [FinViz Screener 指南]({{ '/zh/skills/finviz-screener/' | relative_url }})。
{: .tip }

---

## 故障排除

### 技能无法加载

| 原因 | 处理方法 |
|------|----------|
| SKILL.md 的 `name` 字段与文件夹名不匹配 | 确认 `name` 与文件夹名完全一致 |
| 技能文件夹放置位置错误 | 确认已正确复制到 Claude Code 的 Skills 目录 |
| 启动后新建了顶层 skills 目录 | 重启一次 Claude Code。现有 skills 目录内的变更会自动检测 |

### API 密钥错误

```
ERROR: FMP API key not found. Set FMP_API_KEY environment variable or use --api-key argument.
```

**处理方法：**
1. 确认环境变量已正确设置：`echo $FMP_API_KEY`
2. 在 shell 配置文件（`.zshrc` / `.bashrc`）中添加 `export FMP_API_KEY=...` 并重新加载
3. 如仍无效，通过 `--api-key` 参数直接传入

### 脚本错误（缺少依赖包）

```
ModuleNotFoundError: No module named 'requests'
```

**处理方法：**

```bash
pip install requests beautifulsoup4 lxml pandas numpy yfinance
```

> 所需依赖包因技能而异。请查阅各技能指南的"前提条件"部分。
{: .note }

### FMP API 速率限制

```
ERROR: 429 Too Many Requests - Rate limit exceeded
```

**处理方法：**
1. 脚本会自动在 60 秒后重试
2. 超出免费额度（250 次/天）时，将在次日（UTC 0:00）重置
3. 使用 `--max-candidates` 参数减少分析对象以降低用量
4. 如频繁使用，建议升级到 FMP Starter ($29.99/月)
