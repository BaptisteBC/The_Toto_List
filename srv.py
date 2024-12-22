import socket
import pymysql.cursors
from lib.custom import AESsocket  # Importation de la classe personnalisée pour le chiffrement AES
import json
from datetime import datetime

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
                    command = aesSocket.recv(1024)
                    if not command:  # Si aucune commande reçue, fermer la connexion
                        break

                    print(f"Commande reçue: {command}")
                    response = self.interpretCommand(command)  # Traite la commande
                    aesSocket.send(response)


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
            if command.startswith("MODIF_TACHE"):
                details = command.split("|")[1:]  # Utilise | comme séparateur
                return self.modifTache(*details)

            elif command.startswith("GET_tache"):
                idTache = command.split(":")[1]
                return self.getTache(idTache)

            elif command.startswith("GET_sousTache"):
                idSousTache = command.split(":")[1]
                return self.getSousTache(idSousTache)

            elif command.startswith("modifSousTache"):
                details = command.split("|")[1:]
                return self.modifSousTache(*details)

            elif command.startswith("validationSousTache"):
                details = command.split(":")[1:]
                return self.validationSousTache(*details)

            elif command.startswith("validation"):
                details = command.split(":")[1:]
                return self.validation(*details)

            if command.startswith("creationSousTache"):
                details = command.split("|")[1:]
                return self.creationSousTache(*details)

            else:
                return "Commande inconnue."

        except Exception as e:
            print(f"Erreur dans l'interprétation de la commande: {e}")
            return "Erreur serveur."


    def getTache(self, idTache):
        """
        Récupère les informations sur une tâche spécifique.

        Args:
            idTache (str): ID de la tâche à récupérer.

        Returns:
            str: JSON contenant les informations sur la tâche (avec datetime sérialisé).
        """
        try:
            with self.dbConnection.cursor() as cursor:
                cursor.execute(
                    "SELECT titre_tache, description_tache, datefin_tache, recurrence_tache, daterappel_tache FROM taches WHERE id_tache = %s;",
                    (idTache,)
                )

                results = cursor.fetchall()  # Liste de tuples

                if results:
                    serialized_results = [[ value.strftime('%Y-%m-%d %H:%M:%S') if isinstance(value, datetime) else value for value in row ] for row in results ]
                    return json.dumps(serialized_results)
                else:
                    return json.dumps([])

        except Exception as e:
            print(f"Erreur MySQL: {e}")
            return json.dumps({"error": "Erreur MySQL."})

    def modifTache(self, idTache, titre, description, dateFin, recurrence, dateRappel):
        try:

            with self.dbConnection.cursor() as cursor:
                cursor.execute("""
                    UPDATE taches SET titre_tache = %s, description_tache = %s, datefin_tache = %s, recurrence_tache = %s, daterappel_tache = %s
                    WHERE id_tache = %s;
                """, (titre, description, dateFin, recurrence, dateRappel if dateRappel != 'NULL' else None, idTache))
                self.dbConnection.commit()
                return "Tâche modifiée avec succès."
        except Exception as e:
            print(f"Erreur MySQL: {e}")
            return "Erreur MySQL."

    def getSousTache(self, idSousTache):
        """
        Récupère les informations sur une sous tâche spécifique.

        Args:
            idSousTache (str): ID de la sousSELECT titre_soustache, description_soustache, datefin_soustache, daterappel_soustache FROM soustaches WHERE id_soustache = %s;", (idSousTache,) tâche à récupérer.

        Returns:
            str: JSON contenant les informations sur la tâche (avec datetime sérialisé).
        """
        try:
            with self.dbConnection.cursor() as cursor:
                cursor.execute(
                    "SELECT titre_soustache, description_soustache, datefin_soustache, daterappel_soustache FROM soustaches WHERE id_soustache = %s;", (idSousTache,)
                )
                results = cursor.fetchall()
                if results:
                    serialized_results = [[ value.strftime('%Y-%m-%d %H:%M:%S') if isinstance(value, datetime) else value for value in row ] for row in results ]
                    return json.dumps(serialized_results)
                else:
                    return json.dumps([])

        except Exception as e:
            print(f"Erreur MySQL: {e}")
            return json.dumps({"error": "Erreur MySQL."})
    def modifSousTache(self, idSousTache, titre, description, dateFin, dateRappel):
        try:
            with self.dbConnection.cursor() as cursor:
                cursor.execute("""
                    UPDATE soustaches SET titre_soustache = %s, description_soustache = %s, datefin_soustache = %s, daterappel_soustache = %s
                            WHERE id_soustache = %s;
                """, (titre, description, dateFin,dateRappel if dateRappel != 'NULL' else None, idSousTache))
                self.dbConnection.commit()
                return "Sous tâche modifiée avec succès."
        except Exception as e:
            print(f"Erreur MySQL: {e}")
            return "Erreur MySQL."

    def creationSousTache(self, soustache_id_tache, titre_soustache, description_soustache, datefin_soustache, daterappel_soustache):
        try:
            with self.dbConnection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO soustaches (soustache_id_tache, titre_soustache, description_soustache, datefin_soustache, daterappel_soustache, datecreation_soustache, statut_soustache)
                            VALUES (%s, %s, %s, %s, %s, NOW(), 0);
                        """, (soustache_id_tache, titre_soustache, description_soustache, datefin_soustache,
                              daterappel_soustache if daterappel_soustache != 'NULL' else None) )
                self.dbConnection.commit()
                return "Sous tâche crée avec succès."
        except Exception as e:
            print(f"Erreur MySQL: {e}")
            return "Erreur MySQL."

    def validation(self, idTache, etatValidation):
        try:
            with self.dbConnection.cursor() as cursor:
                cursor.execute("UPDATE taches SET statut_tache = %s WHERE id_tache = %s;", (etatValidation, idTache))
                self.dbConnection.commit()
                return "Validation modifier avec succes"
        except Exception as e:
            print(f"Erreur MySQL: {e}")
            return "Erreur MySQL."

    def validationSousTache(self, idSousTache, etatValidationSousTache):
        try:
            with self.dbConnection.cursor() as cursor:
                cursor.execute("UPDATE soustaches SET statut_soustache = %s WHERE id_soustache = %s;", (etatValidationSousTache, idSousTache))
                self.dbConnection.commit()
                return "Validation sous tache modifier avec succes"
        except Exception as e:
            print(f"Erreur MySQL: {e}")
            return "Erreur MySQL."
if __name__ == "__main__":

    taskServer = TaskServer()
    taskServer.start()