# scheduler.py - Automated task scheduler for AI Employee (Gold Tier)
import schedule
import time
import subprocess
import sys
from pathlib import Path
from datetime import datetime

VAULT_PATH = Path('D:/Ibad Coding/hackathon-0-ditial-fte/AI_Employee_Vault')
PROJECT_ROOT = Path('D:/Ibad Coding/hackathon-0-ditial-fte')
LOG_FILE = VAULT_PATH / 'Logs' / 'scheduler_log.md'


def log(message):
    """Append a timestamped message to the scheduler log."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"- [{timestamp}] {message}\n"

    if not LOG_FILE.exists():
        LOG_FILE.write_text("# Scheduler Log\n\nAutomated actions triggered by scheduler.py\n\n", encoding='utf-8')

    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(entry)

    print(f"[Scheduler] [{timestamp}] {message}")


def find_claude():
    """Find the claude executable, checking common Windows install locations."""
    import shutil
    found = shutil.which('claude') or shutil.which('claude.cmd')
    if found:
        return found
    npm_path = Path.home() / 'AppData' / 'Roaming' / 'npm' / 'claude.cmd'
    if npm_path.exists():
        return str(npm_path)
    return 'claude'


def run_claude_command(command_name, description):
    """Trigger a Claude command via subprocess."""
    log(f"TRIGGERED: {description} (command: {command_name})")
    try:
        claude_exe = find_claude()
        result = subprocess.run(
            [claude_exe, '--print', '--command', command_name],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode == 0:
            log(f"COMPLETED: {description}")
        else:
            log(f"FAILED: {description} | Error: {result.stderr[:200]}")
    except subprocess.TimeoutExpired:
        log(f"TIMEOUT: {description} (exceeded 5 minutes)")
    except FileNotFoundError:
        log(f"SKIPPED: {description} (Claude CLI not found - install it first)")
    except Exception as e:
        log(f"ERROR: {description} | {str(e)[:200]}")


# ---------------------------------------------------------------------------
# Silver Tier scheduled tasks
# ---------------------------------------------------------------------------

def morning_briefing():
    """8:00 AM daily - Process emails and prepare daily update."""
    log("=" * 40)
    log("MORNING BRIEFING - Starting daily routine")
    run_claude_command('process-emails', 'Morning email processing')
    log("MORNING BRIEFING - Complete")


def weekly_audit():
    """Monday 7:00 AM - Full weekly briefing and audit."""
    log("=" * 40)
    log("WEEKLY AUDIT - Starting Monday briefing")
    run_claude_command('weekly-briefing', 'Weekly CEO briefing')
    log("WEEKLY AUDIT - Complete")


def linkedin_draft():
    """Wednesday 10:00 AM - Create LinkedIn post draft."""
    log("=" * 40)
    log("LINKEDIN DRAFT - Creating weekly post")
    run_claude_command('linkedin-post', 'LinkedIn post draft')
    log("LINKEDIN DRAFT - Complete")


def check_approved_posts():
    """Check for approved LinkedIn posts and publish them."""
    services_dir = str(PROJECT_ROOT / 'services')
    if services_dir not in sys.path:
        sys.path.insert(0, services_dir)
    from linkedin_poster import check_approved_posts as check_posts
    log("Checking for approved LinkedIn posts...")
    try:
        check_posts()
        log("LinkedIn approval check complete")
    except Exception as e:
        log(f"LinkedIn check error: {e}")


# ---------------------------------------------------------------------------
# Gold Tier scheduled tasks
# ---------------------------------------------------------------------------

def gold_monday_briefing():
    """Monday 7:00 AM - Gold briefing + Odoo audit."""
    log("=" * 40)
    log("GOLD MONDAY BRIEFING - Weekly briefing + Odoo audit")
    run_claude_command('weekly-briefing', 'Gold weekly CEO briefing')
    try:
        from mcp_server.odoo_mcp import test_connection, get_pending_invoices
        log("Running Odoo audit...")
        if test_connection():
            invoices = get_pending_invoices()
            log(f"Odoo audit: {len(invoices)} pending invoice(s)")
        else:
            log("Odoo audit: connection failed")
    except Exception as e:
        log(f"Odoo audit error: {e}")
    log("GOLD MONDAY BRIEFING - Complete")


def social_post_all():
    """Tuesday + Thursday 9:00 AM - Post approved content on all platforms."""
    log("=" * 40)
    log("SOCIAL POST ALL - Posting approved drafts to all platforms")
    try:
        from services.social_media_manager import post_all_approved
        results = post_all_approved()
        ok = sum(1 for r in results if r.get('success'))
        log(f"SOCIAL POST ALL - {ok}/{len(results)} posted successfully")
    except Exception as e:
        log(f"SOCIAL POST ALL - Error: {e}")


def error_queue_check():
    """Every 30 min - Process error queue."""
    try:
        from services.error_handler import process_error_queue
        result = process_error_queue()
        if result['total'] > 0:
            log(f"Error queue: {result['recovered']} recovered, "
                f"{result['unrecoverable']} unrecoverable out of {result['total']}")
    except Exception as e:
        log(f"Error queue check failed: {e}")


def ralph_loop_if_needed():
    """Every 1 hour - Run Ralph loop only if Needs_Action has files."""
    needs_action = VAULT_PATH / 'Needs_Action'
    files = list(needs_action.glob('*.md')) if needs_action.exists() else []
    if not files:
        return
    log(f"RALPH AUTO - {len(files)} file(s) in Needs_Action, starting loop...")
    try:
        from services.ralph_loop import run_ralph_loop
        result = run_ralph_loop()
        log(f"RALPH AUTO - Finished: {result}")
    except Exception as e:
        log(f"RALPH AUTO - Error: {e}")


def sunday_revenue():
    """Sunday 10:00 PM - Get monthly revenue report."""
    log("=" * 40)
    log("SUNDAY REVENUE - Fetching monthly revenue from Odoo")
    try:
        from mcp_server.odoo_mcp import get_monthly_revenue
        result = get_monthly_revenue()
        log(f"Monthly revenue: ${result['total_revenue']} "
            f"({result['invoice_count']} invoices)")
    except Exception as e:
        log(f"SUNDAY REVENUE - Error: {e}")


# ---------------------------------------------------------------------------
# Schedule setup
# ---------------------------------------------------------------------------

def setup_schedules():
    """Configure all scheduled tasks (Silver + Gold)."""
    # Silver Tier
    schedule.every().day.at("08:00").do(morning_briefing)
    schedule.every().monday.at("07:00").do(weekly_audit)
    schedule.every().wednesday.at("10:00").do(linkedin_draft)
    schedule.every().hour.do(check_approved_posts)

    # Gold Tier
    schedule.every().monday.at("07:00").do(gold_monday_briefing)
    schedule.every().tuesday.at("09:00").do(social_post_all)
    schedule.every().thursday.at("09:00").do(social_post_all)
    schedule.every(30).minutes.do(error_queue_check)
    schedule.every().hour.do(ralph_loop_if_needed)
    schedule.every().sunday.at("22:00").do(sunday_revenue)


def run():
    """Main scheduler loop."""
    print("=" * 60)
    print("[Scheduler] AI Employee Scheduler Starting (Gold Tier)")
    print(f"[Scheduler] Log file: {LOG_FILE}")
    print("=" * 60)
    print()
    print("[Scheduler] Scheduled tasks:")
    print("  Silver Tier:")
    print("  - Daily 8:00 AM    : Morning briefing (process emails)")
    print("  - Monday 7:00 AM   : Weekly audit & CEO briefing")
    print("  - Wednesday 10 AM  : LinkedIn post draft")
    print("  - Every hour       : Check approved LinkedIn posts")
    print()
    print("  Gold Tier:")
    print("  - Monday 7:00 AM   : Gold briefing + Odoo audit")
    print("  - Tue/Thu 9:00 AM  : Social post all platforms")
    print("  - Every 30 min     : Process error queue")
    print("  - Every 1 hour     : Ralph loop (if Needs_Action not empty)")
    print("  - Sunday 10:00 PM  : Monthly revenue report (Odoo)")
    print()
    print("[Scheduler] Running... Press Ctrl+C to stop")
    print()

    log("Scheduler started (Gold Tier)")
    setup_schedules()

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == '__main__':
    run()
