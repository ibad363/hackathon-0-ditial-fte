"""
Session-Based Watcher Template

Use this template for services requiring browser session authentication:
- WhatsApp Web, and services without official APIs
"""

from watchers.base_watcher import BaseWatcher
from pathlib import Path
import logging
from datetime import datetime
import re


class {SERVICE_CLASS}Watcher(BaseWatcher):
    """Watch {SERVICE_NAME} for important events using browser session"""

    def __init__(self, vault_path: str, session_path: str,
                 check_interval: int = {DEFAULT_INTERVAL},
                 headless: bool = True):
        super().__init__(vault_path, check_interval)

        # Session configuration
        self.session_path = Path(session_path)
        self.session_path.mkdir(parents=True, exist_ok=True)
        self.headless = headless

        # Playwright context (initialized in _authenticate)
        self.context = None
        self.page = None

        # Authenticate on init
        self._authenticate()

    def _authenticate(self):
        """Initialize browser session or load existing session"""
        from playwright.sync_api import sync_playwright

        playwright = sync_playwright().start()

        # Try to load existing session
        if self._has_existing_session():
            self.logger.info(f"Loading existing session from {{self.session_path}}")
            browser = playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.session_path),
                headless=self.headless
            )
        else:
            self.logger.info("No existing session found, starting fresh...")
            browser = playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.session_path),
                headless=False  # Show browser for first-time setup
            )

        self.context = browser
        self.page = browser.pages[0] if browser.pages else browser.new_page()

        # Check if authenticated
        if not self._is_authenticated():
            self._setup_authentication()

        self.log_action('authenticated', {{
            'session_path': str(self.session_path)
        }})

    def _has_existing_session(self) -> bool:
        """Check if existing session exists"""
        # Check for session files
        session_files = list(self.session_path.glob('*.json'))
        if session_files:
            # Check if session is recent (last 7 days)
            import time
            latest_file = max(session_files, key=lambda p: p.stat().st_mtime)
            if time.time() - latest_file.stat().st_mtime < 7 * 24 * 3600:
                return True
        return False

    def _is_authenticated(self) -> bool:
        """Check if session is authenticated

        Override this with service-specific authentication check
        """
        # Example for WhatsApp:
        # self.page.goto('https://web.whatsapp.com')
        # self.page.wait_for_load_state('networkidle')
        # return not self.page.query_selector('[data-testid="qrcode"]')

        raise NotImplementedError("Implement _is_authenticated for your service")

    def _setup_authentication(self):
        """Setup authentication for first time

        Override this with service-specific authentication flow
        """
        # Example for WhatsApp:
        # self.page.goto('https://web.whatsapp.com')
        # print("Scan QR code with your mobile app...")
        # self.page.wait_for_selector('[data-intro="true"]', timeout=300000)  # 5 min timeout
        # print("✅ Authenticated!")

        raise NotImplementedError("Implement _setup_authentication for your service")

    def check_for_updates(self) -> list:
        """Check for new items from {SERVICE_NAME}

        Implement your web scraping/polling logic here
        """
        new_items = []

        try:
            # Navigate to service
            self.page.goto("{SERVICE_URL}")
            self.page.wait_for_load_state('networkidle')

            # TODO: Implement scraping logic
            # Example patterns:

            # Pattern 1: Query selector for list items
            # items = self.page.query_selector_all('.message-item')
            # for item in items:
            #     if self._is_new_item(item):
            #         new_items.append({{
            #             'element': item,
            #             'data': self._extract_item_data(item)
            #         }})

            # Pattern 2: Check for unread indicators
            # unread_elements = self.page.query_selector_all('[data-unread="true"]')
            # for element in unread_elements:
            #     new_items.append({{
            #         'element': element,
            #         'url': self.page.url
            #     }})

            # Pattern 3: API calls via JavaScript
            # data = self.page.evaluate('''() => {{
            #     return window.getAppData();
            # }}''')
            # new_items = data.get('newItems', [])

            pass

        except Exception as e:
            self.logger.error(f"Error checking for updates: {{e}}")
            self.log_action('error', {{'error': str(e)}})

            # Try to reload page on error
            try:
                self.page.reload()
            except:
                pass

        return new_items

    def _is_new_item(self, element) -> bool:
        """Check if item is new (not yet processed)"""
        # Get unique identifier from element
        item_id = self._get_element_id(element)

        # Check if already processed
        return item_id not in self.processed_ids

    def _get_element_id(self, element) -> str:
        """Extract unique ID from element"""
        # Try different attributes
        for attr in ['data-id', 'id', 'data-message-id', 'data-timestamp']:
            value = element.get_attribute(attr)
            if value:
                return f"{{SERVICE_LOWER}}_{{value}}"

        # Fallback: use element text content
        text = element.inner_text()[:100]
        import hashlib
        content_hash = hashlib.md5(text.encode()).hexdigest()
        return f"{SERVICE_LOWER}_hash_{{content_hash}}"

    def _extract_item_data(self, element) -> dict:
        """Extract data from element"""
        data = {{
            'id': self._get_element_id(element),
            'html': element.inner_html(),
            'text': element.inner_text(),
        }}

        # Extract specific data attributes
        for attr in element.get_attributes():
            if attr.startswith('data-'):
                key = attr[5:]  # Remove 'data-' prefix
                value = element.get_attribute(attr)
                data[key] = value

        return data

    def get_item_id(self, item) -> str:
        """Get unique identifier for item"""
        if isinstance(item, dict):
            if 'id' in item:
                return item['id']
            if 'element' in item:
                return self._get_element_id(item['element'])

        return f"{SERVICE_LOWER}}_{{hash(item)}}"

    def create_action_file(self, item) -> Path:
        """Create action file in Needs_Action folder"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Extract data
        if isinstance(item, dict) and 'element' in item:
            element = item['element']
            item_id = self._get_element_id(element)
            item_text = element.inner_text()[:200]
        else:
            item_id = str(item.get('id', 'unknown'))
            item_text = item.get('text', str(item))[:200]

        safe_title = re.sub(r'[^\w-]', '_', item_text[:50])
        filename = f"{SERVICE_UPPER}_{{timestamp}}_{{safe_title}}.md"
        filepath = self.needs_action / filename

        content = f"""---
type: {SERVICE_LOWER}_event
service: {SERVICE_NAME}
id: {item_id}
timestamp: {datetime.utcnow().isoformat()}
priority: high
status: pending
---

# {SERVICE_CLASS} Event

**Event ID:** {item_id}
**Detected:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

## Event Details

{{item_text}}

## Suggested Actions

- [ ] Review event details
- [ ] Take action via web interface
- [ ] Archive after processing
"""

        filepath.write_text(content)
        self.log_action('created_action_file', {{
            'filename': filename,
            'item_id': item_id
        }})

        return filepath

    def cleanup(self):
        """Cleanup browser resources"""
        if self.context:
            self.context.close()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='{SERVICE_CLASS} Watcher')
    parser.add_argument('--vault', default='AI_Employee_Vault',
                       help='Path to vault')
    parser.add_argument('--session', default='./{SERVICE_LOWER}_session',
                       help='Path to browser session')
    parser.add_argument('--interval', type=int, default={DEFAULT_INTERVAL},
                       help='Check interval in seconds')
    parser.add_argument('--no-headless', action='store_true',
                       help='Run browser in visible mode')
    parser.add_argument('--setup', action='store_true',
                       help='Run initial authentication setup')
    parser.add_argument('--dry-run', action='store_true',
                       help='Dry run mode')

    args = parser.parse_args()

    headless = not args.no_headless

    try:
        watcher = {SERVICE_CLASS}Watcher(
            vault_path=args.vault,
            session_path=args.session,
            check_interval=args.interval,
            headless=headless
        )

        if args.dry_run:
            print(f"Would start {SERVICE_NAME} watcher in dry run mode")
        else:
            watcher.run()

    except KeyboardInterrupt:
        print("\nStopping watcher...")
        watcher.cleanup()
    except Exception as e:
        print(f"Error: {{e}}")
        watcher.cleanup()
        raise
