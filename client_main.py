# client_main.py

import json
from pathlib import Path

import requests


# Adresse de ton endpoint FastAPI
api_url = "http://127.0.0.1:8000/predict"

# Chemin vers ton fichier JSON
json_file = Path("data/api_data.json")


# On ouvre le fichier JSON
with json_file.open("r", encoding="utf-8") as file:
    individuals = json.load(file)

# Ici, individuals contient ta liste de 10 dictionnaires
print(f"{len(individuals)} individu(s) trouvé(s)\n")


# On parcourt la liste des individus
# enumerate sert seulement à afficher 1, 2, 3...
for index, individual in enumerate(individuals, start=1):
    # On envoie un individu à l'API
    response = requests.post(api_url, json=individual)

    # On transforme la réponse JSON de l'API en dictionnaire Python
    result = response.json()

    print(f"--- Individu {index} ---")
    print("Input :")
    print(json.dumps(individual, ensure_ascii=False, indent=2))

    print("Output :")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print()