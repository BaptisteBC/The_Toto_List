import pytest
from unittest.mock import MagicMock, patch
import pymysql
from script import obfuscation, start_server, AESsocket


# Mock des tables et données fictives
@pytest.fixture
def setup_database():
    conn = pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='root',
        db='test'
    )
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS xner1etn (id INT, nom VARCHAR(50));")
    cursor.execute("INSERT INTO xner1etn (id, nom) VALUES (1, 'TestUser');")
    conn.commit()
    yield
    cursor.execute("DROP TABLE xner1etn;")
    conn.close()


# Test de la fonction obfuscation
def test_obfuscation(setup_database):
    requete = "SELECT * FROM utilisateur"
    resultats = obfuscation(requete)
    assert resultats == [(1, 'TestUser')]  # Vérifiez les résultats attendus


# Mock de la connexion réseau
@patch('socket.socket')
@patch('script.AESsocket')
def test_server(mock_socket, mock_aes_socket):
    # Mock du socket serveur
    mock_client_socket = MagicMock()
    mock_socket.return_value.accept.return_value = (mock_client_socket, ('127.0.0.1', 12345))

    # Mock des données reçues et envoyées
    mock_client_socket.recv.return_value = b"SELECT * FROM utilisateur"
    mock_client_socket.sendall = MagicMock()

    with patch('script.obfuscation', return_value=[(1, 'TestUser')]):
        start_server()

    # Vérifiez que les données ont été envoyées correctement
    mock_client_socket.sendall.assert_called_with(b"(1, 'TestUser')")


# Test d'erreur dans la requête
def test_obfuscation_error(setup_database):
    requete = "SELECT * FROM table_inexistante"
    with pytest.raises(Exception):
        obfuscation(requete)
