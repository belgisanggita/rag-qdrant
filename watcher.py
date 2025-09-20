import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import subprocess

WATCH_FOLDER = "example_docs"

class IngestHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(".txt"):
            print(f"[MODIFIED] {event.src_path}")
            self.run_ingest()

    def on_created(self, event):
        if event.src_path.endswith(".txt"):
            print(f"[CREATED] {event.src_path}")
            self.run_ingest()

    def on_deleted(self, event):
        if event.src_path.endswith(".txt"):
            print(f"[DELETED] {event.src_path}")
            self.run_ingest()

    def run_ingest(self):
        print("[Ingesting] Running ingest.py...")
        subprocess.run(["python", "ingest.py"])

def start_watcher():
    event_handler = IngestHandler()
    observer = Observer()
    observer.schedule(event_handler, path=WATCH_FOLDER, recursive=False)
    observer.start()
    print(f"[Watcher] Monitoring changes in '{WATCH_FOLDER}'...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
