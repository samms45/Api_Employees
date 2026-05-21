# BDD/models.py

###############################################
# Imports SQLAlchemy
###############################################

# Column :
# permet de définir une colonne dans une table SQL
#
# Integer, String, Float, DateTime :
# types des colonnes PostgreSQL
#
# ForeignKey :
# permet de créer une relation entre deux tables
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String

# declarative_base :
# permet de créer la classe Base utilisée par SQLAlchemy
#
# relationship :
# permet de définir les relations entre les tables côté Python
from sqlalchemy.orm import declarative_base, relationship


###############################################
# Imports date / heure
###############################################

# datetime :
# permet de générer une date et une heure
from datetime import datetime

# ZoneInfo :
# permet d'utiliser un fuseau horaire précis
# ici Europe/Paris pour la date de création
from zoneinfo import ZoneInfo


###############################################
# Base SQLAlchemy
###############################################

# Base est la classe mère de tous les modèles SQLAlchemy.
# Toutes les tables doivent hériter de Base pour être connues par SQLAlchemy.
Base = declarative_base()


###############################################
# Table InputData
###############################################

class InputData(Base):
    """
    Table contenant les données d'entrée envoyées à l'API.

    Chaque ligne représente un employé soumis au modèle
    pour obtenir une prédiction.
    """

    # Nom réel de la table dans PostgreSQL
    __tablename__ = "inputs"

    # Date et heure de création de l'entrée.
    # Ce champ est rempli automatiquement à chaque insertion.
    # Il permet d'assurer la traçabilité des prédictions.
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(ZoneInfo("Europe/Paris"))
    )

    # Identifiant unique de chaque entrée
    id = Column(Integer, primary_key=True, index=True)

    # Données personnelles / professionnelles de l'employé
    age = Column(Integer, nullable=False)
    genre = Column(String, nullable=False)
    revenu_mensuel = Column(Integer, nullable=False)
    statut_marital = Column(String, nullable=False)
    poste = Column(String, nullable=False)

    # Expérience professionnelle
    nombre_experiences_precedentes = Column(Integer, nullable=False)
    annee_experience_totale = Column(Integer, nullable=False)
    annees_dans_l_entreprise = Column(Integer, nullable=False)
    annees_dans_le_poste_actuel = Column(Integer, nullable=False)

    # Indicateurs de satisfaction
    satisfaction_employee_environnement = Column(Integer, nullable=False)
    note_evaluation_precedente = Column(Integer, nullable=False)
    satisfaction_employee_nature_travail = Column(Integer, nullable=False)
    satisfaction_employee_equipe = Column(Integer, nullable=False)
    satisfaction_employee_equilibre_pro_perso = Column(Integer, nullable=False)

    # Conditions de travail et rémunération
    heure_supplementaires = Column(String, nullable=False)
    augmentation_precedente_salaire_pct = Column(Float, nullable=False)
    nombre_participation_pee = Column(Integer, nullable=False)
    nb_formations_suivies = Column(Integer, nullable=False)
    distance_domicile_travail = Column(Integer, nullable=False)

    # Formation et mobilité
    niveau_education = Column(Integer, nullable=False)
    domaine_etude = Column(String, nullable=False)
    frequence_deplacement = Column(String, nullable=False)

    # Évolution interne
    annees_depuis_la_derniere_promotion = Column(Integer, nullable=False)
    annes_sous_responsable_actuel = Column(Integer, nullable=False)

    # Variables calculées utilisées par le modèle ML
    ratio_salaire_poste = Column(Float, nullable=False)
    ratio_stagnation = Column(Float, nullable=False)
    poste_penibilite_voyage = Column(String, nullable=False)
    attente_promotion_pure = Column(Integer, nullable=False)
    ratio_fidelite_manager = Column(Float, nullable=False)


###############################################
# Table PredictionResult
###############################################

class PredictionResult(Base):
    """
    Table contenant le résultat de prédiction associé
    à une entrée de la table InputData.

    Chaque prédiction est liée à un seul input.
    """

    # Nom réel de la table dans PostgreSQL
    __tablename__ = "predictions"

    # Identifiant unique de chaque prédiction
    id = Column(Integer, primary_key=True, index=True)

    # Clé étrangère vers la table inputs.
    # unique=True impose une relation 1 input = 1 prédiction.
    input_id = Column(Integer, ForeignKey("inputs.id"), unique=True, nullable=False)

    # Résultat numérique du modèle :
    # 0 = reste
    # 1 = départ
    predi = Column(Integer, nullable=False)

    # Probabilité associée au départ
    proba = Column(Float, nullable=False)

    # Résultat textuel retourné par l'API
    # Exemple : "Départ" ou "Reste"
    resultat = Column(String, nullable=False)


###############################################
# Relations entre les tables
###############################################

# Relation côté InputData.
# Permet d'accéder à la prédiction associée à une entrée :
# input_data.prediction
InputData.prediction = relationship(
    "PredictionResult",
    back_populates="parent",
    uselist=False,
)

# Relation côté PredictionResult.
# Permet d'accéder aux données d'entrée associées :
# prediction.parent
PredictionResult.parent = relationship(
    "InputData",
    back_populates="prediction",
)