from lib.custom import SecureSocket

# Exemple d'utilisation pour un client
secure_socket = SecureSocket.create_socket('127.0.0.1', 5000, is_server=False)
secure_socket.send("Hello, secure world!")
response = secure_socket.recv(1024)
print("Réponse :", response)