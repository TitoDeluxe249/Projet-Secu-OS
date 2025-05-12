import hashlib
import os

# Assure-toi que le dossier "config/" existe
os.makedirs("../config", exist_ok=True)  # le .. remonte d'un niveau depuis /monitoring/

# Demande le mot de passe
mot_de_passe = input("Choisir un mot de passe admin : ")
hash_mdp = hashlib.sha256(mot_de_passe.encode()).hexdigest()

# Enregistre le hash dans le fichier
with open("../config/password.hash", "w") as f:
    f.write(hash_mdp)

print("✅ Mot de passe enregistré avec succès.")
