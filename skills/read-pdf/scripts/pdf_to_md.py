#!/usr/bin/env python3
"""Convert a PDF to a temporary Markdown file using markitdown."""

import sys
import tempfile
from pathlib import Path

def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: pdf_to_md.py <path-to-pdf>", file=sys.stderr)
        return 2

    pdf_path = Path(sys.argv[1]).expanduser().resolve()
    if not pdf_path.exists():
        print(f"File not found: {pdf_path}", file=sys.stderr)
        return 1
    if pdf_path.suffix.lower() != ".pdf":
        print(f"Not a PDF file: {pdf_path}", file=sys.stderr)
        return 1

    try:
        from markitdown import MarkItDown
    except ImportError:
        print("markitdown not installed. Run: pip install 'markitdown[pdf]'", file=sys.stderr)
        return 2

    md = MarkItDown(enable_plugins=False)
    result = md.convert(str(pdf_path))

    out_name = pdf_path.stem.strip() + ".md"
    out_path = Path(tempfile.gettempdir()) / out_name
    out_path.write_text(result.markdown, encoding="utf-8")
    print(out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
