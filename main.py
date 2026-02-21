#!/usr/bin/env python3
"""AI Employee - Personal Digital FTE (Silver Tier)

Launch all watchers and the scheduler from a single entry point.
Usage:
    python main.py              # Run everything
    python main.py --watcher    # Run only file watcher
    python main.py --gmail      # Run only Gmail watcher
    python main.py --scheduler  # Run only scheduler
    python main.py --linkedin   # Run LinkedIn poster (manual mode)
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


def main():
    args = sys.argv[1:]

    if '--watcher' in args:
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
        print("  AI Employee - Digital FTE (Silver Tier)")
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
