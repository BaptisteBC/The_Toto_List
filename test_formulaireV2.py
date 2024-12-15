import pytest
from unittest.mock import MagicMock, patch
from FormulaireV2 import FormulaireTache


@pytest.fixture
def form():
    """Fixture pour créer une instance de FormulaireTache."""
    form = FormulaireTache()
    # Simuler les éléments de l'interface graphique pour éviter l'utilisation réelle de PyQt
    form.combo_box_listes = MagicMock()
    form.combo_box_utilisateurs = MagicMock()
    return form


@pytest.fixture
def mock_aes_socket():
    """Fixture pour simuler un socket sécurisé."""
    mock_socket = MagicMock()
    mock_socket.recv.return_value = b'{"nom_liste": "Liste Test"}'  # Exemple de réponse du serveur pour la liste
    return mock_socket


@patch('formulaire_tache.AESsocket', return_value=MagicMock())
def test_connexion(mock_aes_socket_class, form):
    """Test de la connexion au serveur."""
    mock_aes_socket_class.return_value = mock_aes_socket()

    # Simuler la connexion
    aes_socket = form.conection()

    # Vérifier que la connexion a bien été établie
    assert aes_socket is not None
    aes_socket.send.assert_called_once()  # Vérifier qu'un envoi de message a eu lieu


@patch('formulaire_tache.AESsocket', return_value=MagicMock())
def test_charger_listes(mock_aes_socket_class, form, mock_aes_socket):
    """Test de la fonction ChargerListes pour récupérer les listes."""
    mock_aes_socket_class.return_value = mock_aes_socket

    # Simuler la récupération des listes
    form.ChargerListes()

    # Vérifier que la méthode send a bien été appelée pour demander les listes
    mock_aes_socket.send.assert_called_with("GET_LISTES")

    # Vérifier que la méthode recv a renvoyé une réponse simulée
    mock_aes_socket.recv.assert_called_once_with(1024)

    # Vérifier que les listes sont ajoutées dans la combo box
    form.combo_box_listes.addItems.assert_called_with(["Liste Test"])


@patch('formulaire_tache.AESsocket', return_value=MagicMock())
def test_envoi_donnees(mock_aes_socket_class, form, mock_aes_socket):
    """Test de l'envoi des données de création de tâche."""
    mock_aes_socket_class.return_value = mock_aes_socket

    # Simuler l'entrée des données dans le formulaire
    form.champ_nom.setText("Tâche Test")
    form.champ_description.setPlainText("Description de la tâche")
    form.champ_date.setDate(form.champ_date.currentDate())
    form.champ_statut.setCurrentText("à faire")
    form.champ_date_rappel.setDate(form.champ_date.currentDate())
    form.combo_box_utilisateurs.currentText.return_value = "Utilisateur Test"
    form.combo_box_listes.currentText.return_value = "Liste Test"

    # Simuler la soumission du formulaire
    form.Envoie()

    # Vérifier que les messages de création ont bien été envoyés
    assert mock_aes_socket.send.called
    assert "CREATION_TACHE" in str(mock_aes_socket.send.call_args)


@patch('formulaire_tache.AESsocket', return_value=MagicMock())
def test_erreur_connexion(mock_aes_socket_class, form):
    """Test de la gestion d'erreur lors de la connexion au serveur."""
    mock_aes_socket_class.return_value = None

    # Simuler une tentative de connexion
    form.conection()

    # Vérifier qu'il n'y a pas de socket et qu'aucun envoi n'a eu lieu
    assert form.conection() is None


@patch('formulaire_tache.AESsocket', return_value=MagicMock())
def test_erreur_chargement_listes(mock_aes_socket_class, form, mock_aes_socket):
    """Test de la gestion d'erreur lors du chargement des listes."""
    mock_aes_socket_class.return_value = mock_aes_socket
    mock_aes_socket().recv.side_effect = Exception("Erreur de récupération des listes")

    # Simuler l'appel pour charger les listes
    form.ChargerListes()

    # Vérifier qu'il y a eu un message d'erreur
    assert form.findChild(QMessageBox) is not None


if __name__ == "__main__":
    pytest.main()
