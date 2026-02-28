---
name: mcp-builder
description: Templates for generating MCP server code and configurations
license: MIT
---

# MCP Builder Templates

---

## Tool Definition Template

```json
{
  "name": "tool_name",
  "description": "What this tool does",
  "inputSchema": {
    "type": "object",
    "properties": {
      "param1": {
        "type": "string",
        "description": "Parameter description"
      }
    },
    "required": ["param1"]
  }
}
```

---

## MCP Server Structure (Node.js)

```
notion-mcp/
├── package.json
├── index.js
├── README.md
└── tools/
    └── definitions.json
```

---

## MCP Server Structure (Python)

```
notion-mcp/
├── pyproject.toml
├── main.py
├── README.md
└── tools/
    └── definitions.json
```

---

## Tool Schema Examples

### List Tool
```json
{
  "name": "list_databases",
  "description": "List all Notion databases",
  "inputSchema": {
    "type": "object",
    "properties": {}
  }
}
```

### Query Tool
```json
{
  "name": "query_database",
  "description": "Query a Notion database",
  "inputSchema": {
    "type": "object",
    "properties": {
      "database_id": {
        "type": "string",
        "description": "Database ID to query"
      },
      "filter": {
        "type": "object",
        "description": "Query filter"
      }
    },
    "required": ["database_id"]
  }
}
```

### Create Tool
```json
{
  "name": "create_page",
  "description": "Create a new page in Notion",
  "inputSchema": {
    "type": "object",
    "properties": {
      "parent_id": {
        "type": "string",
        "description": "Parent page/database ID"
      },
      "title": {
        "type": "string",
        "description": "Page title"
      },
      "content": {
        "type": "string",
        "description": "Page content (markdown)"
      }
    },
    "required": ["parent_id", "title"]
  }
}
```
