# audit_logger.py - Structured JSON audit logging
#
# log_action(action_type, actor, target, parameters, result, approval_status)
# Saves to Logs/Audit/[YYYY-MM-DD].json
# 90-day retention (auto-cleans on each call)

import json
import os
from pathlib import Path
from datetime import datetime, timedelta

VAULT_PATH = Path('D:/Ibad Coding/hackathon-0-ditial-fte/AI_Employee_Vault')
AUDIT_DIR  = VAULT_PATH / 'Logs' / 'Audit'
RETENTION_DAYS = 90

AUDIT_DIR.mkdir(parents=True, exist_ok=True)


def log_action(action_type: str, actor: str, target: str,
               parameters: dict = None, result: str = '',
               approval_status: str = 'N/A') -> dict:
    """
    Log a structured audit entry.

    Args:
        action_type:     e.g. 'email_sent', 'invoice_created', 'post_published'
        actor:           who/what performed it, e.g. 'gmail_watcher', 'ralph_loop'
        target:          what it acted on, e.g. 'invoice_123', 'linkedin_draft'
        parameters:      dict of relevant params
        result:          'success', 'failure', or descriptive string
        approval_status: 'approved', 'pending', 'rejected', 'N/A'

    Returns:
        The entry dict that was written.
    """
    entry = {
        'timestamp': datetime.now().isoformat(),
        'action_type': action_type,
        'actor': actor,
        'target': target,
        'parameters': parameters or {},
        'result': result,
        'approval_status': approval_status,
    }

    today_file = AUDIT_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.json"

    # Load existing entries for today
    entries = []
    if today_file.exists():
        try:
            entries = json.loads(today_file.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, ValueError):
            entries = []

    entries.append(entry)
    today_file.write_text(json.dumps(entries, indent=2, default=str), encoding='utf-8')

    # Run retention cleanup
    _enforce_retention()

    return entry


def _enforce_retention():
    """Delete audit JSON files older than RETENTION_DAYS."""
    cutoff = datetime.now() - timedelta(days=RETENTION_DAYS)
    for f in AUDIT_DIR.glob('*.json'):
        # Parse date from filename YYYY-MM-DD.json
        try:
            file_date = datetime.strptime(f.stem, '%Y-%m-%d')
            if file_date < cutoff:
                f.unlink()
        except ValueError:
            pass
