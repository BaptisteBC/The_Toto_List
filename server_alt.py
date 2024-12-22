from lib.custom import SecureSocket

# Exemple d'utilisation pour un serveur
secure_socket, addr = SecureSocket.create_socket('127.0.0.1', 5000, is_server=True)
print("Connexion depuis :", addr)
message = secure_socket.recv(1024)
print("Message reçu :", message)
secure_socket.send("Hello back!")