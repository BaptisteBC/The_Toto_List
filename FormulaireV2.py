import sys
import pymysql.cursors
import pymysql
import socket
from lib.custom import AEScipher, AESsocket
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QComboBox, QDateEdit, QVBoxLayout, QPushButton, QMessageBox)
from PyQt5.QtCore import QDate
from datetime import datetime


"""version du formulaire pour contacter directement le serveur python """

class FormulaireTache(QWidget):
    """Interface graphique pour le formulaire de création de tâche.

    Attributes:
        connexion (pymysql.Connection): Connexion à la base de données MySQL.
        groupes (list): Liste des groupes.
        listes (list): Liste des listes.
        utilisateurs (list): Liste des utilisateurs.
        tags (list): Liste des tags.
    """

    def __init__(self):
        """Initialise le formulaire, la connexion MySQL et charge les données requises."""
        super().__init__()
        self.setWindowTitle("Formulaire de Tâche")
        self.setGeometry(100, 100, 400, 600)


        if self.connexion is None:
            QMessageBox.critical(self, "Erreur", "Impossible de se connecter à la base de données.")
            return

        layout = QVBoxLayout()

        # Configuration du formulaire
        self.label_nom = QLabel("Nom de la tâche :")
        self.champ_nom = QLineEdit()
        layout.addWidget(self.label_nom)
        layout.addWidget(self.champ_nom)

        # Champ de description
        self.label_description = QLabel("Description :")
        self.champ_description = QTextEdit()
        layout.addWidget(self.label_description)
        layout.addWidget(self.champ_description)

        # Date d'échéance
        self.label_date = QLabel("Date d'échéance :")
        self.champ_date = QDateEdit()
        self.champ_date.setDate(QDate.currentDate())
        layout.addWidget(self.label_date)
        layout.addWidget(self.champ_date)

        # Statut de la tâche
        self.label_statut = QLabel("Statut de la tâche :")
        self.champ_statut = QComboBox()
        self.champ_statut.addItems(["à faire", "en cours", "terminé"])
        layout.addWidget(self.champ_statut)

        self.label = QLabel("Sélectionnez une Liste :")
        layout.addWidget(self.label)


        NomListe = self.ObtenirNomListe

        # ComboBox pour afficher les noms
        self.combo_box = QComboBox()
        self.combo_box.addItems(NomListe)
        layout.addWidget(self.combo_box)

        # Date d'échéance
        self.label_date_rappel = QLabel("Date de rappel :")
        self.champ_date_rappel = QDateEdit()
        self.champ_date_rappel(QDate.currentDate())
        layout.addWidget(self.label_date_rappel)
        layout.addWidget(self.champ_date_rappel)


        # Bouton pour soumettre
        self.bouton_soumettre = QPushButton("Soumettre")
        self.bouton_soumettre.clicked.connect(self.Envoie())
        layout.addWidget(self.bouton_soumettre)

        self.setLayout(layout)

    def conection(self):
        # Connexion au serveur
        ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ClientSocket.connect(('localhost', 12345))

        # Upgrade la connexion à une connexion sécurisée avec AES et Diffie-Hellman
        AesSocket = AESsocket(ClientSocket, is_server=False)


    def Deconnection(self):
        ClientSockets = self.conection()
        ClientSockets.close()

    def ObtenirNomListe(self):

        MIdListe = f"SELECT taches_id_liste FROM listes"


    def Envoie(self):

        TitreTache = self.champ_nom.text().strip()
        Description = self.champ_description.toPlainText().strip()
        DateEcheance = self.champ_date.date().toString("yyyy-MM-dd")
        Statut = self.champ_statut.currentText().lower()
        UtilisateurConnecte = utilistateur
        DateRappel = self.champ_date_rappel.date().toString("yyyy-MM-dd")




        ClientSocket = self.conection()
        AesSocket = AESsocket(ClientSocket, is_server=False)

        MIdUtilisateur = f"SELECT taches_id_utilisateur FROM utilisateurs WHERE pseudo = {UtilisateurConnecte}"

        AesSocket.send(MIdUtilisateur)

        RIdUtilisateur = self.AesSocket.recv(1024)




        Message = f"INSERT INTO taches (id_tache, taches_id_groupe, taches_id_utilisateur, taches_id_liste, titre_tache, description_tache, datecreation_tache, datefin_tache, recurrence_tache, statut_tache, daterappel_tache, datesuppression_tache) VALUES (NULL,'NULL',{RIdUtilisateur},'1' , {TitreTache}, {Description}, CURRENT_TIMESTAMP, {DateEcheance}, '', {Statut} ,{DateRappel}, NULL);"

        AesSocket.send(Message)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    formulaire = FormulaireTache()
    formulaire.show()
    sys.exit(app.exec())