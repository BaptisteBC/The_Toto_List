import socket
import pymysql.cursors
from lib.custom import AESsocket
import json
from datetime import datetime

class TaskServer:
    """
    Classe représentant le serveur de gestion des tâches.

    :param host: Adresse IP ou nom d'hôte pour le serveur, defaults to 'localhost'
    :type host: str, optional
    :param port: Port sur lequel le serveur écoute, defaults to 12345
    :type port: int, optional
    :param dbConnection: Connexion à la base de données MySQL
    :type dbConnection: pymysql.connections.Connection
    """

    def __init__(self, host='localhost', port=12345):
        """
        Initialise le serveur avec les paramètres réseau et configure la connexion à la base de données.

        :param host: Adresse IP ou nom d'hôte pour le serveur, defaults to 'localhost'
        :type host: str, optional
        :param port: Port sur lequel le serveur écoutera, defaults to 12345
        :type port: int, optional
        """
        self.host = host
        self.port = port

        self.dbConnection = pymysql.connect(
            host='127.0.0.1' ,
            user = 'root',
            password = 'toto',
            database = 'TheTotoDB',
            port = 3306 ,

        )

    def start(self):
        """
        Démarre le serveur et écoute les connexions entrantes.
        Chaque client est servi via un socket sécurisé AES.

        :raises Exception: Si une erreur se produit lors de la gestion des sockets ou de la communication.
        """
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.bind((self.host, self.port))
        serverSocket.listen(5)
        print(f"Serveur en écoute sur {self.host}:{self.port}")

        while True:
            clientSocket, clientAddress = serverSocket.accept()
            print(f"Connexion établie avec {clientAddress}")

            aesSocket = AESsocket(clientSocket, is_server=True)

            try:
                while True:
                    command = aesSocket.recv(1024)
                    if not command:
                        break

                    print(f"Commande reçue: {command}")
                    response = self.interpretCommand(command)
                    aesSocket.send(response)

            except Exception as e:
                print(f"Erreur: {e}")

            finally:
                clientSocket.close()
                print(f"Connexion fermée avec {clientAddress}")

    def interpretCommand(self, command):
        """
        Interprète et exécute une commande reçue du client.

        :param command: Commande envoyée par le client
        :type command: str
        :return: Réponse à retourner au client
        :rtype: str
        """
        try:
            if command.startswith("MODIF_TACHE"):
                details = command.split("|")[1:]
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

        :param idTache: ID de la tâche à récupérer
        :type idTache: str
        :return: JSON contenant les informations sur la tâche (avec datetime sérialisé)
        :rtype: str
        :raises Exception: Si une erreur MySQL se produit
        """
        try:
            with self.dbConnection.cursor() as cursor:
                cursor.execute(
                    "SELECT titre_tache, description_tache, datefin_tache, recurrence_tache, daterappel_tache FROM taches WHERE id_tache = %s;",
                    (idTache,)
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

    def modifTache(self, idTache, titre, description, dateFin, recurrence, dateRappel):
        """
        Modifie une tâche existante.

        :param idTache: ID de la tâche à modifier
        :type idTache: str
        :param titre: Nouveau titre de la tâche
        :type titre: str
        :param description: Nouvelle description de la tâche
        :type description: str
        :param dateFin: Nouvelle date de fin de la tâche
        :type dateFin: str
        :param recurrence: Nouvelle récurrence de la tâche
        :type recurrence: str
        :param dateRappel: Nouvelle date de rappel de la tâche, peut être 'NULL'
        :type dateRappel: str, optional
        :return: Message de succès ou d'erreur
        :rtype: str
        :raises Exception: Si une erreur MySQL se produit
        """
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
        Récupère les informations sur une sous-tâche spécifique.

        :param idSousTache: ID de la sous-tâche à récupérer
        :type idSousTache: str
        :return: JSON contenant les informations sur la sous-tâche (avec datetime sérialisé)
        :rtype: str
        :raises Exception: Si une erreur MySQL se produit
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
        """
        Modifie une sous-tâche existante.

        :param idSousTache: ID de la sous-tâche à modifier
        :type idSousTache: str
        :param titre: Nouveau titre de la sous-tâche
        :type titre: str
        :param description: Nouvelle description de la sous-tâche
        :type description: str
        :param dateFin: Nouvelle date de fin de la sous-tâche
        :type dateFin: str
        :param dateRappel: Nouvelle date de rappel de la sous-tâche, peut être 'NULL'
        :type dateRappel: str, optional
        :return: Message de succès ou d'erreur
        :rtype: str
        :raises Exception: Si une erreur MySQL se produit
        """
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
        """
        Crée une nouvelle sous-tâche.

        :param soustache_id_tache: ID de la tâche parent
        :type soustache_id_tache: str
        :param titre_soustache: Titre de la nouvelle sous-tâche
        :type titre_soustache: str
        :param description_soustache: Description de la nouvelle sous-tâche
        :type description_soustache: str
        :param datefin_soustache: Date de fin de la nouvelle sous-tâche
        :type datefin_soustache: str
        :param daterappel_soustache: Date de rappel de la nouvelle sous-tâche, peut être 'NULL'
        :type daterappel_soustache: str, optional
        :return: Message de succès ou d'erreur
        :rtype: str
        :raises Exception: Si une erreur MySQL se produit
        """
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
        """
        Modifie le statut de validation d'une tâche.

        :param idTache: ID de la tâche à valider
        :type idTache: str
        :param etatValidation: Nouveau statut de validation
        :type etatValidation: str
        :return: Message de succès ou d'erreur
        :rtype: str
        :raises Exception: Si une erreur MySQL se produit
        """
        try:
            with self.dbConnection.cursor() as cursor:
                cursor.execute("UPDATE taches SET statut_tache = %s WHERE id_tache = %s;", (etatValidation, idTache))
                self.dbConnection.commit()
                return "Validation modifier avec succes"
        except Exception as e:
            print(f"Erreur MySQL: {e}")
            return "Erreur MySQL."

    def validationSousTache(self, idSousTache, etatValidationSousTache):
        """
        Modifie le statut de validation d'une sous-tâche.

        :param idSousTache: ID de la sous-tâche à valider
        :type idSousTache: str
        :param etatValidationSousTache: Nouveau statut de validation
        :type etatValidationSousTache: str
        :return: Message de succès ou d'erreur
        :rtype: str
        :raises Exception: Si une erreur MySQL se produit
        """
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