import socket
from random import Random
import lib.pyDHE as pyDHE
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
from Cryptodome.Util.Padding import pad, unpad
from base64 import b64encode, b64decode
from Cryptodome.Util.number import long_to_bytes


class AEScipher:
    """
    Classe pour gérer le chiffrement et le déchiffrement des données avec AES en mode CBC.

    Attributs :
    ----------
    - key : bytes
        La clé AES utilisée pour le chiffrement/déchiffrement (doit être de 16, 24 ou 32 octets).
    - cipher : Cryptodome.Cipher.AES
        Instance de l'objet de chiffrement AES.

    Méthodes :
    ---------
    - encrypt(data)
        Chiffre une chaîne de caractères avec AES (CBC).
    - decrypt(data)
        Déchiffre une chaîne de caractères chiffrée avec AES (CBC).
    """

    def __init__(self, key):
        """
        Initialise une instance d'AEScipher avec une clé AES.

        Paramètres :
        -----------
        - key : bytes
            Clé AES utilisée pour le chiffrement et le déchiffrement.
        """
        self.cipher = None
        self.key = key

    def encrypt(self, data):
        """
        Chiffre les données en utilisant AES en mode CBC.

        Paramètres :
        -----------
        - data : str
            Les données à chiffrer (doivent être une chaîne de caractères).

        Retourne :
        ---------
        - bytes :
            Les données chiffrées encodées en Base64.

        Exceptions :
        -----------
        - TypeError : Si `data` n'est pas une chaîne de caractères.
        - ValueError : Si une erreur survient lors du chiffrement.
        """
        iv = get_random_bytes(AES.block_size)
        self.cipher = AES.new(self.key, AES.MODE_CBC, iv)

        if not isinstance(data, str):
            raise TypeError("Le message doit être une chaîne de caractères (string).")

        try:
            encrypted_data = iv + self.cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
            return b64encode(encrypted_data)
        except Exception as e:
            raise ValueError(f"Erreur lors du chiffrement : {e}")

    def decrypt(self, data):
        """
        Déchiffre les données en utilisant AES en mode CBC.

        Paramètres :
        -----------
        - data : bytes
            Les données chiffrées encodées en Base64.

        Retourne :
        ---------
        - str :
            Les données déchiffrées sous forme de chaîne de caractères.

        Exceptions :
        -----------
        - ValueError : Si une erreur survient lors du déchiffrement ou si les données sont invalides.
        """
        try:
            if len(data) == 0: # correspond à la fermeture connexion
                pass
            else:
                raw = b64decode(data)
                self.cipher = AES.new(self.key, AES.MODE_CBC, raw[:AES.block_size])
                decrypted_data = unpad(self.cipher.decrypt(raw[AES.block_size:]), AES.block_size)
                return decrypted_data.decode('utf-8')
        except (ValueError, TypeError) as e:
            raise ValueError(f"Erreur lors du déchiffrement : {e}")


class AESsocket:
    """
    Classe pour établir une communication sécurisée via un socket, utilisant Diffie-Hellman
    pour générer une clé de session partagée et AES pour chiffrer les données.

    Attributs :
    ----------
    - socket : socket
        L'instance du socket utilisé pour la communication.
    - is_server : bool
        Indique si le socket agit en tant que serveur.
    - aes : AEScipher
        Instance de la classe AEScipher pour gérer le chiffrement.

    Méthodes :
    ---------
    - _diffie_hellman()
        Effectue l'échange de clés Diffie-Hellman et initialise la session AES.
    - send(data)
        Envoie des données chiffrées via le socket.
    - recv(bufsize)
        Reçoit des données chiffrées via le socket et les déchiffre.
    - close()
        Ferme la connexion socket.
    """

    def __init__(self, socket, is_server=False):
        """
        Initialise un socket sécurisé et lance l'échange Diffie-Hellman.

        Paramètres :
        -----------
        - socket : socket
            Le socket utilisé pour la communication.
        - is_server : bool
            Indique si le socket est un serveur (par défaut : False).
        """
        self.socket = socket
        self.is_server = is_server
        self.aes = None
        self._diffie_hellman()

    def _diffie_hellman(self):
        """
        Effectue l'échange de clés Diffie-Hellman pour établir une clé de session partagée
        et initialise AES avec la clé dérivée.
        """
        dh = pyDHE.new()

        try:
            if self.is_server:
                client_public_key = int(self.socket.recv(1024).decode())
                server_public_key = dh.getPublicKey()
                self.socket.send(str(server_public_key).encode())
            else:
                client_public_key = dh.getPublicKey()
                self.socket.send(str(client_public_key).encode())
                server_public_key = int(self.socket.recv(1024).decode())

            shared_key = dh.update(client_public_key if self.is_server else server_public_key)
            aes_key = long_to_bytes(shared_key)[:32]
            self.aes = AEScipher(aes_key)
        except (ValueError, TypeError, socket.error) as e:
            raise ConnectionError(f"Erreur lors de l'échange Diffie-Hellman : {e}")

    def send(self, data):
        """
        Envoie des données chiffrées via le socket.

        Paramètres :
        -----------
        - data : str
            Les données à envoyer.

        Exceptions :
        -----------
        - ValueError : Si le message est vide.
        - ConnectionError : Si une erreur survient lors de l'envoi.
        """
        if not data:
            raise ValueError("Le message est vide, impossible d'envoyer des données vides.")

        try:
            encrypted_data = self.aes.encrypt(data)
            return self.socket.send(encrypted_data)
        except (AttributeError, socket.error) as e:
            raise ConnectionError(f"Erreur lors de l'envoi des données : {e}")

    def recv(self, bufsize):
        """
        Reçoit des données chiffrées via le socket et les déchiffre.

        Paramètres :
        -----------
        - bufsize : int
            Taille maximale des données à recevoir.

        Retourne :
        ---------
        - str :
            Les données reçues et déchiffrées.

        Exceptions :
        -----------
        - ConnectionError : Si une erreur survient lors de la réception.
        """
        try:
            encrypted_data = self.socket.recv(bufsize)
            return self.aes.decrypt(encrypted_data)
        except (ValueError, TypeError, socket.error) as e:
            raise ConnectionError(f"Erreur lors de la réception des données : {e}")

    def close(self):
        """
        Ferme la connexion socket.
        """
        self.socket.close()


class SecureSocket:
    """
    Classe utilitaire pour créer et initialiser des sockets sécurisés.

    Méthodes statiques :
    -------------------
    - create_socket(host, port, is_server)
        Crée un socket sécurisé avec support AES et Diffie-Hellman.
    """

    @staticmethod
    def create_socket(host, port, is_server=False):
        """
        Crée et initialise un socket sécurisé.

        Paramètres :
        -----------
        - host : str
            L'adresse IP ou le nom d'hôte.
        - port : int
            Le port à utiliser pour la connexion.
        - is_server : bool
            Indique si le socket agit en tant que serveur (par défaut : False).

        Retourne :
        ---------
        - AESsocket :
            Une instance de la classe AESsocket pour la communication sécurisée.
        """
        base_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if is_server:
            base_socket.bind((host, port))
            base_socket.listen(5)
            client_socket, addr = base_socket.accept()
            return AESsocket(client_socket, is_server=True), addr
        else:
            base_socket.connect((host, port))
            return AESsocket(base_socket, is_server=False)
