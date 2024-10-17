import pytest
from testMotDePasse import evaluerMotDePasse

def test_tres_securise():
    # Mot de passe avec tous les critères respectés
    assert evaluerMotDePasse("Aa1!abcd") == "Très sécurisé"

def test_securise():
    # Mot de passe respectant 4 critères (pas de caractère spécial)
    assert evaluerMotDePasse("Aa1bcdef") == "Sécurisé"

def test_moyennement_securise():
    # Mot de passe respectant 3 critères (pas de majuscule, pas de caractère spécial)
    assert evaluerMotDePasse("a1bcdefg") == "Moyennement sécurisé"

def test_faible():
    # Mot de passe respectant 2 critères (longueur et minuscules seulement)
    assert evaluerMotDePasse("abcdefgh") == "Faible"

def test_tres_faible():
    # Mot de passe ne respectant qu'un seul ou aucun critère
    assert evaluerMotDePasse("abc") == "Très faible"

def test_mot_de_passe_court():
    # Mot de passe trop court, même s'il contient des majuscules, chiffres et caractères spéciaux
    assert evaluerMotDePasse("Aa1!") == "Très faible"

if __name__ == "__main__":
    pytest.main()