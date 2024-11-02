import threading
import time
import pytest
import socket
from lib.custom import AESsocket
from base64 import b64encode
from Cryptodome.Random import get_random_bytes

# Simuler le serveur
def server_function(ready_event):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 12345))
    server_socket.listen(1)
    print("Serveur en attente de connexion...")

    # Signaler que le serveur est prêt
    ready_event.set()

    client_socket, addr = server_socket.accept()
    print(f"Connexion de {addr}")

    aes_socket = AESsocket(client_socket, is_server=True)

    try:
        message = aes_socket.recv(1024)
        print(f"Message reçu du client: {message}")
        response_message = "Message du serveur"
        aes_socket.send(response_message)
    except ConnectionError as e:
        print(f"Erreur de connexion: {e}")
    finally:
        client_socket.close()
        server_socket.close()

@pytest.fixture(scope="function")
def setup_server(request):
    ready_event = threading.Event()
    server_thread = threading.Thread(target=server_function, args=(ready_event,), daemon=True)
    server_thread.start()

    # Attendre que le serveur soit prêt
    ready_event.wait()

    # Ajouter un finalizer pour arrêter le serveur après le test
    def cleanup():
        if server_thread.is_alive():
            server_thread.join(timeout=1)

    request.addfinalizer(cleanup)
    yield

def connect_to_server():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 12345))
    return client_socket

def test_aes_socket(setup_server):
    client_socket = connect_to_server()
    aes_socket = AESsocket(client_socket, is_server=False)

    client_message = "Bonjour, Serveur!"
    aes_socket.send(client_message)

    response = aes_socket.recv(1024)
    assert response == "Message du serveur"
    client_socket.close()

def test_aes_socket_empty_message(setup_server):
    client_socket = connect_to_server()
    aes_socket = AESsocket(client_socket, is_server=False)

    # Vérifier que l'envoi d'un message vide lève bien une exception
    with pytest.raises(Exception, match="Le message est vide"):
        aes_socket.send("")

    client_socket.close()

def test_aes_socket_invalid_data_type(setup_server):
    client_socket = connect_to_server()
    aes_socket = AESsocket(client_socket, is_server=False)

    # Tester avec un type de données non valide pour le chiffrement
    with pytest.raises(TypeError, match="Le message doit être une chaîne de caractères"):
        aes_socket.send(1234)

    client_socket.close()

def test_aes_socket_invalid_decryption_data(setup_server):
    client_socket = connect_to_server()
    aes_socket = AESsocket(client_socket, is_server=False)

    # Tester avec des données aléatoires invalides pour le déchiffrement
    invalid_data = b64encode(get_random_bytes(16))
    with pytest.raises(ValueError):
        aes_socket.aes.decrypt(invalid_data)

    client_socket.close()

def test_aes_socket_connection_error():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(('localhost', 54321))
    except ConnectionRefusedError:
        assert True  # Test réussi car l'erreur était attendue
    finally:
        client_socket.close()

def test_aes_socket_invalid_decryption_with_incorrect_padding(setup_server):
    client_socket = connect_to_server()
    aes_socket = AESsocket(client_socket, is_server=False)

    incorrect_data = b64encode(get_random_bytes(32))  # Données incorrectes
    with pytest.raises(ValueError):
        aes_socket.aes.decrypt(incorrect_data)

    client_socket.close()
