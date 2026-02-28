#!/usr/bin/env python3
"""
WhatsApp Scan Script - Quick scan for important messages

Usage:
    python scan_whatsapp.py                    # Scan once
    python scan_whatsapp.py --urgent-only       # Only urgent messages
    python scan_whatsapp.py --summary           # Generate summary
"""
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

def scan_whatsapp(vault_path=".", session_path="../whatsapp_session", urgent_only=False):
    """Run WhatsApp watcher and process results."""
    vault = Path(vault_path).resolve()
    session = Path(session_path).resolve()

    print(f"Scanning WhatsApp...")
    print(f"Vault: {vault}")
    print(f"Session: {session}")
    print("-" * 60)

    # Run the watcher
    watcher_script = vault / "watchers" / "whatsapp_watcher_simple.py"

    if not watcher_script.exists():
        print(f"Error: Watcher script not found at {watcher_script}")
        return False

    result = subprocess.run(
        ["python", str(watcher_script), "--vault", str(vault), "--session", str(session)],
        capture_output=True,
        text=True,
        cwd=str(vault)
    )

    # Print output
    if result.stdout:
        print(result.stdout)

    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False

    # Check results
    needs_action = vault / "Needs_Action"
    whatsapp_files = list(needs_action.glob("WHATSAPP_*.md"))

    if urgent_only:
        # Filter for urgent keywords
        urgent_files = []
        for f in whatsapp_files:
            content = f.read_text()
            if "urgent" in content.lower() or "asap" in content.lower():
                urgent_files.append(f)
        whatsapp_files = urgent_files

    print("\n" + "=" * 60)
    print(f"SCAN COMPLETE")
    print("=" * 60)
    print(f"Total messages found: {len(whatsapp_files)}")
    print()

    # Show recent files
    recent = sorted(whatsapp_files, key=lambda p: p.stat().st_mtime, reverse=True)[:10]

    for i, f in enumerate(recent, 1):
        content = f.read_text()

        # Extract sender
        for line in content.split('\n'):
            if line.startswith("## From:"):
                sender = line.split(":", 1)[1].strip()
                break
        else:
            sender = "Unknown"

        # Extract keywords
        for line in content.split('\n'):
            if line.startswith("## Detected Keywords"):
                idx = content.split('\n').index(line)
                keywords_line = content.split('\n')[idx + 1]
                keywords = keywords_line.strip()
                break
        else:
            keywords = "N/A"

        print(f"{i}. {f.name}")
        print(f"   From: {sender}")
        print(f"   Keywords: {keywords}")
        print()

    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scan WhatsApp for important messages")
    parser.add_argument("--vault", default=".", help="Path to vault")
    parser.add_argument("--session", default="../whatsapp_session", help="Path to browser session")
    parser.add_argument("--urgent-only", action="store_true", help="Only show urgent messages")

    args = parser.parse_args()

    success = scan_whatsapp(args.vault, args.session, args.urgent_only)
    sys.exit(0 if success else 1)
