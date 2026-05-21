# BDD/connexion.py

###############################################
# Imports SQLAlchemy
###############################################

# create_engine :
# permet de créer la connexion principale vers PostgreSQL
from sqlalchemy import create_engine

# sessionmaker :
# permet de créer des sessions de travail avec la base
from sqlalchemy.orm import sessionmaker


###############################################
# Imports projet
###############################################

# Base contient les modèles SQLAlchemy définis dans models.py
# Elle connaît donc les tables InputData et PredictionResult
from BDD.models import Base


###############################################
# Imports environnement
###############################################

import os
from dotenv import load_dotenv


###############################################
# Chargement des variables d'environnement
###############################################

# Charge les variables définies dans le fichier .env
load_dotenv()

# Récupère l'URL de connexion PostgreSQL
# Exemple :
# postgresql+psycopg2://user:password@localhost:5432/database_name
DATABASE_URL = os.getenv("DATABASE_URL")


###############################################
# Configuration PostgreSQL
###############################################

# Si DATABASE_URL existe :
# on active PostgreSQL
if DATABASE_URL:

    # Crée l'objet de connexion principal à PostgreSQL
    engine = create_engine(DATABASE_URL)

    # Crée une "fabrique" de sessions.
    # Une session permet de lire et écrire dans la base.
    SessionLocal = sessionmaker(
        autocommit=False,  # on valide manuellement avec db.commit()
        autoflush=False,   # évite l'envoi automatique immédiat des changements
        bind=engine,       # la session utilise cette connexion PostgreSQL
    )

# Si DATABASE_URL n'existe pas :
# on désactive PostgreSQL.
# C'est utile sur Hugging Face, où l'API peut fonctionner sans BDD.
else:

    engine = None
    SessionLocal = None


###############################################
# Création des tables
###############################################

def create_tables() -> None:
    """
    Crée les tables PostgreSQL définies dans models.py.

    Cette fonction utilise Base.metadata.create_all()
    pour créer automatiquement les tables :
    - inputs
    - predictions
    """

    # Si PostgreSQL est activé
    if engine is not None:
        Base.metadata.create_all(bind=engine)
        print("Succès : les tables sont créées.")


###############################################
# Gestion des sessions de base de données
###############################################

def get_db():
    """
    Fournit une session PostgreSQL à FastAPI.

    Cette fonction est utilisée avec Depends(get_db)
    dans les routes FastAPI.

    Elle ouvre une session au début de la requête,
    puis la ferme automatiquement à la fin.
    """

    # Si PostgreSQL est désactivé, on retourne None.
    # Cela permet à l'API de fonctionner sur Hugging Face sans BDD.
    if SessionLocal is None:
        yield None
        return

    # Ouverture d'une session PostgreSQL
    db = SessionLocal()

    try:
        # Donne la session à FastAPI
        yield db

    finally:
        # Ferme toujours la session après la requête
        db.close()


###############################################
# Exécution directe du fichier
###############################################

# Permet de créer les tables en lançant :
# uv run python -m BDD.connexion
if __name__ == "__main__":
    create_tables()