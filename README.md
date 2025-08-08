# Surveillance de disponibilités logements CROUS

Ce script Python permet de surveiller les nouvelles disponibilités de logements sur le site [trouverunlogement.lescrous.fr](https://trouverunlogement.lescrous.fr) et d’envoyer une notification Discord dès qu’un nouveau logement devient disponible.

---

## Fonctionnalités

- Scrape les pages de résultats de logements CROUS.
- Garde en mémoire l’état précédent des disponibilités.
- Détecte les nouveaux logements disponibles.
- Met à jour les logements qui ne sont plus disponibles.
- Envoie une notification via un webhook Discord à chaque nouveau logement disponible.
- Sauvegarde l’état dans un fichier JSON local (`etat_disponibilite.json`).

---

## Prérequis

- Python 3.7+
- Clé Discord webhook (URL) pour recevoir les notifications.

---

## Installation

1. Cloner ce dépôt :
    ```bash
    git clone https://github.com/ton-utilisateur/ton-repo.git
    cd ton-repo
    ```

2. Installer les dépendances :
    ```bash
    pip install -r requirements.txt
    ```

3. Créer un fichier `.env` à la racine avec ta variable d’environnement Discord webhook :
    ```
    discord_webhook_url=https://discord.com/api/webhooks/XXX/YYY
    ```

---

## Usage

Lancer le script :
```bash
python script.py
