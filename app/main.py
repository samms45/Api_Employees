from pathlib import Path
import os
import urllib.request

import joblib
import pandas as pd
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from BDD.connexion import get_db
from BDD.models import InputData, PredictionResult


###############################################
# Configuration générale
###############################################

# Charge les variables d'environnement depuis le fichier .env
load_dotenv()

# Création de l'application FastAPI
app = FastAPI(title="API prédiction employés")

# Récupération de la clé API depuis les variables d'environnement
API_KEY = os.getenv("API_KEY")

# Vérifie si PostgreSQL doit être utilisé
# true  -> utilisation de PostgreSQL en local
# false -> désactivation de PostgreSQL sur Hugging Face
USE_DATABASE = os.getenv("USE_DATABASE", "true").lower() == "true"


###############################################
# Chargement du modèle Machine Learning
###############################################

# Chemin racine du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# Chemin local du modèle
MODEL_PATH = BASE_DIR / "models" / "model.joblib"

# Si le modèle existe en local, on le charge directement
if MODEL_PATH.exists():
    model = joblib.load(MODEL_PATH)

# Sinon, on le télécharge depuis GitHub
# Cas utilisé notamment lors du déploiement Hugging Face
else:
    MODEL_URL = "https://github.com/samms45/Api_Employees/raw/dev/models/model.joblib"

    # Téléchargement du modèle
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)

    # Chargement du modèle après téléchargement
    model = joblib.load(MODEL_PATH)


###############################################
# Sécurité API Key
###############################################

def verify_api_key(mot_passe_api: str = Header(None)):
    """
    Vérifie que la requête contient la bonne clé API.

    La clé est attendue dans le header HTTP :
    mot-passe-api

    Si la clé est absente ou incorrecte,
    l'API retourne une erreur 401.
    """
    if mot_passe_api != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Clé API invalide ou manquante"
        )

    return mot_passe_api


###############################################
# Gestion optionnelle de PostgreSQL
###############################################

def get_database():
    """
    Fournit une session PostgreSQL à FastAPI.

    En local :
    - PostgreSQL est activé avec USE_DATABASE=true.

    Sur Hugging Face :
    - PostgreSQL peut être désactivé avec USE_DATABASE=false.
    """
    if not USE_DATABASE:
        yield None
    else:
        yield from get_db()


###############################################
# Schéma Pydantic des données entrantes
###############################################

class EmployeeDataInput(BaseModel):
    """
    Schéma des données attendues par l'endpoint /predict.

    Pydantic vérifie automatiquement :
    - la présence des champs obligatoires
    - les types attendus
    - la structure de la requête JSON
    """

    age: int
    genre: str
    revenu_mensuel: int
    statut_marital: str
    poste: str
    nombre_experiences_precedentes: int
    annee_experience_totale: int
    annees_dans_l_entreprise: int
    annees_dans_le_poste_actuel: int
    satisfaction_employee_environnement: int
    note_evaluation_precedente: int
    satisfaction_employee_nature_travail: int
    satisfaction_employee_equipe: int
    satisfaction_employee_equilibre_pro_perso: int
    heure_supplementaires: str
    augmentation_precedente_salaire_pct: float
    nombre_participation_pee: int
    nb_formations_suivies: int
    distance_domicile_travail: int
    niveau_education: int
    domaine_etude: str
    frequence_deplacement: str
    annees_depuis_la_derniere_promotion: int
    annes_sous_responsable_actuel: int
    ratio_salaire_poste: float
    ratio_stagnation: float
    poste_penibilite_voyage: str
    attente_promotion_pure: int
    ratio_fidelite_manager: float


###############################################
# Schéma Pydantic de la réponse API
###############################################

class PredictionResponse(BaseModel):
    """
    Structure de la réponse retournée par l'API.
    """

    prediction: int
    probabilite_depart: float
    resultat: str


###############################################
# Route accueil
###############################################

@app.get("/")
def read_root():
    """
    Route simple permettant de vérifier que l'API fonctionne.
    """
    return {"message": "API OK"}


###############################################
# Route prédiction
###############################################

@app.post("/predict", response_model=PredictionResponse)
def predict(
    data: EmployeeDataInput,
    db: Session = Depends(get_database),
    api_key: str = Depends(verify_api_key)
) -> PredictionResponse:
    """
    Endpoint principal de prédiction.

    Étapes :
    1. reçoit les données employé
    2. valide les données avec Pydantic
    3. transforme les données en DataFrame pandas
    4. envoie les données au modèle ML
    5. retourne la prédiction
    6. enregistre les inputs/outputs en BDD si PostgreSQL est activé
    """
    try:
        # Conversion du schéma Pydantic en dictionnaire Python
        data_dict = data.model_dump()

        # Transformation en DataFrame pour le modèle ML
        input_df = pd.DataFrame([data_dict])

        # Prédiction du modèle
        prediction = int(model.predict(input_df)[0])

        # Probabilité de départ
        probabilite_depart = float(model.predict_proba(input_df)[0][1])

        # Interprétation textuelle du résultat
        resultat = "Départ" if prediction == 1 else "Reste"

        # Enregistrement en base uniquement si PostgreSQL est activé
        if USE_DATABASE and db is not None:
            # Enregistrement des données d'entrée
            input_record = InputData(**data_dict)
            db.add(input_record)
            db.commit()
            db.refresh(input_record)

            # Enregistrement du résultat de prédiction
            prediction_record = PredictionResult(
                input_id=input_record.id,
                predi=prediction,
                proba=probabilite_depart,
                resultat=resultat,
            )
            db.add(prediction_record)
            db.commit()

        # Réponse retournée à l'utilisateur
        return PredictionResponse(
            prediction=prediction,
            probabilite_depart=round(probabilite_depart, 2),
            resultat=resultat,
        )

    except Exception as e:
        # Annule les changements en base en cas d'erreur
        if USE_DATABASE and db is not None:
            db.rollback()

        # Affiche l'erreur dans les logs serveur
        print("ERREUR DETAILLEE :", e)

        # Retourne une erreur HTTP 500
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")


###############################################
# Route historique des résultats
###############################################

@app.get("/results")
def get_results(
    db: Session = Depends(get_database),
    api_key: str = Depends(verify_api_key)
) -> list[dict]:
    """
    Retourne l'historique des prédictions enregistrées en base.

    Cette route fonctionne uniquement lorsque PostgreSQL est activé.
    Sur Hugging Face, elle retourne une erreur 503 car la BDD est désactivée.
    """

    # Si PostgreSQL est désactivé
    if not USE_DATABASE or db is None:
        raise HTTPException(
            status_code=503,
            detail="Base de données désactivée dans cet environnement"
        )

    # Jointure entre les inputs et les prédictions
    rows = (
        db.query(InputData, PredictionResult)
        .join(PredictionResult, InputData.id == PredictionResult.input_id)
        .order_by(InputData.id)
        .all()
    )

    results = []

    # Construction d'une réponse lisible en JSON
    for input_row, prediction_row in rows:
        results.append(
            {
                "input_id": input_row.id,
                "age": input_row.age,
                "genre": input_row.genre,
                "poste": input_row.poste,
                "revenu_mensuel": input_row.revenu_mensuel,
                "prediction": prediction_row.predi,
                "probabilite_depart": prediction_row.proba,
                "resultat": prediction_row.resultat,
            }
        )

    return results