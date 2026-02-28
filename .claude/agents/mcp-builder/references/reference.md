---
name: mcp-builder
description: Reference documentation for building MCP (Model Context Protocol) servers
license: MIT
---

# MCP Builder Reference

---

## MCP SDK

### Node.js SDK
```javascript
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
```

### Python SDK
```python
from mcp.server import Server
```

---

## Server Capabilities

```json
{
  "capabilities": {
    "tools": {},
    "resources": {},
    "prompts": {}
  }
}
```

---

## Tool Handler Pattern

```javascript
case 'my_tool':
  try {
    const result = await myTool(args);
    return {
      content: [{ type: 'text', text: result }]
    };
  } catch (error) {
    return {
      content: [{ type: 'text', text: `Error: ${error.message}` }],
      isError: true
    };
  }
```

---

## Error Handling

Always return proper error responses:

```javascript
return {
  content: [{ type: 'text', text: error.message }],
  isError: true
};
```

---

## Input Validation

Use JSON schema for input validation:

```javascript
const schema = {
  type: 'object',
  properties: {
    param1: { type: 'string' }
  },
  required: ['param1']
};
```
