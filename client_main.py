# client_main.py

###############################################
# Imports
###############################################

# json :
# permet de lire et afficher des données au format JSON
import json

# Path :
# permet de gérer proprement les chemins de fichiers
from pathlib import Path

# os :
# permet de récupérer les variables d'environnement
import os

# load_dotenv :
# permet de charger les variables du fichier .env
from dotenv import load_dotenv

# requests :
# permet d'envoyer des requêtes HTTP vers l'API
import requests


###############################################
# Chargement des variables d'environnement
###############################################

# Charge le fichier .env local
load_dotenv()


###############################################
# Configuration du client API
###############################################

# URL locale de l'endpoint /predict.
# L'API doit être lancée avant d'exécuter ce script :
# uv run uvicorn app.main:app --reload
api_url = "http://127.0.0.1:8000/predict"

# Chemin vers le fichier JSON contenant plusieurs individus à tester
json_file = Path("data/api_data.json")

# Header contenant la clé API.
# La vraie clé est récupérée depuis .env pour éviter de l'écrire en dur dans le code.
headers = {
    "mot-passe-api": os.getenv("API_KEY")
}


###############################################
# Chargement des données de test
###############################################

# Lecture du fichier data/api_data.json
with json_file.open("r", encoding="utf-8") as file:
    individuals = json.load(file)

# Affiche le nombre d'individus trouvés dans le fichier JSON
print(f"{len(individuals)} individu(s) trouvé(s)\n")


###############################################
# Envoi automatique des requêtes à l'API
###############################################

# Pour chaque individu du fichier JSON :
# - envoie une requête POST vers /predict
# - récupère la réponse JSON
# - affiche l'input et l'output
for index, individual in enumerate(individuals, start=1):
    response = requests.post(
        api_url,
        json=individual,
        headers=headers
    )

    # Conversion de la réponse HTTP en dictionnaire Python
    result = response.json()

    # Affichage lisible du résultat
    print(f"--- Individu {index} ---")

    print("Input :")
    print(json.dumps(individual, ensure_ascii=False, indent=2))

    print("Output :")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    print()