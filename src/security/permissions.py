import os
import stat
import subprocess

def show_permissions(file_path):
    st = os.stat(file_path)
    permissions = stat.filemode(st.st_mode)
    owner = st.st_uid
    group = st.st_gid
    print(f"🔐 Fichier : {file_path}")
    print(f"📄 Droits : {permissions}")
    print(f"👤 UID : {owner} | 🧑‍🤝‍🧑 GID : {group}")

def modify_permissions(file_path, mode):
    try:
        os.chmod(file_path, int(mode, 8))
        print(f"✅ Permissions modifiées en {mode} pour {file_path}")
    except Exception as e:
        print(f"❌ Erreur : {e}")
