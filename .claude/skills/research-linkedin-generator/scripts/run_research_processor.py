#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Research Processor Runner - PM2 Entry Point

Runs the Research LinkedIn Generator daily at scheduled times.
Called by PM2 cron job.

Usage:
    python run_research_processor.py --vault AI_Employee_Vault
"""

from __future__ import annotations

import sys
import os
from pathlib import Path

# Fix Windows encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from research import ResearchLinkedInGenerator


def main():
    """Run daily research processing"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Research Processor - Daily LinkedIn Content Generator"
    )
    parser.add_argument(
        "--vault",
        default="AI_Employee_Vault",
        help="Path to Obsidian vault"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("RESEARCH PROCESSOR - Daily LinkedIn Content Generation")
    print("=" * 60)
    print(f"Vault: {args.vault}")
    print(f"Time: {os.popen('date /t && time /t').read().strip()}")
    print()

    # Check if GLM_API_KEY is set
    if not os.getenv("GLM_API_KEY"):
        print("[WARNING] GLM_API_KEY environment variable not set")
        print("[INFO] Research processor requires GLM API key to generate posts")
        print("[INFO] Skipping research processing (will retry at next scheduled run)")
        print("\n" + "=" * 60)
        print("Research processor skipped (missing API key)")
        print("=" * 60)
        return 0

    try:
        generator = ResearchLinkedInGenerator(args.vault)

        # Process daily research topics
        generator.process_daily_research()
        print("\n" + "=" * 60)
        print("Research processor completed successfully")
        print("=" * 60)
        return 0
    except Exception as e:
        print(f"\n[ERROR] Research processor failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
