"""
OAuth 2.0 Watcher Template

Use this template for services requiring OAuth 2.0 authentication:
- Slack, Gmail, Calendar, Jira, Notion, etc.
"""

from watchers.base_watcher import BaseWatcher
from pathlib import Path
import json
import logging
from datetime import datetime


class {SERVICE_CLASS}Watcher(BaseWatcher):
    """Watch {SERVICE_NAME} for important events using OAuth 2.0"""

    def __init__(self, vault_path: str, credentials_path: str,
                 check_interval: int = {DEFAULT_INTERVAL}):
        super().__init__(vault_path, check_interval)

        # Credentials
        self.credentials_path = Path(credentials_path)
        self.token_path = self.credentials_path.parent / '.{SERVICE_LOWER}_token.json'

        # API client (will be initialized in _authenticate)
        self.client = None

        # User info (for mention detection, etc.)
        self.user_id = None
        self.bot_id = None

        # Authenticate on init
        self._authenticate()

    def _authenticate(self):
        """Load or refresh OAuth token"""
        # Check if token file exists
        if not self.token_path.exists():
            raise FileNotFoundError(
                f"Token file not found: {self.token_path}\n"
                f"Run OAuth flow first:\n"
                f"  python -m watchers.{SERVICE_LOWER}_watcher --auth"
            )

        # Load token
        with open(self.token_path) as f:
            token_data = json.load(f)

        access_token = token_data.get('access_token')
        if not access_token:
            raise ValueError("Invalid token file - missing access_token")

        # Check if token needs refresh
        expiry_time = token_data.get('expires_at')
        if expiry_time:
            from datetime import datetime
            if datetime.utcnow().timestamp() >= expiry_time:
                access_token = self._refresh_token(token_data)

        # Initialize API client with token
        self.client = self._create_client(access_token)

        # Get user/bot info
        self._get_user_info()

        self.log_action('authenticated', {'user_id': self.user_id})

    def _refresh_token(self, token_data: dict) -> str:
        """Refresh OAuth access token"""
        refresh_token = token_data.get('refresh_token')
        if not refresh_token:
            raise ValueError("No refresh_token available")

        # Load credentials
        with open(self.credentials_path) as f:
            credentials = json.load(f)

        # Make refresh request
        import requests

        response = requests.post(
            token_data['refresh_url'],  # URL for token refresh
            data={
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': credentials['client_id'],
                'client_secret': credentials['client_secret'],
            }
        )

        if response.status_code != 200:
            raise Exception(f"Token refresh failed: {response.text}")

        new_token_data = response.json()

        # Update expiry
        expires_in = new_token_data.get('expires_in', 3600)
        new_token_data['expires_at'] = (
            datetime.utcnow().timestamp() + expires_in - 300  # 5 min buffer
        )

        # Save updated token
        with open(self.token_path, 'w') as f:
            json.dump(new_token_data, f, indent=2)

        self.log_action('refreshed_token', {'expires_at': new_token_data['expires_at']})

        return new_token_data['access_token']

    def _create_client(self, access_token: str):
        """Create API client with access token

        Override this method to return service-specific client
        """
        # Example for requests-based client:
        # import requests
        # self.session = requests.Session()
        # self.session.headers.update({'Authorization': f'Bearer {access_token}'})

        raise NotImplementedError("Implement _create_client for your service")

    def _get_user_info(self):
        """Get current user/bot info

        Override this method to fetch user info from API
        """
        # Example:
        # user_info = self.client.get('/user/me').json()
        # self.user_id = user_info['id']

        raise NotImplementedError("Implement _get_user_info for your service")

    def check_for_updates(self) -> list:
        """Check for new items from {SERVICE_NAME}

        Implement your polling logic here
        """
        new_items = []

        try:
            # TODO: Implement API call to check for updates
            # Example patterns:

            # Pattern 1: Simple list endpoint
            # response = self.client.get('/items', params={
            #     'since': self.last_check_time
            # })
            # items = response.json()['items']

            # Pattern 2: Check specific resources
            # for channel_id in self.monitored_channels:
            #     response = self.client.get(f'/channels/{{channel_id}}/messages')
            #     items.extend(response.json()['messages'])

            # Pattern 3: Search/query
            # response = self.client.get('/search', params={{
            #     'q': 'is:unread',
            #     'limit': 50
            # }})
            # items = response.json()['results']

            pass

        except Exception as e:
            self.logger.error(f"Error checking for updates: {e}")
            self.log_action('error', {'error': str(e)})

        return new_items

    def get_item_id(self, item) -> str:
        """Get unique identifier for item

        Override if item structure is different
        """
        # Common patterns:
        # return item['id']
        # return item['message_id']
        # return f"{{item['type']}}_{{item['timestamp']}}"

        if 'id' in item:
            return f"{SERVICE_LOWER}_{{item['id']}}"

        # Fallback: hash of content
        import hashlib
        content_hash = hashlib.md5(str(item).encode()).hexdigest()
        return f"{SERVICE_LOWER}_hash_{{content_hash}}"

    def create_action_file(self, item) -> Path:
        """Create action file in Needs_Action folder

        Customize the frontmatter and content structure for your service
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Extract relevant info from item
        item_id = item.get('id', 'unknown')
        item_title = item.get('title', item.get('subject', str(item)[:50]))
        safe_title = re.sub(r'[^\w-]', '_', item_title)

        filename = f"{SERVICE_UPPER}_{{timestamp}}_{{safe_title}}.md"
        filepath = self.needs_action / filename

        # Build frontmatter
        frontmatter = {
            'type': '{SERVICE_LOWER}_event',
            'service': '{SERVICE_NAME}',
            'id': item_id,
            'timestamp': datetime.utcnow().isoformat(),
            'priority': 'high',
            'status': 'pending',
        }

        # Add service-specific fields
        if 'from' in item:
            frontmatter['from'] = item['from']
        if 'author' in item:
            frontmatter['author'] = item['author']
        if 'url' in item:
            frontmatter['url'] = item['url']

        # Build content
        content = f"""---
{''.join(f'{{k}}: {{v}}\n' for k, v in frontmatter.items())}---

# {SERVICE_CLASS} Event

**ID:** {item_id}
**Detected:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

## Event Details

{{self._format_item_details(item)}}

## Suggested Actions

- [ ] Review event details
- [ ] Determine action needed
- [ ] Execute action
- [ ] Archive after processing
"""

        filepath.write_text(content)
        self.log_action('created_action_file', {
            'filename': filename,
            'type': '{SERVICE_LOWER}_event',
            'item_id': item_id
        })

        return filepath

    def _format_item_details(self, item: dict) -> str:
        """Format item details for action file

        Override to customize how item data is displayed
        """
        # Example implementation:
        details = []
        for key, value in item.items():
            if key not in ['id', 'type']:
                details.append(f"**{key}:** {value}")
        return '\n'.join(details)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='{SERVICE_CLASS} Watcher')
    parser.add_argument('--vault', default='AI_Employee_Vault',
                       help='Path to vault')
    parser.add_argument('--credentials', default='.{SERVICE_LOWER}_credentials.json',
                       help='Path to credentials file')
    parser.add_argument('--interval', type=int, default={DEFAULT_INTERVAL},
                       help='Check interval in seconds')
    parser.add_argument('--auth', action='store_true',
                       help='Run OAuth authentication flow')
    parser.add_argument('--dry-run', action='store_true',
                       help='Dry run mode')

    args = parser.parse_args()

    if args.auth:
        # Run OAuth flow
        print("Starting OAuth authentication flow...")
        # TODO: Implement OAuth flow
        print("OAuth flow not yet implemented")
    else:
        # Run watcher
        watcher = {SERVICE_CLASS}Watcher(
            vault_path=args.vault,
            credentials_path=args.credentials,
            check_interval=args.interval
        )

        if args.dry_run:
            print(f"Would start {SERVICE_NAME} watcher in dry run mode")
        else:
            watcher.run()
