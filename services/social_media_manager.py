# social_media_manager.py - Orchestrates all social media platforms
#
# create_all_drafts(content)  → creates drafts for Facebook, Instagram, Twitter
# post_all_approved()         → posts all approved files from Approved/
# get_weekly_summary()        → reads platform logs, returns summary

import os
from pathlib import Path
from datetime import datetime

from mcp_server.social_playwright_base import (
    VAULT_PATH, APPROVED_DIR, PENDING_DIR, _log,
)
from mcp_server.facebook_playwright import FacebookPoster
from mcp_server.instagram_playwright import InstagramPoster
from mcp_server.twitter_playwright import TwitterPoster

DEFAULT_IMAGE = Path('D:/Ibad Coding/hackathon-0-ditial-fte/assets/default_post_image.png')

PLATFORMS = {
    'facebook':  FacebookPoster(),
    'instagram': InstagramPoster(),
    'twitter':   TwitterPoster(),
}


def create_all_drafts(content: str, topic: str = 'General',
                      image_path: str = None) -> list:
    """
    Create a post draft for every platform.
    Returns list of draft file paths.
    """
    drafts = []
    for name, poster in PLATFORMS.items():
        img = image_path
        # Instagram always needs an image
        if name == 'instagram' and not img:
            img = str(DEFAULT_IMAGE)
        path = poster.create_post_draft(content, topic=topic, image_path=img)
        drafts.append(path)
    print(f"\n[Social Manager] {len(drafts)} drafts created in {PENDING_DIR}")
    print(f"[Social Manager] Review and move to {APPROVED_DIR} to authorise.\n")
    return drafts


def post_all_approved() -> list:
    """
    Scan Approved/ for social media draft files and post them.
    Returns list of result dicts.
    """
    results = []
    approved_files = list(APPROVED_DIR.glob('*.md'))

    platform_map = {
        'FACEBOOK': PLATFORMS['facebook'],
        'INSTAGRAM': PLATFORMS['instagram'],
        'TWITTER': PLATFORMS['twitter'],
    }

    for fpath in approved_files:
        name_upper = fpath.stem.upper()
        for prefix, poster in platform_map.items():
            if name_upper.startswith(f'{prefix}_DRAFT'):
                # Read content from draft
                text = fpath.read_text(encoding='utf-8')
                content = _extract_content(text)
                image   = _extract_image(text)
                result  = poster.post_approved_content(
                    fpath.name, content, image
                )
                results.append({
                    'platform': poster.PLATFORM,
                    'file': fpath.name,
                    **result,
                })
                break

    if not results:
        print("[Social Manager] No approved social media drafts found.")
    else:
        for r in results:
            status = 'OK' if r['success'] else 'FAILED'
            print(f"  [{status}] {r['platform']}: {r['message']}")

    return results


def get_weekly_summary() -> str:
    """
    Read platform logs and return a summary string.
    """
    lines = []
    lines.append(f"# Social Media Weekly Summary")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    for platform in ['Facebook', 'Instagram', 'Twitter']:
        log_file = VAULT_PATH / 'Social' / platform / f'{platform.lower()}_log.md'
        posts_file = VAULT_PATH / 'Social' / platform / f'{platform.lower()}_posts.md'

        lines.append(f"## {platform}")

        if log_file.exists():
            log_lines = log_file.read_text(encoding='utf-8').strip().splitlines()
            lines.append(f"- Log entries: {len(log_lines)}")
        else:
            lines.append("- No log entries yet.")

        if posts_file.exists():
            post_count = posts_file.read_text(encoding='utf-8').count('**Posted:**')
            lines.append(f"- Posts made: {post_count}")
        else:
            lines.append("- No posts yet.")

        lines.append('')

    summary = '\n'.join(lines)
    print(summary)
    return summary


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_content(draft_text: str) -> str:
    """Extract post content from the draft markdown."""
    marker = '### Content\n'
    idx = draft_text.find(marker)
    if idx == -1:
        return draft_text
    start = idx + len(marker)
    end = draft_text.find('\n---', start)
    if end == -1:
        return draft_text[start:].strip()
    return draft_text[start:end].strip()


def _extract_image(draft_text: str) -> str:
    """Extract image path from frontmatter."""
    for line in draft_text.splitlines():
        if line.startswith('image:'):
            val = line.split(':', 1)[1].strip()
            if val and val != 'none':
                return val
    return None
