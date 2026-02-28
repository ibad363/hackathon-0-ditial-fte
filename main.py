"""AI Employee - Personal Digital FTE (Gold Tier)

Launch all watchers and the scheduler from a single entry point.
Usage:
    python main.py              # Run everything
    python main.py --watcher    # Run only file watcher
    python main.py --gmail      # Run only Gmail watcher
    python main.py --scheduler  # Run only scheduler
    python main.py --linkedin   # Run LinkedIn poster (manual mode)
    python main.py --odoo       # Test Odoo connection (Gold Tier)
    python main.py --setup      # One-time social media session setup
    python main.py --social     # Create social media drafts
    python main.py --post-social # Post all approved social media drafts
    python main.py --sessions   # Check all browser sessions
    python main.py --ralph      # Run Ralph autonomous loop
    python main.py --audit      # Process error queue + degradation report
    python main.py --gold       # Run everything in Gold mode
"""
import sys
import threading
import time


def run_filesystem_watcher():
    """Start the filesystem drop folder watcher."""
    from watchdog.observers import Observer
    from watchers.filesystem_watcher import DropFolderHandler

    vault_path = 'D:/Ibad Coding/hackathon-0-ditial-fte/AI_Employee_Vault'
    drop_folder = 'D:/Ibad Coding/hackathon-0-ditial-fte/drop_folder'

    handler = DropFolderHandler(vault_path)
    observer = Observer()
    observer.schedule(handler, path=drop_folder, recursive=False)
    observer.start()
    print("[Main] Filesystem watcher started")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def run_gmail_watcher():
    """Start the Gmail watcher."""
    from watchers.gmail_watcher import run
    run()


def run_scheduler():
    """Start the task scheduler."""
    from services.scheduler import run
    run()


def run_linkedin():
    """Run LinkedIn poster in manual mode."""
    from services.linkedin_poster import create_linkedin_draft, check_approved_posts

    print("=" * 50)
    print("[LinkedIn Poster] Manual Mode")
    print("=" * 50)
    print("\nOptions:")
    print("1. Create a test draft")
    print("2. Check and post approved drafts")

    choice = input("\nEnter choice (1/2): ").strip()

    if choice == '1':
        test_content = """Excited to share our latest project update!

We've been building an AI-powered personal employee system that automates daily tasks like email processing, scheduling, and content creation.

The key insight? AI works best when it has clear guardrails and human approval loops.

#AI #Automation #Productivity #TechInnovation #BuildInPublic"""
        create_linkedin_draft(test_content, topic="AI Employee Project Update")
    elif choice == '2':
        check_approved_posts()
    else:
        print("Invalid choice")


def run_odoo():
    """Test Odoo connection (Gold Tier)."""
    from mcp_server.odoo_mcp import test_connection

    print("=" * 50)
    print("[Odoo] Testing connection...")
    print("=" * 50)
    success = test_connection()
    if success:
        print("[Odoo] Connection OK")
    else:
        print("[Odoo] Connection FAILED — check .env and Error_Queue/")


def run_setup():
    """One-time social media session setup."""
    from scripts.setup_social_sessions import setup_sessions
    setup_sessions()


def run_social():
    """Create social media drafts for all platforms."""
    from services.social_media_manager import create_all_drafts

    print("=" * 50)
    print("[Social] Creating drafts for all platforms...")
    print("=" * 50)
    content = input("\nEnter post content:\n> ").strip()
    topic = input("Enter topic (or press Enter for 'General'):\n> ").strip() or 'General'
    create_all_drafts(content, topic=topic)


def run_post_social():
    """Post all approved social media drafts."""
    from services.social_media_manager import post_all_approved

    print("=" * 50)
    print("[Social] Posting all approved drafts...")
    print("=" * 50)
    post_all_approved()


def run_sessions():
    """Check all browser sessions."""
    from services.session_manager import check_all_sessions

    print("=" * 50)
    print("[Sessions] Checking all platform sessions...")
    print("=" * 50)
    check_all_sessions()


def run_ralph():
    """Run Ralph autonomous processing loop."""
    from services.ralph_loop import run_ralph_loop

    print("=" * 50)
    print("[Ralph] Starting autonomous loop...")
    print("=" * 50)
    result = run_ralph_loop()
    print(f"\n[Ralph] Finished: {result}")


def run_audit():
    """Process error queue and run degradation report."""
    from services.error_handler import process_error_queue, graceful_degradation_report

    print("=" * 50)
    print("[Audit] Processing error queue...")
    print("=" * 50)
    eq_result = process_error_queue()
    print(f"\nError queue: {eq_result}\n")

    print("=" * 50)
    print("[Audit] Running degradation report...")
    print("=" * 50)
    graceful_degradation_report()


def run_gold():
    """Run everything in Gold mode: watchers + Gold scheduler."""
    print("=" * 60)
    print("  AI Employee - Digital FTE (Gold Tier)")
    print("  Starting ALL Gold services...")
    print("=" * 60)
    print()

    # Filesystem watcher thread
    t1 = threading.Thread(target=run_filesystem_watcher, daemon=True)
    t1.start()
    print("[Gold] Filesystem watcher thread started")

    # Gmail watcher thread
    t2 = threading.Thread(target=run_gmail_watcher, daemon=True)
    t2.start()
    print("[Gold] Gmail watcher thread started")

    # Session check (non-blocking)
    try:
        from services.session_manager import check_all_sessions
        print("\n[Gold] Browser session status:")
        check_all_sessions()
        print()
    except Exception as e:
        print(f"[Gold] Session check skipped: {e}\n")

    # Error queue check (non-blocking)
    try:
        from services.error_handler import process_error_queue
        result = process_error_queue()
        if result['total'] > 0:
            print(f"[Gold] Error queue: {result['recovered']} recovered, "
                  f"{result['unrecoverable']} remaining\n")
    except Exception:
        pass

    # Gold scheduler on main thread (keeps process alive)
    print("[Gold] Starting Gold scheduler on main thread...")
    print()
    run_scheduler()


def main():
    args = sys.argv[1:]

    if '--gold' in args:
        run_gold()
    elif '--ralph' in args:
        run_ralph()
    elif '--audit' in args:
        run_audit()
    elif '--setup' in args:
        run_setup()
    elif '--social' in args:
        run_social()
    elif '--post-social' in args:
        run_post_social()
    elif '--sessions' in args:
        run_sessions()
    elif '--odoo' in args:
        run_odoo()
    elif '--watcher' in args:
        run_filesystem_watcher()
    elif '--gmail' in args:
        run_gmail_watcher()
    elif '--scheduler' in args:
        run_scheduler()
    elif '--linkedin' in args:
        run_linkedin()
    else:
        # Run all services
        print("=" * 60)
        print("  AI Employee - Digital FTE (Gold Tier)")
        print("  Starting all services...")
        print("=" * 60)
        print()

        # Start filesystem watcher in a thread
        t1 = threading.Thread(target=run_filesystem_watcher, daemon=True)
        t1.start()
        print("[Main] Filesystem watcher thread started")

        # Start Gmail watcher in a thread
        t2 = threading.Thread(target=run_gmail_watcher, daemon=True)
        t2.start()
        print("[Main] Gmail watcher thread started")

        # Run scheduler on main thread (keeps process alive)
        print("[Main] Starting scheduler on main thread...")
        print()
        run_scheduler()


if __name__ == "__main__":
    main()
