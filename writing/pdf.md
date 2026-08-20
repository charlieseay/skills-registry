---
name: pdf
category: writing
description: Pdf skill
triggers:
  patterns:
  - pdf
  contexts:
  - writing
success_indicators:
- Task completed successfully
- Output verified
when_to_use: Use when pdf skill
when_NOT_to_use: Use specific skills when they better match the task
avg_completion_time_mins: 15
agents_supported:
- claude-code
- nvidia-agent
- helmsman
- aider
---

Convert a Markdown file to PDF using Chrome headless.

## How to use
The user will either:
- Pass a file path as the argument (e.g. `/pdf path/to/file.md`)
- Have a file open or selected in the IDE — use that file

If no file is specified and none is open, ask the user which file to convert.

The output PDF is saved to the **reports directory** at `[your-reports-directory]`, organized by project subfolder. The project subfolder is inferred from the source file's parent directory name (e.g., `Projects/MyProject/Tech Spec.md` → `reports/MyProject/Tech Spec.pdf`).

If the source file isn't inside a recognizable project folder, save to the reports root.

Do NOT auto-open the PDF after conversion — just report the link. The user may batch multiple reports.

The reports are accessible at `[your-reports-url]` via your file server.

## Conversion pipeline

**Step 1 — Render Mermaid diagrams to PNG (if any)**

Before converting Markdown to HTML, check for ` ```mermaid ` code blocks. If found:

1. Extract each Mermaid block to a temp `.mmd` file (`/tmp/mermaid_<basename>_<index>.mmd`)
2. Render each to PNG using the Mermaid CLI:
   ```bash
   npx --yes @mermaid-js/mermaid-cli -i /tmp/mermaid_<name>_<n>.mmd -o /tmp/mermaid_<name>_<n>.png -b white -w 1200 --scale 2
   ```
3. In the Python conversion step, replace each ```` ```mermaid ``` ```` block with a base64-embedded `<img>` tag:
   ```python
   import base64
   b64 = base64.b64encode(pathlib.Path(png_path).read_bytes()).decode()
   replacement = f'![Diagram](data:image/png;base64,{b64})'
   ```

This ensures Mermaid diagrams render as actual images in the PDF. The original `.md` file is never modified — Mermaid source stays in the Markdown for Obsidian rendering.

**Step 2 — Markdown → HTML**

Use Python to convert the Markdown file to a styled HTML document. Install `markdown` into a venv if not available (prefer the project's `.venv` if one exists, otherwise use a temp venv or `pip install --user markdown`).

```python
import markdown, pathlib, re, base64

MD_FILE = "<absolute path to input .md>"
OUT_HTML = "/tmp/<basename>.html"

md_text = pathlib.Path(MD_FILE).read_text()

# Strip YAML frontmatter if present
if md_text.startswith("---"):
    end = re.search(r"\n---\n", md_text[3:])
    if end:
        md_text = md_text[3 + end.end():]

# Replace mermaid blocks with rendered PNGs (see Step 1)
diagram_idx = [0]
def replace_mermaid(match):
    png_path = f"/tmp/mermaid_<basename>_{diagram_idx[0]}.png"
    diagram_idx[0] += 1
    p = pathlib.Path(png_path)
    if p.exists():
        b64 = base64.b64encode(p.read_bytes()).decode()
        return f'![Diagram](data:image/png;base64,{b64})'
    return '> *(Diagram not available)*'

md_text = re.sub(r'```mermaid\n.*?```', replace_mermaid, md_text, flags=re.DOTALL)

# Strip Obsidian wikilinks: [[target|label]] → label, [[target]] → target
md_text = re.sub(r'\[\[([^\]|]+)\|([^\]]+)\]\]', r'\2', md_text)
md_text = re.sub(r'\[\[([^\]]+)\]\]', r'\1', md_text)

html_body = markdown.markdown(
    md_text,
    extensions=["tables", "fenced_code", "toc"]
)

full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{pathlib.Path(MD_FILE).stem}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
         max-width: 860px; margin: 2rem auto; padding: 0 1.5rem;
         font-size: 14px; line-height: 1.6; color: #222; }}
  h1 {{ font-size: 1.8rem; border-bottom: 2px solid #333; padding-bottom: .3rem; }}
  h2 {{ font-size: 1.3rem; border-bottom: 1px solid #ccc; padding-bottom: .2rem; margin-top: 1.8rem; }}
  h3 {{ font-size: 1.1rem; }}
  table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
  th, td {{ border: 1px solid #ccc; padding: 6px 10px; text-align: left; }}
  th {{ background: #f0f0f0; font-weight: 600; }}
  code {{ background: #f5f5f5; padding: 2px 5px; border-radius: 3px;
          font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 0.88em; }}
  pre {{ background: #f5f5f5; padding: 1rem; border-radius: 4px; overflow-x: auto; }}
  pre code {{ background: none; padding: 0; }}
  blockquote {{ border-left: 3px solid #aaa; margin: 0; padding-left: 1rem; color: #555; }}
  a {{ color: #0066cc; }}
  hr {{ border: none; border-top: 1px solid #ddd; margin: 1.5rem 0; }}
  img {{ max-width: 100%; height: auto; margin: 1rem 0; border-radius: 4px; }}
</style>
</head>
<body>
{html_body}
</body>
</html>"""

pathlib.Path(OUT_HTML).write_text(full_html)
```

**Step 3 — HTML → PDF via Chrome headless**

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu \
  --print-to-pdf="<absolute path to output .pdf>" \
  "file://<absolute path to OUT_HTML>"
```

Chrome headless is the standard PDF export method on this Mac. No extra tools needed — Chrome is always available at `/Applications/Google Chrome.app`.

## After conversion
- Report the output PDF path to the user as a clickable markdown link
- Report the file size
- Do NOT auto-open the PDF — just provide the link

## Notes
- Always use absolute paths — Chrome headless requires `file://` URLs with absolute paths
- The `markdown` Python package supports `tables`, `fenced_code`, and `toc` extensions — always enable all three
- YAML frontmatter (lines between `---` delimiters at the top of the file) should be stripped before conversion so it doesn't appear in the PDF
- Obsidian wikilinks (`[[target]]`, `[[target|label]]`) should be stripped to plain text before conversion
- Mermaid diagrams are always rendered to PNG and embedded — never show placeholder text in PDFs
- The source `.md` file is never modified — all transformations happen on the in-memory copy

## Lessons

- **2026-06-15** — `task_completed__cve_fix__weasyprint_in_s`: Task completed: CVE fix: weasyprint in stripe-mcp (CVE-2025-68616 HIGH) [src: task-1000735]
