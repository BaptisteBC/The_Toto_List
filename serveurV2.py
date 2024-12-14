import socket
import pymysql.cursors
from lib.custom import AESsocket  # Importation de la classe personnalisée pour le chiffrement AES

class TaskServer:
    """
    Classe représentant le serveur de gestion des tâches.

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
            host='localhost',
            user='root',  # Remplacez par votre utilisateur MySQL
            password='password',  # Remplacez par votre mot de passe MySQL
            database='taskManagement',  # Nom de votre base de données
            cursorclass=pymysql.cursors.DictCursor
        )

    def start(self):
        """
        Démarre le serveur et écoute les connexions entrantes.
        Chaque client est servi via un socket sécurisé AES.
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
            aesSocket = AESsocket(clientSocket, isServer=True)

            try:
                while True:
                    # Réception d'une commande depuis le client
                    command = aesSocket.recv(1024).decode('utf-8')
                    if not command:  # Si aucune commande reçue, fermer la connexion
                        break

                    print(f"Commande reçue: {command}")
                    response = self.interpretCommand(command)  # Traite la commande
                    aesSocket.send(response.encode('utf-8'))  # Envoie la réponse au client

            except Exception as e:
                print(f"Erreur: {e}")

            finally:
                # Ferme le socket client après utilisation
                clientSocket.close()
                print(f"Connexion fermée avec {clientAddress}")

    def interpretCommand(self, command):
        """
        Interprète et exécute une commande reçue du client.

        Args:
            command (str): Commande envoyée par le client.

        Returns:
            str: Réponse à retourner au client.
        """
        try:
            # Gestion des différentes commandes possibles
            if command.startswith("ID_UTILISATEUR:"):
                pseudo = command.split(":")[1]
                return self.getUserId(pseudo)

            elif command.startswith("ID_LISTE:"):
                listName = command.split(":")[1]
                return self.getListId(listName)

            elif command.startswith("CREATION_TACHE:"):
                details = command.split(":")[1:]
                return self.createTask(*details)

            elif command == "GET_LISTES":
                return self.getAllLists()

            else:
                return "Commande inconnue."

        except Exception as e:
            print(f"Erreur dans l'interprétation de la commande: {e}")
            return "Erreur serveur."

    def getAllLists(self):
        """
        Récupère toutes les listes disponibles dans la base de données.

        Returns:
            str: Une liste des noms de listes en format JSON, ou un message d'erreur.
        """
        try:
            with self.dbConnection.cursor() as cursor:
                cursor.execute("SELECT nom_liste FROM listes")
                results = cursor.fetchall()

                if results:
                    # Crée une liste des noms des listes et la convertit en chaîne JSON
                    listNames = [result['nom_liste'] for result in results]
                    return str(listNames)
                else:
                    return "Aucune liste disponible."

        except Exception as e:
            print(f"Erreur MySQL: {e}")
            return "Erreur MySQL."

    def getUserId(self, pseudo):
        """
        Récupère l'ID d'un utilisateur à partir de son pseudo.

        Args:
            pseudo (str): Pseudo de l'utilisateur.

        Returns:
            str: ID de l'utilisateur ou un message d'erreur si l'utilisateur est introuvable.
        """
        try:
            with self.dbConnection.cursor() as cursor:
                cursor.execute("SELECT id_utilisateur FROM utilisateurs WHERE pseudo = %s", (pseudo,))
                result = cursor.fetchone()

                if result:
                    return str(result['id_utilisateur'])
                else:
                    return "Utilisateur introuvable."

        except Exception as e:
            print(f"Erreur MySQL: {e}")
            return "Erreur MySQL."

    def getListId(self, listName):
        """
        Récupère l'ID d'une liste à partir de son nom.

        Args:
            listName (str): Nom de la liste.

        Returns:
            str: ID de la liste ou un message d'erreur si la liste est introuvable.
        """
        try:
            with self.dbConnection.cursor() as cursor:
                cursor.execute("SELECT id_liste FROM listes WHERE nom_liste = %s", (listName,))
                result = cursor.fetchone()

                if result:
                    return str(result['id_liste'])
                else:
                    return "Liste introuvable."

        except Exception as e:
            print(f"Erreur MySQL: {e}")
            return "Erreur MySQL."

    def createTask(self, userId, listId, taskTitle, taskDescription, dueDate, status, reminderDate):
        """
        Crée une nouvelle tâche dans la base de données.

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
