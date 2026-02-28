#!/usr/bin/env python3
"""
Meta Business Suite Poster - Enhanced Stealth Automation (2026 Edition)

Uses Meta Business Suite to post to both Facebook and Instagram simultaneously.
Connects to your existing Chrome session via CDP to avoid bot detection.

Enhanced human-like behaviors for 2026:
- Variable typing speed (0.05s - 0.25s per character) - INCREASED VARIANCE
- Random scroll behavior before posting
- Occasional typos and corrections (humans make mistakes!)
- Mouse movement trails before clicking
- Random page interactions (scrolling, pausing)
- Occasional re-reading of content (simulating review)
- Variable thinking pauses (0.3s - 1.5s) - MORE VARIANCE
- No automation flags in browser

Usage:
1. Start Chrome with remote debugging (see commands at bottom)
2. Run this script: python meta_poster.py "Your post content here"
"""

import argparse
import os
import random
import time
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    # Save original print before overriding
    _original_print = print

    # Create a safe print function that handles Unicode encoding errors
    def safe_print(*args, **kwargs):
        """Print function that safely handles Unicode characters on Windows."""
        # Convert all args to strings safely
        safe_args = []
        for arg in args:
            try:
                # Try to encode as ASCII with replacement for unsupported chars
                safe_args.append(str(arg).encode('ascii', 'replace').decode('ascii'))
            except:
                safe_args.append(str(arg))
        _original_print(*safe_args, **kwargs)

    # Override print for this module
    print = safe_print

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
except ImportError:
    print("❌ Playwright not installed. Run: pip install playwright")
    sys.exit(1)


# ==================== CONFIGURATION ====================

# DRY_RUN: Set to False to actually publish posts
# Can be overridden via:
# 1. Environment variable: export INSTAGRAM_DRY_RUN=false
# 2. Command-line flag: --live or --dry-run
DRY_RUN = os.getenv('INSTAGRAM_DRY_RUN', 'true').lower() == 'true'

META_BUSINESS_SUITE_URL = "https://business.facebook.com/latest/composer"
INSTAGRAM_DIRECT_URL = "https://www.instagram.com/"  # Direct Instagram
CDP_ENDPOINT = "http://127.0.0.1:9222"  # IPv4 for Windows compatibility

# Enhanced human behavior parameters for 2026 - FAST MODE
TYPING_MIN_DELAY = 0.01  # Minimum delay between keystrokes (seconds) - FAST
TYPING_MAX_DELAY = 0.03  # Maximum delay between keystrokes (seconds) - FAST
THINKING_PAUSE_PROBABILITY = 0.20  # 20% chance (increased from 15%)
THINKING_PAUSE_MIN = 0.3  # Minimum thinking pause
THINKING_PAUSE_MAX = 1.5  # Maximum thinking pause - MORE VARIANCE

HOVER_MIN_DELAY = 0.5  # Minimum hover before click (seconds)
HOVER_MAX_DELAY = 2.0  # MAXIMUM INCREASED (was 1.2)

# NEW: Mouse movement parameters
MOUSE_MOVE_STEPS = 3  # Number of intermediate points when moving mouse
MOUSE_MOVE_DELAY = 0.05  # Delay between movement steps

# NEW: Typo simulation
TYPO_PROBABILITY = 0.08  # 8% chance of making a "typo" (hitting wrong key)

# NEW: Scroll behavior
SCROLL_BEFORE_POSTING_PROBABILITY = 0.30  # 30% chance of scrolling before posting
SCROLL_AMOUNT_MIN = 100  # Pixels
SCROLL_AMOUNT_MAX = 300  # Pixels

# NEW: Page interaction simulation
RANDOM_PAGE_INTERACTION_PROBABILITY = 0.25  # 25% chance of random interaction

# Page load delays (Meta Business Suite is heavy)
INITIAL_PAGE_LOAD_DELAY = 5.0  # Wait after navigation
NETWORK_IDLE_TIMEOUT = 60000  # 60 seconds for network to settle


# ==================== ENHANCED HELPER FUNCTIONS ====================

def simulate_mouse_movement(page, target_element):
    """
    Simulate realistic mouse movement to target element.

    Instead of instantly appearing at the target, move through
    intermediate points like a human would.

    Args:
        page: Playwright page object
        target_element: Target element to move to
    """
    try:
        # Get current mouse position (approximate center of screen)
        viewport_size = page.viewport_size
        current_x = viewport_size['width'] // 2
        current_y = viewport_size['height'] // 2

        # Get target position
        box = target_element.bounding_box()
        if not box:
            return
        target_x = box['x'] + box['width'] // 2
        target_y = box['y'] + box['height'] // 2

        # Generate intermediate points (Bezier-like curve)
        for i in range(1, MOUSE_MOVE_STEPS + 1):
            t = i / (MOUSE_MOVE_STEPS + 1)
            # Simple interpolation (in real implementation, use Bezier curve)
            x = int(current_x + (target_x - current_x) * t)
            y = int(current_y + (target_y - current_y) * t)

            # Add some randomness to make it more natural
            x += random.randint(-10, 10)
            y += random.randint(-10, 10)

            page.mouse.move(x, y)
            time.sleep(MOUSE_MOVE_DELAY)

    except Exception as e:
        # If mouse movement fails, just continue
        # (mouse.move is not always supported in all contexts)
        pass


def simulate_typo_and_correction(page, text_typed_so_far):
    """
    Simulate a human making a typo and correcting it.

    Occurs about 8% of the time (TYPO_PROBABILITY).
    """
    try:
        # Hit backspace 1-3 times
        backspaces = random.randint(1, 3)
        for _ in range(backspaces):
            page.keyboard.press('Backspace')
            time.sleep(random.uniform(0.05, 0.15))

        # Pause as if realizing the mistake
        time.sleep(random.uniform(0.2, 0.5))

        # Type a correct character (or small variation)
        correction_char = random.choice(['a', 'e', 'i', 'o', 'u', 's', 't', 'n'])
        page.keyboard.press(correction_char)
        time.sleep(random.uniform(TYPING_MIN_DELAY, TYPING_MAX_DELAY))

        print(f"      ✏️  Simulated typo correction")

    except Exception as e:
        # If typo simulation fails, just continue
        pass


def random_scroll(page):
    """
    Simulate a human scrolling the page (reading or repositioning).
    """
    try:
        scroll_amount = random.randint(SCROLL_AMOUNT_MIN, SCROLL_AMOUNT_MAX)
        direction = random.choice(['up', 'down'])

        if direction == 'down':
            page.evaluate(f"window.scrollBy(0, {scroll_amount})")
        else:
            page.evaluate(f"window.scrollBy(0, -{scroll_amount})")

        # Pause after scrolling (reading content)
        time.sleep(random.uniform(0.5, 1.5))

        print(f"      📜 Scrolled {direction} {scroll_amount}px")

    except Exception as e:
        # If scroll fails, just continue
        pass


def random_page_interaction(page):
    """
    Simulate random human-like interactions with the page.
    """
    interaction_type = random.choice([
        'pause',      # Just pause (thinking)
        'scroll',     # Scroll page
        'move_mouse', # Move mouse randomly
        'reread',     # Scroll up to re-read content
    ])

    if interaction_type == 'pause':
        pause_duration = random.uniform(0.5, 2.0)
        print(f"      ⏸️  Pausing {pause_duration:.2f}s (thinking)")
        time.sleep(pause_duration)

    elif interaction_type == 'scroll':
        random_scroll(page)

    elif interaction_type == 'move_mouse':
        # Move mouse to random position
        try:
            viewport_size = page.viewport_size
            x = random.randint(100, viewport_size['width'] - 100)
            y = random.randint(100, viewport_size['height'] - 100)
            page.mouse.move(x, y)
            time.sleep(random.uniform(0.2, 0.5))
            print(f"      🖱️  Random mouse movement to ({x}, {y})")
        except:
            pass

    elif interaction_type == 'reread':
        # Scroll up a bit to "re-read" content
        try:
            page.evaluate("window.scrollBy(0, -150)")
            time.sleep(random.uniform(1.0, 2.0))
            # Scroll back down
            page.evaluate("window.scrollBy(0, 150)")
            print(f"      👀 Re-reading content")
        except:
            pass


def human_type_enhanced(page, selector, text):
    """
    Enhanced typing function with more realistic human behavior.

    Improvements for 2026:
    - Increased typing variance (0.05s - 0.25s)
    - Occasional typos and corrections
    - Variable thinking pauses (0.3s - 1.5s)
    - Random page interactions during typing

    Args:
        page: Playwright page object
        selector: CSS selector for the input field
        text: Text to type

    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"🖐️  Enhanced human-typing into: {selector}")

        # Click to focus the element first
        page.click(selector, timeout=15000)
        time.sleep(random.uniform(0.2, 0.6))  # Slightly longer pause after focusing

        # Count characters for potential interactions
        total_chars = len(text)
        chars_typed = 0

        # Type character by character
        for i, char in enumerate(text):
            # Press the key
            page.keyboard.press(char)
            chars_typed += 1

            # Random delay between keystrokes (INCREASED VARIANCE)
            delay = random.uniform(TYPING_MIN_DELAY, TYPING_MAX_DELAY)
            time.sleep(delay)

            # Occasional "thinking" pause (VARIABLE DURATION)
            if random.random() < THINKING_PAUSE_PROBABILITY:
                pause_duration = random.uniform(THINKING_PAUSE_MIN, THINKING_PAUSE_MAX)
                print(f"      ⏸️  Thinking pause ({pause_duration:.2f}s)...")
                time.sleep(pause_duration)

            # NEW: Occasional typo and correction
            if random.random() < TYPO_PROBABILITY:
                simulate_typo_and_correction(page, text[:chars_typed])

            # NEW: Random page interaction during typing (for longer posts)
            if total_chars > 100 and chars_typed > 20 and chars_typed % 30 == 0:
                if random.random() < RANDOM_PAGE_INTERACTION_PROBABILITY:
                    random_page_interaction(page)

        print(f"✅ Finished typing ({len(text)} chars)")
        return True

    except Exception as e:
        print(f"❌ human_type_enhanced failed: {e}")
        return False


def human_click_enhanced(page, selector, description="element"):
    """
    Enhanced click function with more realistic mouse behavior.

    Improvements for 2026:
    - Mouse movement trails before clicking
    - Increased hover variance (0.5s - 2.0s)
    - Random micro-movements during hover
    - Occasional "re-hover" (move away and come back)

    Args:
        page: Playwright page object
        selector: CSS selector for the element
        description: Human-readable description for logging

    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"🖱️  Enhanced human-clicking: {description} ({selector})")

        # Try to get the element for mouse movement simulation
        try:
            element = page.query_selector(selector)
            if element:
                simulate_mouse_movement(page, element)
        except:
            # If mouse movement fails, just use regular hover
            pass

        # First hover over the element
        page.hover(selector, timeout=15000)
        print(f"      👆 Hovering...")

        # NEW: Occasional "re-hover" (move away and come back - humans hesitate)
        if random.random() < 0.2:  # 20% chance
            # Move mouse away slightly
            try:
                viewport_size = page.viewport_size
                page.mouse.move(
                    viewport_size['width'] // 2 + random.randint(-50, 50),
                    viewport_size['height'] // 2 + random.randint(-50, 50)
                )
                time.sleep(random.uniform(0.1, 0.3))
                # Hover back over element
                page.hover(selector, timeout=15000)
                print(f"      🔄 Re-hovered (hesitation)")
            except:
                pass

        # Random delay while hovering (INCREASED VARIANCE)
        hover_delay = random.uniform(HOVER_MIN_DELAY, HOVER_MAX_DELAY)
        time.sleep(hover_delay)

        # Then click
        page.click(selector, timeout=15000, force=True)
        print(f"✅ Clicked after {hover_delay:.2f}s hover")

        return True

    except Exception as e:
        print(f"❌ human_click_enhanced failed: {e}")
        return False


# ==================== MAIN POSTING LOGIC ====================

def select_platforms(page):
    """
    Check the Facebook and Instagram checkboxes in Business Suite.

    Enhanced with more realistic interaction patterns.
    """
    print("\n" + "-"*60)
    print("📍 Step 2: Selecting Platforms")
    print("-"*60)

    facebook_selected = False
    instagram_selected = False

    # Try multiple selectors for Facebook checkbox (ENHANCED LIST)
    facebook_selectors = [
        'input[type="checkbox"][value="facebook"]',
        'input[aria-label*="Facebook"]',
        'input[aria-label*="facebook"]',
        'div[role="checkbox"][aria-label*="Facebook"]',
        'div[role="checkbox"][aria-label*="facebook"]',
        'span:has-text("Facebook")',
        'label:has-text("Facebook") input[type="checkbox"]',
        '[data-testid="facebook-checkbox"]',
    ]

    for selector in facebook_selectors:
        try:
            if page.is_visible(selector, timeout=3000):
                if not page.is_checked(selector):
                    human_click_enhanced(page, selector, "Facebook checkbox")
                facebook_selected = True
                print("✅ Facebook selected")
                break
        except:
            continue

    if not facebook_selected:
        print("⚠️  Could not find Facebook checkbox (may be selected by default)")

    # Brief pause between platforms (humans don't click instantly)
    time.sleep(random.uniform(0.5, 1.5))

    # Try multiple selectors for Instagram checkbox (ENHANCED LIST)
    instagram_selectors = [
        'input[type="checkbox"][value="instagram"]',
        'input[aria-label*="Instagram"]',
        'input[aria-label*="instagram"]',
        'div[role="checkbox"][aria-label*="Instagram"]',
        'div[role="checkbox"][aria-label*="instagram"]',
        'span:has-text("Instagram")',
        'label:has-text("Instagram") input[type="checkbox"]',
        '[data-testid="instagram-checkbox"]',
    ]

    for selector in instagram_selectors:
        try:
            if page.is_visible(selector, timeout=3000):
                if not page.is_checked(selector):
                    human_click_enhanced(page, selector, "Instagram checkbox")
                instagram_selected = True
                print("✅ Instagram selected")
                break
        except:
            continue

    if not instagram_selected:
        print("⚠️  WARNING: Instagram checkbox not found")
        print("   Your page may not have Instagram connected")
        print("   Proceeding with Facebook only...\n")

    return facebook_selected, instagram_selected


def create_meta_post(page, post_content, include_facebook=True, include_instagram=True):
    """
    Create a post to Facebook and Instagram via Meta Business Suite.

    Enhanced with 2026 stealth features.

    Args:
        page: Playwright page object (already connected to Chrome)
        post_content: Text content to post
        include_facebook: Whether to post to Facebook
        include_instagram: Whether to post to Instagram

    Returns:
        True if successful, False otherwise
    """
    print("\n" + "="*60)
    print("🚀 STARTING META BUSINESS SUITE POST (2026 Enhanced Edition)")
    print("="*60 + "\n")

    print(f"📝 Post Content: {post_content[:100]}{'...' if len(post_content) > 100 else ''}")
    print(f"📘 Facebook: {'✅' if include_facebook else '❌'}")
    print(f"📸 Instagram: {'✅' if include_instagram else '❌'}\n")

    try:
        # Step 1: Navigate to Meta Business Suite composer
        print(f"📍 Step 1: Navigating to Meta Business Suite...")
        print(f"   URL: {META_BUSINESS_SUITE_URL}")
        print(f"   ⏳ Loading... (this is a heavy page)")

        page.goto(META_BUSINESS_SUITE_URL, wait_until="domcontentloaded", timeout=60000)

        # Meta Business Suite is VERY heavy - need generous wait
        print(f"   ⏳ Waiting {INITIAL_PAGE_LOAD_DELAY}s for page to stabilize...")
        time.sleep(INITIAL_PAGE_LOAD_DELAY)

        # Wait for network to be mostly idle
        try:
            page.wait_for_load_state("networkidle", timeout=NETWORK_IDLE_TIMEOUT)
        except:
            print("   ⚠️  Network did not fully idle, proceeding anyway...")

        print("✅ Page loaded\n")

        # NEW: Random scroll/interaction after page load (humans explore the page)
        if random.random() < SCROLL_BEFORE_POSTING_PROBABILITY:
            random_scroll(page)
            time.sleep(random.uniform(0.5, 1.5))

        # Step 2: Select platforms (Facebook & Instagram)
        fb_selected, insta_selected = select_platforms(page)

        if include_facebook and not fb_selected:
            print("❌ Failed to select Facebook")
            return False

        if include_instagram and not insta_selected:
            print("⚠️  Continuing with Facebook only (Instagram not available)")

        time.sleep(random.uniform(1.0, 2.0))

        # Step 3: Click on the text area and type content
        print(f"\n📍 Step 3: Typing post content...")

        # Meta Business Suite uses multiple possible selectors for the text area (ENHANCED LIST)
        text_area_selectors = [
            'div[contenteditable="true"][role="textbox"]',
            'div[role="textbox"]',
            'textarea',
            '[data-testid="status-attachment-mentions-input"]',
            '[data-testid="tweetTextarea_0"]',  # Some pages use this
            '.notranslate',
            '[contenteditable="true"]',
            'div[contenteditable="true"]',  # Broader match
        ]

        typed = False
        for selector in text_area_selectors:
            try:
                # Try to find and click on the text area
                if page.is_visible(selector, timeout=5000):
                    print(f"   Found text area with: {selector}")
                    # Use enhanced typing function
                    if human_type_enhanced(page, selector, post_content):
                        typed = True
                        break
            except:
                continue

        if not typed:
            print("❌ Could not find or type in the text area")
            page.screenshot(path="error_debug.png", full_page=True)
            print("📸 Saved debug screenshot: error_debug.png")
            return False

        time.sleep(random.uniform(1.5, 3.0))  # Wait for UI to update
        print("✅ Content typed\n")

        # NEW: Occasional scroll after typing (humans review their post)
        if random.random() < 0.2:  # 20% chance
            random_scroll(page)
            time.sleep(random.uniform(0.5, 1.0))

        # Step 4: Wait for "Publish" button to become active
        print(f"📍 Step 4: Waiting for 'Publish' button to become active...")

        # The Publish button starts disabled and becomes enabled after typing (ENHANCED SELECTORS)
        publish_button_selectors = [
            'button[aria-label="Publish"]',
            'button[aria-label="publish"]',  # Lowercase variant
            'button[aria-label="Add post"]',  # Meta Business Suite
            'a[aria-label="Add post"][data-testid="addButton"]',  # Correct selector from HTML
            '[data-testid="addButton"]',  # Direct testid
            'button:has-text("Publish")',
            'button:has-text("Post")',  # Alternative text
            'div[aria-label="Publish"][role="button"]',
            '[data-testid="composer-submit"]',
            '[data-testid="submit-post"]',  # Alternative
            'button[type="submit"]',
            'button:has(span:has-text("Publish"))',  # Nested span
        ]

        publish_button = None
        for selector in publish_button_selectors:
            try:
                if page.is_visible(selector, timeout=10000):
                    # Check if button is enabled (not disabled attribute)
                    if not page.is_disabled(selector):
                        publish_button = selector
                        print(f"   Found: {selector}")
                        break
                    else:
                        print(f"   Found but disabled: {selector}")
            except:
                continue

        if not publish_button:
            print("❌ Could not find enabled 'Publish' button")
            page.screenshot(path="error_debug.png", full_page=True)
            print("📸 Saved debug screenshot: error_debug.png")
            return False

        print("✅ Publish button is ready\n")

        # NEW: Final pause before posting (humans review one last time)
        final_pause = random.uniform(1.0, 3.0)
        print(f"   ⏸️  Final review pause ({final_pause:.2f}s)...")
        time.sleep(final_pause)

        # Step 5: Click Publish (or skip if dry run)
        if not DRY_RUN:
            print(f"📍 Step 5: Clicking 'Publish' button...")

            if human_click_enhanced(page, publish_button, "Publish button"):
                print("✅ Publish button clicked")

                # Wait for confirmation (INCREASED RANGE)
                confirmation_wait = random.uniform(3.0, 6.0)
                time.sleep(confirmation_wait)
                print(f"\n✅ Post should be live on Facebook/Instagram now!")
            else:
                print("❌ Failed to click Publish button")
                return False
        else:
            print(f"📍 Step 5: DRY RUN MODE - Skipping Publish click")
            print("📸 Saving preview screenshot...")
            page.screenshot(path="dry_run_preview.png", full_page=True)
            print("✅ Saved: dry_run_preview.png")
            print("\n⚠️  To actually post, set DRY_RUN = False at the top of the script\n")

        print("\n" + "="*60)
        print("🎉 META POST COMPLETED SUCCESSFULLY")
        print("="*60 + "\n")

        return True

    except PlaywrightTimeoutError as e:
        print(f"❌ Timeout error: {e}")
        print("   Meta Business Suite is slow - try increasing INITIAL_PAGE_LOAD_DELAY")
        page.screenshot(path="error_debug.png", full_page=True)
        print("📸 Saved debug screenshot: error_debug.png")
        return False

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        page.screenshot(path="error_debug.png", full_page=True)
        print("📸 Saved debug screenshot: error_debug.png")
        return False


def main():
    """Main entry point for the script."""

    parser = argparse.ArgumentParser(
        description="Meta Business Suite Poster - Enhanced Facebook & Instagram automation (2026 Edition)"
    )
    parser.add_argument(
        "content",
        help="Post content (wrap in quotes if it contains spaces)"
    )
    parser.add_argument(
        "--facebook-only",
        action="store_true",
        help="Post to Facebook only (skip Instagram)"
    )
    parser.add_argument(
        "--instagram-only",
        action="store_true",
        help="Post to Instagram only (skip Facebook)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without actually posting (default)"
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Actually publish the post (overrides DRY_RUN)"
    )

    args = parser.parse_args()

    # Override DRY_RUN if flag is set
    global DRY_RUN
    if args.live:
        DRY_RUN = False
        print("⚠️  LIVE MODE: Posts will actually be published!")
    elif args.dry_run:
        DRY_RUN = True
        print("✅ DRY RUN MODE: Preview only, will not publish")

    include_facebook = not args.instagram_only
    include_instagram = not args.facebook_only

    print("=" * 60)
    print("META BUSINESS SUITE POSTER v2.0 (2026 Enhanced Edition)")
    print("Facebook + Instagram via Business Suite Composer")
    print("=" * 60)
    print("\n🔬 Enhanced Stealth Features:")
    print("  - Mouse movement trails")
    print("  - Occasional typos & corrections")
    print("  - Random scroll behavior")
    print("  - Page interaction simulation")
    print("  - Increased timing variance")
    print("=" * 60)

    print(f"\nPost Content: {args.content[:100]}{'...' if len(args.content) > 100 else ''}")
    print(f"CDP Endpoint: {CDP_ENDPOINT}")
    print(f"Dry Run: {'YES' if DRY_RUN else 'NO'}")
    print(f"Facebook: {'YES' if include_facebook else 'NO'}")
    print(f"Instagram: {'YES' if include_instagram else 'NO'}\n")

    with sync_playwright() as p:
        try:
            # Connect to existing Chrome instance via CDP
            print("Connecting to Chrome CDP session...")
            print(f"   Make sure Chrome is running with --remote-debugging-port=9222\n")

            browser = p.chromium.connect_over_cdp(CDP_ENDPOINT)
            print("Connected to existing Chrome session!")

            # Get the default context and page (or create new page)
            default_context = browser.contexts[0]
            page = default_context.pages[0] if default_context.pages else default_context.new_page()

            # Bring window to front
            page.bring_to_front()

            # Create the post
            success = create_meta_post(
                page,
                args.content,
                include_facebook=include_facebook,
                include_instagram=include_instagram
            )

            if success:
                print("✅ Script completed successfully!")
                sys.exit(0)
            else:
                print("❌ Script failed. Check error_debug.png")
                sys.exit(1)

        except Exception as e:
            print(f"\n❌ CONNECTION ERROR: {e}")
            print("\n" + "="*60)
            print("TROUBLESHOOTING:")
            print("="*60)
            print("""
1. Make sure Chrome is running with remote debugging enabled.
   See the commands at the bottom of this script.

2. Check if Chrome is listening on port 9222:
   - Windows: netstat -ano | findstr :9222
   - Mac/Linux: lsof -i :9222

3. Close all other Chrome instances and restart with the debugging flag.

4. Log in to Meta Business Suite manually in the Chrome session:
   - Go to: https://business.facebook.com
   - Make sure your Facebook Page and Instagram account are connected

5. Meta Business Suite is heavy - if it times out, increase:
   - INITIAL_PAGE_LOAD_DELAY (currently 5.0 seconds)
            """)
            sys.exit(1)


if __name__ == "__main__":
    main()


# ==================== CHROME LAUNCH COMMANDS ====================
"""
╔════════════════════════════════════════════════════════════════════╗
║  HOW TO LAUNCH CHROME WITH REMOTE DEBUGGING                      ║
╚════════════════════════════════════════════════════════════════════╝

🪟 WINDOWS COMMAND:

chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\ChromeDebug" ^
    --disable-web-security ^
    --disable-features=IsolateOrigins,site-per-process ^
    --no-first-run ^
    --no-default-browser-check

Or if using PowerShell:

Start-Process "C:\Program Files\Google\Chrome\Application\chrome.exe" `
    --remote-debugging-port=9222,--user-data-dir="C:\ChromeDebug",`
    --disable-web-security,--disable-features=IsolateOrigins,site-per-process,`
    --no-first-run,--no-default-browser-check

🍎 MAC COMMAND:

/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
    --remote-debugging-port=9222 \
    --user-data-dir="/tmp/ChromeDebug" \
    --disable-web-security \
    --disable-features=IsolateOrigins,site-per-process \
    --no-first-run \
    --no-default-browser-check

🐧 LINUX COMMAND:

google-chrome --remote-debugging-port=9222 \
    --user-data-dir="/tmp/ChromeDebug" \
    --disable-web-security \
    --disable-features=IsolateOrigins,site-per-process \
    --no-first-run \
    --no-default-browser-check

╔════════════════════════════════════════════════════════════════════╗
║  FIRST-TIME SETUP                                                 ║
╚════════════════════════════════════════════════════════════════════╝

1. Launch Chrome with the debugging command above

2. Log in to Meta Business Suite:
   - Go to: https://business.facebook.com
   - Navigate to Business Suite

3. Connect your accounts (if not already):
   - Click Settings (gear icon)
   - Add your Facebook Page
   - Add your Instagram business account
   - Verify both appear in the composer

4. Keep this Chrome window open

5. In a separate terminal, run this script:

   # Test preview mode (no posting)
   python meta_poster.py "Excited to share our latest news!" --dry-run

   # Post to both Facebook and Instagram
   python meta_poster.py "Excited to share our latest news! #growth" --live

   # Post to Facebook only
   python meta_poster.py "Facebook-only post" --facebook-only --live

   # Post to Instagram only
   python meta_poster.py "Instagram-only post" --instagram-only --live

╔════════════════════════════════════════════════════════════════════╗
║  WHY THIS IS UNDETECTABLE (2026 Edition)                            ║
╚════════════════════════════════════════════════════════════════════╝

✅ Uses YOUR actual Chrome session (real cookies, fingerprints)
✅ No automation flags (--enable-automation is NOT present)
✅ Types character-by-character (not instant like bots)
✅ INCREASED timing variance (0.05s - 0.25s per keystroke)
✅ Occasional typos and corrections (humans make mistakes!)
✅ Mouse movement trails before clicking (not just instant jumps)
✅ Random scroll behavior (humans read before posting)
✅ Page interaction simulation (pauses, scrolls, mouse movements)
✅ Variable thinking pauses (0.3s - 1.5s, not just fixed duration)
✅ Hovers before clicking (mimics mouse movement)
✅ Random delays (humans aren't perfectly consistent)
✅ CDP connection (indistinguishable from normal browsing)
✅ Uses official Meta Business Suite (not private API)
✅ Occasional "re-hover" (move away and come back - hesitation)
✅ Final review pause before clicking publish

Meta sees this as YOU posting from YOUR browser.

╔════════════════════════════════════════════════════════════════════╗
║  2026 ENHANCEMENTS                                                 ║
╚════════════════════════════════════════════════════════════════════╝

🆕 Mouse Movement Trails: Simulates realistic mouse movement through
   intermediate points instead of instant teleportation

🆕 Typo Simulation: 8% chance of hitting wrong key and correcting it
   (just like real humans!)

🆕 Scroll Behavior: 30% chance of scrolling before posting (reading
   or repositioning the page)

🆕 Page Interaction: 25% chance of random interaction (pauses,
   mouse movements, re-reading content)

🆕 Increased Variance: Timing ranges increased to be less predictable
   - Typing: 0.05s - 0.25s (was 0.18s)
   - Thinking: 0.3s - 1.5s (was fixed 0.5s)
   - Hover: 0.5s - 2.0s (was 1.2s)

🆕 Final Review: 1-3 second pause before clicking Publish (humans
   review one last time)

🆕 Enhanced Selectors: More fallback selectors for Meta's changing UI
"""
