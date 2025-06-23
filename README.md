# 🔐 Projet Secu-OS – Surveillance et Contrôle des Fichiers

## 🧠 Description

Secu-OS est une application Python de surveillance de fichiers, conçue pour observer en temps réel :
- Les modifications de fichiers
- Les suppressions
- Les changements de permissions ou de propriétaires
- Les accès non autorisés

Le projet propose :
- Une **interface graphique (GUI)** intuitive pour les utilisateurs
- Une **interface en ligne de commande (CLI)** pour les administrateurs ou utilisateurs avancés
- Un système de **journalisation détaillée** (`logs/events.log`)
- Une **gestion des utilisateurs** avec rôles (`admin`, `user1`, etc.)

---

## 🚀 Fonctionnalités principales

- 📁 Surveillance d’un dossier spécifique
- 📝 Modification et suppression des fichiers avec logs
- 👮 Attribution de droits d’accès par utilisateur
- 📄 Visualisation des métadonnées (UID, GID, permissions)
- ✏️ Création et modification de fichiers directement via l’interface
- 📊 Interface CLI avec interactions simples

---

## 📦 Installation

### Prérequis

- Python 3.10+
- pip (gestionnaire de paquets Python)

### Installation rapide

```bash
git clone https://github.com/ton-pseudo/projet-secu-os.git
cd projet-secu-os
pip install -r requirements.txt
```
### Créer un environnement virtuel :

```bash
python -m venv venv
```

### L’activer :

```bash
.\venv\Scripts\activate
```
