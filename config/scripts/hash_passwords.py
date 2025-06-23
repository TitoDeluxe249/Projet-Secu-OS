import json
import bcrypt

users_path = "config/users.json"

# Charger les utilisateurs
with open(users_path, "r") as f:
    users = json.load(f)

# Hasher les mots de passe
for user in users:
    password = user["password"].encode("utf-8")
    hashed = bcrypt.hashpw(password, bcrypt.gensalt())
    user["password"] = hashed.decode("utf-8")

# Sauvegarder le fichier
with open(users_path, "w") as f:
    json.dump(users, f, indent=2)

print("Mots de passe hashés avec succès.")
