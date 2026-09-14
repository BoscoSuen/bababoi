# Documentation Contributor Guide

This guide explains how to write and maintain articles in the `docs/` directory. Follow these conventions so that new pages look consistent, render correctly on the Jekyll site, and integrate smoothly with the bilingual (English / Chinese) structure.

---

## Table of Contents

- [Directory Structure](#directory-structure)
- [Page Types](#page-types)
- [YAML Frontmatter Reference](#yaml-frontmatter-reference)
- [Hand-Written Skill Guide (★) Template](#hand-written-skill-guide--template)
- [Auto-Generated Skill Guide Template](#auto-generated-skill-guide-template)
- [Bilingual (en/zh) Rules](#bilingual-enzh-rules)
- [Styling Reference](#styling-reference)
- [Checklist: Adding a New Skill Guide](#checklist-adding-a-new-skill-guide)
- [Checklist: Adding a New Playbook](#checklist-adding-a-new-playbook)
- [Conventions and Pitfalls](#conventions-and-pitfalls)

---

## Directory Structure

```
docs/
├── _config.yml                  # Jekyll configuration (theme, callouts, search)
├── _includes/
│   └── nav_footer_custom.html   # EN/JP language toggle in sidebar
├── _sass/
│   └── custom/custom.scss       # Badge styles, hero, category cards
├── index.md                     # Root landing page (language selector)
├── en/                          # English documentation
│   ├── index.md                 # EN top page (parent for all EN children)
│   ├── getting-started.md
│   ├── glossary.md              # Plain-language trading terms (matched with ZH)
│   ├── your-first-week.md       # Seven-day onboarding guide (matched with ZH)
│   ├── playbooks/
│   │   └── index.md             # Playbook parent page
│   ├── faq.md                   # First-timer FAQ (matched with ZH)
│   ├── skill-catalog.md         # Full catalog table (all skills)
│   └── skills/
│       ├── index.md             # Skill Guides index (★ legend, guide table)
│       ├── vcp-screener.md      # Example: hand-written ★ guide
│       └── sector-analyst.md    # Example: auto-generated guide
├── zh/                          # Chinese documentation (mirrors en/)
│   ├── index.md
│   ├── getting-started.md
│   ├── glossary.md
│   ├── your-first-week.md
│   ├── playbooks/
│   │   └── index.md
│   ├── faq.md
│   ├── skill-catalog.md
│   └── skills/
│       ├── index.md
│       ├── vcp-screener.md      # Translated ★ guide
│       └── sector-analyst.md    # Untranslated stub
└── internal/                    # Internal docs (excluded from Jekyll build)
    ├── README.md
    └── revisions/
```

**Key points:**
- `en/` and `zh/` are parallel trees with identical file names.
- `internal/` is excluded from the site build via `_config.yml`.
- This README is for contributors on GitHub; it is not part of the published site navigation.

---

## Page Types

| Type | Location | Purpose |
|------|----------|---------|
| **Landing page** | `index.md` (root) | Language selector only |
| **Top page** | `en/index.md`, `zh/index.md` | Category cards, quick-start steps |
| **Getting Started** | `en/getting-started.md` | Installation, API setup, first-skill tutorial |
| **FAQ** | `en/faq.md`, `zh/faq.md` | First-timer setup, cost, safety, and scope questions |
| **Skill Catalog** | `en/skill-catalog.md` | Full table of all skills with descriptions and API badges |
| **Skill Guide (★)** | `en/skills/<name>.md` | Hand-written 10-section detailed guide |
| **Skill Guide (auto)** | `en/skills/<name>.md` | Auto-generated from SKILL.md: overview, workflow, resources |

Hand-written guides are marked with ★ in `en/skills/index.md` and `zh/skills/index.md`.

---

## Skill Doc Ownership

The committed `docs/{en,zh}/skills/*.md` pages are the **source of truth** — the
generator does not own them retroactively (most pages, especially the ZH
translations, were hand-curated after first generation).

- A page declares ownership via a `generated:` frontmatter key:
  `generated: true` = generator-owned (drift-gated); `generated: false` **or the
  key absent** = hand-maintained & protected. Skills in the generator's
  `HAND_WRITTEN` set are always protected.
- `generate_skill_docs.py --overwrite` **refuses** hand-maintained pages.
  `--force` is the only override and is **never** used in CI/pre-commit.
- The `skill-docs-drift` pre-commit hook + CI step run
  `generate_skill_docs.py --check`, which content-compares **only**
  `generated: true` pages and verifies every skill has EN+ZH pages with a valid
  marker. It **never** reverts hand-maintained pages.
- A brand-new auto page created by the generator is stamped `generated: true`
  (gate-owned until a human hand-edits it and flips the marker to `false` /
  removes it). After adding or removing skills, re-run the generator to refresh
  `nav_order` on generator-owned pages.

> Skill-doc ownership is declared by the per-page `generated:` marker
> (introduced in #104). The earlier per-skill doc-ownership boolean in
> `skills-index.yaml` was removed as a follow-up cleanup.

---

## YAML Frontmatter Reference

Every page requires YAML frontmatter. Fields vary by page type.

### Skill Guide Frontmatter (en)

```yaml
---
layout: default
title: "Skill Name"          # Displayed in sidebar and browser tab
grand_parent: English        # Always "English" for en/ skill guides
parent: Skill Guides         # Always "Skill Guides" for en/ skill guides
nav_order: 44                # Position in sidebar (see numbering rules below)
lang_peer: /zh/skills/skill-name/   # URL of the Chinese version
permalink: /en/skills/skill-name/   # Explicit URL path
---
```

### Skill Guide Frontmatter (zh)

```yaml
---
layout: default
title: "Skill Name"          # Keep the English skill name as title
grand_parent: 中文            # Always "中文" for zh/ skill guides
parent: 技能指南              # Always "技能指南" for zh/ skill guides
nav_order: 44                # Must match the en/ counterpart
lang_peer: /en/skills/skill-name/
permalink: /zh/skills/skill-name/
---
```

### Field Reference

| Field | Required | Description |
|-------|----------|-------------|
| `layout` | Yes | Always `default` |
| `title` | Yes | Page title. Use the English skill name even in zh/ pages |
| `grand_parent` | Yes (skills) | `English` or `中文`. Omit for top-level pages |
| `parent` | Yes | `Skill Guides` (en) or `技能指南` (zh). For top-level pages, use `English` or `中文` |
| `nav_order` | Yes | Numeric sidebar position. See [nav_order numbering](#nav_order-numbering) |
| `lang_peer` | Yes | Absolute URL path to the other-language version |
| `permalink` | Yes | Explicit URL path (prevents Jekyll auto-generation) |
| `has_children` | Conditional | Set to `true` only on index pages that have child pages |
| `nav_exclude` | Conditional | Set to `true` to hide from sidebar (used on root `index.md`) |

---

## Hand-Written Skill Guide (★) Template

Hand-written guides use a 10-section structure. This is the gold standard for documentation quality.

### Section Structure

```markdown
# Skill Name
{: .no_toc }

One-sentence description of what the skill does.
{: .fs-6 .fw-300 }

[Download Skill Package (.skill)](https://github.com/tradermonty/claude-trading-skills/raw/main/skill-packages/<name>.skill){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
[View Source on GitHub](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/<name>){: .btn .fs-5 .mb-4 .mb-md-0 }

<details open markdown="block">
  <summary>Table of Contents</summary>
  {: .text-delta }
- TOC
{:toc}
</details>

---

## 1. Overview
## 2. Prerequisites
## 3. Quick Start
## 4. How It Works
## 5. Usage Examples
## 6. Understanding the Output
## 7. Tips & Best Practices
## 8. Combining with Other Skills
## 9. Troubleshooting
## 10. Reference
```

### Section Guidelines

| Section | Content | Tips |
|---------|---------|------|
| **1. Overview** | What the skill does, what problem it solves, key features | Start with "what it solves" to hook the reader |
| **2. Prerequisites** | API keys, Python version, dependencies | Use `{: .api_required }` callout for API requirements |
| **3. Quick Start** | Minimal command to get first results | Include both CLI and natural-language prompt examples |
| **4. How It Works** | Internal pipeline, algorithm, phases | Use ASCII diagrams or numbered steps |
| **5. Usage Examples** | 4-6 real-world scenarios with prompts and expected output | Each example: Prompt → What happens → Why useful |
| **6. Understanding the Output** | Output file format, field definitions, rating tables | Use tables for score ranges and interpretations |
| **7. Tips & Best Practices** | Expert advice for getting the most value | Bullet list of actionable tips |
| **8. Combining with Other Skills** | Multi-skill workflows | Table format: Workflow name → Steps |
| **9. Troubleshooting** | Common errors and fixes | H3 per error scenario with Cause → Fix format |
| **10. Reference** | CLI arguments table, scoring component weights | Full table of all flags with defaults |

### Chinese ★ Guide Conventions

Chinese translations should:
- Keep the `# Skill Name` title in English (same as en/ version)
- Translate all section headings (e.g., "1. 概述", "2. 前提条件", "3. 快速开始")
- Translate descriptions and explanations into natural Simplified Chinese
- Keep CLI commands, code blocks, and technical terms (API names, parameter flags) in English
- Use Chinese badge text: `无需API`, `FMP必需`, `FINVIZ可选`
- Use `目录` instead of `Table of Contents` in the TOC summary

Standard section heading translations:

| EN | ZH |
|----|-----|
| 1. Overview | 1. 概述 |
| 2. Prerequisites | 2. 前提条件 |
| 3. Quick Start | 3. 快速开始 |
| 4. How It Works | 4. 工作原理 |
| 5. Usage Examples | 5. 使用示例 |
| 6. Understanding the Output | 6. 理解输出 |
| 7. Tips & Best Practices | 7. 技巧与最佳实践 |
| 8. Combining with Other Skills | 8. 与其他技能组合 |
| 9. Troubleshooting | 9. 故障排除 |
| 10. Reference | 10. 参考 |

---

## Auto-Generated Skill Guide Template

Auto-generated guides are simpler and extracted from the skill's SKILL.md. They follow this structure:

```markdown
# Skill Name
{: .no_toc }

Description from SKILL.md frontmatter.
{: .fs-6 .fw-300 }

<span class="badge badge-free">No API</span>

[Download Skill Package (.skill)](...){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
[View Source on GitHub](...){: .btn .fs-5 .mb-4 .mb-md-0 }

<details open markdown="block">
  <summary>Table of Contents</summary>
  {: .text-delta }
- TOC
{:toc}
</details>

---

## 1. Overview
## 2. When to Use
## 3. Prerequisites
## 4. Quick Start
## 5. Workflow
## 6. Resources
```

Auto-generated guides typically have 6 sections instead of 10. They lack the detailed examples, troubleshooting, and CLI reference found in ★ guides.

---

## Bilingual (en/zh) Rules

### Creating Both Versions

Every skill guide must have files in **both** `en/skills/` and `zh/skills/`:
- Same file name in both directories
- Same `nav_order` value in both
- `lang_peer` fields pointing to each other

### Fully Translated Page

Both files contain complete content in their respective languages. See `vcp-screener.md` for a reference implementation.

### Untranslated Stub (zh/)

If a Chinese translation is not yet available, create a stub page:

```markdown
---
layout: default
title: "Skill Name"
grand_parent: 中文
parent: 技能指南
nav_order: 44
lang_peer: /en/skills/skill-name/
permalink: /zh/skills/skill-name/
---

# Skill Name
{: .no_toc }

Description (can remain in English).
{: .fs-6 .fw-300 }

<span class="badge badge-free">No API</span>

> **Note:** This page has not yet been translated into Chinese.
> Please refer to the [English version]({{ '/en/skills/skill-name/' | relative_url }}) for the full guide.
{: .warning }

---

[下载技能包 (.skill)](...){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
[在GitHub上查看源码](...){: .btn .fs-5 .mb-4 .mb-md-0 }

[查看英文版指南]({{ '/en/skills/skill-name/' | relative_url }}){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
```

### Language Toggle

The sidebar language toggle (`EN | ZH`) is rendered automatically by `_includes/nav_footer_custom.html` when `lang_peer` is set.

---

## Styling Reference

### API Badges

```markdown
<!-- Required API -->
<span class="badge badge-api">FMP Required</span>

<!-- Optional API -->
<span class="badge badge-optional">FINVIZ Optional</span>

<!-- No API needed -->
<span class="badge badge-free">No API</span>

<!-- Workflow skill -->
<span class="badge badge-workflow">Workflow</span>
```

Chinese equivalents:

```markdown
<span class="badge badge-api">FMP必需</span>
<span class="badge badge-optional">FINVIZ可选</span>
<span class="badge badge-free">无需API</span>
<span class="badge badge-workflow">工作流</span>
```

### Callouts

Four callout types are defined in `_config.yml`:

```markdown
> This is a note.
{: .note }

> This is a warning.
{: .warning }

> This is a tip.
{: .tip }

> FMP API key is required.
{: .api_required }
```

### Buttons

```markdown
<!-- Primary button (blue) -->
[Label](url){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }

<!-- Secondary button (outline) -->
[Label](url){: .btn .fs-5 .mb-4 .mb-md-0 }
```

### Table of Contents

Always use this exact pattern at the top of every page (after the subtitle):

```markdown
<details open markdown="block">
  <summary>Table of Contents</summary>
  {: .text-delta }
- TOC
{:toc}
</details>
```

For Chinese pages, replace the summary text:

```markdown
<details open markdown="block">
  <summary>目录</summary>
  {: .text-delta }
- TOC
{:toc}
</details>
```

### Internal Links

Always use Liquid's `relative_url` filter for internal links:

```markdown
<!-- Link to another page -->
[FinViz Screener]({{ '/en/skills/finviz-screener/' | relative_url }})

<!-- Link to Chinese version -->
[中文版]({{ '/zh/skills/skill-name/' | relative_url }})
```

Never hardcode absolute URLs for internal pages. The `relative_url` filter ensures correct paths regardless of the `baseurl` setting.

### External Links (GitHub)

```markdown
<!-- Download button -->
[Download Skill Package (.skill)](https://github.com/tradermonty/claude-trading-skills/raw/main/skill-packages/<name>.skill){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }

<!-- Source link button -->
[View Source on GitHub](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/<name>){: .btn .fs-5 .mb-4 .mb-md-0 }
```

### Code Blocks

Always specify the language for syntax highlighting:

````markdown
```bash
python3 skills/vcp-screener/scripts/screen_vcp.py --output-dir reports/
```

```python
import os
fmp_api_key = os.environ.get('FMP_API_KEY')
```

```yaml
---
layout: default
title: "Skill Name"
---
```
````

### Heading Exclusion

Use `{: .no_toc }` on the page title (H1) to exclude it from the auto-generated TOC:

```markdown
# Skill Name
{: .no_toc }
```

---

## Checklist: Adding a New Skill Guide

Follow these steps when adding a new skill guide page:

### 1. Create the English page

- [ ] Create `docs/en/skills/<skill-name>.md`
- [ ] File name: kebab-case, lowercase, matching the skill directory name
- [ ] Add YAML frontmatter (see [reference above](#skill-guide-frontmatter-en))
- [ ] Choose a `nav_order` number (see [numbering rules](#nav_order-numbering))
- [ ] Write content using the [★ template](#hand-written-skill-guide--template) or [auto template](#auto-generated-skill-guide-template)

### 2. Create the Chinese page

- [ ] Create `docs/zh/skills/<skill-name>.md` with matching file name
- [ ] Use the zh/ frontmatter pattern (see [reference above](#skill-guide-frontmatter-zh))
- [ ] Same `nav_order` as the en/ version
- [ ] Either translate fully or use the [untranslated stub pattern](#untranslated-stub-zh)

### 3. Update index pages

- [ ] Add the skill to `docs/en/skills/index.md` (Available Guides table)
  - Include ★ marker if hand-written
  - Include API badge
- [ ] Add the skill to `docs/zh/skills/index.md` (可用指南 table)
  - Same ★ marker and badge

### 4. Update catalog pages

- [ ] Add the skill to the appropriate category in `docs/en/skill-catalog.md`
- [ ] Add the skill to the matching category in `docs/zh/skill-catalog.md`

### 5. Verify

- [ ] `lang_peer` links are correct in both directions
- [ ] `permalink` paths match the file locations
- [ ] `nav_order` does not conflict with existing pages
- [ ] API badges are consistent across index, catalog, and guide pages
- [ ] All internal links use `{{ '...' | relative_url }}` syntax

---

## Checklist: Adding a New Playbook

Playbooks are workflow-level guides (a multi-skill routine end to end), distinct
from single-skill guides. They live under the **Playbooks** (`实战手册`) nav
parent — a three-level hierarchy: `English`/`中文` → `Playbooks`/`实战手册` →
the playbook page. Reuse this convention for every new playbook (e.g. a future
Kanchi dividend playbook); do **not** re-add a playbook as a flat top-level page
under `English`/`中文`.

### 1. Create the English page

- [ ] Create `docs/en/playbooks/<playbook-name>.md`
- [ ] `parent: Playbooks` and `grand_parent: English` are **required**
- [ ] Pick a `nav_order` on the child scale under the parent (10, 12, 14, 20, … — use an unused value)

```yaml
---
layout: default
title: <Playbook Name> Playbook
parent: Playbooks
grand_parent: English
nav_order: 30
lang_peer: /zh/playbooks/<playbook-name>/
permalink: /en/playbooks/<playbook-name>/
---
```

### 2. Create the Chinese page

- [ ] Create `docs/zh/playbooks/<playbook-name>.md` with the same file name
- [ ] `parent: 实战手册` and `grand_parent: 中文` are **required**
- [ ] **Same** `nav_order` as the en/ version
- [ ] Write natural Simplified Chinese, not a heading-for-heading translation

```yaml
---
layout: default
title: <Playbook Name> 实战手册
parent: 实战手册
grand_parent: 中文
nav_order: 30
lang_peer: /en/playbooks/<playbook-name>/
permalink: /zh/playbooks/<playbook-name>/
---
```

### 3. Update the parent index pages

- [ ] Add the playbook to the list in `docs/en/playbooks/index.md`
- [ ] Add it to `docs/zh/playbooks/index.md` — the parent index lists the available playbooks; it is not an empty navigation container

### 4. Verify

- [ ] `parent` / `grand_parent` match the language (EN: `Playbooks` / `English`; ZH: `实战手册` / `中文`)
- [ ] EN and ZH use identical `nav_order`
- [ ] `permalink` matches the file path and is **preserved** — never change a published playbook URL
- [ ] Set `lang_peer` in both directions **only when the counterpart page exists**; if it does not, add the counterpart in the same PR or open an explicit follow-up issue (do not leave a `lang_peer` pointing at a missing page)
- [ ] Chinese-only headings used as in-page link targets need an explicit `{#ascii-id}` — kramdown strips non-ASCII characters when generating heading ids, so a `[..](#中文标题)` link will not resolve
- [ ] All internal links use `{{ '...' | relative_url }}` syntax
- [ ] Sidebar shows `Playbooks` / `实战手册` as a collapsible parent with the new page nested as a child (not a flat top-level item), on both mobile and desktop widths; the EN/ZH language toggle works on the page

---

## Conventions and Pitfalls

### nav_order Numbering

Current `nav_order` assignments for top-level en/ pages:

| nav_order | Page |
|-----------|------|
| 1 | Getting Started |
| 2 | Skill Catalog |
| 3 | Skill Guides (index) |
| 4 | Workflows |
| 5 | Skillsets |
| 6 | Find Your Workflow |
| 7 | Glossary |
| 8 | Your First Week |
| 9 | Playbooks |
| 10 | FAQ |

`Playbooks` (`实战手册`) is a `has_children` parent. Its child playbook pages
use their own `nav_order` scale scoped to the parent (currently 10, 12, 14, 20 —
see [Adding a New Playbook](#checklist-adding-a-new-playbook)), independent of this
top-level table.

Skill guide pages use `nav_order` values from 1 to ~50. To avoid conflicts:
1. Check existing values in `docs/en/skills/` before assigning
2. Use the next available number
3. Ensure en/ and zh/ versions use the **same** `nav_order`

### File Naming

- Always use **kebab-case**: `vcp-screener.md`, not `VCP_Screener.md`
- The file name should match the skill directory name under `skills/`
- Never include spaces in file names

### Common Mistakes

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| Forgetting `lang_peer` | No language toggle in sidebar | Add the field pointing to the counterpart |
| Missing `permalink` | Jekyll generates unexpected URL paths | Always set explicit `permalink` |
| Mismatched `nav_order` | EN and ZH pages appear at different sidebar positions | Use identical values |
| Hardcoded internal URLs | Links break if `baseurl` changes | Use `{{ '...' | relative_url }}` |
| Forgetting to update index pages | New guide is invisible in the guide listing | Update both `en/skills/index.md` and `zh/skills/index.md` |
| Forgetting to update catalog | Skill missing from the catalog overview | Update both `en/skill-catalog.md` and `zh/skill-catalog.md` |
| Using `{:toc}` without `{: .no_toc }` on H1 | Page title appears redundantly in TOC | Add `{: .no_toc }` after the H1 |
| Badge inconsistency | Confusing API requirement information | Keep badges identical across guide, index, and catalog |

### Content Language Rules

- **English pages (`en/`)**: All content in English
- **Chinese pages (`zh/`)**: Descriptions and explanations in Simplified Chinese; code, CLI commands, parameter names, and technical terms remain in English
- **Skill titles**: Always in English in both en/ and zh/ pages (for searchability)
- **API badge text**: Localized (`FMP Required` vs `FMP必需`)

### Jekyll Build Notes

- This `docs/README.md` is visible on GitHub but will also be processed by Jekyll. It is not linked in the site navigation because it has no `parent` or `nav_order` frontmatter.
- `docs/internal/` is excluded from the build via `_config.yml`.
- Custom callout types (`warning`, `note`, `tip`, `api_required`) are defined in `_config.yml` under the `callouts` key.
- Custom badge CSS classes (`badge-free`, `badge-api`, `badge-optional`, `badge-workflow`) are defined in `_sass/custom/custom.scss`.
