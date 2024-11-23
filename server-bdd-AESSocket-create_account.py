import socket
import threading
from lib.custom import AEScipher, AESsocket
import pymysql
import time
import sys,os
import cryptocode
import datetime
import hashlib
import re


class Server:
    def __init__(self):
        '''
        constructeur de la classe serveur, permet d'initialiser toutes les variables
        '''
        # Configuration du serveur
        self.HOST = '0.0.0.0'
        self.PORT = 55555
        self.serverstatus=1
        # Connexion à la base de données MySQL
        self.db_connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='thetotodb'
        )

        #liste de tous les clients connectés
        self.clients = []

        # Création du socket serveur
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.HOST, self.PORT))

        self.server_socket.listen()




        # Créer un thread pour écouter les connexions
        threading.Thread(target=self.listen_connections).start()

        #démarage du thread de commande permettant l'administration du serveur
        threading.Thread(target=self.commande).start()

    def listen_connections(self):
        """
        fonction permettant d'ecouter les nouvelles connections en continu grâce au thread si un client souhaite se connecter.
        :return: void
        """
        while self.serverstatus==1:
            # Accepter une connexion client
            client_socket, client_address = self.server_socket.accept()
            # Upgrade la connexion à une connexion sécurisée avec AES et Diffie-Hellman
            client_socket = AESsocket(client_socket, is_server=True)


            # Ajouter le client à la liste
            self.clients.append((client_socket, client_address))

            # Créer un thread pour gérer le client
            threading.Thread(target=self.handle_client, args=(client_socket, client_address)).start()

    def handle_client(self, client_socket, client_address):
        '''
        fonction petmettant au serveur d'authentifier le client et de recevoir les message des clients afin de les diffuser a tout le monde
        et ecriture du message dans la base de donnée dans la table correspondante au canal

        :param client_socket: objet de type socket ayant tout les parametres du socket du client tel que son addresse, son port,...
        :param client_address: liste contenant l'adresse ip et le port utilisé pour la communication (non utilisé pour le moment)
        :return: void
        '''

        try:

            # Réception du nom d'utilisateur et du mot de passe du client
            informations = client_socket.recv(1024)
            print(informations)
            #Si le message débute avec "AUTH", cela signifie que le client essaye de se connecter. Le serveur  va donc procéder a l'authentification
            if informations.startswith("AUTH"):
                typeRequete, utilisateur, MDP = informations.split(":")
                print(utilisateur)
                print(MDP)

                #test de passage des identifiants
                cursor = self.db_connection.cursor()
                cursor.execute("SELECT pseudonyme_utilisateur,motdepasse_utilisateur FROM utilisateurs WHERE pseudonyme_utilisateur = %s AND motdepasse_utilisateur = %s", (utilisateur, MDP))
                user = cursor.fetchone()
                cursor.close()

                if user:
                    nom_utilisateur,MDP = user
                    # Envoyer l'autorisation au client avec le numéro d'utilisateur et les droits d'accès
                    #print(f"AUTHORIZED,{userid},{username},{access_rights}")
                    print(f"AUTHORIZED,{utilisateur},{MDP}\n")
                    client_socket.send(f"AUTHORIZED,zerertghyrila*mle=1é&")
                    time.sleep(0.5)



                # si cela ne correspond pas, le serveur renvoie un message d'echec et va alors fermer le socket
                else:
                    # Envoi d'une autorisation refusée au client
                    time.sleep(5) # pour eviter le bruteforce
                    client_socket.send("UNAUTHORIZED")
                    print("UNAUTHORIZED")
                    # Fermer la connexion du client
                    try:
                        #client_socket.close()
                        AESsocket.close(client_socket)
                    except Exception as e:
                        print(f"Erreur lors de la fermeture du socket : {e}")

            #Si le message débute avec "CREATE_ACCOUNT", cela signifie que le client essaye de créer un compte. Le serveur  va donc procéder a sa création
            elif informations.startswith("CREATE_ACCOUNT"):
                try:
                    typeRequete, email, nom, prenom, pseudo, motDePasse = informations.split(":")
                    cursor = self.db_connection.cursor()

                    # On va alors restester les champs (comme dans le programme du client) afin de s'assurer que les champs sont bien formatés
                    # Vérifier les champs non vides
                    if not (email and nom and prenom and pseudo and motDePasse):
                        client_socket.send("CREATE_ACCOUNT_ERROR")
                        return
                        # Vérification du format de l'email
                    if not self.validationDesEmail(email):
                        client_socket.send("CREATE_ACCOUNT_ERROR")
                        print(f'le champ email n\'est pas valide : {email}')
                        return
                    try:


                        # Vérifier si l'email ou le pseudo existe déjà
                        cursor.execute(
                            "SELECT * FROM utilisateurs WHERE email_utilisateur = %s OR pseudonyme_utilisateur = %s",
                            (email, pseudo))
                        existing_user = cursor.fetchone()

                        if existing_user:
                            try:
                                # Si l'email ou le pseudo existe déjà
                                if existing_user[4] == email:  # Index 4 correspond à `email_utilisateur` dans la table
                                    client_socket.send("EMAIL_TAKEN")
                                    print("EMAIL_TAKEN")
                                elif existing_user[6] == pseudo:  # Index 6 correspond à `pseudonyme_utilisateur`
                                    client_socket.send("PSEUDO_TAKEN")
                                    print("PSEUDO_TAKEN")
                            except Exception as e:
                                print(f'erreur lors du test des informations du compte {e}')
                        else:
                            # Insérer le nouvel utilisateur
                            cursor.execute("""
                                   INSERT INTO utilisateurs (id_utilisateur, id_groupe, nom_utilisateur, prenom_utilisateur, email_utilisateur, motdepasse_utilisateur, pseudonyme_utilisateur, totp_utilisateur)
                                   VALUES (NULL, NULL, %s, %s, %s, %s, %s, '0')
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

            else:
                print("quygdqz")


        except Exception as e:
            print(f"Erreur lors du traitement du client : {e}")
            try :
                # client_socket.close()
                AESsocket.close(client_socket)
            except Exception as e:
                print(f"Erreur lors de la fermeture du socket : {e}")


    def validationDesEntrées(self, input_text):
        """
        Vérifie selon un regex la présence de certains caracteres dans les champs d'identifications
        :param input_text: les diférents champs recu par le serveur
        :return: bool
        """
        # définission des caracteres interdits
        forbidden_pattern = r"[:;,']"
        return not re.search(forbidden_pattern, input_text)

    def validationDesEmail(self, email):
        """
        Vérifie si une adresse email a un format valide.
        :param email: str
        :return: bool
        """
        email_regex = r'^[a-zA-Z0-9._+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None

    def broadcast(self, message, sender_address):
        '''
        fonction permettant d'envoyer les message a chaque client
        :param message: message a envoyer a tous les utilisateurs
        :param sender_address: adresse ip de l'expéditeur
        :return: void
        '''
        # Diffusion du message à tous les clients
        for client in self.clients:
            try:
                # Envoi du message à chaque client meme a l'expéditeur afin de voir si la connexion au serveur est active

                client[0].send(message.encode())
            except:
                # En cas d'erreur, fermer la connexion du client
                self.remove_client(client[0])

    def remove_client(self, client_socket):
        '''
        fonction permettant de supprimer des client en cas de problèmes ou si le client se déconnecte.
        :param client_socket: objet de la classe socket.socket stockant les parametres du client
        :return: void
        '''
        # Retirer un client de la liste

        for client in self.clients:
            # si le client correspont au socket de la liste client, on ferme son socket
            if client[0] == client_socket:

                self.clients.remove(client)


    def commande(self):
        '''
        fonction permettant a l'administrateur d'écrire des commandes afin d'administer le serveur
        l'administrateur effecue les commandes via la console python pour voir la liste des commandes: "/help" ou "/?"
        (thread)
        :return: void
        '''
        while 1==1:
            #print('.\n')
            time.sleep(5)
            # non utilisé pour le moment

if __name__ == '__main__':

    server = Server()
    sys.exit()