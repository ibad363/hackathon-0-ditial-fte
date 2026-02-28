#!/usr/bin/env python3
"""
Watcher Builder - Generate production-ready watcher scripts

This script creates complete watcher implementations based on user specifications.
"""

import argparse
import re
import sys
from pathlib import Path
from datetime import datetime

# Template for watchers
WATCHER_TEMPLATE = '''"""{service_name} Watcher for AI Employee System"""

{imports}

class {service_class}Watcher(BaseWatcher):
    """Watch {service_name} for important events"""

    def __init__(self, vault_path: str{init_params}, check_interval: int = {default_interval}):
        super().__init__(vault_path, check_interval)
{init_body}

        # Authenticate on init
        self._authenticate()

    def _authenticate(self):
        """{auth_comment}"""
{auth_method}

    def check_for_updates(self) -> list:
        """Check for new items from {service_name}"""
        new_items = []

        try:
{check_method}
        except Exception as e:
            self.logger.error(f"Error checking for updates: {{e}}")
            self.log_action('error', {{'error': str(e)}})

        return new_items

    def get_item_id(self, item) -> str:
        """Get unique identifier for item"""
        return "{item_id_prefix}_{{item_id}}"

    def create_action_file(self, item) -> Path:
        """Create action file in Needs_Action folder"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_title = re.sub(r'[^\\w-]', '_', str(item.get('title', 'item'))[:50])
        filename = "{action_file_prefix}_{{timestamp}}_{{safe_title}}.md"

        filepath = self.needs_action / filename

        content = f\"\"\"---
type: {action_type}
service: {service_name}
{frontmatter_fields}
timestamp: {{datetime.utcnow().isoformat()}}
priority: high
status: pending
---

# {action_title}

{content_template}

## Suggested Actions

- [ ] Review and take action
- [ ] Archive after processing
\"\"\"

        filepath.write_text(content)
        self.log_action('created_action_file', {{
            'filename': filename,
            'type': '{action_type}'
        }})

        return filepath


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='{service_class} Watcher')
    parser.add_argument('--vault', default='AI_Employee_Vault', help='Path to vault')
{cli_args}
    parser.add_argument('--interval', type=int, default={default_interval}, help='Check interval in seconds')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')

    args = parser.parse_args()

    watcher = {service_class}Watcher(
        vault_path=args.vault{watcher_init_args}
        check_interval=args.interval
    )

    if args.dry_run:
        print(f"Would start {service_name} watcher in dry run mode")
    else:
        watcher.run()
'''


def generate_watcher(
    service_name: str,
    auth_type: str = "token",
    check_interval: int = 60,
    output_path: str = "watchers",
    imports: str = "",
    init_params: str = "",
    init_body: str = "",
    auth_method: str = "",
    check_method: str = "",
    item_id_field: str = "id"
):
    """
    Generate a complete watcher script

    Args:
        service_name: Name of service (e.g., "slack", "telegram")
        auth_type: Type of authentication (oauth, token, session)
        check_interval: Seconds between checks
        output_path: Where to save the generated file
        imports: Custom import statements
        init_params: Additional __init__ parameters
        init_body: Additional __init__ body code
        auth_method: Custom authentication method
        check_method: Custom check_for_updates implementation
        item_id_field: Field to use as unique ID
    """
    # Convert service name to class name
    service_class = ''.join(word.capitalize() for word in service_name.split('_'))

    # Prepare template variables
    template_vars = {
        'service_name': service_name,
        'service_class': service_class,
        'imports': imports or "from watchers.base_watcher import BaseWatcher",
        'init_params': init_params,
        'init_body': init_body,
        'auth_comment': f"Authenticate with {service_name}",
        'auth_method': auth_method,
        'check_method': check_method,
        'default_interval': check_interval,
        'item_id_prefix': service_name,
        'action_file_prefix': service_name.upper(),
        'action_type': f"{service_name}_event",
        'action_title': f"{service_class} Event",
        'frontmatter_fields': "id: {item_id}\ndate: {item_date}",
        'content_template': "**Event:** {item_data}",
    }

    # Check if custom implementation provided
    if not auth_method:
        template_vars['auth_method'] = f"""        # Load authentication credentials
        if not hasattr(self, 'token') or not self.token:
            raise ValueError("Authentication token not provided")

        self.log_action('authenticated', {{'service': '{service_name}'}})"""

    if not check_method:
        template_vars['check_method'] = """        # TODO: Implement API call to check for updates
        # Example:
        # response = self.client.get('/items')
        # new_items = response.json()['items']

        pass"""

    # Generate watcher code
    watcher_code = WATCHER_TEMPLATE.format(**template_vars)

    # Write to file
    output_file = Path(output_path) / f"{service_name}_watcher.py"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(watcher_code)

    print(f"✅ Generated watcher: {output_file}")

    # Generate PM2 config entry
    pm2_entry = generate_pm2_config(service_name, auth_type)
    print(f"\n📋 Add this to process-manager/pm2.config.js:\n{pm2_entry}")

    # Generate credential setup instructions
    print(f"\n🔑 Credential Setup:")
    if auth_type == "oauth":
        print("""
1. Create OAuth app in {service} developer console
2. Set redirect URI: http://localhost:8080/callback
3. Export credentials:
   export {SERVICE}_CLIENT_ID="your_client_id"
   export {SERVICE}_CLIENT_SECRET="your_client_secret"
4. Run authentication flow:
   python -m watchers.{service}_watcher --auth
""".format(service=service_name, SERVICE=service_name.upper()))
    elif auth_type == "token":
        print(f"""
1. Get API token from {service_name} developer settings
2. Export token:
   export {service_name.upper()}_TOKEN="your_token_here"
3. Test token:
   python -m watchers.{service_name}_watcher --test-token
""")
    else:  # session
        print(f"""
1. Run setup wizard:
   python -m watchers.{service_name}_watcher --setup
2. Scan QR code with {service_name} mobile app
3. Session will be saved automatically
""")

    return output_file


def generate_pm2_config(service_name: str, auth_type: str) -> str:
    """Generate PM2 configuration entry"""

    entry = f'''  {{
    name: "{service_name}-watcher",
    "script": "python -m watchers.{service_name}_watcher --vault AI_Employee_Vault",'''

    if auth_type == "token":
        entry += f'''
    "interpreter": "python3",
    "exec_mode": "fork",
    "autorestart": true,
    "watch": false,
    "max_restarts": 10,
    "max_memory_restart": "500M",
    "env": {{
      "PYTHONUNBUFFERED": "1",
      "VAULT_PATH": "AI_Employee_Vault",
      "{service_name.upper()}_TOKEN": "${{{service_name.upper()}_TOKEN}}"
    }}
  }}'''
    elif auth_type == "oauth":
        entry += f'''
    "interpreter": "python3",
    "exec_mode": "fork",
    "autorestart": true,
    "watch": false,
    "max_restarts": 10,
    "max_memory_restart": "500M",
    "env": {{
      "PYTHONUNBUFFERED": "1",
      "VAULT_PATH": "AI_Employee_Vault",
      "{service_name.upper()}_CLIENT_ID": "${{{service_name.upper()}_CLIENT_ID}}",
      "{service_name.upper()}_CLIENT_SECRET": "${{{service_name.upper()}_CLIENT_SECRET}}"
    }}
  }}'''
    else:  # session
        entry += f'''
    "interpreter": "python3",
    "exec_mode": "fork",
    "autorestart": true,
    "watch": false,
    "max_restarts": 10,
    "max_memory_restart": "500M",
    "env": {{
      "PYTHONUNBUFFERED": "1",
      "VAULT_PATH": "AI_Employee_Vault",
      "{service_name.upper()}_SESSION": "./{service_name}_session"
    }}
  }}'''

    return entry


def main():
    parser = argparse.ArgumentParser(
        description='Watcher Builder - Generate production-ready watchers'
    )
    parser.add_argument('service', help='Service name (e.g., slack, telegram, jira)')
    parser.add_argument('--auth', choices=['oauth', 'token', 'session'],
                       default='token', help='Authentication type')
    parser.add_argument('--interval', type=int, default=60,
                       help='Check interval in seconds')
    parser.add_argument('--output', default='watchers',
                       help='Output directory for generated watcher')

    args = parser.parse_args()

    print(f"🏗️  Building {args.service} watcher...")
    print(f"   Auth: {args.auth}")
    print(f"   Interval: {args.interval}s")
    print()

    generate_watcher(
        service_name=args.service,
        auth_type=args.auth,
        check_interval=args.interval,
        output_path=args.output
    )

    print()
    print("✅ Watcher generation complete!")
    print()
    print("Next steps:")
    print("1. Review generated code")
    print("2. Implement TODO sections")
    print("3. Set up credentials")
    print("4. Add PM2 config to process-manager/pm2.config.js")
    print("5. Test: python -m watchers.{}_watcher --dry-run".format(args.service))


if __name__ == '__main__':
    main()
