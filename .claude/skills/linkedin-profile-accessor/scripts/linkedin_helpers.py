"""
LinkedIn Profile Accessor - Helper Functions

Utility functions for LinkedIn profile extraction and analysis.
"""

import re
import random
import time
from typing import Optional, List, Any
from pathlib import Path
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError

from .linkedin_selectors import LOGIN_INDICATORS


# Configuration
PROFILE_ACCESS_DELAY = 3.0  # Base delay between profile accesses (seconds)
SCREENSHOT_DIR = "AI_Employee_Vault/Screenshots/"


async def extract_text_with_fallbacks(
    page: Page,
    selectors: List[str],
    timeout: int = 5000
) -> Optional[str]:
    """
    Try multiple selectors and return the first match.

    Args:
        page: Playwright Page instance
        selectors: List of CSS selectors to try (in order)
        timeout: Timeout for each selector in milliseconds

    Returns:
        Extracted text or None if no selector matches
    """
    for selector in selectors:
        try:
            element = await page.wait_for_selector(selector, timeout=timeout)
            if element:
                text = await element.inner_text()
                if text and text.strip():
                    return clean_text(text)
        except (PlaywrightTimeoutError, Exception):
            continue

    return None


async def extract_list_with_fallbacks(
    page: Page,
    selectors: List[str],
    timeout: int = 5000
) -> List[str]:
    """
    Extract multiple text elements using selector fallbacks.

    Args:
        page: Playwright Page instance
        selectors: List of CSS selectors to try (in order)
        timeout: Timeout for each selector in milliseconds

    Returns:
        List of extracted texts
    """
    for selector in selectors:
        try:
            elements = await page.query_selector_all(selector)
            if elements:
                texts = []
                for element in elements:
                    text = await element.inner_text()
                    if text and text.strip():
                        texts.append(clean_text(text))
                if texts:
                    return texts
        except Exception:
            continue

    return []


async def extract_attribute_with_fallbacks(
    page: Page,
    selectors: List[str],
    attribute: str,
    timeout: int = 5000
) -> Optional[str]:
    """
    Extract an attribute from elements using selector fallbacks.

    Args:
        page: Playwright Page instance
        selectors: List of CSS selectors to try (in order)
        attribute: Attribute name to extract (e.g., 'href', 'src')
        timeout: Timeout for each selector in milliseconds

    Returns:
        Attribute value or None if no selector matches
    """
    for selector in selectors:
        try:
            element = await page.wait_for_selector(selector, timeout=timeout)
            if element:
                value = await element.get_attribute(attribute)
                if value:
                    return value
        except (PlaywrightTimeoutError, Exception):
            continue

    return None


async def wait_for_load_state(
    page: Page,
    state: str = "domcontentloaded",
    timeout: int = 30000
) -> None:
    """
    Wait for page to reach a specific load state.

    Args:
        page: Playwright Page instance
        state: Load state to wait for ('domcontentloaded', 'load', 'networkidle')
        timeout: Maximum wait time in milliseconds
    """
    try:
        await page.wait_for_load_state(state, timeout=timeout)
    except Exception as e:
        # Don't fail, just log
        pass


async def human_delay(min_sec: float = 1.0, max_sec: float = 3.0) -> None:
    """
    Add a random delay to mimic human behavior.

    Args:
        min_sec: Minimum delay in seconds
        max_sec: Maximum delay in seconds
    """
    delay = random.uniform(min_sec, max_sec)
    await asyncio_sleep(delay)


async def asyncio_sleep(seconds: float) -> None:
    """Async sleep wrapper."""
    import asyncio
    await asyncio.sleep(seconds)


def human_delay_sync(min_sec: float = 1.0, max_sec: float = 3.0) -> None:
    """
    Synchronous version of human_delay.

    Args:
        min_sec: Minimum delay in seconds
        max_sec: Maximum delay in seconds
    """
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)


def clean_text(text: str) -> str:
    """
    Clean and normalize extracted text.

    Args:
        text: Raw text to clean

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove special characters that might be artifacts
    text = text.replace('\u200b', '')  # Zero-width space
    text = text.replace('\u00a0', ' ')  # Non-breaking space

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def count_words(text: str) -> int:
    """
    Count words in text (handles multiple languages).

    Args:
        text: Text to count words in

    Returns:
        Number of words
    """
    if not text:
        return 0

    # Split by whitespace and filter empty strings
    words = text.split()
    return len([w for w in words if w.strip()])


def extract_numbers(text: str) -> List[int]:
    """
    Extract all numbers from text.

    Args:
        text: Text to extract numbers from

    Returns:
        List of integers found
    """
    if not text:
        return []

    # Find all numbers (including formatted numbers like "1,000")
    numbers = re.findall(r'[\d,]+', text)
    result = []
    for num in numbers:
        try:
            result.append(int(num.replace(',', '')))
        except ValueError:
            continue

    return result


def extract_date_range(text: str) -> tuple[Optional[str], Optional[str]]:
    """
    Extract start and end dates from a date range string.

    Args:
        text: Date range text (e.g., "Jan 2020 - Present", "2019 - 2021")

    Returns:
        Tuple of (start_date, end_date)
    """
    if not text:
        return None, None

    # Common patterns
    patterns = [
        r'(\w+ \d{4})\s*-\s*(\w+ \d{4}|Present)',
        r'(\d{4})\s*-\s*(\d{4}|Present)',
        r'(\w+ \d{4})\s*to\s*(\w+ \d{4}|Present)',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            start = match.group(1)
            end = match.group(2) if match.group(2) != "Present" else None
            return start, end

    # Try to extract any years
    years = re.findall(r'\d{4}', text)
    if len(years) >= 1:
        start = years[0]
        end = years[1] if len(years) > 1 else None
        return start, end

    return None, None


def parse_connections_count(text: str) -> Optional[int]:
    """
    Parse connection count from text (e.g., "500+", "1.2k", "1,234").

    Args:
        text: Text containing connection count

    Returns:
        Integer connection count or None
    """
    if not text:
        return None

    text = text.lower().strip()

    # Handle "500+" format
    if text.endswith('+'):
        text = text[:-1]

    # Handle "k" format (1.2k = 1200)
    if 'k' in text:
        try:
            return int(float(text.replace('k', '').strip()) * 1000)
        except ValueError:
            pass

    # Handle regular numbers with commas
    numbers = extract_numbers(text)
    if numbers:
        return numbers[0]

    return None


def is_logged_in(page: Page) -> bool:
    """
    Check if user is logged into LinkedIn.

    Args:
        page: Playwright Page instance

    Returns:
        True if logged in, False otherwise
    """
    for indicator in LOGIN_INDICATORS:
        try:
            element = page.query_selector(indicator)
            if element:
                return True
        except Exception:
            continue

    return False


async def scroll_to_element(page: Page, selector: str) -> bool:
    """
    Scroll to make element visible.

    Args:
        page: Playwright Page instance
        selector: CSS selector of element to scroll to

    Returns:
        True if successful, False otherwise
    """
    try:
        await page.evaluate(f"""(selector) => {{
            const element = document.querySelector(selector);
            if (element) {{
                element.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                return true;
            }}
            return false;
        }}""", selector)
        return True
    except Exception:
        return False


async def take_screenshot(
    page: Page,
    filename: str,
    directory: str = SCREENSHOT_DIR
) -> str:
    """
    Take a screenshot of the current page.

    Args:
        page: Playwright Page instance
        filename: Screenshot filename
        directory: Directory to save screenshot

    Returns:
        Full path to screenshot file
    """
    # Create directory if it doesn't exist
    screenshot_dir = Path(directory)
    screenshot_dir.mkdir(parents=True, exist_ok=True)

    # Full path
    filepath = screenshot_dir / filename

    # Take screenshot
    await page.screenshot(path=str(filepath), full_page=True)

    return str(filepath)


def build_profile_url(profile_id: str) -> str:
    """
    Build LinkedIn profile URL from profile ID.

    Args:
        profile_id: LinkedIn profile ID

    Returns:
        Full LinkedIn profile URL
    """
    return f"https://www.linkedin.com/in/{profile_id}/"


def extract_profile_id_from_url(url: str) -> Optional[str]:
    """
    Extract profile ID from LinkedIn URL.

    Args:
        url: LinkedIn profile URL

    Returns:
        Profile ID or None
    """
    # Pattern: linkedin.com/in/[profile-id]/
    match = re.search(r'linkedin\.com/in/([^/]+)', url)
    if match:
        return match.group(1)

    return None


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def extract_keywords(text: str) -> List[str]:
    """
    Extract keywords from text.

    Args:
        text: Text to extract keywords from

    Returns:
        List of keywords (sorted by frequency)
    """
    if not text:
        return []

    # Common words to ignore
    stop_words = {
        'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'from',
        'by', 'about', 'as', 'into', 'through', 'during', 'before', 'after',
        'above', 'below', 'between', 'under', 'again', 'further', 'then', 'once'
    }

    # Tokenize
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())

    # Filter stop words and count
    word_count = {}
    for word in words:
        if word not in stop_words:
            word_count[word] = word_count.get(word, 0) + 1

    # Sort by frequency
    sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)

    return [word for word, count in sorted_words if count >= 2]


def validate_profile_id(profile_id: str) -> bool:
    """
    Validate LinkedIn profile ID format.

    Args:
        profile_id: Profile ID to validate

    Returns:
        True if valid format, False otherwise
    """
    if not profile_id:
        return False

    # Basic validation: alphanumeric with hyphens, 3-100 chars
    pattern = r'^[a-zA-Z0-9-]{3,100}$'
    return bool(re.match(pattern, profile_id))


def format_duration(start_date: str, end_date: Optional[str] = None) -> str:
    """
    Format duration between two dates.

    Args:
        start_date: Start date string
        end_date: End date string or None for current

    Returns:
        Formatted duration string (e.g., "3 years", "6 months")
    """
    try:
        # Extract years
        start_year = int(re.search(r'\d{4}', start_date).group()) if start_date else 0

        if end_date and end_date.lower() != "present":
            end_year = int(re.search(r'\d{4}', end_date).group())
        else:
            from datetime import datetime
            end_year = datetime.now().year

        years = end_year - start_year

        if years >= 1:
            return f"{years} year{'s' if years > 1 else ''}"
        else:
            return "Less than a year"

    except Exception:
        return start_date
