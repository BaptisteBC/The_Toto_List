import socket
import pymysql.cursors
from lib.custom import AESsocket  # Importation de la classe personnalisée pour le chiffrement AES
import json
from datetime import datetime, timedelta

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
            host='127.0.0.1' , # Remplace par l'adresse IP publique ou le nom d'hôte de la base de données distante
            user = 'root',  # Le nom d'utilisateur de la base de données
            password = 'toto',  # Le mot de passe associé à l'utilisateur
            database = 'TheTotoDB',  # Le nom de la base de données
            port = 3306 , # Le port spécifique sur lequel le serveur MySQL écoute
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

            elif command == "GET_TIME":
                return self.GetTime()

            else:
                return "Commande inconnue."

        except Exception as e:
            print(f"Erreur dans l'interprétation de la commande: {e}")
            return "Erreur serveur."


    def getUserId(self):
        """
        Récupère les ID et pseudonymes des utilisateurs.

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

        # Récupérer toutes les tâches

    def GetTime(self):
        """
        Récupère toutes les tâches et leur applique les vérifications pour déterminer les tâches à colorer.

        Returns:
            str: JSON contenant les tâches et leurs informations avec une indication de couleur (rouge, orange, aucune).
        """
        try:
            with self.dbConnection.cursor() as cursor:
                cursor.execute("SELECT titre_tache, datefin_tache, daterappel_tache FROM taches")
                results = cursor.fetchall()

                if results:
                    # Transforme les résultats en liste d'objets avec gestion des couleurs
                    tasks = []
                    for row in results:
                        titre = row["titre_tache"]
                        date_fin = row["datefin_tache"]
                        date_rappel = row["daterappel_tache"]

                        # Appliquer la logique des couleurs
                        rouge = self.checkFinTaches(date_fin) if date_fin else False
                        orange = self.checkRappelTaches(date_rappel) if date_rappel else False

                        couleur = "rouge" if rouge else "orange" if orange else "aucune"

                        tasks.append({
                            "titre": titre,
                            "date_fin": date_fin,
                            "date_rappel": date_rappel,
                            "couleur": couleur
                        })

                    return json.dumps(tasks, ensure_ascii=False)  # Renvoi des données sous forme de chaîne JSON
                else:
                    return json.dumps({"message": "Aucune tâche disponible."})

        except Exception as e:
            print(f"Erreur MySQL: {e}")
            return json.dumps({"error": "Erreur MySQL."})

    def checkFinTaches(self, datefin_tache):
        """
        Vérifie si une tâche doit être marquée en rouge (J-10 avant la date de fin).

        Args:
            datefin_tache (str ou datetime): La date de fin de la tâche.

        Returns:
            bool: True si la tâche doit être marquée en rouge, False sinon.
        """
        try:
            today = datetime.today().date()

            if isinstance(datefin_tache, datetime):
                due_date_obj = datefin_tache.date()
            else:
                due_date_obj = datetime.strptime(datefin_tache, "%Y-%m-%d").date()

            delta = due_date_obj - today
            return delta == timedelta(days=10)

        except Exception as e:
            print(f"Erreur lors de la comparaison des dates: {e}")
            return False


    def checkRappelTaches(self, daterappel_tache):
        """
        Vérifie si une tâche doit être marquée en orange (date de rappel = aujourd'hui).

        Args:
            daterappel_tache (str ou datetime): La date de rappel de la tâche.

        Returns:
            bool: True si la tâche doit être marquée en orange, False sinon.
        """
        try:
            today = datetime.today().date()

            if isinstance(daterappel_tache, datetime):
                reminder_date_obj = daterappel_tache.date()
            else:
                reminder_date_obj = datetime.strptime(daterappel_tache, "%Y-%m-%d").date()

            return reminder_date_obj == today

        except Exception as e:
            print(f"Erreur lors de la comparaison des dates: {e}")
            return False





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




