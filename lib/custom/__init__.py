import socket
from abc import abstractstaticmethod, abstractmethod
from random import Random
import lib.pyDHE as pyDHE
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
from Cryptodome.Util.Padding import pad, unpad
from base64 import b64encode, b64decode
from Cryptodome.Util.number import long_to_bytes
import time


class AEScipher:
    """
    Classe pour gérer le chiffrement et le déchiffrement des données avec AES en mode CBC.

    :param key: Clé AES utilisée pour le chiffrement et le déchiffrement (doit être de 16, 24 ou 32 octets).
    :type key: bytes
    :raises ValueError: Si la clé fournie n'a pas une longueur valide.
    """

    def __init__(self, key):
        """
        Initialise une instance d'AEScipher avec une clé AES.

        :param key: Clé AES utilisée pour le chiffrement et le déchiffrement.
        :type key: bytes
        :raises ValueError: Si la clé fournie n'a pas une longueur valide.
        """
        if len(key) not in [16, 24, 32]:
            raise ValueError("La clé doit être de 16, 24 ou 32 octets.")
        self.key = key
        self.cipher = None

    def encrypt(self, data):
        """
        Chiffre les données en utilisant AES en mode CBC.

        :param data: Les données à chiffrer (doivent être une chaîne de caractères).
        :type data: str
        :return: Les données chiffrées encodées en Base64.
        :rtype: bytes
        :raises TypeError: Si `data` n'est pas une chaîne de caractères.
        :raises ValueError: Si une erreur survient lors du chiffrement.
        """
        if not isinstance(data, str):
            raise TypeError("Le message doit être une chaîne de caractères (string).")

        iv = get_random_bytes(AES.block_size)
        self.cipher = AES.new(self.key, AES.MODE_CBC, iv)

        try:
            encrypted_data = iv + self.cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
            return b64encode(encrypted_data)
        except Exception as e:
            raise ValueError(f"Erreur lors du chiffrement : {e}")

    def decrypt(self, data):
        """
        Déchiffre les données en utilisant AES en mode CBC.

        :param data: Les données chiffrées encodées en Base64.
        :type data: bytes
        :return: Les données déchiffrées sous forme de chaîne de caractères.
        :rtype: str
        :raises ValueError: Si une erreur survient lors du déchiffrement ou si les données sont invalides.
        """
        if not isinstance(data, bytes):
            raise TypeError("Les données doivent être encodées en bytes.")

        try:
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

    :param socket: L'instance du socket utilisé pour la communication.
    :type socket: socket.socket
    :param is_server: Indique si le socket agit en tant que serveur (par défaut : False).
    :type is_server: bool
    :raises ConnectionError: Si une erreur survient lors de l'échange Diffie-Hellman.
    """

    def __init__(self, socket, is_server=False):
        """
        Initialise un socket sécurisé et lance l'échange Diffie-Hellman.

        :param socket: Le socket utilisé pour la communication.
        :type socket: socket.socket
        :param is_server: Indique si le socket est un serveur (par défaut : False).
        :type is_server: bool
        :raises ConnectionError: Si une erreur survient lors de l'initialisation de Diffie-Hellman.
        """
        self.socket = socket
        self.is_server = is_server
        self.aes = None
        self._diffie_hellman()

    def _diffie_hellman(self):
        """
        Effectue l'échange de clés Diffie-Hellman pour établir une clé de session partagée
        et initialise AES avec la clé dérivée.

        :raises ConnectionError: Si une erreur survient lors de l'échange Diffie-Hellman.
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

        :param data: Les données à envoyer.
        :type data: str
        :return: Le nombre d'octets envoyés.
        :rtype: int
        :raises ValueError: Si le message est vide.
        :raises ConnectionError: Si une erreur survient lors de l'envoi.
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

        :param bufsize: Taille maximale des données à recevoir.
        :type bufsize: int
        :return: Les données reçues et déchiffrées.
        :rtype: str
        :raises ConnectionError: Si une erreur survient lors de la réception.
        """
        try:
            encrypted_data = self.socket.recv(bufsize)
            return self.aes.decrypt(encrypted_data)
        except (ValueError, TypeError, socket.error) as e:
            raise ConnectionError(f"Erreur lors de la réception des données : {e}")

    def close(self):
        """
        Ferme la connexion socket.

        :raises socket.error: Si une erreur survient lors de la fermeture du socket.
        """
        try:
            self.socket.close()
        except socket.error as e:
            raise ConnectionError(f"Erreur lors de la fermeture du socket : {e}")


class SecureSocket:
    """Classe utilitaire pour créer et initialiser des sockets sécurisés.

    Méthodes :
    ----------
    :method create_socket:
        Crée un socket sécurisé avec support AES et Diffie-Hellman.
    """

    @staticmethod
    def create_socket(host, port, is_server=False, maxclient: int | None = 20, delay: int | None = None):
        """Crée un socket sécurisé avec support AES et Diffie-Hellman.

        :param host: Adresse hôte à utiliser pour la connexion.
        :type host: str
        :param port: Port à utiliser pour la connexion.
        :type port: int
        :param is_server: Indique si le socket agit en tant que serveur (par défaut : False).
        :type is_server: bool
        :param maxclient: Nombre maximum de clients acceptés par le serveur (si is_server est True).
            Valeur par défaut : 20.
        :type maxclient: int | None
        :param delay: Délai en secondes avant de créer la connexion (optionnel).
        :type delay: int | None

        :raises NotImplementedError: Si la méthode n'est pas implémentée dans une sous-classe.
        :return: Une instance de socket sécurisé.
        :rtype: SecureSocket | None
        """
        raise NotImplementedError('Méthode non implémentée')

