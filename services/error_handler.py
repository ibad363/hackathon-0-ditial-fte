# error_handler.py - Retry logic, error queue processing, and graceful degradation
#
# wrap_with_retry(func, max_retries=3, service_name)
#   Retry delays: 1min → 5min → 30min. After 3 fails → ALERT in Dashboard.md
# process_error_queue()
#   Read Error_Queue/, attempt recovery, log results
# graceful_degradation_report()
#   Check all services, update Dashboard.md status

import time
import traceback
from pathlib import Path
from datetime import datetime

VAULT_PATH  = Path('D:/Ibad Coding/hackathon-0-ditial-fte/AI_Employee_Vault')
ERROR_QUEUE = VAULT_PATH / 'Error_Queue'
AUDIT_DIR   = VAULT_PATH / 'Logs' / 'Audit'
DASHBOARD   = VAULT_PATH / 'Dashboard.md.md'

RETRY_DELAYS = [60, 300, 1800]  # 1min, 5min, 30min in seconds

for _d in [ERROR_QUEUE, AUDIT_DIR]:
    _d.mkdir(parents=True, exist_ok=True)


def _log(level: str, msg: str):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] [{level}] {msg}"
    print(line)
    log_file = AUDIT_DIR / 'error_handler_log.md'
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def _append_dashboard(text: str):
    """Append a line to the Recent Activity section of Dashboard.md."""
    if not DASHBOARD.exists():
        return
    content = DASHBOARD.read_text(encoding='utf-8')
    marker = '## Recent Activity'
    idx = content.find(marker)
    if idx == -1:
        # Append at end
        content += f"\n{text}\n"
    else:
        insert_at = idx + len(marker)
        date_str = datetime.now().strftime('%Y-%m-%d')
        content = content[:insert_at] + f"\n- [{date_str}] {text}" + content[insert_at:]
    DASHBOARD.write_text(content, encoding='utf-8')


# ---------------------------------------------------------------------------
# wrap_with_retry
# ---------------------------------------------------------------------------

def wrap_with_retry(func, max_retries: int = 3, service_name: str = 'unknown'):
    """
    Call func(). On failure, retry up to max_retries times with escalating delays.
    Delays: 1min → 5min → 30min.
    After all retries exhausted, write ALERT to Dashboard.md.

    Returns:
        The return value of func() on success, or None on total failure.
    """
    last_error = None
    for attempt in range(max_retries):
        try:
            _log('INFO', f"[{service_name}] Attempt {attempt + 1}/{max_retries}")
            result = func()
            _log('INFO', f"[{service_name}] Success on attempt {attempt + 1}")
            return result
        except Exception as e:
            last_error = e
            delay = RETRY_DELAYS[min(attempt, len(RETRY_DELAYS) - 1)]
            _log('WARN', f"[{service_name}] Attempt {attempt + 1} failed: {e}. "
                         f"Retrying in {delay}s...")

            # Save error to queue
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            err_file = ERROR_QUEUE / f"retry_{service_name}_{timestamp}.md"
            err_file.write_text(
                f"# Retry Error\n\n"
                f"**Service:** {service_name}\n"
                f"**Attempt:** {attempt + 1}/{max_retries}\n"
                f"**Time:** {datetime.now()}\n"
                f"**Error:** {e}\n"
                f"**Traceback:**\n```\n{traceback.format_exc()}\n```\n",
                encoding='utf-8',
            )

            if attempt < max_retries - 1:
                time.sleep(delay)

    # All retries exhausted
    alert = f"ALERT: {service_name} failed after {max_retries} retries — {last_error}"
    _log('ERROR', alert)
    _append_dashboard(f"🚨 {alert}")
    return None


# ---------------------------------------------------------------------------
# process_error_queue
# ---------------------------------------------------------------------------

def process_error_queue() -> dict:
    """
    Read all .md files in Error_Queue/, attempt basic recovery, log results.

    Returns:
        { total, recovered, unrecoverable, files }
    """
    _log('INFO', 'Processing error queue...')
    error_files = sorted(ERROR_QUEUE.glob('*.md'))

    if not error_files:
        _log('INFO', 'Error queue is empty.')
        return {'total': 0, 'recovered': 0, 'unrecoverable': 0, 'files': []}

    results = {'total': len(error_files), 'recovered': 0, 'unrecoverable': 0, 'files': []}

    for fpath in error_files:
        content = fpath.read_text(encoding='utf-8')
        entry = {'file': fpath.name, 'status': 'unrecoverable'}

        # Basic recovery: if the error mentions connection/timeout, mark as transient
        lower = content.lower()
        is_transient = any(kw in lower for kw in [
            'timeout', 'connection', 'temporary', 'network',
            'unavailable', 'refused', 'reset',
        ])

        if is_transient:
            entry['status'] = 'recovered_transient'
            results['recovered'] += 1
            # Move to Done (archive)
            done_dir = VAULT_PATH / 'Done'
            done_dir.mkdir(parents=True, exist_ok=True)
            fpath.rename(done_dir / f"resolved_{fpath.name}")
            _log('INFO', f"Transient error archived: {fpath.name}")
        else:
            results['unrecoverable'] += 1
            _log('WARN', f"Unrecoverable error remains: {fpath.name}")

        results['files'].append(entry)

    _log('INFO', f"Error queue processed: {results['recovered']} recovered, "
                 f"{results['unrecoverable']} unrecoverable out of {results['total']}")
    return results


# ---------------------------------------------------------------------------
# graceful_degradation_report
# ---------------------------------------------------------------------------

def graceful_degradation_report() -> dict:
    """
    Check all services and update Dashboard.md with current status.

    Returns:
        dict of service statuses.
    """
    _log('INFO', 'Running graceful degradation report...')

    services = {}

    # 1. Filesystem watcher
    try:
        from watchers.filesystem_watcher import DropFolderHandler
        services['filesystem_watcher'] = 'OK'
    except Exception as e:
        services['filesystem_watcher'] = f'DEGRADED: {e}'

    # 2. Gmail watcher
    try:
        from watchers.gmail_watcher import run
        services['gmail_watcher'] = 'OK'
    except Exception as e:
        services['gmail_watcher'] = f'DEGRADED: {e}'

    # 3. Scheduler
    try:
        from services.scheduler import run
        services['scheduler'] = 'OK'
    except Exception as e:
        services['scheduler'] = f'DEGRADED: {e}'

    # 4. LinkedIn poster
    try:
        from services.linkedin_poster import create_linkedin_draft
        services['linkedin_poster'] = 'OK'
    except Exception as e:
        services['linkedin_poster'] = f'DEGRADED: {e}'

    # 5. Odoo
    try:
        from mcp_server.odoo_mcp import test_connection
        services['odoo'] = 'OK'
    except Exception as e:
        services['odoo'] = f'DEGRADED: {e}'

    # 6. Social media
    try:
        from services.social_media_manager import create_all_drafts
        services['social_media'] = 'OK'
    except Exception as e:
        services['social_media'] = f'DEGRADED: {e}'

    # 7. Error queue size
    error_count = len(list(ERROR_QUEUE.glob('*.md')))
    services['error_queue_size'] = error_count

    # Update Dashboard
    date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ok_count = sum(1 for v in services.values() if v == 'OK')
    total_svc = sum(1 for k in services if k != 'error_queue_size')
    degraded = [k for k, v in services.items() if isinstance(v, str) and v.startswith('DEGRADED')]

    status_line = f"System Health: {ok_count}/{total_svc} services OK"
    if degraded:
        status_line += f" | Degraded: {', '.join(degraded)}"
    if error_count:
        status_line += f" | Errors in queue: {error_count}"

    _append_dashboard(f"Health check: {status_line}")

    _log('INFO', status_line)
    for svc, status in services.items():
        print(f"  {svc:25s} -> {status}")

    return services
