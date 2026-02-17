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
        
        # Fix: Dono errors pakdo — FileNotFoundError AND PermissionError
        for attempt in range(10):
            try:
                # Pehle check karo file exist karti hai?
                if not source.exists():
                    time.sleep(1)
                    continue
                
                shutil.copy2(source, dest)
                print(f"✅ Copied: {source.name}")
                self.create_metadata(source, dest)  # yeh bhi fix kiya
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
    print("Ab drop_folder mein koi file daalo...\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n🛑 Watcher band ho gaya.")
    observer.join()




# import time
# import shutil
# from pathlib import Path
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler
# from datetime import datetime

# # ============================
# # YAHAN APNA PATH DAALO
# # ============================
# VAULT_PATH = 'D:/Ibad Coding/hackathon-0-ditial-fte/AI_Employee_Vault'
# WATCH_FOLDER = 'D:/Ibad Coding/hackathon-0-ditial-fte/drop_folder'
# # ============================

# class NewFileHandler(FileSystemEventHandler):
#     def __init__(self):
#         self.needs_action = Path(VAULT_PATH) / "Needs_Action"
    
#     def on_created(self, event):
#         if event.is_directory:
#             return
        
#         source = Path(event.src_path)
#         print(f"Naya file aaya: {source.name}")
        
#         # Needs_Action mein copy karo
#         dest = self.needs_action / f"TASK_{source.name}"
#         shutil.copy2(source, dest)
        
#         # Ek markdown note banao Claude ke liye
#         timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
#         note_path = self.needs_action / f"TASK_{source.stem}_info.md"
#         note_path.write_text(f"""---
# type: file_task
# original_file: {source.name}
# received: {timestamp}
# status: pending
# ---

# ## Naya Kaam Aaya Hai

# File ka naam: {source.name}
# Kab aaya: {timestamp}

# ## Claude Ko Karna Hai
# - [ ] File padhna
# - [ ] Samajhna kya action chahiye
# - [ ] Dashboard update karna
# - [ ] Done folder mein move karna
# """)
#         print(f"✅ Claude ke liye task file bana di: {note_path.name}")

# # Script start karo
# print(f"👀 Watcher chal raha hai: {WATCH_FOLDER}")
# print("Ab Inbox folder mein koi file daalo...")

# handler = NewFileHandler()
# observer = Observer()
# observer.schedule(handler, WATCH_FOLDER, recursive=False)
# observer.start()

# try:
#     while True:
#         time.sleep(1)
# except KeyboardInterrupt:
#     observer.stop()
#     print("Watcher band ho gaya.")

# observer.join()