from pathlib import Path

import joblib
import pandas as pd
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from BDD.connexion import get_db
from BDD.models import InputData, PredictionResult

app = FastAPI(title="API prédiction employés")

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model.joblib"
model = joblib.load(MODEL_PATH)


class EmployeeDataInput(BaseModel):
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


class PredictionResponse(BaseModel):
    prediction: int
    probabilite_depart: float
    resultat: str


@app.get("/")
def read_root():
    return {"message": "API OK"}


@app.post("/predict", response_model=PredictionResponse)
def predict(data: EmployeeDataInput, db: Session = Depends(get_db)) -> PredictionResponse:
    try:
        data_dict = data.model_dump()

        input_record = InputData(**data_dict)
        db.add(input_record)
        db.commit()
        db.refresh(input_record)

        input_df = pd.DataFrame([data_dict])

        prediction = int(model.predict(input_df)[0])
        probabilite_depart = float(model.predict_proba(input_df)[0][1])
        resultat = "Départ" if prediction == 1 else "Reste"

        prediction_record = PredictionResult(
            input_id=input_record.id,
            predi=prediction,
            proba=probabilite_depart,
            resultat=resultat,
        )
        db.add(prediction_record)
        db.commit()
        db.refresh(prediction_record)

        return PredictionResponse(
            prediction=prediction,
            probabilite_depart=round(probabilite_depart, 2),
            resultat=resultat,
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")
    


@app.get("/results")
def get_results(db: Session = Depends(get_db)) -> list[dict]:
    # Cette route sert à voir l'historique input + output
    rows = (
        db.query(InputData, PredictionResult)
        .join(PredictionResult, InputData.id == PredictionResult.input_id)
        .order_by(InputData.id)
        .all()
    )

    results = []

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