import json
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi.testclient import TestClient

from app.main import app


# Charge les variables du fichier .env
load_dotenv()

# Crée un client de test pour appeler l'API sans lancer uvicorn
client = TestClient(app)

# Récupère la clé API depuis le fichier .env
API_KEY = os.getenv("API_KEY")

# Chemin vers le fichier JSON de test
DATA_PATH = Path("data/api_data.json")


def recuperer_premier_individu():
    """Lit le fichier JSON et retourne le premier individu."""
    with DATA_PATH.open("r", encoding="utf-8") as file:
        individuals = json.load(file)

    return individuals[0]


def test_accueil_api():
    """Vérifie que la route GET / fonctionne."""
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "API OK"


def test_prediction_sans_cle_api():
    """Vérifie que /predict refuse une requête sans clé API."""
    individual = recuperer_premier_individu()

    response = client.post("/predict", json=individual)

    assert response.status_code == 401


def test_prediction_avec_cle_api():
    """Vérifie que /predict retourne une prédiction avec une clé API valide."""
    individual = recuperer_premier_individu()

    response = client.post(
        "/predict",
        json=individual,
        headers={"mot-passe-api": API_KEY}
    )

    assert response.status_code == 200

    data = response.json()

    assert "prediction" in data
    assert "probabilite_depart" in data
    assert "resultat" in data


def test_resultats_avec_cle_api():
    """Vérifie que /results retourne une liste avec une clé API valide."""
    response = client.get(
        "/results",
        headers={"mot-passe-api": API_KEY}
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)