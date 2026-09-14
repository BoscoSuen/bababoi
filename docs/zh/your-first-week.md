---
layout: default
title: 第一周
parent: 中文
nav_order: 8
lang_peer: /en/your-first-week/
permalink: /zh/your-first-week/
---

# 第一周
{: .no_toc }

从安装到可复现的行情检查、首次日志登记、首次周度回顾，
7 天完成的入门指南。
{: .fs-6 .fw-300 }

<details open markdown="block">
  <summary>目录</summary>
  {: .text-delta }
- TOC
{:toc}
</details>

---

## 开始之前

需要的是：支持 Skills 功能的 Claude 计划、Python 3.9 以上、`git`、`uv`、
可连接公开 CSV 的网络环境。FMP、FINVIZ Elite、券商凭证等
**付费市场数据 API 不需要**。

> "无需付费 API"不等于"离线"。两个行情分析技能会下载公开 CSV。
> 日志和周度回顾在本地完成。
> 本指南不下单，也不将报告作为交易信号。
{: .note }

以下可复制的命令面向 Claude Code 或仓库根目录的终端。
在 Web App 中可从
[`skill-packages/`](https://github.com/tradermonty/claude-trading-skills/tree/main/skill-packages)
上传 `trading-skills-navigator`、`market-breadth-analyzer`、`uptrend-analyzer`、
`exposure-coach`、`trader-memory-core`、`weekly-performance-digest` 的
`.skill` 文件。

## 第 1 天 — 准备可复现的环境

如尚未克隆，请克隆仓库并安装锁定的运行时依赖。

```bash
git clone https://github.com/tradermonty/claude-trading-skills.git
cd claude-trading-skills
uv sync --locked
mkdir -p reports/first-week state/first-week-theses first-week-inputs
```

后续操作均在仓库根目录执行。为使用锁定环境中的 `requests`、`PyYAML`、`jsonschema`，
将 Python 命令统一为 `uv run python`。

## 第 2 天 — 让 Navigator 选择入口

向确定性 Navigator 查询适合初学者的 15 分钟例程。

<!-- first-week-navigator-command:start -->
```bash
uv run python skills/trading-skills-navigator/scripts/recommend.py \
  --query "I want a 15-minute daily market check without paid API keys" \
  --no-api \
  --time-budget 15m \
  --experience beginner \
  --format json
```
<!-- first-week-navigator-command:end -->

确认 JSON 中的以下字段：

```text
primary_workflow.id = market-regime-daily
primary_workflow.api_profile = no-api-basic
no_api_path = true
```

Navigator 仅提供推荐，不会自动执行其他技能。步骤和所需产出物的权威来源是
[`market-regime-daily`](https://github.com/tradermonty/claude-trading-skills/blob/main/workflows/market-regime-daily.yaml)
manifest。

## 第 3 天 — 运行无需付费 API 的行情检查

运行使用公开数据的两项必需分析。

```bash
uv run python skills/market-breadth-analyzer/scripts/market_breadth_analyzer.py \
  --output-dir reports/first-week

uv run python skills/uptrend-analyzer/scripts/uptrend_analyzer.py \
  --output-dir reports/first-week
```

从每项分析中各选择一个带时间戳的 JSON 文件。breadth 的匹配模式
有意排除 `market_breadth_history.json`。

```bash
breadth_json="$(find reports/first-week -maxdepth 1 -type f \
  -name 'market_breadth_????-??-??_??????.json' -print | sort | tail -n 1)"
uptrend_json="$(find reports/first-week -maxdepth 1 -type f \
  -name 'uptrend_analysis_????-??-??_??????.json' -print | sort | tail -n 1)"

test -n "$breadth_json" && test -f "$breadth_json"
test -n "$uptrend_json" && test -f "$uptrend_json"
```

工作流中的 market-top 步骤是可选的，因此在这条最小路径中跳过。
仅将获取到的两个产出物传给 Exposure Coach。

```bash
uv run python skills/exposure-coach/scripts/calculate_exposure.py \
  --breadth "$breadth_json" \
  --uptrend "$uptrend_json" \
  --output-dir reports/first-week
```

查看最新的 `exposure_posture_*.json`。

```bash
exposure_json="$(find reports/first-week -maxdepth 1 -type f \
  -name 'exposure_posture_????-??-??_??????.json' -print | sort | tail -n 1)"
test -n "$exposure_json" && test -f "$exposure_json"

uv run python - "$exposure_json" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as report_file:
    report = json.load(report_file)

for key in (
    "inputs_provided",
    "inputs_missing",
    "confidence",
    "recommendation",
    "exposure_ceiling_pct",
):
    print(f"{key}: {report[key]}")
PY
```

确认 `inputs_provided` 包含 `breadth` 和 `uptrend`，`inputs_missing` 中有被跳过的序列，
且 `confidence: LOW`。由于缺少关键输入 regime 和 top-risk，
故障安全推荐为 `REDUCE_ONLY` 或 `CASH_PRIORITY`，
不会是 `NEW_ENTRY_ALLOWED`。这是**输入不足时的降级策略**，
而非对整体市场看空的完整判断。如果使用可选的扩展功能，
请在对应技能指南中确认额外的数据要求。

## 第 4 天 — 创建首条日志记录

手动创建 1 条 `IDEA`。请使用真实股票代码和可证伪的陈述，
不要为了填充教程而创建虚构条目或仓位。

<!-- first-week-manual-json:start -->
```json
{
  "ticker": "AMD",
  "thesis_statement": "Observe whether AMD holds above the prior breakout area for five sessions.",
  "thesis_type": "growth_momentum"
}
```
<!-- first-week-manual-json:end -->

保存此 JSON 并执行 ingest。

```bash
cat > first-week-inputs/manual-idea.json <<'JSON'
{
  "ticker": "AMD",
  "thesis_statement": "Observe whether AMD holds above the prior breakout area for five sessions.",
  "thesis_type": "growth_momentum"
}
JSON
```

<!-- first-week-ingest-command:start -->
```bash
uv run python skills/trader-memory-core/scripts/trader_memory_cli.py ingest \
  --source manual \
  --input first-week-inputs/manual-idea.json \
  --state-dir state/first-week-theses
```
<!-- first-week-ingest-command:end -->

命令会显示生成的 thesis ID 并创建 `IDEA`。不会将交易变为 ACTIVE，
也不会下单。

## 第 5 天 — 修改之前先读取日志

列出实际记录的状态。

```bash
uv run python skills/trader-memory-core/scripts/trader_memory_cli.py store \
  --state-dir state/first-week-theses \
  list

uv run python skills/trader-memory-core/scripts/trader_memory_cli.py review \
  --state-dir state/first-week-theses \
  review-due
```

确认 ticker、thesis type、status 与输入一致。在另行验证设置之前，
保持 `IDEA` 状态不变。为保证 schema 和生命周期校验，请通过 CLI 操作，
不要手动编辑 YAML 状态文件。

## 第 6 天 — 将步骤变成例程

在考虑新的波段风险之前，重复第 3 天的操作。遵守简短的检查清单：

1. 阅读两个分析器的数据新鲜度警告。
2. 确认 Exposure Coach 实际接收了哪些输入。
3. 将缺失的输入视为缺失，不要用猜测填补。
4. 记录策略和判断理由，而非预测。
5. 下单和风险决策在此工作流之外，按自己的规则执行。

日常输出用于过程改进：如果策略为限制性，减少研究时间；
仅在完整审查允许后才进入其他个股分析。输出不是单独的买卖信号。

## 第 7 天 — 进行首次周度回顾

从本地日志生成最近 7 天的摘要。

```bash
uv run python skills/weekly-performance-digest/scripts/generate_weekly_digest.py \
  --state-dir state/first-week-theses \
  --output-dir reports/first-week \
  --verbose
```

如果没有已平仓的交易，零记录报告就是正确结果。不要为了填充指标
而创建虚构交易。阅读生成的 `weekly_digest_*.md`，然后回答：

1. 是否在考虑风险之前进行了行情检查。
2. 是否区分了缺失输入和中性信号。
3. 写下的是可证伪的论点还是叙事故事。
4. 下周要维持或修改的过程规则是什么。

至此，您已在无需付费数据 API 的情况下完成了最小的
Plan → Record → Review → Improve 循环。
在此例程可复现后，请进入[选择工作流]({{ '/zh/find-your-workflow/' | relative_url }})。
