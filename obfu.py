import pymysql
import socket

from lib.custom import AEScipher, AESsocket



# Connexion au serveur
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 12345))

# Upgrade la connexion à une connexion sécurisée avec AES et Diffie-Hellman
client_socket = AESsocket(client_socket, is_server=False)

# Dictionnaire de mappage des tables
mtables = {
    "utilisateur": "xner1etn",
    "groupes_utilisateurs": "frfrce",
    "etiquettes_elements": "dvei4agt",
    "groupes": "zhuf9gee",
    "taches": "dpam6ddv",
    "journalisation": "qhds3lem",
    "istes": "naod2mef",
}

def obfuscation(requete):
    # Connexion à la base de données MariaDB
    conn = pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='root',
        db='test'
    )

    cursor = conn.cursor()

    for table_orig in mtables.keys():
        if table_orig in requete:
            # Obtenir le nom de la table obfusquée
            table_obfusquee = mtables[table_orig]
            # Construire la nouvelle requête
            requete = requete.replace(table_orig, table_obfusquee)
            break  # Sortir de la boucle après le premier remplacement

    # Exécution de la requête obfusquée sur la base de données
    cursor.execute(requete)
    resultats = cursor.fetchall()

    # Fermer la connexion
    conn.close()

    return resultats

def start_server():
    host = '0.0.0.0'  # Écouter sur toutes les interfaces réseau
    port = 40000

    # Initialisation du serveur
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print("Serveur en attente de connexion...")

    client_socket, addr = server_socket.accept()
    print(f"Connexion de {addr}")

    # Upgrade la connexion à une connexion sécurisée avec AES et Diffie-Hellman
    client_socket = AESsocket(client_socket, is_server=True)

    print("ok")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connexion établie avec {client_address}")

        try:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break

            print(f"Requête reçue : {data}")

            # Appeler la fonction d'obfuscation
            try:
                resultats = obfuscation(data)
                response = "\n".join([str(row) for row in resultats])
            except Exception as e:
                response = f"Erreur lors de l'exécution de la requête : {str(e)}"

            # Envoyer la réponse au client
            client_socket.sendall(response.encode('utf-8'))

        except Exception as e:
            print(f"Erreur : {str(e)}")
        finally:
            client_socket.close()

if __name__ == "__main__":
    start_server()
