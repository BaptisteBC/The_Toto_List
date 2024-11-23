import sys
import time
import re
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QLineEdit, QPushButton, QLabel, \
    QDialog, QMessageBox, QComboBox, QMenu, QAction
from PyQt5.QtGui import QKeySequence
import socket
from lib.custom import AEScipher, AESsocket
import threading
import hashlib

from conda.instructions import PRINT
from sqlalchemy import Executable


class AuthWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.HOST = '127.0.0.1'
        self.PORT = 55555
        self.mode = "login"  # Par défaut, mode connexion
        self.initUI()
        self.utilisateur= None

    def initUI(self):
        """
        initialisation de la fenetre
        :return:
        """
        self.setGeometry(300, 300, 300, 300)
        self.setWindowTitle('Authentification')

        self.layout = QVBoxLayout()

        # Appel à la méthode pour afficher le formulaire de connexion
        self.affichageFormulaireAuthentification()

        self.setLayout(self.layout)

    def effacerWidgets(self):
        """
        cette methode efface tout les widgets du formulaire lors du switch entre "connexion" et "Inscription" de l'utilisateur lors de l'appui sur le bouton
        :return:
        """
        # Supprime tous les widgets existants du layout
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def affichageFormulaireAuthentification(self):
        """
        cette methode permet l'affichage du formulaire d'authentification lors du lancement de l'applicatif
        :return: void
        """
        self.effacerWidgets()

        # Widgets pour le formulaire de connexion
        self.lblUtilisateur = QLabel('Nom d\'utilisateur:', self)
        self.tbxUtilisateur = QLineEdit(self)
        self.lblmotDePasse = QLabel('Mot de passe:', self)
        self.tbxmotDePasse = QLineEdit(self)
        self.tbxmotDePasse.setEchoMode(QLineEdit.Password)

        self.btnLogin = QPushButton('Se connecter', self)
        self.btnLogin.clicked.connect(self.authentificationUtilisateur)
        self.btnLogin.setDefault(True)

        try:
            self.btnSwitch = QPushButton('Créer un compte', self)
            self.btnSwitch.clicked.connect(self.affichageFormulaireInscription)
        except Exception as e:
            QMessageBox.critical("Erreur",f'Erreur lors du chargement du formulaire d\'inscription {e}')
        # Ajouter les widgets au layout
        self.layout.addWidget(self.lblUtilisateur)
        self.layout.addWidget(self.tbxUtilisateur)
        self.layout.addWidget(self.lblmotDePasse)
        self.layout.addWidget(self.tbxmotDePasse)
        self.layout.addWidget(self.btnLogin)
        self.layout.addWidget(self.btnSwitch)

    def affichageFormulaireInscription(self):
        """
        cette methode va afficher le formulaire d'inscription pour les nouveaux utilisateurs
        :return: void
        """
        try :
            self.effacerWidgets()
            self.setWindowTitle('Inscription')

            # Widgets pour le formulaire de création de compte
            self.lblEmail = QLabel('Email:', self)
            self.tbxEmail = QLineEdit(self)

            self.lblNom = QLabel('Nom:', self)
            self.tbxNom = QLineEdit(self)

            self.lblPrenom = QLabel('Prénom:', self)
            self.tbxPrenom = QLineEdit(self)

            self.lblPseudo = QLabel('Pseudo:', self)
            self.tbxPseudo = QLineEdit(self)

            self.lblmotDePasse = QLabel('Mot de passe:', self)
            self.tbxmotDePasse = QLineEdit(self)
            self.tbxmotDePasse.setEchoMode(QLineEdit.Password)

            self.btnInscription = QPushButton('Créer un compte', self)
            self.btnInscription.clicked.connect(self.inscriptionUtilisateur)
            self.btnInscription.setDefault(True)

            self.btnSwitch = QPushButton('Retour à la connexion', self)
            self.btnSwitch.clicked.connect(self.affichageFormulaireAuthentification)

            # Ajouter les widgets au layout
            self.layout.addWidget(self.lblEmail)
            self.layout.addWidget(self.tbxEmail)
            self.layout.addWidget(self.lblNom)
            self.layout.addWidget(self.tbxNom)
            self.layout.addWidget(self.lblPrenom)
            self.layout.addWidget(self.tbxPrenom)
            self.layout.addWidget(self.lblPseudo)
            self.layout.addWidget(self.tbxPseudo)
            self.layout.addWidget(self.lblmotDePasse)
            self.layout.addWidget(self.tbxmotDePasse)
            self.layout.addWidget(self.btnInscription)
            self.layout.addWidget(self.btnSwitch)
        except Exception as e:
            QMessageBox.critical(self, 'Erreur', f"Erreur lors du chargement du formulaire : {e}")


    def authentificationUtilisateur(self):
        """
        Fonction qui traite le formulaire de connexion et qui envoie les champs au serveur
        :return:
        """
        self.utilisateur = self.tbxUtilisateur.text()
        self.motDePasse = self.tbxmotDePasse.text()

        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((self.HOST, self.PORT))
            client_socket = AESsocket(client_socket, is_server=False)

            credentials = f"AUTH:{self.utilisateur}:{self.motDePasse}" #AUTH -> signale au serveur une demande d'authentification

            print(credentials)
            client_socket.send(credentials)
            response = client_socket.recv(1024)

            if response.startswith("AUTHORIZED"):
                self.accept()
            else:
                QMessageBox.critical(self, 'Erreur', 'Nom d\'utilisateur ou mot de passe incorrect.')
            client_socket.close()
        except Exception as e:
            QMessageBox.critical(self, 'Erreur', f"Erreur lors de l'authentification: {e}")

    def inscriptionUtilisateur(self):
        """
        fonction qui affiche et traite la requete de creation de compte
        :return: void
        """
        email = self.tbxEmail.text()
        nom = self.tbxNom.text()
        prenom = self.tbxPrenom.text()
        pseudo = self.tbxPseudo.text()
        motDePasse = self.tbxmotDePasse.text()



        # Vérifier les champs non vides
        if not (email and nom and prenom and pseudo and motDePasse):
            QMessageBox.critical(self, 'Erreur', 'Tous les champs sont obligatoires.')
            return
            # Vérification du format de l'email
        if not self.validationDesEmail(email):
            QMessageBox.critical(self, 'Erreur', 'Adresse email invalide.')
            return
        try :
            if not all(self.validationDesEntrées(field) for field in [nom, prenom, pseudo, motDePasse]):
                QMessageBox.critical(self, 'Erreur', 'Les champs ne doivent pas contenir les caractères interdits ')
                # creation du compte
            try:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((self.HOST, self.PORT))
                client_socket = AESsocket(client_socket, is_server=False)

                message = f"CREATE_ACCOUNT:{email}:{nom}:{prenom}:{pseudo}:{motDePasse}" #CREATE_ACCOUNT -> signale au serveur une demande de création de comptes
                client_socket.send(message)
                response = client_socket.recv(1024)

                if response.startswith("ACCOUNT_CREATED"):
                    QMessageBox.information(self, 'Succès', 'Compte créé avec succès !')
                    self.affichageFormulaireAuthentification()
                elif response.startswith("EMAIL_TAKEN"):
                    QMessageBox.information(self, 'Erreur', 'L\'addresse mail est déja utilisé.')

                elif response.startswith("PSEUDO_TAKEN"):
                    QMessageBox.information(self, 'Erreur', 'Le pseudo est déja utilisé.')
                client_socket.close()

            except Exception as e:
                QMessageBox.critical(self, 'Erreur', f"Erreur : {e}")
            return


        except Exception as e:
            QMessageBox.critical(self, 'Erreur', f'Erreur lors de la vérification des champs {e}')



    def validationDesEntrées(self, input_text):
        """
        Vérifie selon un regex la présence de certains caracteres dans les champs d'identifications
        :param input_text: les diférents champs utilisés dans le formulaire
        :return:
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
    def getIdentifiants(self):
        return self.utilisateur, self.motDePasse



class ChangemotDePasseWindow(QDialog):
    '''
    cette classe va ouvrir une fenetre afin que l'utilisateur puisse changer son mot de passe
    '''
    def __init__(self, utilisateur, client_socket):
        super().__init__()
        self.initUI()
        self.utilisateur = utilisateur
        self.client_socket = client_socket

    def initUI(self):
        """
        initialisation et affichage du formulaire de changement de mot de Passe
        :return: void
        """
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('Changer le mot de passe')

        self.lblNouvMDP = QLabel('Nouveau mot de passe:', self)
        self.tbxNouvMDP = QLineEdit(self)
        self.tbxNouvMDP.setEchoMode(QLineEdit.motDePasse)

        self.lblConfirm = QLabel('Confirmer le mot de passe:', self)
        self.tbxConfirm = QLineEdit(self)
        self.tbxConfirm.setEchoMode(QLineEdit.motDePasse)

        self.btnChangerMDP = QPushButton('Changer le mot de passe', self)
        self.btnChangerMDP.clicked.connect(self.change_motDePasse)

        layout = QVBoxLayout()
        layout.addWidget(self.lblNouvMDP)
        layout.addWidget(self.tbxNouvMDP)
        layout.addWidget(self.lblConfirm)
        layout.addWidget(self.tbxConfirm)
        layout.addWidget(self.btnChangerMDP)

        self.setLayout(layout)

    def change_motDePasse(self):
        """
        NON FONCTIONNEL
        :return:
        """
        new_motDePasse = self.tbxNouvMDP.text()
        confirm_motDePasse = self.tbxConfirm.text()

        # Vérifiez que les mots de passe correspondent
        if new_motDePasse == confirm_motDePasse:
            try:
                new_motDePasse = hashlib.sha256(new_motDePasse.encode("utf-8")).hexdigest()
                message = f"/ChangemotDePasse {self.utilisateur} {new_motDePasse}"
                self.client_socket.send(message.encode())

                response = self.client_socket.recv(1024).decode()
                if response.startswith("/motDePasseChanged"):
                    QMessageBox.information(self, 'Changement de mot de passe', 'Mot de passe changé avec succès!')
                    self.accept()
                else:
                    QMessageBox.critical(self, 'Erreur', 'Échec du changement de mot de passe.')
            except Exception as e:
                print(f"Erreur lors du changement de mot de passe: {e}")
                QMessageBox.critical(self, 'Erreur', f'{e}\n')
        else:
            QMessageBox.critical(self, 'Erreur', f'Les mots de passe ne correspondent pas.\n')


class fenetre(QMainWindow):
    """
    classe ou l'interface Utilisateur avec toutes les taches affichés va s'executer
    """
    def __init__(self, pseudonyme_utilisateur, motdepasse_utilisateur):
        super().__init__()
        self.HOST = '127.0.0.1'
        self.PORT = 55555
        self.utilisateur = pseudonyme_utilisateur
        self.motDePasse = motdepasse_utilisateur
        self.initUI()
        #print(pseudonyme_utilisateur, motdepasse_utilisateur)

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.HOST, self.PORT))
        self.client_socket = AESsocket(self.client_socket, is_server=False)
        time.sleep(0.5)
        self.client_socket.send(f"AUTH:{pseudonyme_utilisateur}:{motdepasse_utilisateur}")
        #self.client_socket.send(self.motDePasse)


        self.creerActions()
        self.creerMenu()

    def creerMenu(self):
        """
        permet de faire un menu d'actions
        :return:
        """
        menuBar = self.menuBar()
        file = menuBar.addMenu("Option")
        file.addAction(self.actChangemotDePasse)
        file.addAction(self.actExit)

    def creerActions(self):
        """
        permet de définir les raccourci clavier afin de faire des actions
        :return:
        """
        self.actChangemotDePasse = QAction("Changer de mot de passe", self)
        self.actChangemotDePasse.setShortcut(QKeySequence("Ctrl+P"))
        self.actChangemotDePasse.triggered.connect(self.fenetreChangementMDP)

        self.actExit = QAction("Exit", self)
        self.actExit.setShortcut(QKeySequence("Alt+F4"))
        self.actExit.setStatusTip("Exit")
        self.actExit.triggered.connect(self.fermeture)

    def fermeture(self):
        self.client_socket.close()
        self.close()
        app.exit(0)
        sys.exit(0)

    def fenetreChangementMDP(self):
        """
        va appeler la classe qui permettera de modifier le mot de passe
        :return: void
        """
        try:
            change_motDePasse_window = ChangemotDePasseWindow(self.utilisateur, self.client_socket)
            if change_motDePasse_window.exec() == QDialog.Accepted:
                QMessageBox.information("Mot de passe changé avec succès!")
                #print("Mot de passe changé avec succès!")
        except Exception as e:
            QMessageBox.critical("Erreur",f'Erreur lors du changement de mot de passe {e}')

    def initUI(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    auth_window = AuthWindow()
    if auth_window.exec() == QDialog.Accepted:
        pseudonyme_utilisateur, motdepasse_utilisateur = auth_window.getIdentifiants()
        #print(f"username :{pseudonyme_utilisateur} | motDePasse :{motdepasse_utilisateur}")
        client_window = fenetre(pseudonyme_utilisateur, motdepasse_utilisateur)
        client_window.show()
        sys.exit(app.exec_())