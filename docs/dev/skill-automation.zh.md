# 技能自动化快速入门

本 GitHub 维护者指南说明了之前在主 README 中记载的
两个仓库自动化管道。不包含在初学者的交易引导或
文档站点导航中。

- [返回 README](../../README.zh.md)
- [English](skill-automation.md)
- [维护 Runbook（英语）](maintenance-runbook.md)
- [自我改善实现详情（英语）](../../CLAUDE.md#skill-self-improvement-loop)
- [自动生成实现详情（英语）](../../CLAUDE.md#skill-auto-generation-pipeline)

以下命令均从仓库根目录执行。环境搭建、drift gate、
恢复步骤、定时任务的故障排查请参考
[maintenance runbook](maintenance-runbook.md)。

## 安全性与副作用

`--dry-run` 会抑制 branch 和 PR 的创建，但不会使 filesystem 变为只读。
当前实现的边界如下所示。

| 模式 | 读取 | 本地写入 | Claude CLI | Git / GitHub 写入 |
| --- | --- | --- | --- | --- |
| 自我改善 dry-run | skill、仓库 metadata、现有 state | lock/log、auto-review 产出物、每日 summary、`.skill_improvement_state.json` | 无 | 无 |
| 自我改善正常执行 | skill、仓库 metadata、现有 state | review 产出物、log、summary、state、需要时为选定 skill | Claude CLI 可用时每次正常执行会 review 选定 skill，仅在 auto score 低于阈值时编辑 | 执行 `git pull --ff-only`。可能创建 branch、commit、push、PR，并删除已 merged 或 closed 的本地 automation branch |
| 自动生成 daily dry-run | 现有 idea backlog | lock/log、每日 summary、`.skill_generation_state.json` | 无 | 无。backlog status 也不会变更 |
| 自动生成 weekly dry-run | `~/.claude/projects/` 下的 allowlist 对象 session log | `raw_candidates.yaml`、lock/log、每周 summary、`.skill_generation_state.json` | 无 | 无。backlog 也不会更新 |
| 自动生成 weekly 正常执行 | allowlist 对象 session log 和现有 backlog | raw candidate、backlog、log、summary、state | 可能将 session 来源 signal 和长度/数量受限的 user-message sample 传给 abstraction prompt。由此生成的 candidate description 传给 scoring prompt。原始 session-log 文件本身不会直接发送 | 无 |
| 自动生成 daily 正常执行 | 现有 idea backlog 和仓库文件 | `skills/<name>/`、生成的中英文 skill docs 和 index/catalog、需要时的 `pyproject.toml`、report、backlog、log、summary、state | 设计和 review 选定 skill | 执行 `git pull --ff-only`。删除同名的过期本地 branch 后，可能创建 branch、commit、push、PR，并删除已 merged 或 closed 的本地 automation branch |

此表说明的是直接执行 Python orchestrator 时的行为。自我改善的 `launchd`
wrapper 管理专用 checkout，会执行 `fetch`、`checkout -B main origin/main`、
`reset --hard origin/main`、`clean -fd`。启用前请确认
[专用 checkout 的说明](maintenance-runbook.md#the-improvement-loop-runs-in-its-own-checkout)。

自动生成 daily 正常执行不会生成或更新 `skill-packages/<name>.skill`。
review 后需另行生成 package。

```bash
python3 scripts/package_skills.py --skill <name>
```

weekly 正常执行前请确认输入内容。输入源文件在本地，但
调用 `claude -p` 的 abstraction/scoring 阶段不完全在本地处理完成。

## 技能自我改善循环

本节面向贡献者。初次使用的人请跳过此节，
从 README 的 Core + Satellite 引导开始。

这是一个持续 review 和改善技能质量的自动管道。每天的 `launchd`
任务选择一个技能，用 Dual Axis Reviewer 进行评分，
如果得分低于 90/100，则通过 `claude -p` 应用改善并创建 PR。

### 工作原理

1. **轮询选择** — 按顺序遍历除 Reviewer 自身外的所有技能。状态持久化于 `logs/.skill_improvement_state.json`。
2. **自动评分** — 执行 `run_dual_axis_review.py` 获取确定性分数（0-100）。
3. **改善门控** — 当 `auto_review.score < 90` 时，Claude CLI 修正 SKILL.md 和参考资料。
4. **质量门控** — 改善后重新评分（启用测试）。如果分数未提升则回滚。
5. **PR 创建** — 将变更提交到 feature branch，并创建 GitHub PR 供人工 review。
6. **每日摘要** — 将结果输出到 `reports/skill-improvement-log/YYYY-MM-DD_summary.md`。

### 手动执行

```bash
# Dry-run：仅评分，不进行改善或 PR 创建
python3 scripts/run_skill_improvement_loop.py --dry-run

# 完整执行：评分，必要时改善，创建 PR
python3 scripts/run_skill_improvement_loop.py
```

之前的 README 中还记载了以下命令。

```bash
python3 scripts/run_skill_improvement_loop.py --dry-run --all
```

当前的 orchestration CLI 不接受 `--all`。如需在不修改的情况下 review
全部 skill，请直接执行 Reviewer。

```bash
uv run skills/dual-axis-skill-reviewer/scripts/run_dual_axis_review.py \
  --project-root . --all --output-dir reports/
```

### launchd 配置 (macOS)

每天 05:00 通过 macOS `launchd` 自动执行。

```bash
# 安装 agent
cp launchd/com.trade-analysis.skill-improvement.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.trade-analysis.skill-improvement.plist

# 确认
launchctl list | grep skill-improvement

# 手动触发
launchctl start com.trade-analysis.skill-improvement
```

### 主要文件

| 文件 | 用途 |
| --- | --- |
| `scripts/run_skill_improvement_loop.py` | Orchestration 脚本（选择、评分、改善、PR） |
| `scripts/run_skill_improvement.sh` | launchd 用 shell wrapper |
| `launchd/com.trade-analysis.skill-improvement.plist` | macOS launchd agent 配置 |
| `skills/dual-axis-skill-reviewer/` | Reviewer 技能（评分引擎） |
| `logs/.skill_improvement_state.json` | 轮询状态和历史记录 |
| `reports/skill-improvement-log/` | 每日摘要报告 |

## 技能自动生成管道

本节面向贡献者。这不是交易运营所必需的 workflow，
而是仓库维护用的自动化。

从 session log 中挖掘技能创意（每周），并自动执行设计、review、PR 创建
（每天）的管道。与自我改善循环联动，持续扩展技能目录。

### 工作原理

1. **每周挖掘** — 扫描 Claude Code session log，检测可技能化的重复模式。按新颖性、可行性、交易价值对每个创意评分。
2. **Backlog 评分** — 将排名后的创意保存到 `logs/.skill_generation_backlog.yaml`，带状态追踪（`pending`、`in_progress`、`completed`、`design_failed`、`review_failed`、`pr_failed`）。
3. **每日选择** — 选择最高分的 `pending` 创意。`design_failed`/`pr_failed` 重试一次（`review_failed` 表示内容质量问题，为最终判定）。
4. **设计与 Review** — Skill Designer 构建完整技能（SKILL.md、参考资料、脚本），Dual Axis Reviewer 评分。分数低则标记为 `review_failed`。
5. **PR 创建** — 将新技能提交到 feature branch，并创建 GitHub PR 供人工 review。

### 手动执行

```bash
# 每周：从 session log 中挖掘和评分创意
python3 scripts/run_skill_generation_pipeline.py --mode weekly --dry-run

# 每天：从 backlog 最高分创意设计技能
python3 scripts/run_skill_generation_pipeline.py --mode daily --dry-run

# 完整执行（创建 branch、设计技能、创建 PR）
python3 scripts/run_skill_generation_pipeline.py --mode daily
```

### launchd 配置 (macOS)

通过每周和每天两个 `launchd` agent 自动执行。

```bash
# 安装 agent
cp launchd/com.trade-analysis.skill-generation-weekly.plist ~/Library/LaunchAgents/
cp launchd/com.trade-analysis.skill-generation-daily.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.trade-analysis.skill-generation-weekly.plist
launchctl load ~/Library/LaunchAgents/com.trade-analysis.skill-generation-daily.plist

# 确认
launchctl list | grep skill-generation

# 手动触发
launchctl start com.trade-analysis.skill-generation-weekly
launchctl start com.trade-analysis.skill-generation-daily
```

### 主要文件

| 文件 | 用途 |
| --- | --- |
| `scripts/run_skill_generation_pipeline.py` | Orchestration 脚本（挖掘、选择、设计、review、PR） |
| `scripts/run_skill_generation.sh` | launchd 用 shell wrapper |
| `launchd/com.trade-analysis.skill-generation-weekly.plist` | 每周挖掘计划（周六 06:00） |
| `launchd/com.trade-analysis.skill-generation-daily.plist` | 每日生成计划（07:00） |
| `skills/skill-idea-miner/` | 挖掘与评分技能 |
| `skills/skill-designer/` | 技能设计 prompt 构建器 |
| `logs/.skill_generation_backlog.yaml` | 带状态追踪的评分创意 backlog |
| `logs/.skill_generation_state.json` | 执行历史和状态 |
| `reports/skill-generation-log/` | 每日生成摘要报告 |
