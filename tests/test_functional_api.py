import json
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

from app.main import app
from BDD.connexion import SessionLocal
from BDD.models import InputData, PredictionResult


###############################################
# Configuration des tests
###############################################

# Charge les variables d'environnement depuis le fichier .env
load_dotenv()

# Crée un client de test FastAPI.
# Cela permet d'appeler les endpoints sans lancer uvicorn.
client = TestClient(app)

# Récupère la clé API depuis les variables d'environnement.
API_KEY = os.getenv("API_KEY")

# Chemin du fichier contenant des exemples d'individus à tester.
DATA_PATH = Path("data/api_data.json")


###############################################
# Fonction utilitaire
###############################################

def recuperer_premier_individu():
    """
    Lit le fichier data/api_data.json
    et retourne le premier individu.

    Cette fonction évite de dupliquer le chargement JSON
    dans plusieurs tests.
    """
    with DATA_PATH.open("r", encoding="utf-8") as file:
        individuals = json.load(file)

    return individuals[0]


###############################################
# Test route accueil GET /
###############################################

def test_accueil_api():
    """
    Vérifie que la route GET / fonctionne correctement.

    Résultat attendu :
    - status code 200
    - message de confirmation "API OK"
    """
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "API OK"


###############################################
# Test sécurité : appel sans clé API
###############################################

def test_prediction_sans_cle_api():
    """
    Vérifie que l'endpoint /predict refuse une requête
    lorsque la clé API est absente.

    Résultat attendu :
    - status code 401 Unauthorized
    """
    individual = recuperer_premier_individu()

    response = client.post("/predict", json=individual)

    assert response.status_code == 401


###############################################
# Test fonctionnel : prédiction avec clé API
###############################################

def test_prediction_avec_cle_api():
    """
    Vérifie que l'endpoint /predict fonctionne
    lorsqu'une clé API valide est fournie.

    Résultat attendu :
    - status code 200
    - présence des champs prediction, probabilite_depart et resultat
    """
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


###############################################
# Test fonctionnel : consultation des résultats
###############################################

def test_resultats_avec_cle_api():
    """
    Vérifie que l'endpoint /results retourne bien une liste
    lorsque la clé API est valide.

    Résultat attendu :
    - status code 200
    - réponse au format liste
    """
    response = client.get(
        "/results",
        headers={"mot-passe-api": API_KEY}
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


###############################################
# Test invalide : valeur manquante
###############################################

def test_prediction_donnee_invalide():
    """
    Vérifie que l'API refuse une requête incomplète.

    Ici, plusieurs champs obligatoires sont volontairement absents.
    FastAPI/Pydantic doit donc retourner une erreur de validation.

    Résultat attendu :
    - status code 422 Unprocessable Entity
    """
    response = client.post(
        "/predict",
        headers={"mot-passe-api": API_KEY},
        json={
            "age": 35,
            "genre": "Homme"
        }
    )

    assert response.status_code == 422


###############################################
# Test base de données : insertion après prédiction
###############################################

def test_prediction_insere_dans_la_base_de_donnees():
    """
    Vérifie qu'un appel valide à /predict insère bien
    les données dans PostgreSQL.

    Le test vérifie :
    - qu'une ligne est ajoutée dans la table InputData
    - qu'une ligne est ajoutée dans la table PredictionResult
    - que le champ created_at est bien renseigné

    Si la base n'est pas disponible, le test est ignoré.
    """

    # Si aucune session PostgreSQL n'est disponible,
    # on ignore ce test pour éviter un échec inutile.
    if SessionLocal is None:
        pytest.skip("Base de données non disponible")

    # Payload complet simulant un employé envoyé à l'API.
    payload = {
        "age": 37,
        "genre": "M",
        "revenu_mensuel": 2090,
        "statut_marital": "Célibataire",
        "poste": "Consultant",
        "nombre_experiences_precedentes": 6,
        "annee_experience_totale": 7,
        "annees_dans_l_entreprise": 0,
        "annees_dans_le_poste_actuel": 0,
        "satisfaction_employee_environnement": 4,
        "note_evaluation_precedente": 2,
        "satisfaction_employee_nature_travail": 3,
        "satisfaction_employee_equipe": 2,
        "satisfaction_employee_equilibre_pro_perso": 3,
        "heure_supplementaires": "oui",
        "augmentation_precedente_salaire_pct": 0.15,
        "nombre_participation_pee": 0,
        "nb_formations_suivies": 3,
        "distance_domicile_travail": 2,
        "niveau_education": 2,
        "domaine_etude": "Autre",
        "frequence_deplacement": "Occasionnel",
        "annees_depuis_la_derniere_promotion": 0,
        "annes_sous_responsable_actuel": 0,
        "ratio_salaire_poste": 0.6456256776,
        "ratio_stagnation": 0.0,
        "poste_penibilite_voyage": "Consultant_Occasionnel",
        "attente_promotion_pure": 0,
        "ratio_fidelite_manager": 0.0
    }

    # Ouverture d'une session directe avec PostgreSQL.
    db = SessionLocal()

    try:
        # Comptage des lignes avant l'appel API.
        nb_inputs_avant = db.query(InputData).count()
        nb_predictions_avant = db.query(PredictionResult).count()

        # Appel de l'endpoint /predict.
        response = client.post(
            "/predict",
            headers={"mot-passe-api": API_KEY},
            json=payload
        )

        # Vérifie que l'API répond correctement.
        assert response.status_code == 200

        # Comptage des lignes après l'appel API.
        nb_inputs_apres = db.query(InputData).count()
        nb_predictions_apres = db.query(PredictionResult).count()

        # Vérifie qu'une nouvelle entrée a été ajoutée dans chaque table.
        assert nb_inputs_apres == nb_inputs_avant + 1
        assert nb_predictions_apres == nb_predictions_avant + 1

        # Récupère la dernière entrée insérée.
        derniere_entree = db.query(InputData).order_by(InputData.id.desc()).first()

        # Vérifie que l'entrée existe et que la date de création est renseignée.
        assert derniere_entree is not None
        assert derniere_entree.created_at is not None

    finally:
        # Fermeture de la session PostgreSQL.
        db.close()