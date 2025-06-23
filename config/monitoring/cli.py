import os
import json
from access_control import afficher_droits, modifier_droits
from file_watcher import lancer_surveillance, arreter_surveillance
from datetime import datetime
import getpass

def log_to_file(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user = getpass.getuser()
    full_msg = f"[{timestamp}] ({user}) [{level}] {message}"

    # Affichage dans le terminal
    print(full_msg)

    # Écriture dans le fichier
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(full_msg + "\n")
    except Exception as e:
        print(f"[ERREUR LOG] {e}")

WATCHLIST_PATH = "../config/watchlist.json"
LOG_PATH = "../logs/events.log"

def afficher_menu():
    print("\n=== MENU DE SURVEILLANCE ===")
    print("1. Lancer la surveillance")
    print("2. Ajouter un fichier à surveiller")
    print("3. Supprimer un fichier de la surveillance")
    print("4. Afficher/modifier les droits d’un fichier")
    print("5. Afficher les logs")
    print("0. Quitter")

def afficher_log_terminal(message):
    print(f"[LOG] {message}")

def demarrer_surveillance():
    utilisateur = input("Entrez votre nom d'utilisateur")
    try:
        print("→ Démarrage de la surveillance...\n(CTRL+C pour arrêter)")
        lancer_surveillance(mode="cli", log_callback=afficher_log_terminal)
    except KeyboardInterrupt:
        print("🛑 Arrêt manuel de la surveillance.")
        arreter_surveillance()

def ajouter_fichier():
    chemin = input("Chemin complet du dossier ou fichier à surveiller : ").strip()
    if not os.path.exists(chemin):
        print("❌ Chemin invalide.")
        return

    try:
        with open(WATCHLIST_PATH, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"watched_files": []}

    if chemin in data["watched_files"]:
        print("⚠️  Ce chemin est déjà surveillé.")
    else:
        data["watched_files"].append(chemin)
        with open(WATCHLIST_PATH, "w") as f:
            json.dump(data, f, indent=4)
        print(f"✅ Ajouté à la surveillance : {chemin}")

def supprimer_fichier():
    chemin = input("Chemin complet à retirer de la surveillance : ").strip()

    try:
        with open(WATCHLIST_PATH, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ Liste de surveillance introuvable.")
        return

    if chemin in data["watched_files"]:
        data["watched_files"].remove(chemin)
        with open(WATCHLIST_PATH, "w") as f:
            json.dump(data, f, indent=4)
        print(f"🗑️ Supprimé de la surveillance : {chemin}")
    else:
        print("⚠️  Ce chemin n'était pas surveillé.")

def gestion_droits():
    fichier = input("Chemin du fichier à modifier : ").strip()

    droits_actuels = afficher_droits(fichier)
    if droits_actuels:
        choix = input("Souhaitez-vous modifier les droits ? (o/n) : ").lower()
        if choix == 'o':
            nouveaux = input("Nouveaux droits (ex: 644, 755) : ")
            modifier_droits(fichier, nouveaux)

def afficher_logs():
    if not os.path.exists(LOG_PATH):
        print("❌ Aucun fichier de logs trouvé.")
        return
    print("\n=== LOGS ===")
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        print(f.read())

def menu():
    while True:
        afficher_menu()
        choix = input("Votre choix : ").strip()
        if choix == "1":
            demarrer_surveillance()
        elif choix == "2":
            ajouter_fichier()
        elif choix == "3":
            supprimer_fichier()
        elif choix == "4":
            gestion_droits()
        elif choix == "5":
            afficher_logs()
        elif choix == "0":
            print("👋 Fin du programme.")
            break
        else:
            print("❌ Choix invalide.")

if __name__ == "__main__":
    menu()
