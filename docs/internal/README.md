# Documentation Directory

This directory contains project-wide documentation, revision histories, and improvement records.

## Directory Structure

```
docs/internal/
├── README.md (this file)
├── edge_candidate_agent_design.md
├── edge-institutionalization-process.md
├── kanchi-dividend-skills-runbook.md
└── revisions/
    ├── bubble-detector-v2.0-revision.md
    ├── Breadth Chart Analyst Skill_IMPROVEMENTS_v2.0.md
    └── edge_daily_idea_to_strategy_seed_agent_design_archive_2026-02-23.md
```

## `revisions/`

Contains detailed revision and improvement records for each skill.

### Files:

- **`bubble-detector-v2.0-revision.md`** - Comprehensive improvement summary for Bubble Detector skill v2.0
  - Problems identified (4 key issues)
  - Solutions implemented
  - Comparison of improvements (10 points → 3 points case study)
  - Important lessons learned
  - Next steps

## Usage

When making significant improvements to a skill:

1. Document the revision in `revisions/[skill-name]-[version]-revision.md`
2. Include:
   - Problems identified
   - Solutions implemented
   - Before/after comparison
   - Lessons learned
3. Reference the revision document in the skill's main documentation if needed

## Related Directories

- `/[skill-name]/references/` - Skill-specific reference materials
- `/[skill-name]/SKILL.md` - Main skill definition (auto-loaded by Claude Code)

## Runbooks

- **`kanchi-dividend-skills-runbook.md`** - 运营顺序固定用手册
  - 3个技能的执行顺序 (`SOP -> 监控 -> 税务/账户配置`)
  - 日/周/月/季/年度的运营节奏
  - 技能间的输入/输出传递
- **`edge-institutionalization-process.md`** - Edge制度化流程手册
  - `观察 -> 抽象化 -> 策略化 -> 管道` 的分工流程
  - 晋级状态（Hint/Ticket/Concept/Draft/Candidate/Live）
  - Concept/Draft/Pipeline/Promotion 的门控标准
