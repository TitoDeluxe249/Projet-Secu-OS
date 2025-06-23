import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from file_watcher import lancer_surveillance, arreter_surveillance, get_file_properties
from file_watcher import FileEventHandler
import json
import chardet
import os
import threading
import stat
from datetime import datetime

WATCHLIST_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config", "watchlist.json"))

# Fenêtre principale
root = tk.Tk()
root.title("Surveillance de fichiers - Projet Sécu OS")
root.geometry("980x700")

# Frame login
frame_login = tk.Frame(root)
frame_login.pack(expand=True, fill="both")

tk.Label(frame_login, text="Connexion à la plateforme", font=("Helvetica", 14, "bold")).pack(pady=10)

tk.Label(frame_login, text="Nom d'utilisateur").pack()
entry_user = tk.Entry(frame_login)
entry_user.pack()

tk.Label(frame_login, text="Mot de passe").pack()
entry_pass = tk.Entry(frame_login, show="*")
entry_pass.pack()

login_error = tk.Label(frame_login, text="", fg="red")
login_error.pack(pady=5)

# Notebook (les onglets GUI)
notebook = ttk.Notebook(root)
frame_main = tk.Frame(notebook)
frame_logs = tk.Frame(notebook)
frame_props = tk.Frame(notebook)

notebook.add(frame_main, text="Tableau de bord")
notebook.add(frame_logs, text="Logs en direct")
notebook.add(frame_props, text="Propriétés")

# Logs
text_logs = tk.Text(frame_logs, wrap="word", state="disabled")
text_logs.pack(expand=True, fill="both")

status_var = tk.StringVar()
status_var.set("Aucune surveillance active.")
tk.Label(frame_main, textvariable=status_var, fg="blue").pack(pady=5)

watched_path_var = tk.StringVar()
tk.Label(frame_main, textvariable=watched_path_var, fg="gray").pack()

# Variables globales
current_user = None
surveillance_thread = None

def afficher_log_ligne(message):
    text_logs.config(state="normal")
    text_logs.insert("end", message + "\n")
    text_logs.see("end")
    text_logs.config(state="disabled")
    print(f"[GUI] {message}")


def lire_fichier_texte(path):
    encodings = ["utf-8", "utf-16", "utf-8-sig", "latin-1"]
    for enc in encodings:
        try:
            with open(path, "r", encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    return "[Erreur lecture] : Fichier non lisible en texte clair"


def charger_watchlist():
    try:
        with open(WATCHLIST_PATH, "r") as f:
            data = json.load(f)
            return data.get("watched_files", [])
    except:
        return []

def sauvegarder_watchlist(watchlist):
    os.makedirs(os.path.dirname(WATCHLIST_PATH), exist_ok=True)
    with open(WATCHLIST_PATH, "w") as f:
        json.dump({"watched_files": watchlist}, f, indent=4)

# Connexion
def charger_utilisateurs():
    with open("config/users.json", "r") as f:
        return json.load(f)

def verifier_utilisateur(username, password):
    users = charger_utilisateurs()
    for user in users:
        if user["username"] == username and user["password"] == password:
            return user
    return None

def se_connecter_depuis_interface():
    global current_user
    username = entry_user.get()
    password = entry_pass.get()
    user = verifier_utilisateur(username, password)
    if user:
        current_user = user
        afficher_log_ligne(f"🔐 Connecté en tant que {user['username']} (role: {user['role']})")
        frame_login.pack_forget()
        notebook.pack(expand=True, fill="both")
        btn_add.config(state="normal")
        btn_del.config(state="normal")
        btn_start.config(state="normal")
        btn_stop.config(state="normal")
        afficher_fichiers_props()
    else:
        login_error.config(text="❌ Identifiants invalides")

tk.Button(frame_login, text="Connexion", command=se_connecter_depuis_interface).pack(pady=10)

# Boutons
btn_add = tk.Button(frame_main, text="➕ Ajouter un dossier à surveiller", width=40, state="disabled", command=lambda: ajouter_fichier())
btn_add.pack(pady=5)

btn_del = tk.Button(frame_main, text="➖ Supprimer un dossier surveillé", width=40, state="disabled", command=lambda: supprimer_fichier())
btn_del.pack(pady=5)

btn_start = tk.Button(frame_main, text="🟢 Démarrer la surveillance", width=40, state="disabled", command=lambda: demarrer_surveillance())
btn_start.pack(pady=5)

btn_stop = tk.Button(frame_main, text="🔴 Arrêter la surveillance", width=40, state="disabled", command=lambda: arreter_surveillance_gui())
btn_stop.pack(pady=5)

# Fonctions principales
def ajouter_fichier():
    path = filedialog.askdirectory(title="Choisir un dossier à surveiller")
    if path:
        path = os.path.abspath(path)
        lst = charger_watchlist()
        if path not in lst:
            lst.append(path)
            sauvegarder_watchlist(lst)
            afficher_log_ligne(f"✅ Dossier ajouté à la surveillance : {path}")
            watched_path_var.set(f"Chemin surveillé : {path}")
        else:
            messagebox.showinfo("Info", "Ce dossier est déjà surveillé.")

def supprimer_fichier():
    lst = charger_watchlist()
    if not lst:
        messagebox.showinfo("Info", "Aucun fichier à supprimer.")
        return
    win = tk.Toplevel()
    win.title("Supprimer un chemin")
    listbox = tk.Listbox(win, selectmode=tk.SINGLE, width=100)
    listbox.pack(padx=10, pady=10)
    for path in lst:
        listbox.insert(tk.END, path)
    def valider():
        sel = listbox.curselection()
        if sel:
            idx = sel[0]
            chemin = lst.pop(idx)
            sauvegarder_watchlist(lst)
            afficher_log_ligne(f"📉 Dossier retiré de la surveillance : {chemin}")
            watched_path_var.set(f"Chemin surveillé : {lst[-1] if lst else 'Aucun'}")
            win.destroy()
    tk.Button(win, text="Supprimer", command=valider).pack(pady=5)

def demarrer_surveillance():
    global surveillance_thread
    def run():
        try:
            lancer_surveillance(mode="gui", log_callback=afficher_log_ligne, utilisateur=current_user["username"])
            status_var.set("Surveillance active.")
            afficher_log_ligne("🟢 Surveillance active depuis GUI.")
        except Exception as e:
            afficher_log_ligne(f"❌ Erreur : {e}")
    surveillance_thread = threading.Thread(target=run, daemon=True)
    surveillance_thread.start()

def arreter_surveillance_gui():
    try:
        arreter_surveillance()
        status_var.set("Surveillance stoppée.")
        afficher_log_ligne("🟥 Surveillance arrêtée depuis l'interface GUI.")
    except Exception as e:
        afficher_log_ligne(f"❌ Erreur à l'arrêt : {e}")

# Propriétés
def traduire_permissions(perm_str):
    if not perm_str or len(perm_str) != 10:
        return "Inconnu"
    roles = ["Propriétaire", "Groupe", "Autres"]
    droits = {"r": "Lecture", "w": "Écriture", "x": "Exécution", "-": "Aucun"}
    texte = []
    for i, role in enumerate(roles):
        droits_lus = [droits[c] for c in perm_str[1 + i*3:1 + (i+1)*3] if c in droits and c != "-"]
        if not droits_lus:
            droits_lus = ["Aucun"]
        texte.append(f"{role} : {', '.join(droits_lus)}")
    return " | ".join(texte)

def traduire_mode_numerique(octal_str):
    try:
        mode = int(octal_str, 8)
        droits = stat.filemode(mode)
        return traduire_permissions(droits)
    except:
        return "Format invalide"

def afficher_fichiers_props():
    for widget in frame_props.winfo_children():
        widget.destroy()

    chemins = charger_watchlist()
    if not chemins:
        tk.Label(frame_props, text="Aucun chemin surveillé.").pack()
        return

    chemin = chemins[-1]
    try:
        fichiers = os.listdir(chemin)
    except Exception as e:
        tk.Label(frame_props, text=f"Erreur : {e}").pack()
        return

    for fichier in fichiers:
        chemin_fichier = os.path.join(chemin, fichier)
        if os.path.isfile(chemin_fichier):
            row = tk.Frame(frame_props)
            row.pack(fill="x", padx=10, pady=2)
            tk.Label(row, text=fichier, width=40, anchor="w").pack(side="left")

            # === Bouton Information ===
            def creer_afficheur(path):
                def afficher():
                    props = get_file_properties(path)
                    if not props:
                        afficher_log_ligne(f"❌ Impossible d’afficher les propriétés de {path}")
                        return

                    popup = tk.Toplevel()
                    popup.title("Propriétés")
                    popup.geometry("600x550")

                    permissions = props.get('permissions', '?')
                    uid = props.get('uid', '?')
                    gid = props.get('gid', '?')
                    size = props.get('size', '?')

                    tk.Label(popup, text=f"Chemin : {path}", wraplength=580).pack(anchor="w", padx=10)
                    tk.Label(popup, text=f"Droits : {traduire_permissions(permissions)}").pack(anchor="w", padx=10)
                    tk.Label(popup, text=f"UID : {uid} | GID : {gid} | Taille : {size} octets").pack(anchor="w", padx=10)

                    # Zone de contenu
                    tk.Label(popup, text="Contenu du fichier :").pack(anchor="w", padx=10, pady=5)
                    zone_texte = tk.Text(popup, height=10, wrap="word")
                    zone_texte.pack(expand=False, fill="both", padx=10, pady=5)
                    try:
                        contenu = lire_fichier_texte(path)
                        zone_texte.insert("1.0", contenu)
                        zone_texte.config(state="disabled")
                    except Exception as e:
                        zone_texte.insert("1.0", f"[Erreur lecture] : {e}")

                    if current_user and current_user["role"] == "admin":
                        tk.Label(popup, text="Modifier les droits d’accès :").pack(anchor="w", padx=10, pady=5)

                        roles = ["Propriétaire", "Groupe", "Autres"]
                        droits = ["Lecture", "Écriture", "Exécution"]
                        checkboxes = {}

                        for i, role in enumerate(roles):
                            cadre = tk.LabelFrame(popup, text=role, padx=5, pady=5)
                            cadre.pack(anchor="w", padx=15, pady=2)
                            for j, droit in enumerate(droits):
                                var = tk.IntVar()
                                checkboxes[(i, j)] = var
                                tk.Checkbutton(cadre, text=droit, variable=var).grid(row=0, column=j)

                        perm_str = permissions[1:]
                        for i in range(3):
                            triplet = perm_str[i*3:(i+1)*3]
                            checkboxes[(i, 0)].set(1 if triplet[0] == "r" else 0)
                            checkboxes[(i, 1)].set(1 if triplet[1] == "w" else 0)
                            checkboxes[(i, 2)].set(1 if triplet[2] == "x" else 0)

                        def appliquer():
                            try:
                                mode_bits = "-"
                                for i in range(3):
                                    mode = ""
                                    mode += "r" if checkboxes[(i, 0)].get() else "-"
                                    mode += "w" if checkboxes[(i, 1)].get() else "-"
                                    mode += "x" if checkboxes[(i, 2)].get() else "-"
                                    mode_bits += mode
                                rwx_to_oct = lambda c: 4*(c[0] == 'r') + 2*(c[1] == 'w') + 1*(c[2] == 'x')
                                octal = "".join(str(rwx_to_oct(mode_bits[1+i*3:1+(i+1)*3])) for i in range(3))
                                os.chmod(path, int(octal, 8))
                                FileEventHandler.marquer_modifie_depuis_gui(path)
                                afficher_log_ligne(f"[{datetime.now()}] 🔐 {current_user['username']} a modifié les droits de {path} -> {octal}")
                                popup.destroy()
                                afficher_fichiers_props()
                            except Exception as e:
                                messagebox.showerror("Erreur", f"Échec : {e}")

                        tk.Button(popup, text="Appliquer les droits", command=appliquer).pack(pady=5)

                        def supprimer():
                            try:
                                os.remove(path)
                                FileEventHandler.marquer_modifie_depuis_gui(path)
                                afficher_log_ligne(f"[{datetime.now()}] 🗑️ {current_user['username']} a supprimé le fichier {path}")
                                popup.destroy()
                                afficher_fichiers_props()
                            except Exception as e:
                                messagebox.showerror("Erreur", f"Échec de la suppression : {e}")

                        tk.Button(popup, text="Supprimer le fichier", fg="red", command=supprimer).pack(pady=5)

                    tk.Button(popup, text="Fermer", command=popup.destroy).pack(pady=10)

                return afficher

            tk.Button(row, text="Information", command=creer_afficheur(chemin_fichier)).pack(side="right")

            # === Bouton Modifier (accessible à tous les utilisateurs) ===
            def creer_editeur(path):
                def editer():
                    popup = tk.Toplevel()
                    popup.title(f"Modifier - {os.path.basename(path)}")
                    popup.geometry("600x500")

                    text_zone = tk.Text(popup)
                    text_zone.pack(expand=True, fill="both", padx=10, pady=10)

                    try:
                        contenu = lire_fichier_texte(path)
                        text_zone.insert("1.0", contenu)
                    except Exception as e:
                        text_zone.insert("1.0", f"[Erreur lecture] : {e}")

                    def sauvegarder():
                        try:
                            with open(path, "w", encoding="utf-8") as f:
                                f.write(text_zone.get("1.0", tk.END).strip())
                            FileEventHandler.marquer_modifie_depuis_gui(path)
                            afficher_log_ligne(f"[{datetime.now()}] ✏️ {current_user['username']} a modifié le contenu de {path}")
                            popup.destroy()
                        except Exception as e:
                            messagebox.showerror("Erreur", f"Impossible de sauvegarder : {e}")

                    tk.Button(popup, text="Sauvegarder", command=sauvegarder).pack(pady=5)
                    tk.Button(popup, text="Fermer", command=popup.destroy).pack()
                return editer

            tk.Button(row, text="Modifier", command=creer_editeur(chemin_fichier)).pack(side="right")
                # Bouton : Créer un nouveau fichier (accessible à tous)
    def creer_nouveau_fichier():
        popup = tk.Toplevel()
        popup.title("Créer un nouveau fichier")
        popup.geometry("500x400")

        tk.Label(popup, text="Nom du fichier (ex: notes.txt)").pack(pady=5)
        entry_nom = tk.Entry(popup)
        entry_nom.pack(pady=5)

        tk.Label(popup, text="Contenu initial :").pack(pady=5)
        text_contenu = tk.Text(popup, height=10)
        text_contenu.pack(expand=True, fill="both", padx=10, pady=5)

        def creer():
            nom = entry_nom.get().strip()
            contenu = text_contenu.get("1.0", tk.END).strip()
            if not nom:
                messagebox.showerror("Erreur", "⚠️ Nom de fichier requis.")
                return

            chemin_final = os.path.join(chemin, nom)
            try:
                with open(chemin_final, "w", encoding="utf-8") as f:
                    f.write(contenu)
                FileEventHandler.marquer_modifie_depuis_gui(chemin_final)
                afficher_log_ligne(f"[{datetime.now()}] 🆕 {current_user['username']} a créé le fichier {chemin_final}")
                popup.destroy()
                afficher_fichiers_props()
            except Exception as e:
                messagebox.showerror("Erreur", f"Échec de création : {e}")

        tk.Button(popup, text="Créer", command=creer).pack(pady=5)
        tk.Button(popup, text="Annuler", command=popup.destroy).pack()

    tk.Button(frame_props, text="📝 Créer un nouveau fichier", command=creer_nouveau_fichier).pack(pady=10)


             

# Lancer l'appli
root.mainloop()
