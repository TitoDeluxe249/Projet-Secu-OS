import os

class ProprieteSurveillant:
    def __init__(self, fichiers, log_callback):
        self.fichiers = fichiers
        self.log_callback = log_callback
        self.etats = self.sauvegarder_etats()

    def sauvegarder_etats(self):
        etats = {}
        for f in self.fichiers:
            if os.path.exists(f):
                st = os.stat(f)
                etats[f] = (st.st_mode, st.st_uid, st.st_gid, st.st_mtime)
        return etats

    def verifier_modifications(self):
        for f in self.fichiers:
            if os.path.exists(f):
                st = os.stat(f)
                actuel = (st.st_mode, st.st_uid, st.st_gid, st.st_mtime)
                if f in self.etats and self.etats[f] != actuel:
                    self.log_callback(f"🔐 Changement détecté sur {f}")
                    self.etats[f] = actuel
