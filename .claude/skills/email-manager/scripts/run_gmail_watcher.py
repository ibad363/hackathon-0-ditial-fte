#!/usr/bin/env python3
"""
Wrapper script for Gmail Watcher - Runs as a module to fix relative imports.
Located in scripts/ folder, adds parent directory to Python path.
"""
import sys
import os
from pathlib import Path

# Add parent directory (project root) to Python path
project_root = Path(__file__).parent.parent.parent.parent.parent  # Up from .claude/skills/<skill>/scripts/ to project root
sys.path.insert(0, str(project_root))

# Change working directory to project root so relative paths resolve
os.chdir(str(project_root))

if __name__ == "__main__":
    try:
        from watchers.gmail_watcher import main
        main()
    except ImportError as e:
        print(f"Import error: {e}")
        print("Did you run 'uv sync' to install dependencies?")
        print("Required: google-api-python-client, google-auth, google-auth-oauthlib, python-dotenv")
        sys.exit(1)
