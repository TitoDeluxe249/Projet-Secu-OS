import time
import json
import os

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

LOG_PATH = "../logs/events.log"
WATCHLIST_PATH = "../config/watchlist.json"

# Crée le dossier logs si nécessaire
os.makedirs("../logs", exist_ok=True)

def log_event(message):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a") as f:
        f.write(f"[{now}] {message}\n")
    print(f"[LOG] {message}")

class FileEventHandler(FileSystemEventHandler):
    def __init__(self, paths_to_watch):
        self.paths_to_watch = set(paths_to_watch)

    def dispatch(self, event):
        if event.src_path in self.paths_to_watch:
            action = "modifié"
            if event.event_type == "deleted":
                action = "supprimé"
            elif event.event_type == "moved":
                action = f"déplacé vers {event.dest_path}"

            log_event(f"Fichier {event.src_path} a été {action}")

def charger_watchlist():
    try:
        with open(WATCHLIST_PATH, "r") as f:
            data = json.load(f)
            return data.get("watched_files", [])
    except Exception:
        return []

def lancer_surveillance():
    fichiers = charger_watchlist()
    if not fichiers:
        print("❌ Aucun fichier à surveiller. Utilisez le menu pour en ajouter.")
        return

    dossier_parents = set(os.path.dirname(f) for f in fichiers)

    event_handler = FileEventHandler(fichiers)
    observer = Observer()

    for dossier in dossier_parents:
        if os.path.exists(dossier):
            observer.schedule(event_handler, path=dossier, recursive=False)
        else:
            print(f"⚠️ Dossier introuvable : {dossier}")

    observer.start()
    print("✅ Surveillance active. Appuyez sur Ctrl+C pour arrêter.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n🛑 Surveillance arrêtée.")
    observer.join()
