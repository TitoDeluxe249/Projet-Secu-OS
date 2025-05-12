import tkinter as tk
from tkinter import messagebox

def demarrer_gui():
    root = tk.Tk()
    root.title("Surveillance de Fichiers")
    root.geometry("400x400")

    tk.Label(root, text="Interface de Surveillance", font=("Helvetica", 16)).pack(pady=10)

    tk.Button(root, text="Démarrer la surveillance", command=demarrer_surveillance).pack(pady=5)
    tk.Button(root, text="Ajouter un fichier", command=ajouter_fichier).pack(pady=5)
    tk.Button(root, text="Supprimer un fichier", command=supprimer_fichier).pack(pady=5)
    tk.Button(root, text="Gérer les droits", command=gestion_droits).pack(pady=5)
    tk.Button(root, text="Vérifier l'intégrité", command=verifier_integrite).pack(pady=5)
    tk.Button(root, text="Afficher les logs", command=afficher_logs).pack(pady=5)

    root.mainloop()
def fenetre_login():
    from tkinter.simpledialog import askstring
    import hashlib

    password = askstring("Connexion", "Entrez le mot de passe :", show="*")
    if not password:
        return False

    hash_saisi = hashlib.sha256(password.encode()).hexdigest()
    with open("config/password.hash", "r") as f:
        hash_attendu = f.read().strip()
    return hash_saisi == hash_attendu
if __name__ == "__main__":
    if fenetre_login():
        demarrer_gui()
    else:
        print("Mot de passe incorrect. Fermeture.")
