import hashlib
import os

def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        print(f"❌ Fichier introuvable : {file_path}")
        return None

def verify_integrity(file_path, original_hash):
    current_hash = calculate_sha256(file_path)
    if current_hash == original_hash:
        print(f"✅ Intégrité confirmée pour {file_path}")
    else:
        print(f"⚠️ Intégrité compromise pour {file_path}")
        print(f"🔸 Attendu : {original_hash}")
        print(f"🔹 Actuel : {current_hash}")
