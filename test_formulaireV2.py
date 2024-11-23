import pytest
from unittest.mock import MagicMock
from lib.custom import AESsocket
from FormulaireV2 import FormulaireTache


# Test de la méthode ChargerListes pour vérifier si la liste des listes est chargée correctement
def test_charger_listes():
    # Créer une instance du formulaire sans l'interface graphique
    formulaire = FormulaireTache()

    # Simulation de la méthode envoyer_requete pour renvoyer un résultat simulé
    formulaire.envoyer_requete = MagicMock(return_value=[{'nom_liste': 'Liste 1'}, {'nom_liste': 'Liste 2'}])

    formulaire.ChargerListes()

    # Vérifier que la méthode a bien ajouté les listes
    assert formulaire.combo_box_listes.count() == 3  # Liste par défaut + les 2 chargées
    assert formulaire.combo_box_listes.itemText(1) == 'Liste 1'
    assert formulaire.combo_box_listes.itemText(2) == 'Liste 2'


# Test de la méthode ChargeUtilisateurs pour vérifier si la liste des utilisateurs est chargée correctement
def test_charge_utilisateurs():
    formulaire = FormulaireTache()

    # Simulation de la méthode envoyer_requete pour renvoyer un résultat simulé
    formulaire.envoyer_requete = MagicMock(return_value=[{'pseudo': 'user1'}, {'pseudo': 'user2'}])

    formulaire.ChargeUtilisateurs()

    # Vérifier que la méthode a bien ajouté les utilisateurs
    assert formulaire.combo_box_utilisateurs.count() == 3  # Liste par défaut + les 2 utilisateurs
    assert formulaire.combo_box_utilisateurs.itemText(1) == 'user1'
    assert formulaire.combo_box_utilisateurs.itemText(2) == 'user2'


# Test de la connexion sécurisée
def test_conection():
    formulaire = FormulaireTache()

    # Simulation de la méthode AESsocket
    formulaire.conection = MagicMock(return_value=MagicMock(AESsocket))

    # Test de la connexion
    formulaire.conection()

    # Vérifier que la méthode de connexion a bien été appelée
    formulaire.conection.assert_called_once()


# Test de la méthode Envoie pour vérifier que les données sont envoyées correctement
def test_envoie_formulaire():
    formulaire = FormulaireTache()

    # Initialisation des valeurs du formulaire
    formulaire.champ_nom.setText("Test de tâche")
    formulaire.champ_description.setPlainText("Description de la tâche")
    formulaire.champ_date.setDate("2024-12-31")
    formulaire.champ_statut.setCurrentText("en cours")
    formulaire.champ_date_rappel.setDate("2024-12-25")
    formulaire.combo_box_listes.setCurrentText("Liste 1")
    formulaire.combo_box_utilisateurs.setCurrentText("user1")

    # Simuler la réponse de la méthode envoyer_requete pour les utilisateurs et listes
    formulaire.envoyer_requete = MagicMock(return_value=[{'id_utilisateur': 1}, {'id_liste': 1}])

    # Simuler l'envoi de la requête
    formulaire.Envoie()

    # Vérifier que la méthode envoyer_requete a été appelée pour envoyer la requête d'insertion
    formulaire.envoyer_requete.assert_called()

    # Vérifier que la requête d'insertion contient les informations attendues
    assert "INSERT INTO taches" in formulaire.envoyer_requete.call_args[0][0]

