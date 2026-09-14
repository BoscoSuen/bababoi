## Summary / 概要

-

## Related issue / 相关Issue

- Refs or Closes #

## Scope and safety / 范围与安全性

- [ ] This PR does not provide financial advice, buy/sell signals, profit guarantees, or broker execution. / 不包含金融建议、买卖推荐、收益保证或经纪商执行。
- [ ] I removed secrets, API keys, personal information, brokerage account data, and proprietary customer data. / 不包含密钥、API密钥、个人信息、证券账户数据或客户专有数据。
- [ ] This PR contains no unsafe live write and does not mix unrelated cleanup. / 不包含危险的live write或无关的整理。

## Local validation / 本地验证

- [ ] Targeted tests passed with `python3.9 -m pytest <target> -q` (or the repository-compatible Python noted below). / 目标测试已通过。
- [ ] The full skill suite passed with `bash scripts/run_all_tests.sh`, or N/A is explained below. / 全部skill test已通过或N/A原因已记录。
- [ ] `ruff check skills/ scripts/` passed. / lint已通过。
- [ ] `ruff format --check skills/ scripts/` passed. / format check已通过。
- [ ] `codespell --toml pyproject.toml skills/ scripts/` passed. / 拼写检查已通过。
- [ ] `pre-commit run --all-files` passed. / 全部pre-commit hook已通过。
- [ ] `git diff --check` passed. / whitespace check已通过。

## CI and generated-artifact gates / CI与生成物检查

Mark non-applicable items as N/A and explain them under reviewer notes. / 不适用项标记为N/A，并在审查备注中说明原因。

- [ ] GitHub Actions Lint, Security, Metadata + Workflow checks, tests, and Coverage are green. / GitHub Actions全部gate为green。
- [ ] If a skill changed, EN and ZH skill docs are present or regenerated, and its `.skill` package passed `python3 scripts/package_skills.py --check --skill <skill-name>`. / skill变更时已确认英中文档和package。
- [ ] If a skill package needed regeneration, `python3 scripts/package_skills.py --skill <skill-name>` was run before the package check. / 已重新生成所需package。
- [ ] Index/workflow metadata passed `python3 scripts/validate_skills_index.py`, `python3 scripts/validate_skills_index.py --strict-workflows`, and `python3 scripts/validate_skills_index.py --strict-metadata`. / 已验证index和workflow metadata。
- [ ] Skillsets passed `python3 scripts/validate_skillsets.py`. / 已验证skillset。
- [ ] Skill docs passed `python3 scripts/generate_skill_docs.py --check`. / 已确认skill文档drift。
- [ ] Workflow docs passed `python3 scripts/generate_workflow_docs.py --check`. / 已确认workflow文档drift。
- [ ] Skillset docs passed `python3 scripts/generate_skillset_docs.py --check`. / 已确认skillset文档drift。
- [ ] README/CLAUDE catalog output passed `python3 scripts/generate_catalog_from_index.py --check`. / 已确认README/CLAUDE catalog drift。
- [ ] Website EN/ZH skill catalogs passed `python3 scripts/check_skill_catalog.py`. / 已确认网站英中skill catalog的canonical data。
- [ ] Navigator snapshot passed `python3 skills/trading-skills-navigator/scripts/build_snapshot.py --check`. / 已确认navigator snapshot。
- [ ] Changed skill packages passed `python3 scripts/check_package_drift_for_changed_skills.py`. / 已确认变更skill的package drift。
- [ ] Provider response contracts passed `python3 scripts/check_provider_contracts.py check`. / 已确认provider的响应契约。

## Reviewer notes and N/A reasons / 审查备注与N/A原因

-
