# imports here

import socket
import lib.pyDHE as pyDHE
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
from Cryptodome.Util.Padding import pad, unpad
from base64 import b64encode, b64decode
from Cryptodome.Util.number import long_to_bytes


class AEScipher:
    """
    Cette classe implémente le chiffrement et le déchiffrement symétrique en utilisant l'algorithme AES
    en mode CBC (Cipher Block Chaining). Elle permet de chiffrer et déchiffrer des données avec une clé donnée.

    Args:
        key (bytes): La clé de chiffrement utilisée pour AES. La clé doit être d'une longueur compatible
                     avec AES (par exemple 16, 24 ou 32 octets).

    Attributes:
        cipher (AES object): L'objet AES utilisé pour le chiffrement et le déchiffrement.
        key (bytes): La clé de chiffrement utilisée pour initialiser l'objet AES.

    Methods:
        encrypt(data: str) -> bytes:
            Chiffre les données fournies en utilisant la clé AES et un vecteur d'initialisation (IV)
            généré aléatoirement. Le message est d'abord encodé en UTF-8, puis rempli pour correspondre
            à la taille des blocs AES, et enfin chiffré. Le résultat inclut l'IV suivi des données chiffrées,
            le tout encodé en base64 pour la transmission.

        decrypt(data: bytes) -> str:
            Déchiffre les données encodées en base64. L'IV est extrait du début des données chiffrées,
            et est utilisé pour initialiser l'objet AES en mode CBC. Le texte déchiffré est ensuite
            décompressé (unpad) et renvoyé en tant que chaîne de caractères UTF-8.
    """
    def __init__(self, key):
        self.cipher = None
        self.key = key

    def encrypt(self, data):
        iv = get_random_bytes(AES.block_size)
        self.cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return b64encode(iv + self.cipher.encrypt(pad(data.encode('utf-8'), AES.block_size)))

    def decrypt(self, data):
        raw = b64decode(data)
        self.cipher = AES.new(self.key, AES.MODE_CBC, raw[:AES.block_size])
        return unpad(self.cipher.decrypt(raw[AES.block_size:]), AES.block_size)


class AESsocket:
    """
        Cette classe encapsule une socket existante et ajoute des fonctionnalités de chiffrement avec AES
        pour sécuriser les communications réseau. Elle établit une clé AES via un échange de clés Diffie-Hellman
        et utilise cette clé pour chiffrer et déchiffrer les messages envoyés et reçus.

        Args:
            socket (socket.socket): L'objet socket déjà existant, utilisé pour les communications réseau.
            is_server (bool): Un indicateur qui spécifie si l'instance représente un serveur ou un client pour
                              l'échange Diffie-Hellman. Par défaut, il est False (client).

        Attributes:
            socket (socket.socket): L'instance de la socket utilisée pour les transmissions de données.
            is_server (bool): Indique si cette instance est un serveur ou un client pour l'échange Diffie-Hellman.
            aes (AEScipher): L'instance de AEScipher utilisée pour chiffrer et déchiffrer les données après
                             la négociation de la clé AES.

        Methods:
            _diffie_hellman() -> None:
                Effectue un échange de clés Diffie-Hellman pour négocier une clé partagée entre le client et
                le serveur. Cette clé partagée est ensuite utilisée pour générer une clé AES, qui est
                utilisée pour chiffrer les communications.

            send(data: str) -> None:
                Chiffre les données fournies à l'aide de la clé AES négociée, puis les envoie via la socket.

            recv(bufsize: int) -> str:
                Reçoit des données via la socket, les déchiffre à l'aide de la clé AES négociée, et renvoie
                le message sous forme de chaîne de caractères décodée en UTF-8.
        """
    def __init__(self, socket, is_server=False):
        self.socket = socket
        self.is_server = is_server
        self.aes = None
        self._diffie_hellman()

    def _diffie_hellman(self):
        dh = pyDHE.new()

        if self.is_server:
            # Serveur reçoit la clé publique du client
            client_public_key = int(self.socket.recv(1024).decode())
            # Envoie sa propre clé publique
            server_public_key = dh.getPublicKey()
            self.socket.send(str(server_public_key).encode())
        else:
            # Client envoie sa clé publique
            client_public_key = dh.getPublicKey()
            self.socket.send(str(client_public_key).encode())
            # Reçoit la clé publique du serveur
            server_public_key = int(self.socket.recv(1024).decode())

        # Mise à jour avec la clé publique reçue
        shared_key = dh.update(client_public_key if self.is_server else server_public_key)

        # Générer la clé AES à partir de la clé partagée
        aes_key = long_to_bytes(shared_key)[:32]
        self.aes = AEScipher(aes_key)

    def send(self, data):
        return self.socket.send(self.aes.encrypt(data))

    def recv(self, bufsize):
        return self.aes.decrypt(self.socket.recv(bufsize)).decode('utf-8')