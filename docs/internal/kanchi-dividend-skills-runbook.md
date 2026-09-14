# Kanchi Dividend Skills Runbook

本文档是以下3个技能的实际运营顺序固定手册。

- `kanchi-dividend-sop`
- `kanchi-dividend-review-monitor`
- `kanchi-dividend-us-tax-accounting`

## 结论

起始点是 `kanchi-dividend-sop`，这是正确的。
基本流程是 `SOP -> 监控 -> 税务/账户配置`。

## 标准流程

1. 创建选股和买入条件
使用技能: `kanchi-dividend-sop`
执行时机: 新标的评估时、月度回顾时
产出物:
- Screening结果 (`PASS/HOLD-FOR-REVIEW/FAIL`)
- 一页式标的备忘录
- 限价分批买入计划

2. 运行持仓异常检测
使用技能: `kanchi-dividend-review-monitor`
执行时机:
- 日度: T1, T4
- 周度: T3
- 季度: T2, T5
产出物:
- `OK/WARN/REVIEW` 队列
- REVIEW工单

3. 优化税务类别和账户配置
使用技能: `kanchi-dividend-us-tax-accounting`
执行时机: 新标的纳入时、大规模调仓时、年度检查时
产出物:
- 股息类别摘要
- 账户配置建议
- 税务前提的未确定事项清单

## 运营节奏

- 日度: 仅确认 `kanchi-dividend-review-monitor` 的T1/T4
- 周度: 手动确认REVIEW/WARN标的
- 月度: `kanchi-dividend-sop` 更新候选和买入条件
- 季度: T2/T5重新评估 + SOP备忘录更新
- 年度: `kanchi-dividend-us-tax-accounting` 确定税务备忘录

## 技能间的数据传递

1. `kanchi-dividend-sop` → `kanchi-dividend-review-monitor`
传递内容:
- 已纳入/持仓标的列表
- 股息安全性基准值
- 失效条件

2. `kanchi-dividend-review-monitor` → `kanchi-dividend-sop`
传递内容:
- `REVIEW` 判定原因
- 前提崩塌的疑虑
- 重新评估对象的优先级

3. `kanchi-dividend-us-tax-accounting` → `kanchi-dividend-sop`
传递内容:
- 账户约束
- 税务上的优先配置
- 新买入时的配置规则

## 最小执行示例

`kanchi-dividend-review-monitor` 的规则引擎可通过以下方式执行:

```bash
python3 skills/kanchi-dividend-review-monitor/scripts/build_review_queue.py \
  --input /path/to/monitor_input.json \
  --output /path/to/review_queue.json \
  --markdown /path/to/review_queue.md
```

输入格式请参阅 `skills/kanchi-dividend-review-monitor/references/input-schema.md`。
