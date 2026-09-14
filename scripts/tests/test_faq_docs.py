"""Regression tests for the bilingual first-timer FAQ and its entry points."""

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
EN_FAQ = ROOT / "docs" / "en" / "faq.md"
ZH_FAQ = ROOT / "docs" / "zh" / "faq.md"
README_EN = ROOT / "README.md"
README_ZH = ROOT / "README.zh.md"
GETTING_STARTED_EN = ROOT / "docs" / "en" / "getting-started.md"
GETTING_STARTED_ZH = ROOT / "docs" / "zh" / "getting-started.md"
DOCS_GUIDE = ROOT / "docs" / "README.md"

SKILLS_HELP_URL = "https://support.claude.com/en/articles/12512180-use-skills-in-claude"
CLAUDE_CODE_URL = "https://code.claude.com/docs/en/getting-started"
PRICING_URL = "https://claude.com/pricing"
ALLOWED_FAQ_URLS = {SKILLS_HELP_URL, CLAUDE_CODE_URL, PRICING_URL}
TOP_LEVEL_NAV = {
    "getting-started.md": 1,
    "skill-catalog.md": 2,
    "skills/index.md": 3,
    "workflows.md": 4,
    "skillsets.md": 5,
    "find-your-workflow.md": 6,
    "glossary.md": 7,
    "your-first-week.md": 8,
    "playbooks/index.md": 9,
    "faq.md": 10,
}

EXPECTED_FRONTMATTER = {
    EN_FAQ: {
        "layout": "default",
        "title": "Frequently Asked Questions",
        "parent": "English",
        "nav_order": 10,
        "lang_peer": "/zh/faq/",
        "permalink": "/en/faq/",
    },
    ZH_FAQ: {
        "layout": "default",
        "title": "常见问题",
        "parent": "中文",
        "nav_order": 10,
        "lang_peer": "/en/faq/",
        "permalink": "/zh/faq/",
    },
}

TOPIC_MARKERS = {
    "Q01": (("no code", "Claude Web"), ("代码", "Claude Web")),
    "Q02": (("Free", "Claude Code"), ("Free", "Claude Code")),
    "Q03": (("Web", "Claude Code"), ("Web", "Claude Code")),
    "Q04": (("FinViz Screener", "API key"), ("FinViz Screener", "API 密钥")),
    "Q05": (("optional", "skills-index.yaml"), ("可选", "skills-index.yaml")),
    "Q06": (("current pricing", PRICING_URL), ("最新定价", PRICING_URL)),
    "Q07": (("does not place orders", "human"), ("不执行下单", "人工")),
    "Q08": (("not financial advice", "decision"), ("不构成投资建议", "判断")),
    "Q09": (("environment variables", "rotate"), ("环境变量", "轮换")),
    "Q10": (("Chinese", "prompt"), ("中文", "提示词")),
    "Q11": (("guarantee", "source"), ("保证", "来源")),
    "Q12": (("Customize > Skills", "SKILL.md"), ("Customize > Skills", "SKILL.md")),
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_frontmatter(text: str) -> dict:
    match = re.match(r"\A---\n(.*?)\n---\n", text, flags=re.DOTALL)
    assert match, "missing YAML frontmatter"
    return yaml.safe_load(match.group(1))


def question_sections(text: str) -> dict[str, str]:
    matches = list(re.finditer(r"^## (Q\d{2})\.", text, flags=re.MULTILINE))
    return {
        match.group(1): text[match.start() : matches[index + 1].start()]
        if index + 1 < len(matches)
        else text[match.start() :]
        for index, match in enumerate(matches)
    }


def web_install_section(text: str) -> str:
    match = re.search(
        r"^### (?:(?:Use with )?Claude Web App|在 ?Claude Web ?(?:App|应用) ?中使用)\n(.*?)(?=^### |\Z)",
        text,
        flags=re.DOTALL | re.MULTILINE,
    )
    assert match, "missing Claude Web installation section"
    return match.group(1)


def test_faq_pages_have_complete_reciprocal_frontmatter() -> None:
    for path, expected in EXPECTED_FRONTMATTER.items():
        assert parse_frontmatter(read(path)) == expected


def test_top_level_navigation_is_unique_and_matches_in_both_languages() -> None:
    for lang in ("en", "zh"):
        nav_orders = {
            filename: parse_frontmatter(read(ROOT / "docs" / lang / filename))["nav_order"]
            for filename in TOP_LEVEL_NAV
        }

        assert nav_orders == TOP_LEVEL_NAV
        assert len(set(nav_orders.values())) == len(nav_orders)


def test_faq_pages_have_twelve_matched_questions_with_semantic_parity() -> None:
    en_sections = question_sections(read(EN_FAQ))
    zh_sections = question_sections(read(ZH_FAQ))
    expected_ids = list(TOPIC_MARKERS)

    assert list(en_sections) == expected_ids
    assert list(zh_sections) == expected_ids

    for question_id, (en_markers, zh_markers) in TOPIC_MARKERS.items():
        assert all(marker in en_sections[question_id] for marker in en_markers)
        assert all(marker in zh_sections[question_id] for marker in zh_markers)


def test_faq_external_links_use_the_reviewed_static_allowlist() -> None:
    for path in (EN_FAQ, ZH_FAQ):
        urls = set(re.findall(r"https://[^\s)>]+", read(path)))
        assert urls == ALLOWED_FAQ_URLS


def test_readmes_and_getting_started_link_to_the_localized_faq() -> None:
    assert "[FAQ](docs/en/faq.md)" in read(README_EN)
    assert "[常见问题](docs/zh/faq.md)" in read(README_ZH)
    assert "{{ '/en/faq/' | relative_url }}" in read(GETTING_STARTED_EN)
    assert "{{ '/zh/faq/' | relative_url }}" in read(GETTING_STARTED_ZH)


def test_existing_entry_points_describe_current_web_skills_access() -> None:
    for path in (README_EN, README_ZH, GETTING_STARTED_EN, GETTING_STARTED_ZH):
        text = read(path)
        section = web_install_section(text)

        assert SKILLS_HELP_URL in text
        assert "Settings > Capabilities" in section
        assert "Customize > Skills" in section
        assert "Code execution" in section
        assert "Settings > Skills" not in section
        assert "Settings → Skills" not in section


def test_existing_entry_points_do_not_require_a_paid_plan_for_web_skills() -> None:
    forbidden = (
        "Claude Skills require a paid Claude plan",
        "Paid Claude plan that supports the Skills feature",
        "Claude Skills需要付费Claude计划",
        "付费Claude计划 |",
    )

    for path in (README_EN, README_ZH, GETTING_STARTED_EN, GETTING_STARTED_ZH):
        text = read(path)
        assert not any(phrase in text for phrase in forbidden)
        assert "Free" in text
        assert "Claude Code" in text
        assert CLAUDE_CODE_URL in text


def test_getting_started_requires_explicit_skill_visibility_and_enablement_check() -> None:
    en_text = read(GETTING_STARTED_EN)
    zh_text = read(GETTING_STARTED_ZH)

    assert "activates automatically" not in en_text
    assert "自动激活" not in zh_text
    assert "appears in Customize > Skills" in en_text
    assert "enable it if needed" in en_text
    assert "Customize > Skills" in zh_text
    assert "启用" in zh_text


def test_getting_started_only_requires_restart_for_a_new_top_level_skills_directory() -> None:
    en_text = read(GETTING_STARTED_EN)
    zh_text = read(GETTING_STARTED_ZH)

    assert "Restart Claude Code after adding a new skill" not in en_text
    assert "添加新技能后需要重启" not in zh_text
    assert "Top-level skills directory created after this session started" in en_text
    assert "Changes inside an existing skills directory are detected automatically" in en_text
    assert "新建了顶层 skills 目录" in zh_text
    assert "自动检测" in zh_text


def test_portfolio_manager_is_documented_as_read_only_for_orders() -> None:
    en_text = read(GETTING_STARTED_EN)
    zh_text = read(GETTING_STARTED_ZH)

    assert "execute trades" not in en_text
    assert "执行交易" not in zh_text
    assert "Required for Portfolio Manager to retrieve live holdings" in en_text
    assert "Portfolio Manager" in zh_text and "实时持仓" in zh_text
    assert "does not submit broker orders" in en_text
    assert "separate human confirmation and execution" in en_text
    assert "不会向券商发送订单" in zh_text
    assert "人工" in zh_text and "确认" in zh_text


def test_contributor_guide_lists_faq_as_top_level_page_ten() -> None:
    text = read(DOCS_GUIDE)

    assert "│   ├── faq.md" in text
    assert "| **FAQ** | `en/faq.md`, `zh/faq.md` |" in text
    assert "| 10 | FAQ |" in text
