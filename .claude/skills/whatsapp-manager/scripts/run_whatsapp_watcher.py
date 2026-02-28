#!/usr/bin/env python3
"""
Wrapper script for WhatsApp Watcher - Runs as a module to fix relative imports.
Located in scripts/ folder, adds parent directory to Python path.
"""
import sys
import os
from pathlib import Path

# Add parent directory (project root) to Python path
project_root = Path(__file__).parent.parent.parent.parent.parent  # Up from .claude/skills/<skill>/scripts/ to project root
sys.path.insert(0, str(project_root))

# Run the watcher as a module
if __name__ == "__main__":
    from watchers.whatsapp_watcher_playwright import main
    main()
