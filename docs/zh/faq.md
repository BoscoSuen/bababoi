---
layout: default
title: 常见问题
parent: 中文
nav_order: 10
lang_peer: /en/faq/
permalink: /zh/faq/
---

# 常见问题
{: .no_toc }

解答首次安装、运行 Claude Trading Skills 以及安全解读结果时的常见问题。
{: .fs-6 .fw-300 }

<details open markdown="block">
  <summary>目录</summary>
  {: .text-delta }
- TOC
{:toc}
</details>

---

## Q01. 不会写代码也能用吗？

可以。使用打包版在 Claude Web 上操作的基本流程不需要编写代码。
下载 `.skill` 文件并上传，然后用自然语言提出请求即可。
部分技能带有 Python 辅助脚本，使用 Claude Code 则需要文件操作和
终端的基础知识。最简单的入口是
[Claude Web 的使用方法]({{ '/zh/getting-started/' | relative_url }})。

## Q02. 需要哪种 Claude 计划或账号？

Anthropic 的
[Skills 官方帮助](https://support.claude.com/en/articles/12512180-use-skills-in-claude)
说明当前 Free、Pro、Max、Team、Enterprise 均可使用 Skills。
Team 和 Enterprise 还取决于组织设置。Claude Code 是另一种使用方式，
不包含在 Claude.ai 的 Free 计划中。最新的账号要求请查阅
[Claude Code 设置指南](https://code.claude.com/docs/en/getting-started)。

## Q03. 应该用 Claude Web 还是 Claude Code？

如果只想上传一个包、不管理仓库、在对话中推进工作，Claude Web 更合适。
如果需要完整源码、本地辅助脚本、可复现的基于文件的工作流以及技能定制，
请选择 Claude Code。分析目的相似，但安装方式和可用工具不同。

## Q04. 应该先试哪个技能？

推荐 FinViz Screener。基本路径下，它用自然语言的筛选条件生成
FinViz 的过滤器 URL，不需要 API 密钥。
在[快速入门教程]({{ '/zh/getting-started/' | relative_url }})中
可以查看运行示例。其他无需付费数据的入口也列在同一页面。

## Q05. 需要付费的市场数据或券商 API 吗？

并非所有工作流都需要。FMP、FINVIZ Elite、Alpaca 是可选的，
或仅用于特定技能的集成；也有使用公开 CSV、截图、本地文件即可运行的技能。
开始前请在 `skills-index.yaml` 中查看对应技能的 `integrations` 字段。
"无需 API"并不意味着该技能不需要任何输入数据。

## Q06. 实际费用是多少？

使用本仓库本身不产生订阅费用。费用取决于您选择的 Claude 使用方式和计划，
以及可选的数据服务。由于访问条件和价格会变化，请直接查阅
[Claude 最新定价](https://claude.com/pricing)和各数据提供商的页面，
而非依赖本仓库中的固定金额。

## Q07. 技能会自动交易或向券商下单吗？

不会。本仓库支持研究、筛选、仓位计算、记录和再平衡方案，但不执行下单。
即使从 Alpaca 读取投资组合信息，输出仍需人工审查，并在券商端单独确认和执行。
首次使用工作流时，请先用非生产数据进行测试。

## Q08. 输出是投资建议吗？

不是。提供的内容仅用于教育和研究目的，不构成投资建议，也不保证推荐效果
或投资回报。请将所有结果作为您自行判断的参考之一。
在采取行动前，请核实计算、假设、流动性、税务和账户限制，
必要时咨询持有资质的专业人士。

## Q09. API 密钥和非公开的投资组合信息如何处理？

将凭证存储在环境变量或经过审批的密钥管理服务中。
不要粘贴到提示词中、提交到 Git、或保存在生成的报告中。
权限应保持最小化，测试期间优先使用模拟或沙盒凭证。
如果发生泄露，请立即使其失效并轮换（重新生成）。
传递非公开数据前，请确认各技能的输入和输出。

## Q10. 可以用中文提问吗？

可以。即使技能内部有英文技术术语，也可以使用中文提示词。
明确指定股票代码、时间范围、输入来源和期望的输出格式，可以提高解读的稳定性。
本站提供对应的英文和中文指南，需要时可以比照术语。

## Q11. 结果的可信度如何？

没有任何技能保证结果完整或准确。市场数据可能存在延迟、缺失和修正，
不同数据提供商的解读也可能不同。请检查数据来源和时间、警告信息和假设条件，
复现重要计算，并在做出判断前与独立信息源进行比较。

## Q12. 技能不显示或无法运行时应检查什么？

在 Claude Web 中，确认"Code execution and file creation"已启用，
打开 Customize > Skills 检查上传的技能是否在列表中且已启用。
在 Claude Code 中，确认技能文件夹中存在 `SKILL.md` 且位于预期的 skills 目录下；
如果新建了顶层 skills 目录，需要重新加载。
启动后出错时，请根据各技能的前提条件检查所需文件、Python 依赖和 API 凭证。
