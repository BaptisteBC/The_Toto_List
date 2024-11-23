import pytest
from unittest.mock import MagicMock
import pymysql
from datetime import datetime

# Importation des fonctions à tester (ajuster selon le nom de ton fichier source)
from formulaire_tache import creer_connexion_mysql, inserer_tache, valider_date


# Test pour vérifier la connexion MySQL
def test_creer_connexion_mysql(mocker):
    # Mock de la fonction pymysql.connect pour éviter une vraie connexion
    mock_connect = mocker.patch("pymysql.connect", return_value=MagicMock())

    # Appel de la fonction avec des paramètres fictifs
    connexion = creer_connexion_mysql("192.168.1.18", "toto", "toto", "thetotodb")

    # Vérification que pymysql.connect a été appelé avec les bons arguments
    mock_connect.assert_called_once_with(
        host="192.168.1.18", user="toto", password="toto", database="thetotodb", port=3306
    )

    # Vérification de la valeur de retour
    assert connexion is not None


# Test pour l'insertion de tâche dans la base de données
def test_inserer_tache(mocker):
    # Mock de la connexion MySQL et du curseur
    mock_connexion = MagicMock()
    mock_cursor = MagicMock()
    mock_connexion.cursor.return_value.__enter__.return_value = mock_cursor

    titre = "Test de tâche"
    description = "Description de la tâche"
    date_creation = datetime.now()
    date_echeance = "2024-12-31"
    type_recurrence = ""
    statut = "à faire"
    id_groupe = 1
    id_utilisateur = 1
    id_liste = 1
    id_tag = 1
    date_rappel = None

    # Appel de la fonction pour insérer une tâche
    inserer_tache(mock_connexion, titre, description, date_creation, date_echeance, type_recurrence, statut, id_groupe,
                  id_utilisateur, id_liste, id_tag, date_rappel)

    # Vérification que la méthode execute a été appelée avec la bonne requête SQL
    mock_cursor.execute.assert_called_once_with(
        f"""
        INSERT INTO taches (id_tache, taches_id_groupe, taches_id_utilisateur, taches_id_liste, 
            titre_tache, description_tache, datecreation_tache, datefin_tache, recurrence_tache, 
            statut_tache, daterappel_tache, datesuppression_tache) 
        VALUES (NULL, NULL, {id_utilisateur}, '{id_liste}', '{titre}', '{description}', 
            CURRENT_TIMESTAMP, '{date_echeance}', '', '{statut}', {date_rappel if date_rappel else 'NULL'}, NULL);
        """
    )

    # Vérification que la méthode commit a été appelée pour valider l'insertion
    mock_connexion.commit.assert_called_once()


# Test de validation de la date
@pytest.mark.parametrize("date_str, expected", [
    ("2024-12-31", True),
    ("2024-02-30", False),  # Date invalide
    ("2024-02-29", True),   # Année bissextile
    ("31-12-2024", False),  # Mauvais format
    ("2024/12/31", False),  # Mauvais format
])
def test_valider_date(date_str, expected):
    assert valider_date(date_str) == expected
