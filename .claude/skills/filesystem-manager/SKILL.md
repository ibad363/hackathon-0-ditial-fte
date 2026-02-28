---
name: filesystem-manager
description: Monitor a drop folder for new files and automatically create action files with metadata.
license: Apache-2.0
---

# File System Manager

Monitor drop folders for new files and create automated action workflows.

## Purpose

**Detect and Process** new files dropped into watched folders automatically. The File System Manager **monitors** specified folders (e.g., `Inbox/`) for new files, **creating** metadata files and triggering appropriate workflows.

## Design Principles

1. **OS-Level Events**: Uses `watchdog` library for efficient file system monitoring
2. **Zero Configuration**: Works with any file type
3. **Metadata Extraction**: Automatically extracts file information
4. **Workflow Trigger**: Integrates with all other skills

## Usage

```bash
# Monitor Inbox folder
python -m watchers.filesystem_watcher --vault . --watch-folder ./Inbox

# Monitor custom folder
python -m watchers.filesystem_watcher --vault . --watch-folder ./Drops
```

## Workflow

1. **Drop file** into watched folder
2. **Watcher detects** via OS file events
3. **Copies** to `Needs_Action/` with timestamp
4. **Creates** metadata file (`.md`) with:
   - Original file name and path
   - File size and type
   - Suggested actions

## Supported File Types

PDF (.pdf), Word (.docx), Excel (.xlsx), Images (.jpg, .png), Archives (.zip), and 15+ more types.

## Output Format

```
Needs_Action/
├── FILE_20260111_170000_invoice.pdf
└── FILE_20260111_170000_invoice.pdf.md (metadata)
```

## Use Cases

- Invoice processing
- Document review
- Data extraction
- Contract analysis
- Any file-based workflow

## Integration Points

Works with **all other skills** as the primary file ingestion point.
