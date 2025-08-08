import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import json
import os
from dotenv import load_dotenv

# Charge les variables d'environnement depuis .env
load_dotenv()

SAVE_FILE = "etat_disponibilite.json"
DISCORD_WEBHOOK_URL = os.getenv("discord_webhook_url")

def send_notification(name, address, url):
    if not DISCORD_WEBHOOK_URL:
        print("⚠️ Pas de webhook Discord configuré.")
        return
    content = f"🏠 **Nouveau logement dispo !**\n**{name}**\n{address}\n🔗 {url}"
    data = {
        "content": content
    }
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    if response.status_code != 204:
        print(f"Erreur en envoyant Discord : {response.status_code} - {response.text}")

def load_previous_status():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_current_status(data):
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)

def check_residences():
    previous_status = load_previous_status()
    current_status = {}

    #3119
    for accommodation_id in tqdm(range(1, 3119)):
        residence_url = f"https://trouverunlogement.lescrous.fr/tools/41/accommodations/{accommodation_id}"
        response = requests.get(residence_url)

        if response.status_code != 200:
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        name_tag = soup.find("h1")
        name = name_tag.text.strip() if name_tag else f"Logement {accommodation_id}"

        address_tag = soup.find("p", class_="fr-text--lead")
        address = address_tag.text.strip() if address_tag else "Adresse introuvable"

        availability_button = soup.find("button", title=True)
        title = availability_button['title'].strip().lower() if availability_button else ""
        is_available = title != "indisponible"

        current_status[str(accommodation_id)] = is_available

        old_status = previous_status.get(str(accommodation_id), None)

        # Si le logement passe de non dispo à dispo
        if is_available and old_status is False:
            print(f"🔔 Nouveau logement dispo ! {name} — {address}")
            send_notification(name, address, residence_url)

    save_current_status(current_status)

if __name__ == "__main__":
    check_residences()
