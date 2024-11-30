import pytest
from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QApplication
from formulaire_tache import FormulaireTache

# Initialiser une application PyQt5 pour les tests.
@pytest.fixture(scope="module")
def app():
    return QApplication([])

@pytest.fixture
def formulaire(app):
    """Fixture pour créer une instance de FormulaireTache."""
    return FormulaireTache()

def test_initialisation_formulaire(formulaire):
    """Teste si le formulaire est initialisé correctement."""
    assert formulaire.windowTitle() == "Formulaire de Tâche"
    assert formulaire.champ_nom.text() == ""
    assert formulaire.champ_description.toPlainText() == ""
    assert formulaire.champ_date.date().toString("yyyy-MM-dd") != ""
    assert formulaire.champ_statut.count() == 3
    assert formulaire.combo_box_listes.count() == 0
    assert formulaire.combo_box_utilisateurs.count() == 0

@patch('formulaire_tache.AESsocket')
@patch('formulaire_tache.socket.socket')
def test_conection(mock_socket, mock_aes_socket, formulaire):
    """Teste la méthode conection."""
    mock_client_socket = MagicMock()
    mock_socket.return_value = mock_client_socket
    mock_aes_socket.return_value = "mocked AES socket"

    aes_socket = formulaire.conection()
    mock_client_socket.connect.assert_called_once_with(('localhost', 12345))
    assert aes_socket == "mocked AES socket"

def test_charger_listes(formulaire):
    """Teste le chargement des listes."""
    formulaire.envoyer_requete = MagicMock(return_value=[{'nom_liste': 'Liste 1'}, {'nom_liste': 'Liste 2'}])
    formulaire.ChargerListes()

    assert formulaire.combo_box_listes.count() == 2
    assert formulaire.combo_box_listes.itemText(0) == "Liste 1"
    assert formulaire.combo_box_listes.itemText(1) == "Liste 2"

def test_charger_utilisateurs(formulaire):
    """Teste le chargement des utilisateurs."""
    formulaire.envoyer_requete = MagicMock(return_value=[{'pseudo': 'User1'}, {'pseudo': 'User2'}])
    formulaire.ChargeUtilisateurs()

    assert formulaire.combo_box_utilisateurs.count() == 2
    assert formulaire.combo_box_utilisateurs.itemText(0) == "User1"
    assert formulaire.combo_box_utilisateurs.itemText(1) == "User2"

@patch('formulaire_tache.AESsocket')
def test_envoie(mock_aes_socket, formulaire):
    """Teste la méthode Envoie."""
    mock_aes = MagicMock()
    mock_aes_socket.return_value = mock_aes
    formulaire.conection = MagicMock(return_value=mock_aes)

    # Simuler les entrées utilisateur
    formulaire.champ_nom.setText("Tâche test")
    formulaire.champ_description.setPlainText("Description de test")
    formulaire.combo_box_utilisateurs.addItem("User1")
    formulaire.combo_box_listes.addItem("Liste 1")
    formulaire.combo_box_utilisateurs.setCurrentText("User1")
    formulaire.combo_box_listes.setCurrentText("Liste 1")

    mock_aes.recv.side_effect = [
        b'1',  # ID utilisateur
        b'2'   # ID liste
    ]

    formulaire.Envoie()

    # Vérifications des appels réseau
    mock_aes.send.assert_any_call(b"ID_UTILISATEUR:User1")
    mock_aes.send.assert_any_call(b"ID_LISTE:Liste 1")
    assert mock_aes.send.call_count >= 3

    # Vérifie le dernier message envoyé
    args, _ = mock_aes.send.call_args
    assert b"CREATION_TACHE:1:2:Tâche test:Description de test" in args[0]

@patch('formulaire_tache.QMessageBox')
def test_erreur_conection(mock_messagebox, formulaire):
    """Teste si une erreur de connexion est correctement affichée."""
    formulaire.conection = MagicMock(side_effect=Exception("Connexion échouée"))
    formulaire.Envoie()
    mock_messagebox.critical.assert_called_once_with(formulaire, "Erreur", "Erreur lors de l'envoi : Connexion échouée")
