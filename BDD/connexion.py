# BDD/connexion.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from BDD.models import Base

import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


# Si DATABASE_URL existe
# -> PostgreSQL activé
if DATABASE_URL:

    engine = create_engine(DATABASE_URL)

    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

# Sinon (ex : Hugging Face)
# -> PostgreSQL désactivé
else:

    engine = None
    SessionLocal = None


def create_tables() -> None:

    # Création des tables SQLAlchemy
    if engine is not None:
        Base.metadata.create_all(bind=engine)
        print("Succès : les tables sont créées.")


def get_db():

    # Si pas de base PostgreSQL
    if SessionLocal is None:
        yield None
        return

    # Sinon ouverture session DB
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


if __name__ == "__main__":
    create_tables()