import hashlib
import getpass
import os
import json

def authentification():
    try:
        with open("../config/password.hash", "r") as f:
            hash_attendu = f.read().strip()
    except FileNotFoundError:
        print("❌ Fichier de mot de passe introuvable.")
        return False

    mot_de_passe = getpass.getpass("Mot de passe admin : ")
    hash_saisi = hashlib.sha256(mot_de_passe.encode()).hexdigest()

    if hash_saisi == hash_attendu:
        print("✅ Authentification réussie.\n")
        return True
    else:
        print("❌ Mot de passe incorrect.")
        return False

def afficher_menu():
    print("\n=== MENU DE SURVEILLANCE ===")
    print("1. Lancer la surveillance")
    print("2. Ajouter un fichier à surveiller")
    print("3. Supprimer un fichier à surveiller")
    print("4. Afficher/modifier les droits d’un fichier")
    print("5. Vérifier l’intégrité des fichiers")
    print("6. Afficher les logs")
    print("0. Quitter")

def demarrer_surveillance():
    print("→ Surveillance démarrée (fonction à implémenter)")

def ajouter_fichier():
    print("→ Fichier ajouté (fonction à implémenter)")

def supprimer_fichier():
    print("→ Fichier supprimé (fonction à implémenter)")

def gestion_droits():
    print("→ Gestion des droits (fonction à implémenter)")

def verifier_integrite():
    print("→ Vérification d'intégrité (fonction à implémenter)")

def afficher_logs():
    print("→ Affichage des logs (fonction à implémenter)")

def menu():
    while True:
        afficher_menu()
        choix = input("Votre choix : ")
        if choix == "1":
            demarrer_surveillance()
        elif choix == "2":
            ajouter_fichier()
        elif choix == "3":
            supprimer_fichier()
        elif choix == "4":
            gestion_droits()
        elif choix == "5":
            verifier_integrite()
        elif choix == "6":
            afficher_logs()
        elif choix == "0":
            print("Arrêt du programme.")
            break
        else:
            print("Choix invalide.")

if __name__ == "__main__":
    if authentification():
        menu()
    else:
        print("Accès refusé.")
def ajouter_fichier():
    chemin = input("Chemin complet du fichier à surveiller : ")

    try:
        with open("../config/watchlist.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"watched_files": []}

    if chemin in data["watched_files"]:
        print("⚠️  Ce fichier est déjà surveillé.")
    else:
        data["watched_files"].append(chemin)
        with open("../config/watchlist.json", "w") as f:
            json.dump(data, f, indent=4)
        print(f"✅ Fichier ajouté à la liste : {chemin}")
def supprimer_fichier():
    chemin = input("Chemin complet du fichier à supprimer de la surveillance : ")

    try:
        with open("../config/watchlist.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ Aucun fichier de surveillance trouvé.")
        return

    if chemin in data["watched_files"]:
        data["watched_files"].remove(chemin)
        with open("../config/watchlist.json", "w") as f:
            json.dump(data, f, indent=4)
        print(f"🗑️ Fichier supprimé de la liste : {chemin}")
    else:
        print("❌ Ce fichier n’est pas dans la liste.")

