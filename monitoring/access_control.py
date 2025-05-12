import os
import stat

def afficher_droits(fichier):
    try:
        st = os.stat(fichier)
        droits = stat.filemode(st.st_mode)
        print(f"\nDroits actuels pour {fichier} : {droits}")
        return droits
    except FileNotFoundError:
        print("❌ Fichier introuvable.")
        return None

def modifier_droits(fichier, nouveaux_droits):
    try:
        mode = int(nouveaux_droits, 8)  # Ex: "755"
        os.chmod(fichier, mode)
        print(f"✅ Droits modifiés avec succès pour {fichier}")
    except Exception as e:
        print(f"❌ Erreur lors de la modification des droits : {e}")
