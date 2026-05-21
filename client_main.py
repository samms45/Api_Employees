# client_main.py

import json
from pathlib import Path

import os
from dotenv import load_dotenv

load_dotenv()

import requests


api_url = "http://127.0.0.1:8000/predict"
json_file = Path("data/api_data.json")

headers = {
    "mot-passe-api": os.getenv("API_KEY")
}


with json_file.open("r", encoding="utf-8") as file:
    individuals = json.load(file)

print(f"{len(individuals)} individu(s) trouvé(s)\n")

for index, individual in enumerate(individuals, start=1):
    response = requests.post(
        api_url,
        json=individual,
        headers=headers
    )

    result = response.json()

    print(f"--- Individu {index} ---")
    print("Input :")
    print(json.dumps(individual, ensure_ascii=False, indent=2))

    print("Output :")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print()