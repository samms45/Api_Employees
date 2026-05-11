---
title: api-employees-fastapi
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# API de Prédiction de Départ Employé

## 📌 Description

Cette API permet de prédire le risque de départ d’un employé grâce à un modèle de Machine Learning.

Le projet expose un modèle ML via une API FastAPI afin de réaliser des prédictions en temps réel (Live Inference).

Le projet inclut :

- FastAPI
- PostgreSQL
- SQLAlchemy
- Scikit-Learn
- GitHub Actions CI/CD
- Hugging Face Spaces
- Docker

---

# 🚀 API déployée

Swagger :

```txt
https://samss1010-api-employees-fastapi.hf.space/docs
```

API :

```txt
https://samss1010-api-employees-fastapi.hf.space
```

---

# 🏗️ Architecture du projet

```bash
API_Employees/
│
├── app/
├── BDD/
├── data/
├── models/
├── tests/
├── .github/workflows/
│
├── client_main.py
├── Dockerfile
├── pyproject.toml
├── pytest.ini
├── README.md
├── .env
└── uv.lock
```

---

# 📂 Description des dossiers

---

## app/

Contient l’application FastAPI.

### main.py

Fichier principal de l’API :

- création de FastAPI
- chargement du modèle ML
- endpoints `/` et `/predict`
- sécurité API Key

---

## BDD/

Gestion de la base de données PostgreSQL.

### connexion.py

- connexion SQLAlchemy
- création des sessions
- création des tables (InputData et PredictionResult)

### models.py

Définition des tables PostgreSQL avec SQLAlchemy ORM.

---

## data/

Contient les données utilisées par le projet.

### api_data.json

Exemple de données JSON utilisées pour tester l’API.

---

## models/

Contient le modèle Machine Learning sauvegardé.

### model.joblib

Modèle entraîné sauvegardé avec Joblib.

Chargé dans FastAPI pour effectuer les prédictions.

---

## tests/

Contient les tests du projet.

### Tests présents

- tests unitaires
- tests fonctionnels API
- sécurité API Key

Les tests sont exécutés automatiquement dans GitHub Actions.

---

## .github/workflows/

Contient les pipelines GitHub Actions.

### ci.yml

Pipeline CI/CD :

- installation des dépendances
- lancement PostgreSQL
- exécution des tests
- déploiement automatique Hugging Face

---

# 📄 Description des fichiers importants

---

## client_main.py

Script client Python permettant de tester l’API depuis un autre programme.

Permet :

- d’envoyer une requête HTTP
- de tester `/predict`
- de récupérer les résultats JSON

---

## Dockerfile

Permet de containeriser l’application.

Utilisé par Hugging Face Spaces pour :

- construire l’environnement
- installer les dépendances
- lancer FastAPI automatiquement

---

## pyproject.toml

Fichier principal de configuration Python.

Contient :

- dépendances du projet
- configuration uv
- packages Python utilisés

---

## pytest.ini

Configuration globale de Pytest.

Permet :

- configurer les tests
- gérer les options pytest
- simplifier les commandes de test

---

## .env

Contient les variables d’environnement locales.

Le fichier `.env` n’est jamais poussé sur GitHub.

---

# 🧠 Machine Learning

## Objectif

Prédire si un employé risque de quitter l’entreprise.

---

## Type de problème

Classification binaire :

- `0` → reste
- `1` → départ

---

## Modèle

Le modèle est sauvegardé avec :

```python
joblib.dump(model, "model.joblib")
```

Puis chargé dans FastAPI :

```python
joblib.load("models/model.joblib")
```

---

# 🌐 API FastAPI

---

## GET /

Permet de vérifier que l’API fonctionne.

### Réponse

```json
{
  "message": "API opérationnelle"
}
```

---

## POST /predict

Effectue une prédiction de départ employé.

---

## Header obligatoire

```txt
mot-passe-api: sami
```

---

## Exemple de réponse

```json
{
  "prediction": 1,
  "probabilite_depart": 0.76,
  "resultat": "Départ"
}
```

---

# 🗄️ Base de données

Le projet utilise PostgreSQL avec SQLAlchemy ORM.

Connexion :

```python
DATABASE_URL = os.getenv("DATABASE_URL")
```

---

# 🧪 Tests

Le projet utilise Pytest.

Lancer les tests :

```bash
uv run pytest
```

Couverture :

```bash
uv run pytest --cov=app --cov=BDD
```

---

# ⚙️ CI/CD

## CI - Continuous Integration

À chaque push GitHub :

- installation des dépendances
- création PostgreSQL
- exécution des tests
- validation du projet

---

## CD - Continuous Deployment

Lors d’un push sur :

```txt
hf-deploy
```

GitHub Actions :

- lance les tests
- déploie automatiquement sur Hugging Face

---

# ▶️ Lancement local

## 1. Cloner le projet

```bash
git clone https://github.com/samms45/Api_Employees.git
```

---

## 2. Installer les dépendances

```bash
uv sync
```

---

## 3. Configurer .env

```env
API_KEY=sami
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/BDD_employees
```

---

## 4. Créer les tables PostgreSQL

```bash
uv run python -m BDD.connexion
```

---

## 5. Lancer FastAPI

```bash
uv run uvicorn app.main:app --reload
```

---

# 👨‍💻 Auteur

Projet réalisé par SamI.

Projet Data / Machine Learning / MLOps avec API FastAPI, PostgreSQL, CI/CD GitHub Actions et déploiement cloud Hugging Face.