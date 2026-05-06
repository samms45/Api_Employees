# BDD/connexion.py

# create_engine :
# fabrique l'objet qui sait se connecter à PostgreSQL
from sqlalchemy import create_engine

# sessionmaker :
# fabrique des "sessions", donc des connexions de travail vers la base
from sqlalchemy.orm import sessionmaker

# Base :
# contient les tables définies dans models.py
from BDD.models import Base


# Adresse de connexion à PostgreSQL
# format :
# postgresql+psycopg2://utilisateur:mot_de_passe@hote:port/nom_base
DATABASE_URL = "postgresql+psycopg2://postgres:sam123@localhost:5432/BDD_employees"


# engine :
# connexion principale à la base
# SQLAlchemy s'en sert pour envoyer les requêtes
engine = create_engine(DATABASE_URL)


# SessionLocal :
# "usine" qui crée des sessions
# une session = ce qu'on utilise pour lire/écrire dans la base
SessionLocal = sessionmaker(
    autocommit=False,  # on valide nous-mêmes avec db.commit()
    autoflush=False,   # n'envoie pas auto les changements tout de suite
    bind=engine,       # la session utilisera cette connexion
)


def create_tables() -> None:
    # crée toutes les tables définies dans Base
    # ici Base connaît InputData et PredictionResult
    Base.metadata.create_all(bind=engine)
    print("Succès : les tables sont créées.")


def get_db():
    # ouvre une session
    db = SessionLocal()

    try:
        # donne la session à FastAPI
        yield db

    finally:
        # ferme toujours la session à la fin
        db.close()


if __name__ == "__main__":
    # si tu lances ce fichier directement :
    # python BDD/connexion.py
    # alors les tables seront créées
    create_tables()