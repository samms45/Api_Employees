# Image Python officielle
FROM python:3.11-slim

# Dossier de travail dans le conteneur
WORKDIR /app

# Copier tout le projet dans le conteneur
COPY . .

# Installer uv
RUN pip install uv

# Installer les dépendances du projet
RUN uv sync

# Port utilisé par FastAPI
EXPOSE 7860

# Commande de lancement FastAPI
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]