---
layout: default
title: 中文
nav_order: 2
has_children: true
lang_peer: /en/
permalink: /zh/
---

# Claude Trading Skills
{: .no_toc }

<div class="hero">
  <p class="hero-mantra">Empower Solo Traders and Growing Together</p>
  <p class="hero-tagline">由 Claude 驱动的专属市场分析师</p>
</div>

## 什么是 Claude Trading Skills？

Claude Trading Skills 是面向股票投资者和交易者的 **Claude 技能集**。每个技能打包了领域专用的提示词、知识库和辅助脚本，帮助 Claude 支持市场分析、个股筛选、策略验证、投资组合管理等工作。

只需用自然语言下达指令，即可获取结构化报告和可操作的洞察。

<div class="category-cards">
  <div class="category-card">
    <h3>个股筛选</h3>
    <p>基于 CANSLIM、VCP、FinViz、股息筛选器等多种投资方法的筛选技能群。只需用自然语言描述条件，即可生成候选股票列表。</p>
  </div>
  <div class="category-card">
    <h3>市场分析</h3>
    <p>板块轮动、市场广度（Breadth）、技术分析、新闻分析等，评估整体市场健康状况和方向的技能群。</p>
  </div>
  <div class="category-card">
    <h3>策略与研究</h3>
    <p>回测、期权策略、主题检测、配对交易等，支持投资策略构建与验证的技能群。</p>
  </div>
  <div class="category-card">
    <h3>投资组合与执行</h3>
    <p>Portfolio Manager、Position Sizer、财报日历等，涵盖持仓管理、仓位计算、事件监控的技能群。</p>
  </div>
</div>

---

## 三步开始

<div class="steps">
  <div class="step">
    <span class="step-number">1</span>
    <h4>安装</h4>
    <p>将 <code>.skill</code> 文件上传到 Claude Web App，或克隆仓库后部署到 Claude Code。</p>
  </div>
  <div class="step">
    <span class="step-number">2</span>
    <h4>用自然语言下达指令</h4>
    <p>用中文（或英文）告诉 Claude 你想搜索的条件或研究的内容。</p>
  </div>
  <div class="step">
    <span class="step-number">3</span>
    <h4>获取分析结果</h4>
    <p>以 Markdown + JSON 格式接收结构化报告和可操作的洞察。</p>
  </div>
</div>

---

## 推荐技能

| 技能 | 概要 | API |
|------|------|-----|
| [FinViz Screener]({{ '/zh/skills/finviz-screener/' | relative_url }}) | 用自然语言构建 FinViz 筛选条件，在 Chrome 中显示结果 | 不需要 |
| [CANSLIM Screener]({{ '/zh/skills/canslim-screener/' | relative_url }}) | 基于 William O'Neil 的 CANSLIM 方法，对成长股进行 7 维度评分 | FMP 必需 |
| [VCP Screener]({{ '/zh/skills/vcp-screener/' | relative_url }}) | 自动检测 Minervini 的 Volatility Contraction Pattern | FMP 必需 |
| [Theme Detector]({{ '/zh/skills/theme-detector/' | relative_url }}) | 通过三维评分检测跨板块的上涨/下跌主题 | 可选 |

完整技能列表请参阅[技能目录]({{ '/zh/skill-catalog/' | relative_url }})。

---

## 运营工作流

将多个技能组合使用的 Core + Satellite 运营流程请参阅[工作流]({{ '/zh/workflows/' | relative_url }})。每个工作流按顺序记录了使用的技能、判断门控和产出物，从 `workflows/*.yaml` 的权威 manifest 自动生成。

[技能集]({{ '/zh/skillsets/' | relative_url }})是与之配对的"为实现目标需要安装哪些技能"的层级，是与各工作流关联的按类别划分的技能包。从 `skillsets/*.yaml` 自动生成。

---

## 快速入门

初次使用请前往[快速入门]({{ '/zh/getting-started/' | relative_url }})页面，了解安装步骤和 API 密钥配置方法。
