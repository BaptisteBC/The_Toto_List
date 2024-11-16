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

        # Sélection de la liste
        self.label_liste = QLabel("Liste :")
        self.combo_box_listes = QComboBox()
        layout.addWidget(self.label_liste)
        layout.addWidget(self.combo_box_listes)

        self.label_utilisateur = QLabel("Assigné à :")
        self.combo_box_utilisateurs = QComboBox()
        layout.addWidget(self.label_utilisateur)
        layout.addWidget(self.combo_box_utilisateurs)

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

        # Charger les utilisateurs et les listes
        self.ChargeUtilisateurs()
        self.ChargerListes()

    def conection(self):
        # Connexion au serveur
        ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ClientSocket.connect(('localhost', 12345))

        # Upgrade la connexion à une connexion sécurisée avec AES et Diffie-Hellman
        AesSocket = AESsocket(ClientSocket, is_server=False)


    def Deconnection(self):
        ClientSockets = self.conection()
        ClientSockets.close()

    def ChargerListes(self):
        """Charge les listes depuis le serveur et les ajoute au QComboBox."""
        requete_sql = "SELECT nom_liste FROM listes"
        resultats = self.envoyer_requete(requete_sql)

        if resultats:
            noms_listes = [liste['nom_liste'] for liste in resultats]
            self.combo_box_listes.addItems(noms_listes)
        else:
            QMessageBox.warning(self, "Aucune liste",
                                "Aucune liste trouvée ou erreur dans la récupération des données.")

    def ChargeUtilisateurs(self):
        """Charge les utilisateurs depuis le serveur et les ajoute au QComboBox."""
        requete_sql = "SELECT pseudo FROM utilisateurs"
        resultats = self.envoyer_requete(requete_sql)

        if resultats:
            noms_utilisateurs = [utilisateur['pseudo'] for utilisateur in resultats]
            self.combo_box_utilisateurs.addItems(noms_utilisateurs)
        else:
            QMessageBox.warning(self, "Aucun utilisateur",
                                "Aucun utilisateur trouvé ou erreur dans la récupération des données.")

    def Envoie(self):

        TitreTache = self.champ_nom.text().strip()
        Description = self.champ_description.toPlainText().strip()
        DateEcheance = self.champ_date.date().toString("yyyy-MM-dd")
        Statut = self.champ_statut.currentText().lower()
        DateRappel = self.champ_date_rappel.date().toString("yyyy-MM-dd")
        UtilisateurChoisi = self.combo_box_utilisateurs.currentText()
        ListeChoisie = self.combo_box_listes.currentText()


        ClientSocket = self.conection()
        AesSocket = AESsocket(ClientSocket, is_server=False)

        MIdUtilisateur = f"SELECT id_utilisateur FROM utilisateurs WHERE pseudo = '{UtilisateurChoisi}'"
        AesSocket.send(MIdUtilisateur)

        RIdUtilisateur = self.AesSocket.recv(1024)

        IdUtilisateur = RIdUtilisateur[0]['id_utilisateur']


        # Récupérer l'ID de la liste sélectionnée

        RequeteIdListe = f"SELECT id_liste FROM listes WHERE nom_liste = '{ListeChoisie}'"
        RequeteIdListe = self.envoyer_requete(RequeteIdListe)

        if not RequeteIdListe or len(RequeteIdListe) == 0:
            QMessageBox.critical(self, "Erreur", "Impossible de récupérer l'ID de la liste sélectionnée.")
            return

        IdListe = RequeteIdListe[0]['id_liste']

        Message = f"INSERT INTO taches (id_tache, taches_id_groupe, taches_id_utilisateur, taches_id_liste, titre_tache, description_tache, datecreation_tache, datefin_tache, recurrence_tache, statut_tache, daterappel_tache, datesuppression_tache) VALUES (NULL,'NULL',{IdUtilisateur},'{IdListe}' , {TitreTache}, {Description}, CURRENT_TIMESTAMP, {DateEcheance}, '', {Statut} ,{DateRappel}, NULL);"

        AesSocket.send(Message)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    formulaire = FormulaireTache()
    formulaire.show()
    sys.exit(app.exec())