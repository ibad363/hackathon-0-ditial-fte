#!/usr/bin/env python3
"""
MCP Builder - Generate MCP servers
"""

import argparse
import json
from pathlib import Path
from datetime import datetime


MCP_SERVER_TEMPLATE_NODEJS = """/**
 * {SERVICE_NAME} MCP Server
 * Generated: {DATE}
 */

const {{ Server }} = require('@modelcontextprotocol/sdk/server/index.js');
const {{ StdioServerTransport }} = require('@modelcontextprotocol/sdk/server/stdio.js');
const {{
  CallToolRequestSchema,
  ListToolsRequestSchema,
}} = require('@modelcontextprotocol/sdk/types.js');

class {SERVICE_CLASS}Server {{
  constructor() {{
    const serverInfo = {{
      name: '{service_name}-mcp',
      version: '0.1.0',
    }};

    this.server = new Server(
      serverInfo,
      {{
        capabilities: {{
          tools: {{}},
        }},
      }}
    );

    this.setupHandlers();
  }}

  setupHandlers() {{
    // List available tools
    this.server.setRequestHandler(
      ListToolsRequestSchema,
      async () => ({{
        tools: {tools}
      }})
    );

    // Handle tool calls
    this.server.setRequestHandler(
      CallToolRequestSchema,
      async (request) => {{
        const {{ name, arguments: args }} = request.params;

        switch (name) {{
{tool_cases}
          default:
            throw new Error(`Unknown tool: ${{name}}`);
        }}
      }}
    );
  }}

  async run() {{
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
  }}
}}

const server = new {SERVICE_CLASS}Server();
server.run().catch(console.error);
"""

MCP_SERVER_TEMPLATE_PYTHON = """'''
{SERVICE_NAME} MCP Server
Generated: {DATE}
'''

from mcp.server import Server
import {client_import}


class {SERVICE_CLASS}Server:
    def __init__(self):
        self.server = Server('{service_name}-mcp')
        self.client = None

        @self.server.list_tools()
        async def list_tools() -> list:
            return {tools}

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict):
            if name == '{tool_name}':
                return await self.{tool_method}(arguments)
            # Add more tools here
            else:
                raise ValueError(f"Unknown tool: {{name}}")

    async def {tool_method}(self, args: dict):
        # Implement tool logic here
        pass


if __name__ == '__main__':
    import asyncio

    server = {SERVICE_CLASS}Server()
    asyncio.run(server.server.run())
"""


def generate_mcp_server(
    service_name: str,
    tools: list,
    language: str = "nodejs",
    output_path: str = "mcp-servers"
):
    """Generate MCP server"""
    service_class = ''.join(word.capitalize() for word in service_name.split('-'))

    server_dir = Path(output_path) / f"{service_name}-mcp"
    server_dir.mkdir(parents=True, exist_ok=True)

    # Generate server code
    if language == "nodejs":
        template = MCP_SERVER_TEMPLATE_NODEJS
        package_json = {
            "name": f"{service_name}-mcp",
            "version": "0.1.0",
            "type": "module",
            "dependencies": {
                "@modelcontextprotocol/sdk": "^1.0.0"
            }
        }

        (server_dir / "package.json").write_text(json.dumps(package_json, indent=2))
        server_file = server_dir / "index.js"

    else:  # python
        template = MCP_SERVER_TEMPLATE_PYTHON
        pyproject = {
            "name": f"{service_name}-mcp",
            "version": "0.1.0",
            "dependencies": {
                "mcp": "^0.1.0"
            }
        }

        (server_dir / "pyproject.toml").write_text(json.dumps(pyproject, indent=2))
        server_file = server_dir / "main.py"

    # Format tools
    tools_json = json.dumps(tools, indent=12)

    server_code = template.format(
        SERVICE_NAME=service_name.upper(),
        SERVICE_CLASS=service_class,
        service_name=service_name,
        DATE=datetime.utcnow().isoformat(),
        tools=tools_json,
        tool_cases=_generate_tool_cases(tools),
        tool_name=tools[0]['name'] if tools else 'example_tool',
        tool_method=f"{tools[0]['name']}_handler" if tools else 'example_handler',
        client_import=f"{service_name}_client"
    )

    server_file.write_text(server_code)

    # Generate README
    readme = f"""# {service_name} MCP Server

MCP server for {service_name} integration with Claude Code.

## Installation

```bash
cd {server_dir}
{'npm install' if language == 'nodejs' else 'pip install -e .'}
```

## Configuration

Add to `~/.config/claude-code/mcp.json`:

```json
{{
  "mcpServers": {{
    "{service_name}": {{
      "command": "{'node' if language == 'nodejs' else 'python'}",
      "args": ["./{server_dir}/{'index.js' if language == 'nodejs' else 'main.py'}"]
    }}
  }}
}}
```

## Tools

{chr(10).join(f"- {tool['name']}: {tool['description']}" for tool in tools)}
"""

    (server_dir / "README.md").write_text(readme)

    print(f"✅ Generated MCP server: {server_dir}")
    return server_dir


def _generate_tool_cases(tools: list) -> str:
    """Generate switch case statements for tools"""
    cases = []
    for tool in tools:
        cases.append(f"""          case '{tool['name']}':
            return await this.{tool['name']}Handler(args);""")
    return '\n'.join(cases)


def main():
    parser = argparse.ArgumentParser(description='MCP Builder')
    parser.add_argument('service', help='Service name (e.g., notion, jira)')
    parser.add_argument('--language', choices=['nodejs', 'python'],
                       default='nodejs', help='Implementation language')
    parser.add_argument('--output', default='mcp-servers',
                       help='Output directory')

    args = parser.parse_args()

    print(f"🏗️  Building {args.service} MCP server...")

    # Example tools
    tools = [
        {
            "name": "list_items",
            "description": f"List items from {args.service}",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "number",
                        "description": "Max items to return"
                    }
                }
            }
        }
    ]

    generate_mcp_server(
        service_name=args.service,
        tools=tools,
        language=args.language,
        output_path=args.output
    )

    print("\n✅ MCP server generation complete!")
    print("\nNext steps:")
    print("1. Implement tool handlers")
    print("2. Add MCP config to Claude Code")
    print("3. Test with Claude Code")


if __name__ == '__main__':
    main()
