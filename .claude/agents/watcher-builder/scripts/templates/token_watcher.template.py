"""
Token-Based Watcher Template

Use this template for services using API token authentication:
- Telegram, Discord, Stripe, GitHub, etc.
"""

from watchers.base_watcher import BaseWatcher
from pathlib import Path
import logging
from datetime import datetime
import os


class {SERVICE_CLASS}Watcher(BaseWatcher):
    """Watch {SERVICE_NAME} for important events using API token"""

    def __init__(self, vault_path: str, token: str,
                 check_interval: int = {DEFAULT_INTERVAL}):
        super().__init__(vault_path, check_interval)

        # API token
        if not token:
            raise ValueError(
                f"Token must be provided via:\n"
                f"  - {SERVICE_UPPER}_TOKEN environment variable\n"
                f"  - --token command line argument\n"
                f"  - .env file"
            )

        self.token = token
        self.api_base = "{API_BASE}"  # Override with actual API base URL

        # Initialize API client
        self._init_client()

    def _init_client(self):
        """Initialize API client with token

        Override this for service-specific client setup
        """
        # Example for requests-based client:
        # import requests
        # self.session = requests.Session()
        # self.session.headers.update({{
        #     'Authorization': f'Token {{self.token}}',
        #     'Content-Type': 'application/json'
        # }})

        # Example for service SDK:
        # import {SERVICE_LOWER}_sdk
        # self.client = {SERVICE_LOWER}_sdk.Client(token=self.token)

        raise NotImplementedError("Implement _init_client for your service")

    def _make_request(self, method: str, endpoint: str, params: dict = None,
                     data: dict = None) -> dict:
        """Make authenticated API request

        Implements rate limiting and error handling
        """
        import requests
        import time

        url = f"{{self.api_base}}{{endpoint}}"

        headers = {{
            'Authorization': f'Bearer {{self.token}}',
            'Content-Type': 'application/json'
        }}

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data,
                timeout=10
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                # Rate limited - wait and retry
                retry_after = int(e.response.headers.get('Retry-After', 5))
                self.logger.warning(
                    f"Rate limited, waiting {{retry_after}}s"
                )
                time.sleep(retry_after)
                return self._make_request(method, endpoint, params, data)
            elif e.response.status_code == 401:
                raise Exception("Authentication failed - check token")
            else:
                raise

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {{e}}")
            raise

    def check_for_updates(self) -> list:
        """Check for new items from {SERVICE_NAME}

        Implement your polling logic here
        """
        new_items = []

        try:
            # TODO: Implement API call to check for updates
            # Example patterns:

            # Pattern 1: Get updates with offset (Telegram-style)
            # response = self._make_request('GET', '/getUpdates', {{
            #     'offset': self.offset,
            #     'limit': 100
            # }})
            # updates = response.get('result', [])
            #
            # for update in updates:
            #     self.offset = update['update_id'] + 1
            #     if 'message' in update:
            #         new_items.append(update['message'])

            # Pattern 2: List resources with timestamp filter
            # response = self._make_request('GET', '/items', {{
            #     'since': self.last_check_timestamp
            # }})
            # new_items = response.get('items', [])

            # Pattern 3: Check specific endpoints
            # endpoints = ['/inbox', '/mentions', '/notifications']
            # for endpoint in endpoints:
            #     response = self._make_request('GET', endpoint)
            #     new_items.extend(response.get('items', []))

            pass

        except Exception as e:
            self.logger.error(f"Error checking for updates: {{e}}")
            self.log_action('error', {{'error': str(e)}})

        return new_items

    def get_item_id(self, item) -> str:
        """Get unique identifier for item"""
        # Common patterns:
        if 'id' in item:
            return f"{SERVICE_LOWER}_{{item['id']}}"

        # For Telegram-style updates
        if 'update_id' in item:
            return f"{SERVICE_LOWER}_update_{{item['update_id']}}"

        # Fallback: hash of content
        import hashlib
        content_hash = hashlib.md5(str(item).encode()).hexdigest()
        return f"{SERVICE_LOWER}_hash_{{content_hash}}"

    def create_action_file(self, item) -> Path:
        """Create action file in Needs_Action folder"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Extract relevant info
        item_id = item.get('id', 'unknown')
        item_type = item.get('type', 'event')
        safe_title = self._get_safe_title(item)

        filename = f"{SERVICE_UPPER}_{{timestamp}}_{{item_type}}_{{safe_title}}.md"
        filepath = self.needs_action / filename

        # Build frontmatter
        frontmatter = """---
type: {SERVICE_LOWER}_event
service: {SERVICE_NAME}
event_type: {item_type}
id: {item_id}
timestamp: {datetime.utcnow().isoformat()}
priority: high
status: pending
---

# {SERVICE_CLASS} Event

**Event ID:** {item_id}
**Type:** {item_type}
**Detected:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

## Event Details

{self._format_item_details(item)}

## Suggested Actions

- [ ] Review event
- [ ] Determine action needed
- [ ] Execute action via API or manually
- [ ] Archive after processing
"""

        filepath.write_text(content)
        self.log_action('created_action_file', {{
            'filename': filename,
            'type': item_type,
            'item_id': item_id
        }})

        return filepath

    def _get_safe_title(self, item: dict) -> str:
        """Extract safe title from item for filename"""
        # Try different fields
        for field in ['title', 'subject', 'name', 'text', 'description']:
            if field in item and item[field]:
                import re
                return re.sub(r'[^\w-]', '_', str(item[field])[:50])

        return 'item'

    def _format_item_details(self, item: dict) -> str:
        """Format item details for action file"""
        details = []

        # Priority fields
        for field in ['from', 'author', 'user', 'sender', 'source']:
            if field in item:
                details.append(f"**{field.capitalize()}:** {{item[field]}}")

        # Content fields
        for field in ['text', 'content', 'description', 'message']:
            if field in item:
                details.append(f"**{field.capitalize()}:**\n{{item[field]}}")

        # Metadata fields
        metadata = {{k: v for k, v in item.items()
                    if k not in ['id', 'type', 'text', 'content']}}
        if metadata:
            details.append("\n**Metadata:**")
            for key, value in metadata.items():
                details.append(f"  - {key}: {{value}}")

        return '\n'.join(details) if details else "No details available"


if __name__ == '__main__':
    import argparse
    from dotenv import load_dotenv

    # Load .env file
    load_dotenv()

    parser = argparse.ArgumentParser(description='{SERVICE_CLASS} Watcher')
    parser.add_argument('--vault', default='AI_Employee_Vault',
                       help='Path to vault')
    parser.add_argument('--token',
                       default=os.getenv('{SERVICE_UPPER}_TOKEN'),
                       help='API token (or set {SERVICE_UPPER}_TOKEN env var)')
    parser.add_argument('--interval', type=int, default={DEFAULT_INTERVAL},
                       help='Check interval in seconds')
    parser.add_argument('--test-token', action='store_true',
                       help='Test token validity')
    parser.add_argument('--dry-run', action='store_true',
                       help='Dry run mode')

    args = parser.parse_args()

    if not args.token:
        print("Error: Token required")
        print("Set {SERVICE_UPPER}_TOKEN environment variable or use --token argument")
        sys.exit(1)

    if args.test_token:
        print("Testing token...")
        try:
            watcher = {SERVICE_CLASS}Watcher(
                vault_path=args.vault,
                token=args.token,
                check_interval=1
            )
            print("✅ Token is valid!")
        except Exception as e:
            print(f"❌ Token error: {{e}}")
            sys.exit(1)
    else:
        watcher = {SERVICE_CLASS}Watcher(
            vault_path=args.vault,
            token=args.token,
            check_interval=args.interval
        )

        if args.dry_run:
            print(f"Would start {SERVICE_NAME} watcher in dry run mode")
        else:
            watcher.run()
