#!/usr/bin/env python3
"""
Wrapper script for Odoo Watcher - Fixes relative import issues.
Located in scripts/ folder, adds parent directory to Python path.

Usage:
    python scripts/run_odoo_watcher.py --vault AI_Employee_Vault
"""
import sys
from pathlib import Path

# Add parent directory (project root) to Python path
project_root = Path(__file__).parent.parent.parent.parent.parent  # Up from .claude/skills/<skill>/scripts/ to project root
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    import watchers.odoo_watcher
    watchers.odoo_watcher.main()
