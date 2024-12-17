import pytest
from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QApplication
from lib.custom import AESsocket
from main import FormulaireTache


@pytest.fixture(scope="module")
def app():
    """Fixture pour créer une instance QApplication."""
    return QApplication([])


@pytest.fixture
def formulaire(app):
    """Fixture pour créer une instance de FormulaireTache."""
    return FormulaireTache()


def test_conection_success(formulaire):
    """Test que la méthode conection établit correctement une connexion."""
    with patch("socket.socket") as mock_socket:
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        mock_aes_socket = MagicMock(spec=AESsocket)
        with patch("lib.custom.AESsocket", return_value=mock_aes_socket):
            aes_socket = formulaire.conection()
            assert aes_socket == mock_aes_socket
            mock_socket_instance.connect.assert_called_with(('localhost', 12345))


def test_conection_failure(formulaire):
    """Test que la méthode conection gère les échecs de connexion."""
    with patch("socket.socket") as mock_socket:
        mock_socket_instance = MagicMock()
        mock_socket_instance.connect.side_effect = Exception("Connection failed")
        mock_socket.return_value = mock_socket_instance
        aes_socket = formulaire.conection()
        assert aes_socket is None


def test_ChargerListes_success(formulaire):
    """Test que ChargerListes charge correctement les données des listes."""
    mock_aes_socket = MagicMock()
    mock_response = json.dumps([
        {"id": 1, "nom_liste": "Liste 1"},
        {"id": 2, "nom_liste": "Liste 2"}
    ]).encode()

    with patch.object(formulaire, "conection", return_value=mock_aes_socket):
        mock_aes_socket.recv.return_value = mock_response
        formulaire.ChargerListes()
        assert formulaire.listes == {"Liste 1": 1, "Liste 2": 2}
        assert formulaire.combo_box_listes.count() == 2
        assert formulaire.combo_box_listes.itemText(0) == "Liste 1"
        assert formulaire.combo_box_listes.itemText(1) == "Liste 2"


def test_ChargerListes_failure(formulaire):
    """Test que ChargerListes gère les erreurs lors du chargement des listes."""
    with patch.object(formulaire, "conection", return_value=None):
        formulaire.ChargerListes()
        assert formulaire.listes == {}
        assert formulaire.combo_box_listes.count() == 0


def test_ChargerUtilisateurs_success(formulaire):
    """Test que ChargerUtilisateurs charge correctement les utilisateurs."""
    mock_aes_socket = MagicMock()
    mock_response = json.dumps([
        {"id": 1, "pseudo": "User1"},
        {"id": 2, "pseudo": "User2"}
    ]).encode()

    with patch.object(formulaire, "conection", return_value=mock_aes_socket):
        mock_aes_socket.recv.return_value = mock_response
        formulaire.ChargerUtilisateurs()
        assert formulaire.utilisateurs == {"User1": 1, "User2": 2}
        assert formulaire.combo_box_utilisateurs.count() == 2
        assert formulaire.combo_box_utilisateurs.itemText(0) == "User1"
        assert formulaire.combo_box_utilisateurs.itemText(1) == "User2"


def test_ChargerUtilisateurs_failure(formulaire):
    """Test que ChargerUtilisateurs gère les erreurs lors du chargement des utilisateurs."""
    with patch.object(formulaire, "conection", return_value=None):
        formulaire.ChargerUtilisateurs()
        assert formulaire.utilisateurs == {}
        assert formulaire.combo_box_utilisateurs.count() == 0


def test_Envoie_success(formulaire):
    """Test que Envoie fonctionne correctement avec des données valides."""
    mock_aes_socket = MagicMock()
    with patch.object(formulaire, "conection", return_value=mock_aes_socket):
        formulaire.champ_nom.setText("Nouvelle tâche")
        formulaire.champ_description.setPlainText("Description de la tâche")
        formulaire.combo_box_listes.addItem("Liste 1", userData=1)
        formulaire.combo_box_utilisateurs.addItem("User1", userData=1)
        formulaire.combo_box_listes.setCurrentIndex(0)
        formulaire.combo_box_utilisateurs.setCurrentIndex(0)
        formulaire.Envoie()

        expected_message = "CREATION_TACHE:1:1:Nouvelle tâche:Description de la tâche:" \
                           f"{formulaire.champ_date.date().toString('yyyy-MM-dd')}:0:" \
                           f"{formulaire.champ_date_rappel.date().toString('yyyy-MM-dd')}"
        mock_aes_socket.send.assert_called_once_with(expected_message)


def test_Envoie_failure(formulaire):
    """Test que Envoie affiche une erreur si des champs obligatoires sont vides."""
    with patch.object(formulaire, "conection", return_value=None):
        formulaire.champ_nom.clear()
        formulaire.Envoie()
        assert formulaire.champ_nom.text() == ""  # Champ vide doit être détecté
