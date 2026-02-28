#!/usr/bin/env python3
"""
Automation Helpers for LinkedIn (and other social media) posting.

Provides human-like typing and clicking to avoid bot detection.
Used by linkedin_poster.py, twitter_poster.py, etc.
"""

import time
import random


def human_type(page, selector: str, text: str, description: str = "field") -> bool:
    """
    Type text into a field with human-like random delays between keystrokes.

    Args:
        page: Playwright page object
        selector: CSS selector for the input field
        text: Text to type
        description: Label for logging

    Returns:
        True if typing succeeded, False otherwise
    """
    try:
        element = page.locator(selector).first
        element.click()
        time.sleep(random.uniform(0.3, 0.7))

        # Use clipboard paste for speed (100-200x faster than keystroke)
        # This is the "fast copy-paste method" described in SKILL.md
        page.evaluate(
            """(text) => {
                const el = document.querySelector('%s');
                if (el) {
                    el.focus();
                    document.execCommand('insertText', false, text);
                }
            }"""
            % selector.replace("'", "\\'"),
            text,
        )

        time.sleep(random.uniform(0.5, 1.0))
        print(f"      Typed into {description}")
        return True
    except Exception as e:
        print(f"      Failed to type into {description}: {e}")
        return False


def human_click(page, selector: str, description: str = "element") -> bool:
    """
    Click an element with a small random delay to mimic human behavior.

    Args:
        page: Playwright page object
        selector: CSS selector for the element
        description: Label for logging

    Returns:
        True if click succeeded, False otherwise
    """
    try:
        time.sleep(random.uniform(0.2, 0.6))
        element = page.locator(selector).first
        element.click()
        time.sleep(random.uniform(0.3, 0.8))
        print(f"      Clicked {description}")
        return True
    except Exception as e:
        print(f"      Failed to click {description}: {e}")
        return False
