# DOCX Processing Examples

## Basic Conversion

Convert a simple document:
```bash
python scripts/convert_docx_to_md.py document.docx output.md
```

## Processing Long Documents

For documents with 50+ pages:
1. Verify the document opens correctly in Word
2. Run the conversion script
3. Review the output for completeness
4. Adjust formatting as needed

## Sample Workflows

### Workflow 1: Complete Document Analysis
1. Use the conversion script to create a markdown version
2. Review the markdown for missing elements
3. Process the markdown content for analysis

### Workflow 2: Section-by-Section Processing
For extremely large documents:
1. If needed, split the document into logical sections
2. Process each section separately
3. Combine the results maintaining sequence

## Expected Output

The conversion script will produce:
- Headings preserved as # ## ### etc.
- Bold text as **bold**
- Italic text as *italic*
- Lists formatted as markdown lists
- Tables as markdown tables
- Links preserved as markdown links
- Headers and footers as blockquotes