import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import subprocess

WATCH_FOLDER = "example_docs"

class IngestHandler(FileSystemEventHandler):
    def __init__(self, debounce_seconds=1):
        super().__init__()
        self.debounce_seconds = debounce_seconds
        self._timer = None
        self._lock = threading.Lock()

    def on_modified(self, event):
        if event.src_path.endswith(".txt"):
            print(f"[MODIFIED] {event.src_path}")
            self._debounced_run()

    def on_created(self, event):
        if event.src_path.endswith(".txt"):
            print(f"[CREATED] {event.src_path}")
            self._debounced_run()

    def on_deleted(self, event):
        if event.src_path.endswith(".txt"):
            print(f"[DELETED] {event.src_path}")
            self._debounced_run()

    def _debounced_run(self):
        with self._lock:
            if self._timer:
                self._timer.cancel()
            self._timer = threading.Timer(self.debounce_seconds, self.run_ingest)
            self._timer.start()

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

if __name__ == "__main__":
    start_watcher()