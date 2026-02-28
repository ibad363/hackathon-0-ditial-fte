---
name: mcp-builder
description: Examples demonstrating MCP server generation and usage
license: MIT
---

# MCP Builder Examples

---

## Example 1: Generate Notion MCP Server

```bash
python .claude/skills/mcp-builder/scripts/init_mcp.py notion --language nodejs
```

Output: `mcp-servers/notion-mcp/`

---

## Example 2: Generate Python MCP Server

```bash
python .claude/skills/mcp-builder/scripts/init_mcp.py jira --language python
```

---

## Example 3: Generated Server Code

```javascript
/**
 * NOTION MCP Server
 */

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');

class NotionServer {
  setupHandlers() {
    this.server.setRequestHandler(
      ListToolsRequestSchema,
      async () => ({
        tools: [
          {
            name: 'list_databases',
            description: 'List all Notion databases',
            inputSchema: {
              type: 'object',
              properties: {}
            }
          }
        ]
      })
    );
  }
}
```

---

## Configuration

Add to `~/.config/claude-code/mcp.json`:

```json
{
  "mcpServers": {
    "notion": {
      "command": "node",
      "args": ["./mcp-servers/notion-mcp/index.js"],
      "env": {
        "NOTION_API_KEY": "${NOTION_API_KEY}"
      }
    }
  }
}
```
