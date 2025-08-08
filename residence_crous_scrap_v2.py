import requests
from bs4 import BeautifulSoup
import math
import json
import os
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

SAVE_FILE = "etat_disponibilite.json"
DISCORD_WEBHOOK_URL = os.getenv("discord_webhook_url")

def send_notification(nom, adresse, url):
    if not DISCORD_WEBHOOK_URL:
        print("⚠️ Pas de webhook Discord configuré.")
        return
    content = f"🏠 **Nouveau logement dispo !**\n**{nom}**\n{adresse}\n🔗 {url}"
    data = {"content": content}
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    if response.status_code != 204:
        print(f"Erreur en envoyant Discord : {response.status_code} - {response.text}")

def load_previous_status():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_current_status(data):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_total_logements():
    url = "https://trouverunlogement.lescrous.fr/tools/41/search?page=1"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Erreur récupération page 1 : {response.status_code}")
        return 0
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, "html.parser")

    h2_tag = soup.find("h2", class_="SearchResults-mobile svelte-8mr8g")
    if not h2_tag:
        print("Nombre total de logements introuvable.")
        return 0
    
    text = h2_tag.text.strip()
    print(f"Texte récupéré dans h2 : '{text}'")

    import re
    match = re.search(r"(\d+)\s+logements trouvés", text)
    if match:
        return int(match.group(1))
    else:
        print("Format inattendu du texte du nombre de logements.")
        return 0

def parse_page(page_num):
    url = f"https://trouverunlogement.lescrous.fr/tools/41/search?page={page_num}"
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, "html.parser")

    logements = []

    # Trouve tous les <li> contenant les logements
    li_logements = soup.find_all("li", class_="fr-col-12")
    for li in li_logements:
        # Nom + lien
        h3 = li.find("h3", class_="fr-card__title")
        if not h3:
            continue
        a_tag = h3.find("a")
        if not a_tag:
            continue
        nom = a_tag.text.strip()
        lien = "https://trouverunlogement.lescrous.fr" + a_tag['href']

        # Adresse
        adresse_tag = li.find("p", class_="fr-card__desc")
        adresse = adresse_tag.text.strip() if adresse_tag else ""

        # Prix (dans <p class="fr-badge">)
        prix_tag = li.find("p", class_="fr-badge")
        prix = prix_tag.text.strip() if prix_tag else ""

        # Surface (dans <p class="fr-card__detail"> contenant "m²")
        surface = ""
        for detail in li.find_all("p", class_="fr-card__detail"):
            if "m²" in detail.text:
                surface = detail.text.strip()
                break

        # Type (ex: "Individuel")
        type_logement = ""
        for detail in li.find_all("p", class_="fr-card__detail"):
            # Le type a une classe spéciale fr-icon-group-fill
            if "fr-icon-group-fill" in detail.get("class", []):
                type_logement = detail.text.strip()
                break

        # **IMPORTANT : Pas d'info 'available' récupérée, on suppose que tous sont disponibles**
        # On peut imaginer ajouter un test s'il y a une indication de dispo dans le li (ex: un badge)
        
        logements.append({
            "nom": nom,
            "url": lien,
            "adresse": adresse,
            "prix": prix,
            "surface": surface,
            "type": type_logement,
            "available": True  # On considère dispo par défaut
        })

    return logements

def main():
    previous_status = load_previous_status()
    current_status = {}  # on va reconstruire à partir de zéro

    total_logements = get_total_logements()
    if total_logements == 0:
        print("Abandon car pas de logements détectés.")
        return

    pages = math.ceil(total_logements / 24)
    print(f"Nombre total de logements : {total_logements}, sur {pages} pages.")

    logements_ids_actuels = set()

    for page_num in tqdm(range(1, pages + 1)):
        logements = parse_page(page_num)
        for log in logements:
            logement_id = log["url"].split("/")[-1] if log["url"] else log["nom"]
            new_status = log["available"]

            logements_ids_actuels.add(logement_id)
            old_status = previous_status.get(logement_id, False)

            current_status[logement_id] = new_status

            # Notification uniquement si dispo nouvelle
            if new_status and old_status is False:
                print(f"🔔 Nouveau logement dispo ! {log['nom']} — {log['adresse']}")
                if log["url"]:
                    send_notification(log["nom"], log["adresse"], log["url"])

    # Maintenant on gère ceux qui ne sont plus présents : on met à False si avant ils étaient True
    for logement_id, old_status in previous_status.items():
        if logement_id not in logements_ids_actuels:
            if old_status is True:
                print(f"⚠️ Logement plus dispo (absent) : {logement_id}")
            current_status[logement_id] = False

    save_current_status(current_status)

if __name__ == "__main__":
    main()
