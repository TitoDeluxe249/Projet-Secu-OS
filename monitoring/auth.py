def authentification():
    import getpass, hashlib
    mdp_saisi = getpass.getpass("Mot de passe : ")
    hash_saisi = hashlib.sha256(mdp_saisi.encode()).hexdigest()
    with open("config/password.hash", "r") as f:
        hash_attendu = f.read().strip()
    return hash_saisi == hash_attendu
