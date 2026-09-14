"""Regression checks for hand-maintained FXMacroData documentation."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ZH_PAGE = ROOT / "docs" / "zh" / "skills" / "fxmacrodata-calendar.md"


def test_fxmacrodata_zh_page_exists_with_chinese_content() -> None:
    text = ZH_PAGE.read_text(encoding="utf-8")

    assert "generated: false" in text
    assert "FXMacroData Calendar" in text
    assert "无需API" in text
    assert "查看英文版指南" in text
