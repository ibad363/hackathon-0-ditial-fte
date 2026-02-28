---
name: mcp-builder
description: Generate complete MCP (Model Context Protocol) servers with tool definitions. Use when creating new integrations with Claude Code.
---

# MCP Builder Agent

Generate production-ready MCP servers for Claude Code integrations.

## When to Use This Agent

Use when you need to:
- Create a new MCP server for a service
- Add tools to an existing MCP server
- Generate tool schemas and definitions
- Create MCP server scaffolding

## What It Does

1. **MCP Server Generation** - Complete Node.js or Python server
2. **Tool Definitions** - JSON schemas for tool inputs
3. **Configuration** - mcp.json entry
4. **Documentation** - README with setup instructions

## Quick Start

```
Create an MCP server for Notion with:
- list_databases tool
- query_database tool
- create_page tool
```

## Output Structure

```
mcp-servers/
└── notion-mcp/
    ├── package.json (or pyproject.toml)
    ├── index.js (or main.py)
    ├── README.md
    └── tools/
        └── tool_definitions.json
```

## Templates

See `references/FORMS.md` for MCP server templates

## Reference

See `references/reference.md` for MCP SDK documentation

## Examples

See `references/examples.md` for complete MCP server examples
