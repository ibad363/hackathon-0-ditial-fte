---
name: docx-processor
description: Convert Word documents (.docx) to Markdown format, preserving headings, tables, formatting, headers, and footers. Handles large documents (50+ pages).
license: Apache-2.0
---

# DOCX Processor

Convert Word documents to Markdown for processing within the AI Employee vault.

## Purpose

**Convert and extract** content from `.docx` Word documents into clean Markdown format. The DOCX Processor **reads** Word files dropped into the vault (via filesystem-manager or manual placement), **converts** them preserving structure (headings, tables, bold/italic, headers/footers), and **outputs** Markdown files ready for analysis, summarization, or routing by other skills.

## Design Principles

1. **Faithful Conversion**: Preserve document structure and formatting as closely as possible in Markdown
2. **Large Document Support**: Handle documents of 50+ pages without truncation
3. **Zero Configuration**: Works out of the box with any `.docx` file
4. **Vault Integration**: Output goes directly into vault folders for downstream processing

## Usage

```bash
# Convert a single document
python .claude/skills/docx-processor/scripts/convert_docx_to_md.py input.docx output.md

# Install dependencies first (if needed)
python .claude/skills/docx-processor/scripts/install_deps.py
```

## Workflow

1. **Receive** a `.docx` file (from filesystem-manager, Downloads/, or manual drop)
2. **Install** dependencies if not already present (`python-docx`)
3. **Convert** the document to Markdown using the conversion script
4. **Output** the Markdown file to the specified location
5. **Optionally route** the converted file to `Needs_Action/` or another skill for further processing

## Supported Elements

| Element | Markdown Output |
|---------|----------------|
| Headings (H1-H6) | `#` through `######` |
| Bold text | `**bold**` |
| Italic text | `*italic*` |
| Bold + Italic | `***bold italic***` |
| Underline | `<u>underline</u>` |
| Tables | Markdown table syntax |
| Nested tables | Flattened into parent cell |
| Headers | `> Header: text` (blockquote) |
| Footers | `> Footer: text` (blockquote) |

## Dependencies

- `python-docx` - install via `pip install python-docx` or run `scripts/install_deps.py`

## Output Format

Converted files are plain Markdown (`.md`) with:
- Double newlines between paragraphs
- Empty paragraphs stripped
- Tables formatted with header separators
- Headers/footers as blockquotes at top/bottom

## Use Cases

- Converting business documents for vault processing
- Extracting content from contracts, proposals, and reports
- Preparing documents for AI summarization or analysis
- Ingesting Word files dropped into the filesystem-manager watched folder

## Integration Points

- **filesystem-manager**: Detects new `.docx` files and triggers conversion
- **inbox-processor**: Routes converted documents to appropriate folders
- **content-generator**: Uses extracted content as source material
- **weekly-briefing**: Incorporates document summaries into reports

## Limitations

- Images are referenced but not embedded in Markdown output
- Complex layouts (multi-column, text boxes) may lose positioning
- Merged table cells may render incorrectly
- `.doc` (legacy format) is not supported - only `.docx`
- Cross-references and page numbers are not converted

---

*DOCX Processor Skill v1.0*
