from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import shutil
import time

class DropFolderHandler(FileSystemEventHandler):
    def __init__(self, vault_path: str):
        self.needs_action = Path(vault_path) / 'Needs_Action'

    def on_created(self, event):
        if event.is_directory:
            return
        
        source = Path(event.src_path)
        dest = self.needs_action / f'FILE_{source.name}'
        
        # Fix: Catch both FileNotFoundError AND PermissionError
        for attempt in range(10):
            try:
                # First check if the file exists
                if not source.exists():
                    time.sleep(1)
                    continue
                
                shutil.copy2(source, dest)
                print(f"✅ Copied: {source.name}")
                self.create_metadata(source, dest)  # also fixed here
                break
                
            except (PermissionError, FileNotFoundError) as e:
                print(f"⏳ Attempt {attempt+1}/10 - Waiting for file... ({e})")
                time.sleep(1)
        else:
            print(f"❌ Failed to copy after 10 attempts: {source.name}")

    def create_metadata(self, source: Path, dest: Path):
        meta_path = self.needs_action / f'FILE_{source.stem}.md'
        meta_path.write_text(f'''---
type: file_drop
original_name: {source.name}
size: {source.stat().st_size if source.exists() else "unknown"}
received: {time.strftime("%Y-%m-%d %H:%M:%S")}
priority: medium
status: pending
---

## File Content Summary
New file dropped for processing.

## Suggested Actions
- [ ] Review and categorize
- [ ] Process with Claude
- [ ] Move to /Done after completion
''')
        print(f"📝 Metadata created: FILE_{source.stem}.md")

# Setup and run
if __name__ == "__main__":
    vault_path = 'D:/Ibad Coding/hackathon-0-ditial-fte/AI_Employee_Vault'
    drop_folder = 'D:/Ibad Coding/hackathon-0-ditial-fte/drop_folder'

    event_handler = DropFolderHandler(vault_path)
    observer = Observer()
    observer.schedule(event_handler, path=drop_folder, recursive=False)
    observer.start()
    print(f"👀 Watching: {drop_folder}")
    print("Now drop any file into the drop_folder...\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n🛑 Watcher stopped.")
    observer.join()