import socket
from random import Random
import lib.pyDHE as pyDHE
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
from Cryptodome.Util.Padding import pad, unpad
from base64 import b64encode, b64decode
from Cryptodome.Util.number import long_to_bytes


class AEScipher:
    def __init__(self, key):
        self.cipher = None
        self.key = key

    def encrypt(self, data):
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
        try:
            raw = b64decode(data)
            self.cipher = AES.new(self.key, AES.MODE_CBC, raw[:AES.block_size])
            decrypted_data = unpad(self.cipher.decrypt(raw[AES.block_size:]), AES.block_size)
            return decrypted_data.decode('utf-8')
        except (ValueError, TypeError) as e:
            raise ValueError(f"Erreur lors du déchiffrement : {e}")


class AESsocket:
    def __init__(self, socket, is_server=False):
        self.socket = socket
        self.is_server = is_server
        self.aes = None
        self._diffie_hellman()

    def _diffie_hellman(self):
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
        if not data:
            raise ValueError("Le message est vide, impossible d'envoyer des données vides.")

        try:
            encrypted_data = self.aes.encrypt(data)
            return self.socket.send(encrypted_data)
        except (AttributeError, socket.error) as e:
            raise ConnectionError(f"Erreur lors de l'envoi des données : {e}")

    def recv(self, bufsize):
        try:
            encrypted_data = self.socket.recv(bufsize)
            return self.aes.decrypt(encrypted_data)
        except (ValueError, TypeError, socket.error) as e:
            raise ConnectionError(f"Erreur lors de la réception des données : {e}")
    def close(self):
        self.socket.close()
