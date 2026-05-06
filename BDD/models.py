# BDD/models.py

from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class InputData(Base):
    __tablename__ = "inputs"

    id = Column(Integer, primary_key=True, index=True)

    age = Column(Integer, nullable=False)
    genre = Column(String, nullable=False)
    revenu_mensuel = Column(Integer, nullable=False)
    statut_marital = Column(String, nullable=False)
    poste = Column(String, nullable=False)
    nombre_experiences_precedentes = Column(Integer, nullable=False)
    annee_experience_totale = Column(Integer, nullable=False)
    annees_dans_l_entreprise = Column(Integer, nullable=False)
    annees_dans_le_poste_actuel = Column(Integer, nullable=False)
    satisfaction_employee_environnement = Column(Integer, nullable=False)
    note_evaluation_precedente = Column(Integer, nullable=False)
    satisfaction_employee_nature_travail = Column(Integer, nullable=False)
    satisfaction_employee_equipe = Column(Integer, nullable=False)
    satisfaction_employee_equilibre_pro_perso = Column(Integer, nullable=False)
    heure_supplementaires = Column(String, nullable=False)
    augmentation_precedente_salaire_pct = Column(Float, nullable=False)
    nombre_participation_pee = Column(Integer, nullable=False)
    nb_formations_suivies = Column(Integer, nullable=False)
    distance_domicile_travail = Column(Integer, nullable=False)
    niveau_education = Column(Integer, nullable=False)
    domaine_etude = Column(String, nullable=False)
    frequence_deplacement = Column(String, nullable=False)
    annees_depuis_la_derniere_promotion = Column(Integer, nullable=False)
    annes_sous_responsable_actuel = Column(Integer, nullable=False)
    ratio_salaire_poste = Column(Float, nullable=False)
    ratio_stagnation = Column(Float, nullable=False)
    poste_penibilite_voyage = Column(String, nullable=False)
    attente_promotion_pure = Column(Integer, nullable=False)
    ratio_fidelite_manager = Column(Float, nullable=False)


class PredictionResult(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    input_id = Column(Integer, ForeignKey("inputs.id"), unique=True, nullable=False)
    predi = Column(Integer, nullable=False)
    proba = Column(Float, nullable=False)
    resultat = Column(String, nullable=False)


InputData.prediction = relationship(
    "PredictionResult",
    back_populates="parent",
    uselist=False,
)

PredictionResult.parent = relationship(
    "InputData",
    back_populates="prediction",
)


