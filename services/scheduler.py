# scheduler.py - Automated task scheduler for AI Employee
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

    # Initialize log file if it doesn't exist
    if not LOG_FILE.exists():
        LOG_FILE.write_text("# Scheduler Log\n\nAutomated actions triggered by scheduler.py\n\n", encoding='utf-8')

    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(entry)

    print(f"[Scheduler] [{timestamp}] {message}")


def run_claude_command(command_name, description):
    """Trigger a Claude command via subprocess."""
    log(f"TRIGGERED: {description} (command: {command_name})")
    try:
        # Run Claude with the specified command
        result = subprocess.run(
            ['claude', '--print', '--command', command_name],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
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
    # Add services directory to path for import
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


def setup_schedules():
    """Configure all scheduled tasks."""
    # Daily morning briefing at 8:00 AM
    schedule.every().day.at("08:00").do(morning_briefing)

    # Weekly audit every Monday at 7:00 AM
    schedule.every().monday.at("07:00").do(weekly_audit)

    # LinkedIn draft every Wednesday at 10:00 AM
    schedule.every().wednesday.at("10:00").do(linkedin_draft)

    # Check for approved LinkedIn posts every hour
    schedule.every().hour.do(check_approved_posts)


def run():
    """Main scheduler loop."""
    print("=" * 50)
    print("[Scheduler] AI Employee Scheduler Starting")
    print(f"[Scheduler] Log file: {LOG_FILE}")
    print("=" * 50)
    print()
    print("[Scheduler] Scheduled tasks:")
    print("  - Daily 8:00 AM  : Morning briefing (process emails)")
    print("  - Monday 7:00 AM : Weekly audit & CEO briefing")
    print("  - Wednesday 10 AM: LinkedIn post draft")
    print("  - Every hour      : Check approved LinkedIn posts")
    print()
    print("[Scheduler] Running... Press Ctrl+C to stop")
    print()

    log("Scheduler started")
    setup_schedules()

    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == '__main__':
    run()
