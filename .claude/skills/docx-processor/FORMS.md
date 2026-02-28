# DOCX Processor - Forms and Templates

## Conversion Request Template

When requesting a DOCX conversion, provide:

```yaml
---
type: docx-conversion
source_file: /path/to/document.docx
output_file: /path/to/output.md
post_action: [none|route_to_needs_action|summarize]
priority: [high|medium|low]
requested_date: YYYY-MM-DDTHH:MM:SSZ
---
```

## Converted Document Metadata Template

After conversion, **create** this metadata alongside the output:

```yaml
---
type: docx-converted
source_file: /path/to/original.docx
output_file: /path/to/output.md
converted_date: YYYY-MM-DDTHH:MM:SSZ
file_size_bytes: 0
page_estimate: 0
elements_found:
  headings: 0
  tables: 0
  paragraphs: 0
  headers: 0
  footers: 0
status: [success|partial|failed]
notes: ""
---
```

## Processing Decision Tree

```
Is it a .docx file?
├── YES → Run conversion script
│   ├── SUCCESS → Post-action needed?
│   │   ├── route_to_needs_action → Move .md to /Needs_Action/
│   │   ├── summarize → Pass to content-generator for summary
│   │   └── none → Leave .md in output location
│   └── FAILURE → Log error, move to /Needs_Action/ with error note
└── NO → Is it a .doc file?
    ├── YES → Log: unsupported format, notify user
    └── NO → Pass to appropriate skill
```

## Conversion Log Template

**Create** conversion logs at `/Logs/docx_processing_YYYY-MM-DD.md`:

```markdown
# DOCX Processing Log - YYYY-MM-DD

## Summary
- Documents Converted: 0
- Successful: 0
- Failed: 0

## Conversions
### [Time] - filename.docx
- **Source**: /path/to/file.docx
- **Output**: /path/to/file.md
- **Status**: success/failed
- **Elements**: X headings, Y tables, Z paragraphs
- **Notes**: [any issues]

## Errors
[Details of any failed conversions]
```

## Quality Checklist

After conversion, verify:

| Check | Status |
|-------|--------|
| All headings preserved | [ ] |
| Tables formatted correctly | [ ] |
| Bold/italic formatting intact | [ ] |
| No empty/duplicate sections | [ ] |
| Headers/footers included | [ ] |
| Content complete (no truncation) | [ ] |
