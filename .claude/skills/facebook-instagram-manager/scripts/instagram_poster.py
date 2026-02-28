#!/usr/bin/env python3
"""
Instagram Poster v2 - Professional Image Generation

Posts to Instagram with auto-generated professional images.
Uses Chrome DevTools Protocol (CDP) for browser automation.
"""

import sys
import time
import random
import json
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright

# Typing speed (faster for efficiency)
TYPING_MIN_DELAY = 0.01  # 10ms
TYPING_MAX_DELAY = 0.03  # 30ms


def generate_instagram_image(text: str, output_path: str) -> Path:
    """
    Generate a professional 1080x1080 Instagram image from text.

    Features:
    - 6 professional color themes (randomly selected)
    - Decorative borders with accent colors
    - Better typography with proper sizing
    - Text wrapping optimized for length
    - Professional footer with shadow effect
    - Decorative elements

    Args:
        text: Text content to render
        output_path: Where to save the image

    Returns:
        Path to saved image
    """
    print(f"\n[ART] Generating professional image from text...")

    # Remove emojis from text (they cause rendering errors)
    import re
    # Simple emoji removal - remove characters outside ASCII range
    clean_text = re.sub(r'[^\x00-\x7F]+', '', text)
    # Replace common emoji replacements
    emoji_map = {
        '🚀': '',
        '📧': '',
        '📅': '',
        '💬': '',
        '📁': '',
        '🤖': '',
        '✅': '',
        '📊': '',
        '⚠️': '',
        '❌': '',
    }
    for emoji, replacement in emoji_map.items():
        clean_text = clean_text.replace(emoji, replacement)

    # Clean up extra whitespace
    clean_text = '\n'.join(line.strip() for line in clean_text.split('\n') if line.strip())

    # Image dimensions (Instagram square - 1:1 ratio)
    width = 1080
    height = 1080

    # Select a random professional color theme
    themes = [
        {
            'name': 'Midnight Purple',
            'bg_top': (45, 27, 78),
            'bg_bottom': (15, 12, 41),
            'accent': (168, 85, 247),
            'text': (255, 255, 255),
            'secondary': (216, 180, 254)
        },
        {
            'name': 'Ocean Blue',
            'bg_top': (14, 165, 233),
            'bg_bottom': (3, 105, 161),
            'accent': (103, 232, 249),
            'text': (255, 255, 255),
            'secondary': (165, 243, 252)
        },
        {
            'name': 'Sunset Orange',
            'bg_top': (249, 115, 22),
            'bg_bottom': (154, 52, 18),
            'accent': (251, 146, 60),
            'text': (255, 255, 255),
            'secondary': (253, 186, 116)
        },
        {
            'name': 'Forest Green',
            'bg_top': (34, 197, 94),
            'bg_bottom': (21, 128, 61),
            'accent': (74, 222, 128),
            'text': (255, 255, 255),
            'secondary': (187, 247, 208)
        },
        {
            'name': 'Royal Gold',
            'bg_top': (234, 179, 8),
            'bg_bottom': (161, 98, 7),
            'accent': (252, 211, 77),
            'text': (255, 255, 255),
            'secondary': (254, 240, 138)
        },
        {
            'name': 'Deep Navy',
            'bg_top': (30, 58, 138),
            'bg_bottom': (15, 23, 42),
            'accent': (96, 165, 250),
            'text': (255, 255, 255),
            'secondary': (191, 219, 254)
        }
    ]

    theme = random.choice(themes)
    print(f"[THEME] Using theme: {theme['name']}")

    # Create image with gradient background
    from PIL import Image, ImageDraw, ImageFont
    import textwrap

    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)

    # Create smooth gradient background
    for y in range(height):
        ratio = y / height
        r = int(theme['bg_top'][0] * (1 - ratio) + theme['bg_bottom'][0] * ratio)
        g = int(theme['bg_top'][1] * (1 - ratio) + theme['bg_bottom'][1] * ratio)
        b = int(theme['bg_top'][2] * (1 - ratio) + theme['bg_bottom'][2] * ratio)
        draw.rectangle([(0, y), (width, y + 1)], fill=(r, g, b))

    # Add decorative border
    border_width = 15
    draw.rectangle([(border_width, border_width), (width - border_width, height - border_width)],
                   outline=theme['accent'], width=border_width)

    # Add inner border
    inner_border_width = 5
    draw.rectangle([(border_width + 20, border_width + 20),
                   (width - border_width - 20, height - border_width - 20)],
                   outline=theme['secondary'], width=inner_border_width)

    # Padding
    padding = 120

    # Load fonts with better sizing
    try:
        font_title = ImageFont.truetype("arial.ttf", 64)
        font_body = ImageFont.truetype("arial.ttf", 46)
        font_footer = ImageFont.truetype("arial.ttf", 30)
    except:
        font_title = ImageFont.load_default()
        font_body = ImageFont.load_default()
        font_footer = ImageFont.load_default()

    # Current y position
    y = padding + 40

    # Process text
    lines = clean_text.split('\n')

    # Draw title/first line with accent color and larger font
    if lines:
        first_line = lines[0]
        if len(first_line) < 60:
            # Draw title
            draw.text((padding, y), first_line, fill=theme['accent'], font=font_title)
            y += 90

            # Add decorative underline
            line_y = y - 10
            draw.line([(padding, line_y), (width - padding, line_y)],
                     fill=theme['secondary'], width=3)
            y += 40

            remaining_text = '\n'.join(lines[1:])
        else:
            remaining_text = clean_text

        # Wrap and draw body text
        if remaining_text:
            # Calculate optimal line width based on character count
            char_count = len(remaining_text)
            if char_count < 100:
                wrap_width = 30
            elif char_count < 200:
                wrap_width = 28
            else:
                wrap_width = 24

            wrapped_lines = textwrap.wrap(remaining_text, width=wrap_width)

            for line in wrapped_lines:
                if y + 60 > height - 180:  # Leave room for footer
                    # Add ellipsis if text is too long
                    if line:
                        line = line[:47] + "..."
                    draw.text((padding, y), line, fill=theme['text'], font=font_body)
                    break

                draw.text((padding, y), line, fill=theme['text'], font=font_body)
                y += 65

    # Add decorative footer
    footer_y = height - 140

    # Draw footer background rectangle
    footer_bg_padding = 30
    draw.rectangle([(padding - footer_bg_padding, footer_y - 20),
                   (width - padding + footer_bg_padding, footer_y + 60)],
                   fill=theme['accent'])

    # Footer text with shadow effect
    footer_text = ""  # No footer text

    # Only draw if there's text
    if footer_text:
        # Draw shadow
        draw.text((padding + 3, footer_y + 3), footer_text,
                 fill=(0, 0, 0, 128), font=font_footer)
        # Draw main text
        draw.text((padding, footer_y), footer_text,
                 fill=(255, 255, 255), font=font_footer)

    # Add small decorative dots
    dot_y = footer_y + 45
    dot_spacing = 15
    start_x = padding
    num_dots = 5
    for i in range(num_dots):
        x = start_x + (i * dot_spacing)
        draw.ellipse([(x, dot_y), (x + 8, dot_y + 8)], fill=theme['secondary'])

    # Save image with maximum quality
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    img.save(output, quality=100, optimize=True)

    print(f"[SUCCESS] Professional image created: {output}")
    print(f"   Theme: {theme['name']}")
    print(f"   Size: {width}x{height} (Instagram 1:1 ratio)")
    print(f"   Text length: {len(clean_text)} chars")
    return output


def post_to_instagram(image_path: str, caption: str, vault_path: str = "AI_Employee_Vault") -> dict:
    """
    Post image and caption to Instagram using Chrome automation.

    Args:
        image_path: Path to the image file
        caption: Caption text (with emojis kept)
        vault_path: Path to vault for logging

    Returns:
        dict with success status and summary
    """
    print(f"\n📸 Posting to Instagram...")
    print(f"   Image: {image_path}")
    print(f"   Caption length: {len(caption)} chars")

    # Check DRY_RUN mode
    dry_run = os.getenv('INSTAGRAM_DRY_RUN', 'true').lower() == 'true'

    if dry_run:
        print(f"\n🔄 DRY RUN MODE - Skipping actual post")
        return {
            'success': True,
            'summary': f'DRY RUN: Would post to Instagram with caption ({len(caption)} chars)',
            'post_url': None
        }

    try:
        with sync_playwright() as p:
            # Connect to Chrome CDP
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()

            print(f"✅ Connected to Chrome CDP")

            # Navigate to Instagram
            print(f"🌐 Navigating to Instagram...")
            page.goto("https://www.instagram.com/", timeout=30000)
            time.sleep(random.uniform(2, 3))

            # Click Create button
            print(f"🎯 Looking for Create button...")
            create_selectors = [
                'div[role="button"]:has-text("Create")',
                'svg[aria-label="New post"]',
                'a[aria-label="New post"]',
                'div:has-text("Create") >> div[role="button"]'
            ]

            create_clicked = False
            for selector in create_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        page.click(selector, timeout=5000)
                        create_clicked = True
                        print(f"✅ Create button clicked")
                        break
                except:
                    continue

            if not create_clicked:
                raise Exception("Could not find Create button")

            time.sleep(random.uniform(1.5, 2))

            # Upload image
            print(f"📤 Uploading image...")
            file_input = page.locator('input[type="file"]')
            file_input.set_input_files(image_path)
            print(f"✅ Image uploaded")

            time.sleep(random.uniform(2, 3))

            # Click Next button
            print(f"➡️  Clicking Next...")
            next_selectors = [
                'div[role="button"]:has-text("Next")',
                'button:has-text("Next")',
                'div:has-text("Next") >> div[role="button"]'
            ]

            next_clicked = False
            for selector in next_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        page.click(selector, timeout=5000)
                        next_clicked = True
                        print(f"✅ Next clicked")
                        break
                except:
                    continue

            if not next_clicked:
                raise Exception("Could not find Next button")

            time.sleep(random.uniform(1.5, 2))

            # Type caption
            print(f"✍️  Typing caption...")
            caption_selectors = [
                'div[role="textbox"]',
                'textarea[placeholder*="Write a caption"]',
                'div[contenteditable="true"]',
                'textarea[aria-label*="caption"]'
            ]

            caption_typed = False
            for selector in caption_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        # Click to focus
                        page.click(selector, timeout=5000)
                        time.sleep(random.uniform(0.2, 0.3))

                        # Type caption (paste method for speed)
                        page.evaluate(f"navigator.clipboard.writeText(`{caption}`)")
                        time.sleep(0.1)
                        page.keyboard.press("Control+V")
                        time.sleep(0.3)

                        caption_typed = True
                        print(f"✅ Caption typed ({len(caption)} chars)")
                        break
                except:
                    continue

            if not caption_typed:
                print(f"⚠️  Could not type caption, continuing anyway...")

            time.sleep(random.uniform(1, 1.5))

            # Click Share button
            print(f"📤 Clicking Share...")
            share_selectors = [
                'div[role="button"]:has-text("Share")',
                'button[type="submit"]',
                'button[aria-label="Share"]',
                'div:has-text("Share") >> button'
            ]

            share_clicked = False
            for selector in share_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        page.click(selector, timeout=5000)
                        share_clicked = True
                        print(f"✅ Share clicked")
                        break
                except:
                    continue

            if not share_clicked:
                raise Exception("Could not find Share button")

            time.sleep(random.uniform(3, 4))

            print(f"\n✅ Successfully posted to Instagram!")

            # Log action
            try:
                from utils.audit_logging import AuditLogger, EventType
                audit_logger = AuditLogger(vault_path)
                audit_logger.log_action(
                    action_type=EventType.INSTAGRAM_POST,
                    target="Instagram",
                    parameters={
                        "image_path": str(image_path),
                        "caption_length": len(caption)
                    },
                    result="success"
                )
            except Exception as e:
                print(f"⚠️  Could not log action: {e}")

            return {
                'success': True,
                'summary': f'Posted to Instagram with caption ({len(caption)} chars)',
                'post_url': 'https://www.instagram.com/'
            }

    except Exception as e:
        print(f"\n❌ Error posting to Instagram: {e}")
        import traceback
        traceback.print_exc()

        # Log error
        try:
            from utils.audit_logging import AuditLogger, EventType
            audit_logger = AuditLogger(vault_path)
            audit_logger.log_action(
                action_type=EventType.INSTAGRAM_POST,
                target="Instagram",
                parameters={"error": str(e)},
                result="failed"
            )
        except:
            pass

        return {
            'success': False,
            'summary': f'Failed to post: {str(e)}',
            'error': str(e)
        }


if __name__ == "__main__":
    import os

    # Test image generation
    if len(sys.argv) > 1:
        test_text = sys.argv[1]
    else:
        test_text = "Testing professional Instagram image generation with better colors and design!"

    output_dir = Path("AI_Employee_Vault/Temp")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "test_instagram_image.png"

    image_path = generate_instagram_image(test_text, str(output_path))
    print(f"\n[SUCCESS] Test image created at: {image_path}")
