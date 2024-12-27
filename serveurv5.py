import socket
import threading
import pymysql
import time
import sys
from datetime import datetime
import re
import bcrypt
import pymysql.cursors
from lib.custom import AESsocket
import json




class Server:
    """
    Classe représentant le serveur de l'application.

    Cette classe gère les connexions des clients, la communication avec la base de données,
    et l'exécution des commandes envoyées par les clients.
    """
    def __init__(self):
        """
        Initialise le serveur et configure les paramètres nécessaires, y compris la connexion à la base de données,
        le socket serveur et les threads pour écouter les connexions et les commandes.

        :raises pymysql.MySQLError: Si la connexion à la base de données échoue.
        :raises Exception: En cas d'erreur lors de la configuration du serveur.
        """
        self.HOST = '0.0.0.0'
        self.PORT = 55555
        self.serverstatus=1
        self.db_connection = pymysql.connect(
            host='localhost',
            user='root',
            password='toto',
            database='TheTotoDB',
            port=3306
        )

        self.dbConnection = pymysql.connect(
            host='127.0.0.1',
            user='root',
            password='toto',
            database='TheTotoDB',
            port=3306,
            cursorclass=pymysql.cursors.DictCursor
        )

        #liste de tous les clients connectés
        self.clients = []

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.HOST, self.PORT))

        self.server_socket.listen()

        # Créer un thread pour écouter les connexions
        threading.Thread(target=self.listen_connections).start()

        #démarage du thread de commande permettant l'administration du serveur
        threading.Thread(target=self.commande).start()

    def listen_connections(self):
        """
        Écoute les nouvelles connexions des clients en continu grâce à un thread.

        :return: None
        :rtype: None
        """
        while self.serverstatus==1:
            client_socket, client_address = self.server_socket.accept()
            client_socket = AESsocket(client_socket, is_server=True)

            self.clients.append((client_socket, client_address))

            threading.Thread(target=self.handle_client, args=(client_socket, client_address)).start()

    def handle_client(self, client_socket, client_address):
        """
        Gère les interactions avec un client, notamment l'authentification, les requêtes,
        et les réponses aux commandes envoyées par le client.

        :param client_socket: Socket du client.
        :type client_socket: AESsocket
        :param client_address: Adresse IP et port du client.
        :type client_address: tuple
        :raises Exception: En cas d'erreur lors du traitement des données du client.
        """

        try:

            informations = client_socket.recv(1024)
            if informations.startswith("AUTH"):
                typeRequete, utilisateur, MDPclair = informations.split(":")
                print(utilisateur)
                print(MDPclair)

                cursor = self.db_connection.cursor()
                cursor.execute("SELECT pseudonyme_utilisateur,motdepasse_utilisateur FROM utilisateurs WHERE pseudonyme_utilisateur = %s ", (utilisateur))
                user = cursor.fetchone()
                cursor.close()

                if user:
                    nom_utilisateur,MDP = user
                    MDPclair=MDPclair.encode('utf-8')
                    MDP=MDP.encode('utf-8')
                    if bcrypt.checkpw(MDPclair, MDP):
                        print(f"AUTHORIZED,{utilisateur},{MDP}\n")
                        client_socket.send(f"AUTHORIZED,zerertghyrila*mle=1é&")
                        time.sleep(0.5)
                    else :
                        time.sleep(5)
                        client_socket.send("UNAUTHORIZED")
                        print("UNAUTHORIZED")
                        try:
                            AESsocket.close(client_socket)
                        except Exception as e:
                            print(f"Erreur lors de la fermeture du socket : {e}")
                else:
                    time.sleep(5)
                    client_socket.send("UNAUTHORIZED")
                    print("UNAUTHORIZED")
                    try:
                        AESsocket.close(client_socket)
                    except Exception as e:
                        print(f"Erreur lors de la fermeture du socket : {e}")

            elif informations.startswith("CREATE_ACCOUNT"):
                try:
                    typeRequete, email, nom, prenom, pseudo, motDePasse = informations.split(":")
                    cursor = self.db_connection.cursor()


                    if not (email and nom and prenom and pseudo and motDePasse):
                        client_socket.send("CREATE_ACCOUNT_ERROR")
                        return
                    if not self.validationDesEmail(email):
                        client_socket.send("CREATE_ACCOUNT_ERROR")
                        print(f'le champ email n\'est pas valide : {email}')
                        return
                    try:
                        cursor.execute(
                            "SELECT * FROM utilisateurs WHERE email_utilisateur = %s OR pseudonyme_utilisateur = %s",
                            (email, pseudo))
                        existing_user = cursor.fetchone()

                        if existing_user:
                            try:
                                if existing_user[3] == email:
                                    client_socket.send("EMAIL_TAKEN")
                                    print("EMAIL_TAKEN")
                                elif existing_user[5] == pseudo:
                                    client_socket.send("PSEUDO_TAKEN")
                                    print("PSEUDO_TAKEN")
                            except Exception as e:
                                print(f'erreur lors du test des informations du compte {e}')
                        else:
                            cursor.execute("""
                                   INSERT INTO utilisateurs (id_utilisateur, nom_utilisateur, prenom_utilisateur, email_utilisateur, motdepasse_utilisateur, pseudonyme_utilisateur, totp_utilisateur)
                                   VALUES (NULL, %s, %s, %s, %s, %s, '0')
                               """, (nom, prenom, email, motDePasse, pseudo))
                            self.db_connection.commit()
                            client_socket.send("ACCOUNT_CREATED")
                            print("ACCOUNT_CREATED")

                        cursor.close()
                    except Exception as e:
                        print(f'')
                except Exception as e:
                    print(f"Erreur lors de la création de compte : {e}")
                    client_socket.send("CREATE_ACCOUNT_ERROR")

            elif informations.startswith("CHANGE_PASSWORD"):
                print("changement de mot de passe:")
                try :
                    typeRequete, pseudo, motDePasse = informations.split(":")
                    print(informations)
                    cursor = self.db_connection.cursor()
                    cursor.execute(
                        "UPDATE `utilisateurs` SET `motdepasse_utilisateur` = %s WHERE `utilisateurs`.`pseudonyme_utilisateur` = %s; ",
                        (motDePasse,pseudo))
                    self.db_connection.commit()
                    print("PASSWORD_CHANGED")
                    client_socket.send("PASSWORD_CHANGED")
                except Exception as e:
                    print(f'Erreur lors du changment de mot de passe {e}')
                    client_socket.send("PASSWORD_CHANGED_ERROR")

            elif informations.startswith("GET_UTILISATEURS"):
                utilisateurs = self.getUserId()
                try:
                    client_socket.send(utilisateurs)
                except Exception as e:
                    print(f"Erreur lors de l'envoi des utilisateurs : {e}")

            elif informations.startswith("ID_LISTE"):
                listName = informations.split(":")[1]
                client_socket.send(self.getListId(listName))

            elif informations.startswith("CREATION_TACHE"):
                details = informations.split(":")[1:]
                client_socket.send(self.createTask(*details))

            elif informations.startswith("GET_LISTES"):
                listes = self.getListId()
                try:
                    client_socket.send(listes)
                except Exception as e:
                    print(f"Erreur lors de l'envoi des utilisateurs : {e}")

            elif informations.startswith("MODIF_TACHE"):
                details = informations.split("|")[1:]
                client_socket.send(self.modifTache(*details))

            elif informations.startswith("GET_tacheDetail"):
                idTache = informations.split(":")[1]
                client_socket.send(self.getTacheDetail(idTache))

            elif informations.startswith("GET_sousTacheDetail"):
                idSousTache = informations.split(":")[1]
                client_socket.send(self.getSousTacheDetail(idSousTache))

            elif informations.startswith("GET_tache"):
                idTache = informations.split(":")[1]
                client_socket.send(self.getTache(idTache))

            elif informations.startswith("GET_sousTache"):
                idSousTache = informations.split(":")[1]
                client_socket.send(self.getSousTache(idSousTache))

            elif informations.startswith("GET_listeTache"):
                client_socket.send(self.getListeTache())

            elif informations.startswith("GET_listeSousTache"):
                client_socket.send(self.getListeSousTache())

            elif informations.startswith("SUP_Tache"):
                idTache = informations.split(":")[1]
                client_socket.send(self.supprimerTache(idTache))

            elif informations.startswith("SUP_sousTache"):
                idSousTache = informations.split(":")[1]
                client_socket.send(self.supprimerSousTache(idSousTache))

            elif informations.startswith("modifSousTache"):
                details = informations.split("|")[1:]
                client_socket.send(self.modifSousTache(*details))

            elif informations.startswith("validationSousTache"):
                details = informations.split(":")[1:]
                client_socket.send(self.validationSousTache(*details))

            elif informations.startswith("validation"):
                details = informations.split(":")[1:]
                client_socket.send(self.validation(*details))

            elif informations.startswith("creationSousTache"):
                details = informations.split("|")[1:]
                client_socket.send(self.creationSousTache(*details))

            elif informations.startswith("viderCorbeille"):
                client_socket.send(self.viderCorbeille())

            elif informations.startswith("restaurerCorbeille"):
                client_socket.send(self.restaurerCorbeille())
            else:
                return "Commande inconnue."


        except Exception as e:
            print(f"Erreur lors du traitement du client : {e}")
            try :
                AESsocket.close(client_socket)
            except Exception as e:
                print(f"Erreur lors de la fermeture du socket : {e}")

    def validationDesEntrées(self, input_text):
        """
        Vérifie la présence de caractères interdits dans les champs de données.

        :param input_text: Texte à valider.
        :type input_text: str
        :return: True si le texte est valide, False sinon.
        :rtype: bool
        """
        forbidden_pattern = r"[:;,']"
        return not re.search(forbidden_pattern, input_text)

    def validationDesEmail(self, email):
        """
        Vérifie si une adresse email est valide selon un regex.

        :param email: Adresse email à valider.
        :type email: str
        :return: True si l'email est valide, False sinon.
        :rtype: bool
        """
        email_regex = r'^[a-zA-Z0-9._+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None

    def broadcast(self, message, sender_address):
        """
        Envoie un message à tous les clients connectés, sauf à l'expéditeur.

        :param message: Message à envoyer.
        :type message: str
        :param sender_address: Adresse de l'expéditeur.
        :type sender_address: str
        :return: None
        :rtype: None
        """
        for client in self.clients:
            try:
                client[0].send(message.encode())
            except:
                self.remove_client(client[0])

    def remove_client(self, client_socket):
        """
        Supprime un client de la liste des clients connectés.

        :param client_socket: Socket du client à supprimer.
        :type client_socket: AESsocket
        :return: None
        :rtype: None
        """

        for client in self.clients:
            if client[0] == client_socket:

                self.clients.remove(client)



    def commande(self):
        """
        Interface pour l'administration du serveur via des commandes dans la console.

        (Non utilisé pour le moment.)
        :return: None
        :rtype: None
        """
        while 1==1:
            time.sleep(5)
            # non utilisé pour le moment

    def getUserId(self):
        """
        Récupère les ID et pseudonymes des utilisateurs depuis la base de données.

        :return: Une chaîne JSON contenant les utilisateurs ou un message d'erreur.
        :rtype: str
        :raises Exception: Si une erreur MySQL survient.
        """
        try:
            with self.dbConnection.cursor() as cursor:
                cursor.execute("SELECT id_utilisateur, pseudonyme_utilisateur FROM utilisateurs")
                results = cursor.fetchall()

                if results:
                    users = [{"id": row["id_utilisateur"], "pseudo": row["pseudonyme_utilisateur"]} for row in results]
                    return json.dumps(users)
                else:
                    return "Aucun utilisateur trouvé."

        except Exception as e:
            print(f"Erreur MySQL: {e}")
            return "Erreur MySQL."

    def getListId(self):
        """
        Récupère les IDs et noms de toutes les listes disponibles.

        :return: Une chaîne JSON contenant les listes ou un message d'erreur.
        :rtype: str
        :raises Exception: Si une erreur MySQL survient.
        """
        try:
            with self.dbConnection.cursor() as cursor:
                cursor.execute("SELECT id_liste, nom_liste FROM listes")
                results = cursor.fetchall()

                if results:
                    lists = [{"id": row["id_liste"], "nom_liste": row["nom_liste"]} for row in results]
                    return json.dumps(lists)
                else:
                    return json.dumps({"message": "Aucune liste disponible."})

        except Exception as e:
            print(f"Erreur MySQL: {e}")
            return json.dumps({"error": "Erreur MySQL."})

    def createTask(self, userId, listId, taskTitle, taskDescription, dueDate, status, reminderDate):
        """
        Crée une nouvelle tâche dans la base de données.

        :param userId: ID de l'utilisateur assigné.
        :type userId: str
        :param listId: ID de la liste associée.
        :type listId: str
        :param taskTitle: Titre de la tâche.
        :type taskTitle: str
        :param taskDescription: Description de la tâche.
        :type taskDescription: str
        :param dueDate: Date d'échéance (format 'YYYY-MM-DD').
        :type dueDate: str
        :param status: Statut de la tâche.
        :type status: str
        :param reminderDate: Date de rappel (format 'YYYY-MM-DD').
        :type reminderDate: str
        :return: Message de succès ou d'erreur.
        :rtype: str
        :raises Exception: Si une erreur MySQL survient.
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

                taskId = cursor.lastrowid
                listeY = ["titre_tache", "description_tache", "datefin_tache", "statut_tache", "daterappel_tache"]
                listeZ = [taskTitle, taskDescription, dueDate, status, reminderDate]

                chaineEvenement = self.creerChaineEvenement(0, 1, taskId, listeY, listeZ)
                if chaineEvenement:
                    self.journalisation(userId, chaineEvenement)

                return "Tâche créée avec succès."

        except Exception as e:
            print(f"Erreur MySQL: {e}")
            return "Erreur lors de la création de la tâche."

    def getListeTache(self):
        """
        Récupère toutes les tâches depuis la base de données.

        :return: Une chaîne JSON contenant les tâches ou un message d'erreur.
        :rtype: str
        :raises Exception: Si une erreur MySQL survient.
        """
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("SELECT id_tache, titre_tache, statut_tache, datesuppression_tache FROM taches;")
                results = cursor.fetchall()
                if results:
                    serialized_results = [
                        [value.strftime('%Y-%m-%d %H:%M:%S') if isinstance(value, datetime) else value for value in row]
                        for row in results]
                    return json.dumps(serialized_results)
                else:
                    return json.dumps([])
        except Exception as e:
            print(f"Erreur MySQL: {e}")
            return json.dumps({"error": "Erreur MySQL."})

    def getListeSousTache(self):
        """
        Récupère toutes les sous-tâches depuis la base de données.

        :return: Une chaîne JSON contenant les sous-tâches ou un message d'erreur.
        :rtype: str
        :raises Exception: Si une erreur MySQL survient.
        """
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("SELECT id_soustache, titre_soustache, soustache_id_tache, statut_soustache, datesuppression_soustache FROM soustaches;")

                results = cursor.fetchall()
                if results:
                    serialized_results = [
                        [value.strftime('%Y-%m-%d %H:%M:%S') if isinstance(value, datetime) else value for value in row] for row in results]
                    return json.dumps(serialized_results)
                else:
                    return json.dumps([])
        except Exception as e:
            print(f"Erreur MySQL: {e}")
            return json.dumps({"error": "Erreur MySQL."})


    def getTache(self, idTache):
        """
        Récupère les informations d'une tâche spécifique.

        :param idTache: ID de la tâche.
        :type idTache: str
        :return: Une chaîne JSON contenant les détails de la tâche ou un message d'erreur.
        :rtype: str
        :raises Exception: Si une erreur MySQL survient.
        """
        try:
            with self.db_connection.cursor() as cursor:
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

    def getTacheDetail(self, idTache):
        """
        Récupère les détails approfondis d'une tâche.

        :param idTache: ID de la tâche.
        :type idTache: str
        :return: Une chaîne JSON contenant les détails ou un message d'erreur.
        :rtype: str
        :raises Exception: Si une erreur MySQL survient.
        """
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute(
                    "SELECT titre_tache, description_tache,datecreation_tache, datefin_tache, statut_tache, daterappel_tache FROM taches WHERE id_tache = %s;",
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

    def getSousTacheDetail(self, idSousTache):
        """
        Récupère les détails approfondis d'une sous-tâche.

        :param idSousTache: ID de la sous-tâche.
        :type idSousTache: str
        :return: Une chaîne JSON contenant les détails ou un message d'erreur.
        :rtype: str
        :raises Exception: Si une erreur MySQL survient.
        """
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute(
                    "SELECT titre_soustache, description_soustache, datecreation_soustache,datefin_soustache, statut_soustache,daterappel_soustache, soustache_id_tache FROM soustaches WHERE id_soustache = %s ", (idSousTache))
                results = cursor.fetchall()
                if results:
                    serialized_results = [[ value.strftime('%Y-%m-%d %H:%M:%S') if isinstance(value, datetime) else value for value in row ] for row in results ]
                    idTache = serialized_results[0][-1]
                    cursor.execute("SELECT titre_tache FROM taches WHERE id_tache = %s",(idTache))
                    resultsT = cursor.fetchall()

                    nomTache = resultsT[0][0]
                    serialized_results[0].append(nomTache)
                    return json.dumps(serialized_results)
                else:
                    return json.dumps([])

        except Exception as e:
            print(f"Erreur MySQL: {e}")
            return json.dumps({"error": "Erreur MySQL."})

    def supprimerTache(self, idTache):
        """
        Marque une tâche comme supprimée.

        :param idTache: ID de la tâche à supprimer.
        :type idTache: str
        :return: Message de succès ou d'erreur.
        :rtype: str
        :raises Exception: Si une erreur MySQL survient.
        """
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute(f'UPDATE taches SET datesuppression_tache = NOW() WHERE id_tache = "{idTache}";')
                cursor.execute("UPDATE soustaches SET datesuppression_soustache = NOW() WHERE soustache_id_tache = %s",(idTache))
                self.db_connection.commit()
                return "Tâche supprimer avec succès."



        except Exception as e:
            print(f"Erreur MySQL: {e}")
            return "Erreur MySQL."

    def supprimerSousTache(self, idTache):
        """
        Marque une sous-tâche comme supprimée.

        :param idTache: ID de la sous-tâche à supprimer.
        :type idTache: str
        :return: Message de succès ou d'erreur.
        :rtype: str
        :raises Exception: Si une erreur MySQL survient.
        """
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute(f'UPDATE soustaches SET datesuppression_soustache = NOW() '
                                f'WHERE id_soustache = "{idTache}";')
                self.db_connection.commit()
                return "Sous tâche supprimer avec succès."

        except Exception as e:
            print(f"Erreur MySQL: {e}")
            return "Erreur MySQL."

    def modifTache(self, idTache, titre, description, dateFin, recurrence, dateRappel):
        """
        Modifie une tâche existante.

        :param idTache: ID de la tâche.
        :type idTache: str
        :param titre: Nouveau titre.
        :type titre: str
        :param description: Nouvelle description.
        :type description: str
        :param dateFin: Nouvelle date de fin.
        :type dateFin: str
        :param recurrence: Nouvelle récurrence.
        :type recurrence: str
        :param dateRappel: Nouvelle date de rappel.
        :type dateRappel: str
        :return: Message de succès ou d'erreur.
        :rtype: str
        :raises Exception: Si une erreur MySQL survient.
        """
        try:

            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE taches SET titre_tache = %s, description_tache = %s, datefin_tache = %s, recurrence_tache = %s, daterappel_tache = %s
                    WHERE id_tache = %s;
                """, (titre, description, dateFin, recurrence, dateRappel if dateRappel != 'NULL' else None, idTache))
                self.db_connection.commit()
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
            with self.db_connection.cursor() as cursor:
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

        :param idSousTache: ID de la sous-tâche.
        :type idSousTache: str
        :param titre: Nouveau titre.
        :type titre: str
        :param description: Nouvelle description.
        :type description: str
        :param dateFin: Nouvelle date de fin.
        :type dateFin: str
        :param dateRappel: Nouvelle date de rappel.
        :type dateRappel: str
        :return: Message de succès ou d'erreur.
        :rtype: str
        :raises Exception: Si une erreur MySQL survient.
        """
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE soustaches SET titre_soustache = %s, description_soustache = %s, datefin_soustache = %s, daterappel_soustache = %s
                            WHERE id_soustache = %s;
                """, (titre, description, dateFin,dateRappel if dateRappel != 'NULL' else None, idSousTache))
                self.db_connection.commit()
                return "Sous tâche modifiée avec succès."
        except Exception as e:
            print(f"Erreur MySQL: {e}")
            return "Erreur MySQL."

    def creationSousTache(self, soustache_id_tache, titre_soustache, description_soustache, datefin_soustache, daterappel_soustache):
        """
        Crée une nouvelle sous-tâche.

        :param soustache_id_tache: ID de la tâche parent.
        :type soustache_id_tache: str
        :param titre_soustache: Titre de la sous-tâche.
        :type titre_soustache: str
        :param description_soustache: Description de la sous-tâche.
        :type description_soustache: str
        :param datefin_soustache: Date de fin.
        :type datefin_soustache: str
        :param daterappel_soustache: Date de rappel.
        :type daterappel_soustache: str
        :return: Message de succès ou d'erreur.
        :rtype: str
        :raises Exception: Si une erreur MySQL survient.
        """
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO soustaches (soustache_id_tache, titre_soustache, description_soustache, datefin_soustache, daterappel_soustache, datecreation_soustache, statut_soustache)
                            VALUES (%s, %s, %s, %s, %s, NOW(), 0);
                        """, (soustache_id_tache, titre_soustache, description_soustache, datefin_soustache,
                              daterappel_soustache if daterappel_soustache != 'NULL' else None) )
                self.db_connection.commit()
                return "Sous tâche crée avec succès."
        except Exception as e:
            print(f"Erreur MySQL: {e}")
            return "Erreur MySQL."

    def validation(self, idTache, etatValidation):
        """
        Modifie le statut de validation d'une tâche.

        :param idTache: ID de la tâche à valider.
        :type idTache: str
        :param etatValidation: Nouveau statut de validation (ex. "1" pour validé, "0" pour non validé).
        :type etatValidation: str
        :return: Message de succès ou d'erreur.
        :rtype: str
        :raises Exception: Si une erreur MySQL se produit.
        """
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("UPDATE taches SET statut_tache = %s WHERE id_tache = %s;", (etatValidation, idTache))
                self.db_connection.commit()
                return "Validation modifier avec succes"
        except Exception as e:
            print(f"Erreur MySQL: {e}")
            return "Erreur MySQL."

    def validationSousTache(self, idSousTache, etatValidationSousTache):
        """
        Modifie le statut de validation d'une sous-tâche.

        :param idSousTache: ID de la sous-tâche à valider.
        :type idSousTache: str
        :param etatValidationSousTache: Nouveau statut de validation (ex. "1" pour validé, "0" pour non validé).
        :type etatValidationSousTache: str
        :return: Message de succès ou d'erreur.
        :rtype: str
        :raises Exception: Si une erreur MySQL se produit.
        """
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("UPDATE soustaches SET statut_soustache = %s WHERE id_soustache = %s;", (etatValidationSousTache, idSousTache))
                self.db_connection.commit()
                return "Validation sous tache modifier avec succes"
        except Exception as e:
            print(f"Erreur MySQL: {e}")
            return "Erreur MySQL."

    def journalisation(self, utilisateurId: int, typeEvenement: str):
        """Enregistre un événement dans la table de journalisation.

        :param utilisateurId: Identifiant de l'utilisateur.
        :type utilisateurId: int
        :param typeEvenement: Chaine d'evenement, il est conseiller d'utiliser la fonction "creerChaineEvenement".
        :type typeEvenement: str
        :raises pymysql.MySQLError: Erreur lors de l'insertion dans la base de données.
        :return: None
        :rtype: None
        """
        try:
            with self.db_connection.cursor() as cursor:
                dateEvenement = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                requete = """
                INSERT INTO journalisation (journalisation_id_utilisateur, type_evenement, date_evenement)
                VALUES (%s, %s, %s)
                """
                valeurs = (utilisateurId, typeEvenement, dateEvenement)
                cursor.execute(requete, valeurs)
                self.db_connection.commit()
                print("Informations insérées dans la table 'journalisation'.")

        except pymysql.MySQLError as erreur:
            print(f"Erreur d'insertion : {erreur}")


    def creerChaineEvenement(self, premierX: int, deuxiemeX: int, troisiemeX: int, listeY, listeZ):
        """Crée une chaîne d'événements formatée pour la fonction journalisation.

        :param premierX: Type d'évènement : 0 Ajout ; 1 Modification ; 2 Suppression.
        :type premierX: int
        :param deuxiemeX:  Objet affecté par l'évènement : 0 Utilisateur ; 1 Tache ; 2 Sous tâche ; 3 Liste ; 4 Group ; 5 Groupes_utilisateurs ; 6 Etiquettes ; 7 Etiquettes_elements
        :type deuxiemeX: int
        :param troisiemeX: Id de l'entrée affectée.
        :type troisiemeX: int
        :param listeY: Liste de noms ou d'indices de colonnes, selon le cas.
        :type listeY: list | str
        :param listeZ: Liste des valeurs modifiées dans l'ordre des N° de colonne.
        :type listeZ: list
        :raises pymysql.MySQLError: Erreur lors de la connexion à la base de données.
        :raises ValueError: Si certaines colonnes dans listeY ne correspondent pas.
        :return: Chaîne d’événements formatée.
        :rtype: str | None
        """
        try:

            if isinstance(listeY, list):
                if all(isinstance(element, str) for element in listeY):
                    tables = [
                        "utilisateurs", "taches", "soustaches", "listes", "groupes",
                        "groupes_utilisateurs", "etiquettes", "etiquettes_elements"
                    ]
                    nomTable = tables[deuxiemeX]
                    colonnesValides = []
                    for colonne in listeY:
                        with self.db_connection.cursor() as cursor:
                            requete = f"SHOW COLUMNS FROM {nomTable} LIKE %s"
                            cursor.execute(requete, (colonne,))
                            resultat = cursor.fetchall()
                        if resultat:
                            colonnesValides.append(resultat[0])
                    if len(colonnesValides) != len(listeY):
                        print("Certaines colonnes ne correspondent pas, annulation de l'opération.")
                        return None
                    listeY = [colonnesValides.index(colonne) + 1 for colonne in colonnesValides]

            listeYStr = ".".join(map(str, listeY)) if isinstance(listeY, list) else str(listeY)
            zStr = ".".join(map(str, listeZ))
            chaineEvenement = f"{premierX}.{deuxiemeX}.{troisiemeX}.{{{listeYStr}}}.{{{zStr}}}"

            return chaineEvenement

        except pymysql.MySQLError as erreur:
            print(f"Erreur de connexion : {erreur}")

    def viderCorbeille(self):
        """
        Supprime définitivement toutes les tâches et sous-tâches marquées comme supprimées.

        :return: None
        :rtype: None
        :raises Exception: Si une erreur MySQL se produit.
        """
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("DELETE FROM soustaches WHERE datesuppression_soustache is not NULL;")
                cursor.execute("DELETE FROM taches WHERE datesuppression_tache is not NULL;")
                self.db_connection.commit()

        except Exception as e:
            print(f"Erreur MySQL: {e}")
            return json.dumps({"error": "Erreur MySQL."})

    def restaurerCorbeille(self):
        """
        Restaure toutes les tâches et sous-tâches marquées comme supprimées.

        :return: None
        :rtype: None
        :raises Exception: Si une erreur MySQL se produit.
        """
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("UPDATE taches SET datesuppression_tache = NULL WHERE datesuppression_tache IS NOT NULL;")
                cursor.execute("UPDATE soustaches SET datesuppression_soustache = NULL WHERE datesuppression_soustache IS NOT NULL;")
                self.db_connection.commit()

        except Exception as e:
            print(f"Erreur MySQL: {e}")
            return json.dumps({"error": "Erreur MySQL."})



if __name__ == '__main__':

    server = Server()
    sys.exit()