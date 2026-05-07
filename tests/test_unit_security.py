# tests/test_unit_security.py


###### On test cette fonction
## verify_api_key()

import os

import pytest
from fastapi import HTTPException

# On importe directement la fonction de sécurité à tester
# Ici, on ne passe PAS par l'API ni par /predict
from app.main import verify_api_key


def test_cle_api_valide():
    """
    Test unitaire :
    on vérifie que la fonction accepte une bonne clé API.
    """

    # On récupère la vraie clé depuis le fichier .env
    api_key = os.getenv("API_KEY")

    # On appelle directement la fonction verify_api_key
    result = verify_api_key(api_key)

    # Si la clé est bonne, la fonction doit retourner la clé
    assert result == api_key


def test_cle_api_invalide():
    """
    Test unitaire :
    on vérifie que la fonction refuse une mauvaise clé API.
    """

    # pytest.raises vérifie qu'une erreur est bien déclenchée
    with pytest.raises(HTTPException) as erreur:
        verify_api_key("mauvaise_cle")

    # On vérifie que l'erreur est bien une erreur 401
    assert erreur.value.status_code == 401

    # On vérifie aussi le message d'erreur retourné
    assert erreur.value.detail == "Clé API invalide ou manquante"