from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
import os

class FileMonitorHandler(FileSystemEventHandler):
    def __init__(self, logfile="logs/events.log"):
        self.logfile = logfile

    def on_modified(self, event):
        self._log_event("MODIFIED", event.src_path)

    def on_created(self, event):
        self._log_event("CREATED", event.src_path)

    def on_deleted(self, event):
        self._log_event("DELETED", event.src_path)

    def on_moved(self, event):
        self._log_event("MOVED", f"{event.src_path} -> {event.dest_path}")

    def _log_event(self, event_type, path):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"[{now}] {event_type} → {path}"
        print(message)
        os.makedirs(os.path.dirname(self.logfile), exist_ok=True)
        with open(self.logfile, "a") as f:
            f.write(message + "\n")

def start_monitoring(path, logfile="logs/events.log"):
    event_handler = FileMonitorHandler(logfile)
    observer = Observer()
    observer.schedule(event_handler, path=path, recursive=True)
    observer.start()
    print(f"🔍 Surveillance activée sur : {path}")
    try:
        while True:
            pass  # boucle infinie, à remplacer par un signal d’arrêt propre plus tard
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
