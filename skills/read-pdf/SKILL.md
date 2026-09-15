---
name: read-pdf
description: Convert a PDF file to a temporary Markdown file for reading and analysis using markitdown
---

Convert PDF documents to Markdown so their content can be read, searched, and analyzed in context.

## When to Use

- User provides a PDF file path and wants to read or analyze its contents
- A workflow needs to ingest a PDF report (analyst notes, research, filings) before further analysis

## Workflow

1. Accept a PDF file path from the user (absolute or relative to the repo root).
2. Run `scripts/pdf_to_md.py` with the PDF path. The script converts the PDF to Markdown using `markitdown` and writes the output to a temporary `.md` file under the system temp directory.
3. Read the generated Markdown file and present the content to the user, or pass it to downstream skills for analysis.

## Usage

```bash
python3 skills/read-pdf/scripts/pdf_to_md.py <path-to-pdf>
```

The script prints the path of the generated Markdown file to stdout. The file is placed in the system's temp directory and named after the original PDF.

## Output

- A temporary Markdown file containing the full text content of the PDF
- The file path is printed to stdout for downstream consumption
