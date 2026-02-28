#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Facebook Poster v2 - Direct posting to facebook.com with improved button detection

Posts directly to facebook.com using Playwright with CDP connection.
Uses the correct Post button selector: [aria-label="Post"][role="button"]

Usage:
    python facebook_poster_v2.py "Your post content here"
    python facebook_poster_v2.py "Your post content here" --live
"""

import argparse
import os
import time
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Playwright not installed. Run: pip install playwright")
    sys.exit(1)


# ==================== CONFIGURATION ====================

# DRY_RUN: Set to False to actually publish posts
DRY_RUN = os.getenv('FACEBOOK_DRY_RUN', 'true').lower() == 'true'

FACEBOOK_URL = "https://www.facebook.com/"
CDP_ENDPOINT = "http://localhost:9222"


# ==================== HELPER FUNCTIONS ====================

def escape_js_string(text: str) -> str:
    """Escape special characters for JavaScript."""
    return (text
            .replace('\\', '\\\\')
            .replace('"', '\\"')
            .replace('\n', '\\n')
            .replace('\r', '')
            .replace('\t', '\\t'))


# ==================== MAIN ====================

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Post to Facebook directly')
    parser.add_argument('content', help='Post content')
    parser.add_argument('--live', action='store_true', help='Actually publish (not dry-run)')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode (preview only)')

    args = parser.parse_args()

    # Override dry run if specified
    global DRY_RUN
    if args.live:
        DRY_RUN = False
    elif args.dry_run:
        DRY_RUN = True

    print("\n" + "="*60)
    print("FACEBOOK POSTER v2 - Improved Post Button Detection")
    print("="*60)
    print(f"Content: {args.content[:100]}...")
    print(f"Mode: {'LIVE' if not DRY_RUN else 'DRY RUN'}")
    print("="*60 + "\n")

    if DRY_RUN:
        print("DRY RUN MODE: Preview only, will not publish\n")

    try:
        with sync_playwright() as p:
            # Connect to existing Chrome via CDP
            print("Connecting to Chrome CDP...")
            print(f"CDP Endpoint: {CDP_ENDPOINT}")

            try:
                browser = p.chromium.connect_over_cdp(CDP_ENDPOINT)
                print("Connected to Chrome!\n")

                # Get or create page
                contexts = browser.contexts
                if contexts:
                    context = contexts[0]
                    pages = context.pages
                    if pages:
                        page = pages[0]
                    else:
                        page = context.new_page()
                else:
                    print("No browser context found")
                    return False

                print(f"Current URL: {page.url}")

                # Navigate to Facebook if not already there
                if 'facebook.com' not in page.url:
                    print(f"\nNavigating to Facebook...")
                    page.goto(FACEBOOK_URL, wait_until='domcontentloaded', timeout=30000)
                    print("Page loaded")
                    time.sleep(2)
                else:
                    print("Already on Facebook")

                # Wait a moment for page to be ready
                time.sleep(2)

                # Step 1: Find and click the composer box
                print("\nStep 1: Finding composer box...")

                find_composer_js = '''
                () => {
                    // Look for "What's on your mind?" text or aria-label
                    const allElements = document.querySelectorAll('*');
                    for (let elem of allElements) {
                        const text = elem.textContent || elem.innerText || '';

                        // Look for the composer trigger
                        if (text.includes("What's on your mind") ||
                            text.includes("What's on your mind,")) {

                            // Find the clickable area
                            let clickable = elem;
                            while (clickable && clickable.tagName !== 'BODY') {
                                if (clickable.getAttribute('role') === 'textbox' ||
                                    clickable.getAttribute('contenteditable') === 'true' ||
                                    clickable.tagName === 'TEXTAREA' ||
                                    clickable.onclick) {
                                    clickable.click();
                                    return {
                                        found: true,
                                        method: 'click-textbox',
                                        element: clickable.tagName,
                                        text: text.substring(0, 50)
                                    };
                                }
                                clickable = clickable.parentElement;
                            }
                        }
                    }

                    // Fallback: Look for any editable element
                    const editables = document.querySelectorAll('[contenteditable="true"], textarea');
                    if (editables.length > 0) {
                        editables[0].focus();
                        return {
                            found: true,
                            method: 'focus-editable',
                            count: editables.length
                        };
                    }

                    return { found: false, method: 'none' };
                }
                '''

                composer_result = page.evaluate(find_composer_js)
                print(f"Composer search result: {composer_result}")

                if not composer_result.get('found'):
                    print("⚠️  Could not find composer box")
                    print("   Please make sure you can see the 'What's on your mind?' box in Facebook")
                    return False

                print(f"\n✅ Found composer using: {composer_result.get('method')}")

                # Step 2: Add the content
                print("\nStep 2: Adding content...")

                add_content_js = f'''
                () => {{
                    let elem = document.activeElement;

                    // If active element isn't editable, find one
                    if (!elem.getAttribute('contenteditable') && elem.tagName !== 'TEXTAREA') {{
                        const editables = document.querySelectorAll('[contenteditable="true"][data-lexical-editor="true"]');
                        if (editables.length > 0) {{
                            elem = editables[0];
                            elem.focus();
                        }}
                    }}

                    if (!elem) return {{ success: false, error: 'no editable element' }};

                    // Type the full content
                    const text = "{escape_js_string(args.content)}";
                    const maxLength = 63206;  // Facebook's character limit

                    if (text.length > maxLength) {{
                        text = text.substring(0, maxLength) + '...';
                    }}

                    // Set innerHTML directly (faster and more reliable than typing)
                    const p = document.createElement('p');
                    p.setAttribute('dir', 'auto');
                    p.className = elem.className || '';
                    const span = document.createElement('span');
                    span.setAttribute('data-lexical-text', 'true');
                    span.textContent = text;
                    p.appendChild(span);
                    elem.innerHTML = '';
                    elem.appendChild(p);

                    // Trigger input event so Facebook knows content changed
                    elem.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    elem.dispatchEvent(new Event('change', {{ bubbles: true }}));

                    return {{ success: true, chars_typed: text.length }};
                }}
                '''

                content_result = page.evaluate(add_content_js)
                print(f"Content result: {content_result}")

                if not content_result.get('success'):
                    print("❌ Failed to add content")
                    return False

                chars_typed = content_result.get('chars_typed', 0)
                print(f"✅ Content added successfully! ({chars_typed} characters)")

                # Step 2.5: Blur the contenteditable and wait for Facebook to process
                print("\nStep 2.5: Triggering blur event and waiting for Facebook...")

                blur_and_wait_js = '''
                () => {
                    // Find the contenteditable editor
                    const editables = document.querySelectorAll('[contenteditable="true"][data-lexical-editor="true"]');
                    if (editables.length > 0) {
                        editables[0].blur();
                    }

                    // Wait a bit and check if Post button is enabled
                    return { blurred: true };
                }
                '''

                blur_result = page.evaluate(blur_and_wait_js)
                print(f"Blur result: {blur_result}")

                # Wait for Facebook to process the content change
                print("Waiting 2 seconds for Facebook to process content...")
                time.sleep(2)

                if DRY_RUN:
                    print("\n" + "="*60)
                    print("DRY RUN COMPLETE - Post previewed (not published)")
                    print("="*60)
                    browser.close()
                    return True

                # Step 3: Wait for user to review
                print("\n" + "="*60)
                print("Waiting 5 seconds for you to review the post...")
                print("="*60)
                time.sleep(5)

                # Step 4: Find and click the Post button
                print("\nStep 4: Finding Post button...")

                find_post_button_js = '''
                () => {
                    // Look for the Post button using your provided selector
                    const button = document.querySelector('[aria-label="Post"][role="button"]');

                    if (button) {
                        return {
                            found: true,
                            hasTabindex: button.getAttribute('tabindex'),
                            ariaLabel: button.getAttribute('aria-label'),
                            role: button.getAttribute('role'),
                            disabled: button.getAttribute('role') === 'none',
                            classList: button.className.substring(0, 100)
                        };
                    }

                    return { found: false };
                }
                '''

                button_result = page.evaluate(find_post_button_js)
                print(f"Post button result: {button_result}")

                if not button_result.get('found'):
                    print("❌ Could not find Post button")
                    print("   Please click Post manually in Chrome")
                    browser.close()
                    return False

                if button_result.get('disabled'):
                    print("⚠️  Post button is DISABLED")
                    print("   This shouldn't happen - content was added")
                    print("   Please click Post manually in Chrome")
                    browser.close()
                    return False

                print("✅ Post button is ENABLED!")

                # Step 5: Click the Post button
                print("\nStep 5: Clicking Post button...")

                click_button_js = '''
                () => {
                    const button = document.querySelector('[aria-label="Post"][role="button"]');
                    if (button) {
                        // Dispatch full mouse event sequence for more reliable clicking
                        button.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true }));
                        button.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, cancelable: true }));
                        button.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
                        button.click();

                        // Also try triggering on the parent
                        if (button.parentElement) {
                            button.parentElement.dispatchEvent(new MouseEvent('click', { bubbles: true }));
                        }

                        return { success: true };
                    }

                    return { success: false };
                }
                '''

                click_result = page.evaluate(click_button_js)
                print(f"Click result: {click_result}")

                if click_result.get('success'):
                    print("\n✅ Post button clicked successfully!")
                    print("\n📋 Please verify in Chrome if post was published")
                    time.sleep(3)
                else:
                    print("\n⚠️  Could not click Post button")
                    print("   Please click Post button manually in Chrome")

                browser.close()
                return True

            except Exception as e:
                print(f"Error: {e}")
                import traceback
                traceback.print_exc()
                return False

    except Exception as e:
        print(f"Failed to connect to Chrome: {e}")
        print(f"\nMake sure Chrome is running with:")
        print(f"chrome.exe --remote-debugging-port=9222")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
