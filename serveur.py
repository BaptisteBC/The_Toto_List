import socket
import pymysql.cursors
from lib.custom import AESsocket  # Importation de la classe personnalisée pour le chiffrement AES
import json


class TaskServer:
    """
    Classe représentant le serveur de gestion des tâches.

    Cette classe gère un serveur qui communique avec les clients via des sockets sécurisés.
    Le serveur permet de gérer les tâches dans une base de données MySQL.

    Attributes:
        host (str): Adresse IP ou nom d'hôte pour le serveur.
        port (int): Port sur lequel le serveur écoute.
        dbConnection (pymysql.connections.Connection): Connexion à la base de données MySQL.
    """

    def __init__(self, host='localhost', port=12345):
        """
        Initialise le serveur avec les paramètres réseau et configure la connexion à la base de données.

        Args:
            host (str): Adresse IP ou nom d'hôte pour le serveur. Par défaut, 'localhost'.
            port (int): Port sur lequel le serveur écoutera. Par défaut, 12345.
        """
        self.host = host
        self.port = port

        # Configuration de la connexion à la base de données MySQL
        self.dbConnection = pymysql.connect(
            host='127.0.0.1',  # Remplace par l'adresse IP publique ou le nom d'hôte de la base de données distante
            user='root',  # Le nom d'utilisateur de la base de données
            password='toto',  # Le mot de passe associé à l'utilisateur
            database='TheTotoDB',  # Le nom de la base de données
            port=3306,  # Le port spécifique sur lequel le serveur MySQL écoute
            cursorclass=pymysql.cursors.DictCursor
        )

    def start(self):
        """
        Démarre le serveur et écoute les connexions entrantes.

        Cette méthode met en place le serveur pour accepter les connexions entrantes et utilise
        un socket sécurisé AES pour la communication avec le client. Le serveur répond aux
        commandes reçues via un protocole défini.

        Le serveur écoute indéfiniment et gère les connexions jusqu'à ce qu'il soit arrêté manuellement.
        """
        # Création et configuration du socket serveur
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.bind((self.host, self.port))  # Associe le socket à l'adresse et au port
        serverSocket.listen(5)  # Écoute jusqu'à 5 connexions simultanées
        print(f"Serveur en écoute sur {self.host}:{self.port}")

        while True:
            # Acceptation d'une nouvelle connexion client
            clientSocket, clientAddress = serverSocket.accept()
            print(f"Connexion établie avec {clientAddress}")

            # Passage du socket à un socket sécurisé AES
            aesSocket = AESsocket(clientSocket, is_server=True)

            try:
                while True:
                    # Réception d'une commande depuis le client
                    command = aesSocket.recv(1024)
                    if not command:  # Si aucune commande reçue, fermer la connexion
                        break

                    print(f"Commande reçue: {command}")
                    response = self.interpretCommand(command)  # Traite la commande
                    print(response)
                    aesSocket.send(response)  # Envoie la réponse au client

            except Exception as e:
                print(f"Erreur: {e}")

            finally:
                # Ferme le socket client après utilisation
                clientSocket.close()
                print(f"Connexion fermée avec {clientAddress}")

    def interpretCommand(self, command):
        """
        Interprète et exécute une commande reçue du client.

        Cette méthode analyse la commande envoyée par le client et appelle la fonction
        appropriée pour répondre à la demande. Elle gère différentes commandes pour
        récupérer des informations des utilisateurs, des listes, ou pour créer des tâches.

        Args:
            command (str): Commande envoyée par le client.

        Returns:
            str: Réponse à retourner au client.
        """
        try:
            # Gestion des différentes commandes possibles
            if command.startswith("GET_UTILISATEURS"):
                return self.getUserId()

            elif command.startswith("ID_LISTE"):
                listName = command.split(":")[1]
                return self.getListId(listName)

            elif command.startswith("CREATION_TACHE"):
                details = command.split(":")[1:]
                return self.createTask(*details)

            elif command == "GET_LISTES":
                return self.getListId()

            else:
                return "Commande inconnue."

        except Exception as e:
            print(f"Erreur dans l'interprétation de la commande: {e}")
            return "Erreur serveur."

    def getUserId(self):
        """
        Récupère les ID et pseudonymes des utilisateurs.

        Cette méthode interroge la base de données pour obtenir les informations des utilisateurs
        stockées dans la table `utilisateurs`. Elle renvoie une liste d'objets JSON contenant
        les IDs et les pseudonymes des utilisateurs.

        Returns:
            str: Liste d'objets JSON contenant les ID et pseudonymes des utilisateurs.
        """
        try:
            with self.dbConnection.cursor() as cursor:
                cursor.execute("SELECT id_utilisateur, pseudonyme_utilisateur FROM utilisateurs")
                results = cursor.fetchall()

                if results:
                    # Transforme les résultats en liste d'objets
                    users = [{"id": row["id_utilisateur"], "pseudo": row["pseudonyme_utilisateur"]} for row in results]
                    return json.dumps(users)  # Convertit en chaîne JSON
                else:
                    return "Aucun utilisateur trouvé."

        except Exception as e:
            print(f"Erreur MySQL: {e}")
            return "Erreur MySQL."

    def getListId(self):
        """
        Récupère les IDs et noms de toutes les listes disponibles.

        Cette méthode interroge la base de données pour obtenir les informations des listes
        dans la table `listes`. Elle renvoie un objet JSON contenant les IDs et les noms des listes.

        Returns:
            str: JSON contenant les IDs et noms des listes, ou un message d'erreur.
        """
        try:
            with self.dbConnection.cursor() as cursor:
                cursor.execute("SELECT id_liste, nom_liste FROM listes")
                results = cursor.fetchall()

                if results:
                    # Transforme les résultats en liste d'objets
                    lists = [{"id": row["id_liste"], "nom_liste": row["nom_liste"]} for row in results]
                    return json.dumps(lists)  # Convertit en chaîne JSON
                else:
                    return json.dumps({"message": "Aucune liste disponible."})

        except Exception as e:
            print(f"Erreur MySQL: {e}")
            return json.dumps({"error": "Erreur MySQL."})

    def createTask(self, userId, listId, taskTitle, taskDescription, dueDate, status, reminderDate):
        """
        Crée une nouvelle tâche dans la base de données.

        Cette méthode insère une nouvelle tâche dans la table `taches` de la base de données.
        Elle prend les informations de la tâche fournies par le client et les enregistre dans
        la base de données MySQL.

        Args:
            userId (str): ID de l'utilisateur assigné.
            listId (str): ID de la liste associée.
            taskTitle (str): Titre de la tâche.
            taskDescription (str): Description de la tâche.
            dueDate (str): Date d'échéance de la tâche (format 'YYYY-MM-DD').
            status (str): Statut de la tâche ('à faire', 'en cours', 'terminé').
            reminderDate (str): Date de rappel pour la tâche (format 'YYYY-MM-DD').

        Returns:
            str: Message confirmant la création de la tâche ou un message d'erreur.
        """
        try:
            with self.dbConnection.cursor() as cursor:
                sql = (
                    "INSERT INTO taches (taches_id_utilisateur, taches_id_liste, titre_tache, description_tache, "
                    "datecreation_tache, datefin_tache, statut_tache, daterappel_tache) "
                    "VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, %s, %s, %s)"
                )
                cursor.execute(sql, (userId, listId, taskTitle, taskDescription, dueDate, status, reminderDate))
                self.dbConnection.commit()

                return "Tâche créée avec succès."

        except Exception as e:
            print(f"Erreur MySQL: {e}")
            return "Erreur lors de la création de la tâche."


if __name__ == "__main__":
    # Point d'entrée du script : lancement du serveur
    taskServer = TaskServer()
    taskServer.start()
