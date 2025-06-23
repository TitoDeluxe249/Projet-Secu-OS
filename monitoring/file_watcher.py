import time
import json
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime, timedelta
import stat
import getpass  
# Chemins
LOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs", "events.log"))
WATCHLIST_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config", "watchlist.json"))

observer = None
modifications_gui = {}

def get_file_properties(path):
    try:
        stats = os.stat(path)
        return {
            "permissions": stat.filemode(stats.st_mode),
            "uid": stats.st_uid,
            "gid": stats.st_gid,
            "mtime": stats.st_mtime
        }
    except Exception:
        return None

class FileEventHandler(FileSystemEventHandler):
    def __init__(self, paths_to_watch, log_callback=None, current_user="system"):
          self.paths_to_watch = set(os.path.abspath(p) for p in paths_to_watch)
          self.log_callback = log_callback or print
          self.last_properties = {path: get_file_properties(path) for path in self.paths_to_watch}
          self.current_user = current_user  
    @staticmethod
    def marquer_modifie_depuis_gui(path):
       """Appelé depuis le GUI pour éviter les logs en double"""
       modifications_gui[path] = datetime.now()

    def log_event(self, message, path=None, level="INFO"):
        """Affiche et enregistre un événement"""
        # Ignorer si récemment modifié par GUI
        if path and path in modifications_gui:
            if datetime.now() - modifications_gui[path] < timedelta(seconds=2):
                del modifications_gui[path]
                return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user = self.current_user
        full_msg = f"[{timestamp}] ({user}) [{level}] {message}"

        # Affichage dans GUI ou terminal
        self.log_callback(full_msg)

        # Enregistrement dans le fichier logs/events.log
        try:
            os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
            with open(LOG_PATH, "a", encoding="utf-8") as f:
                f.write(full_msg + "\n")
        except Exception as e:
            self.log_callback(f"[ERREUR LOG] {e}")

    def dispatch(self, event):
        """Traite les événements observés par watchdog"""
        path = os.path.abspath(event.src_path)
        matched = any(path.startswith(w) for w in self.paths_to_watch)
        if not matched:
            return

        # Vérifier les changements de propriété
        current_props = get_file_properties(path)
        previous_props = self.last_properties.get(path)

        if current_props and previous_props:
            for key in ["permissions", "uid", "gid"]:
                if current_props.get(key) != previous_props.get(key):
                    self.log_event(
                        f"🔧 {key.upper()} modifié pour {path} → Avant: {previous_props[key]} | Maintenant: {current_props[key]}",
                        path=path,
                        level="MODIF"
                    )
        self.last_properties[path] = current_props

        # Déterminer le type d’action
        if event.event_type == "created":
            self.log_event(f"📁 Fichier {path} a été créé", path=path, level="CREATION")

        elif event.event_type == "modified":
            self.log_event(f"📝 Fichier {path} a été modifié", path=path, level="MODIF")
        elif event.event_type == "deleted":
            self.log_event(f"🗑️ Fichier {path} a été supprimé", path=path, level="SUPPRESSION")
        elif event.event_type == "moved":
          dest_path = os.path.abspath(getattr(event, "dest_path", ""))
          self.log_event(f"📦 Fichier déplacé de {path} vers {dest_path}", path=dest_path, level="DEPLACEMENT")    


def charger_watchlist():
    try:
        with open(WATCHLIST_PATH, "r") as f:
            data = json.load(f)
            return data.get("watched_files", [])
    except Exception as e:
        print(f"Erreur lors du chargement de la watchlist : {e}")
        return []

def lancer_surveillance(mode="gui" , log_callback=None, utilisateur="system"):
    global observer

    if observer is not None and observer.is_alive():
        (log_callback or print)("⚠️ Surveillance déjà active.")
        return

    fichiers = charger_watchlist()
    if not fichiers:
        (log_callback or print)("❌ Aucun fichier à surveiller.")
        return

    fichiers = [os.path.abspath(f) for f in fichiers]
    dossier_parents = {os.path.dirname(f) if os.path.isfile(f) else f for f in fichiers}

    event_handler = FileEventHandler(fichiers, log_callback=log_callback, current_user=utilisateur)
    observer = Observer()

    for dossier in dossier_parents:
        if os.path.isdir(dossier):
            observer.schedule(event_handler, path=dossier, recursive=True)
            (log_callback or print)(f"📡 Surveillance activée sur : {dossier}")

    for f in fichiers:
        (log_callback or print)(f"🔍 Suivi de fichier : {f}")

    observer.start()
    (log_callback or print)("🟢 Surveillance active depuis CLI." if mode == "cli" else "🟢 Surveillance active depuis GUI.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        arreter_surveillance()
        (log_callback or print)("🛑 Surveillance arrêtée proprement.")

def arreter_surveillance():
    global observer
    if observer and observer.is_alive():
        observer.stop()
        observer.join()
        observer = None
