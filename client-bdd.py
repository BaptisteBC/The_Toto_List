import sys
import time

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QLineEdit, QPushButton, QLabel, \
    QDialog, QMessageBox, QComboBox, QMenu, QAction
from PyQt5.QtGui import QKeySequence
import socket
from lib.custom import AEScipher, AESsocket
import threading
import hashlib


class AuthWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

        # Configuration du client
        self.HOST = '127.0.0.1'
        self.PORT = 55555
        self.utilisateur = None
        self.droits = None

        # Afficher la fenêtre d'authentification au lancement de l'application
        self.show_auth_window()

    def initUI(self):
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('Authentification')

        self.lblUtilisateur = QLabel('Nom d\'utilisateur:', self)
        self.lblPassword = QLabel('Mot de passe:', self)

        self.tbxUtilisateur = QLineEdit(self)
        self.tbxPassword = QLineEdit(self)
        self.tbxPassword.setEchoMode(QLineEdit.Password)

        self.btnLogin = QPushButton('Se connecter', self)
        self.btnLogin.clicked.connect(self.authenticate_user)

        layout = QVBoxLayout()
        layout.addWidget(self.lblUtilisateur)
        layout.addWidget(self.tbxUtilisateur)
        layout.addWidget(self.lblPassword)
        layout.addWidget(self.tbxPassword)
        layout.addWidget(self.btnLogin)

        self.setLayout(layout)

    def show_auth_window(self):
        self.show()

    def authenticate_user(self):
        try:
            # Envoyer le nom d'utilisateur et le mot de passe au serveur pour l'authentification
            utilisateur = self.tbxUtilisateur.text()
            MDP = self.tbxPassword.text()
            print(MDP)

            # Envoyer le nom d'utilisateur et le mot de passe au serveur
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.HOST, self.PORT))

            # Upgrade la connexion à une connexion sécurisée avec AES et Diffie-Hellman
            #self.client_socket = AESsocket(self.client_socket, is_server=False)

            # Obligation de mettre un délai entre la connexion au socket et l'envoi des messages sinon la fenêtre est bloquée (test)
            time.sleep(2)
            credentials = f"{utilisateur}:{MDP}"
            self.client_socket.send(credentials.encode())

            # Recevoir la réponse du serveur
            response = self.client_socket.recv(1024).decode()
            print(response)
            if response.startswith("AUTHORIZED"):
                print(utilisateur, ",", MDP)
                self.utilisateur = utilisateur
                self.motDePasse = MDP

                # Fermer la fenêtre d'authentification et afficher la fenêtre principale
                self.accept()
            else:
                # Afficher un message d'erreur en cas d'authentification échouée
                QMessageBox.critical(self, 'Erreur d\'authentification',
                                     'Accès refusé. Veuillez vérifier vos informations.')
                self.client_socket.close()

        except Exception as e:
            print(f"Erreur lors de l'authentification: {e}")
            QMessageBox.critical(self, 'Erreur d\'authentification', f'{e}')

    def get_credentials(self):
        return self.utilisateur, self.motDePasse


class ChangePasswordWindow(QDialog):
    def __init__(self, utilisateur, client_socket):
        super().__init__()
        self.initUI()
        self.utilisateur = utilisateur
        self.client_socket = client_socket

    def initUI(self):
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('Changer le mot de passe')

        self.lblNouvMDP = QLabel('Nouveau mot de passe:', self)
        self.tbxNouvMDP = QLineEdit(self)
        self.tbxNouvMDP.setEchoMode(QLineEdit.Password)

        self.lblConfirm = QLabel('Confirmer le mot de passe:', self)
        self.tbxConfirm = QLineEdit(self)
        self.tbxConfirm.setEchoMode(QLineEdit.Password)

        self.btnChangerMDP = QPushButton('Changer le mot de passe', self)
        self.btnChangerMDP.clicked.connect(self.change_password)

        layout = QVBoxLayout()
        layout.addWidget(self.lblNouvMDP)
        layout.addWidget(self.tbxNouvMDP)
        layout.addWidget(self.lblConfirm)
        layout.addWidget(self.tbxConfirm)
        layout.addWidget(self.btnChangerMDP)

        self.setLayout(layout)

    def change_password(self):
        new_password = self.tbxNouvMDP.text()
        confirm_password = self.tbxConfirm.text()

        # Vérifiez que les mots de passe correspondent
        if new_password == confirm_password:
            try:
                new_password = hashlib.sha256(new_password.encode("utf-8")).hexdigest()
                message = f"/ChangePassword {self.utilisateur} {new_password}"
                self.client_socket.send(message.encode())

                response = self.client_socket.recv(1024).decode()
                if response.startswith("/PasswordChanged"):
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
        self.password = motdepasse_utilisateur
        self.initUI()
        print(pseudonyme_utilisateur, motdepasse_utilisateur)

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.HOST, self.PORT))
        time.sleep(0.5)
        self.client_socket.send(str(self.utilisateur).encode())
        self.client_socket.send(str(self.password).encode())


        self.creerActions()
        self.creerMenu()

    def creerMenu(self):
        menuBar = self.menuBar()
        file = menuBar.addMenu("Option")
        file.addAction(self.actChangePassword)
        file.addAction(self.actExit)

    def creerActions(self):
        self.actChangePassword = QAction("Changer de mot de passe", self)
        self.actChangePassword.setShortcut(QKeySequence("Ctrl+P"))
        self.actChangePassword.triggered.connect(self.fenetreChangementMDP)

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
        change_password_window = ChangePasswordWindow(self.utilisateur, self.client_socket)
        if change_password_window.exec() == QDialog.Accepted:
            print("Mot de passe changé avec succès!")

    def initUI(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    auth_window = AuthWindow()
    if auth_window.exec() == QDialog.Accepted:
        pseudonyme_utilisateur, motdepasse_utilisateur = auth_window.get_credentials()
        print(f"username :{pseudonyme_utilisateur} | password :{motdepasse_utilisateur}")
        client_window = fenetre(pseudonyme_utilisateur, motdepasse_utilisateur)
        client_window.show()
        sys.exit(app.exec_())
