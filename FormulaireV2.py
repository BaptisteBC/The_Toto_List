import sys
import pymysql.cursors  # Module pour gérer les connexions MySQL avec curseurs.
import pymysql  # Module pour interagir avec une base de données MySQL.
import socket  # Pour gérer les connexions réseau via des sockets.
from lib.custom import AEScipher, \
    AESsocket  # Classes personnalisées pour gérer le chiffrement AES et les connexions sécurisées.
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QComboBox,
                             QDateEdit, QVBoxLayout, QPushButton,
                             QMessageBox)  # Modules de PyQt5 pour créer l'interface graphique.
from PyQt5.QtCore import QDate  # Utilisé pour gérer les dates dans PyQt5.
from datetime import datetime  # Utilisé pour les opérations sur les dates/heures.

"""Version du formulaire permettant de contacter directement le serveur Python."""


class FormulaireTache(QWidget):
    """
    Classe représentant l'interface graphique pour créer une tâche.

    Attributes:
        connexion (pymysql.Connection): Connexion à la base de données MySQL.
        groupes (list): Liste des groupes (optionnel pour extension future).
        listes (list): Liste des listes disponibles pour organiser les tâches.
        utilisateurs (list): Liste des utilisateurs assignables à une tâche.
        tags (list): Liste des tags disponibles pour catégoriser une tâche (future extension).
    """

    def __init__(self):
        """Initialise le formulaire, la connexion MySQL et charge les données nécessaires."""
        super().__init__()

        # Configure la fenêtre principale
        self.setWindowTitle("Formulaire de Tâche")
        self.setGeometry(100, 100, 400, 600)  # Définit la taille et la position de la fenêtre.

        layout = QVBoxLayout()  # Utilise un layout vertical pour organiser les widgets.

        # Champ pour le nom de la tâche
        self.label_nom = QLabel("Nom de la tâche :")
        self.champ_nom = QLineEdit()  # Zone de texte pour saisir le nom.
        layout.addWidget(self.label_nom)
        layout.addWidget(self.champ_nom)

        # Champ pour la description de la tâche
        self.label_description = QLabel("Description :")
        self.champ_description = QTextEdit()  # Zone de texte multi-lignes pour la description.
        layout.addWidget(self.label_description)
        layout.addWidget(self.champ_description)

        # Sélecteur pour la date d'échéance
        self.label_date = QLabel("Date d'échéance :")
        self.champ_date = QDateEdit()  # Widget pour sélectionner une date.
        self.champ_date.setDate(QDate.currentDate())  # Initialise avec la date actuelle.
        layout.addWidget(self.label_date)
        layout.addWidget(self.champ_date)

        # Sélecteur pour le statut de la tâche
        self.label_statut = QLabel("Statut de la tâche :")
        self.champ_statut = QComboBox()  # Menu déroulant pour sélectionner le statut.
        self.champ_statut.addItems(["à faire", "en cours", "terminé"])  # Options possibles.
        layout.addWidget(self.label_statut)
        layout.addWidget(self.champ_statut)

        # Menu déroulant pour sélectionner la liste
        self.label_liste = QLabel("Liste :")
        self.combo_box_listes = QComboBox()  # Liste déroulante pour choisir une liste.
        layout.addWidget(self.label_liste)
        layout.addWidget(self.combo_box_listes)

        # Menu déroulant pour sélectionner l'utilisateur assigné
        self.label_utilisateur = QLabel("Assigné à :")
        self.combo_box_utilisateurs = QComboBox()  # Liste déroulante pour choisir un utilisateur.
        layout.addWidget(self.label_utilisateur)
        layout.addWidget(self.combo_box_utilisateurs)

        # Sélecteur pour la date de rappel
        self.label_date_rappel = QLabel("Date de rappel :")
        self.champ_date_rappel = QDateEdit()  # Widget pour sélectionner une date de rappel.
        self.champ_date_rappel.setDate(QDate.currentDate())  # Initialise avec la date actuelle.
        layout.addWidget(self.label_date_rappel)
        layout.addWidget(self.champ_date_rappel)

        # Bouton pour soumettre le formulaire
        self.bouton_soumettre = QPushButton("Soumettre")
        self.bouton_soumettre.clicked.connect(self.Envoie)  # Connecte le bouton à la méthode Envoie.
        layout.addWidget(self.bouton_soumettre)

        self.setLayout(layout)  # Applique le layout défini à la fenêtre.

        # Charger les utilisateurs et les listes disponibles
        self.ChargeUtilisateurs()
        self.ChargerListes()

    def conection(self):
        """Établit une connexion sécurisée au serveur via un socket."""
        ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Création d'un socket.
        ClientSocket.connect(('localhost', 12345))  # Connexion au serveur local sur le port 12345.

        # Passe le socket à une version sécurisée avec AES.
        AesSocket = AESsocket(ClientSocket, is_server=False)

    def Deconnection(self):
        """Ferme la connexion avec le serveur."""
        ClientSocket = self.conection()
        ClientSocket.close()

    def ChargerListes(self):
        """Charge les listes disponibles depuis la base de données et les ajoute au menu déroulant."""
        requete_sql = "SELECT nom_liste FROM listes"  # Requête pour récupérer les noms des listes.
        resultats = self.envoyer_requete(requete_sql)  # Envoie la requête et récupère les résultats.

        if resultats:  # Si des résultats sont retournés
            noms_listes = [liste['nom_liste'] for liste in resultats]  # Extrait les noms.
            self.combo_box_listes.addItems(noms_listes)  # Ajoute les noms au menu déroulant.
        else:  # Si aucune liste n'est trouvée
            QMessageBox.warning(self, "Aucune liste",
                                "Aucune liste trouvée ou erreur dans la récupération des données.")

    def ChargeUtilisateurs(self):
        """Charge les utilisateurs depuis la base de données et les ajoute au menu déroulant."""
        requete_sql = "SELECT pseudo FROM utilisateurs"  # Requête pour récupérer les pseudos.
        resultats = self.envoyer_requete(requete_sql)  # Envoie la requête et récupère les résultats.

        if resultats:  # Si des résultats sont retournés
            noms_utilisateurs = [utilisateur['pseudo'] for utilisateur in resultats]  # Extrait les pseudos.
            self.combo_box_utilisateurs.addItems(noms_utilisateurs)  # Ajoute les pseudos au menu déroulant.
        else:  # Si aucun utilisateur n'est trouvé
            QMessageBox.warning(self, "Aucun utilisateur",
                                "Aucun utilisateur trouvé ou erreur dans la récupération des données.")

    def Envoie(self):
        """Récupère les données du formulaire et les envoie au serveur."""
        # Récupère les informations saisies dans le formulaire.
        TitreTache = self.champ_nom.text().strip()
        Description = self.champ_description.toPlainText().strip()
        DateEcheance = self.champ_date.date().toString("yyyy-MM-dd")
        Statut = self.champ_statut.currentText().lower()
        DateRappel = self.champ_date_rappel.date().toString("yyyy-MM-dd")
        UtilisateurChoisi = self.combo_box_utilisateurs.currentText()
        ListeChoisie = self.combo_box_listes.currentText()

        # Connexion sécurisée au serveur.
        ClientSocket = self.conection()
        AesSocket = AESsocket(ClientSocket, is_server=False)

        # Récupération de l'ID utilisateur.
        MIdUtilisateur = f"SELECT id_utilisateur FROM utilisateurs WHERE pseudo = '{UtilisateurChoisi}'"
        AesSocket.send(MIdUtilisateur)
        RIdUtilisateur = AesSocket.recv(1024)
        IdUtilisateur = RIdUtilisateur[0]['id_utilisateur']

        # Récupération de l'ID liste.
        RequeteIdListe = f"SELECT id_liste FROM listes WHERE nom_liste = '{ListeChoisie}'"
        RequeteIdListe = self.envoyer_requete(RequeteIdListe)

        if not RequeteIdListe or len(RequeteIdListe) == 0:  # Vérifie si l'ID liste est valide.
            QMessageBox.critical(self, "Erreur", "Impossible de récupérer l'ID de la liste sélectionnée.")
            return

        IdListe = RequeteIdListe[0]['id_liste']

        # Prépare la requête d'insertion.
        Message = (f"INSERT INTO taches (id_tache, taches_id_groupe, taches_id_utilisateur, taches_id_liste, "
                   f"titre_tache, description_tache, datecreation_tache, datefin_tache, recurrence_tache, "
                   f"statut_tache, daterappel_tache, datesuppression_tache) "
                   f"VALUES (NULL, NULL, {IdUtilisateur}, '{IdListe}', {TitreTache}, {Description}, "
                   f"CURRENT_TIMESTAMP, {DateEcheance}, '', {Statut}, {DateRappel}, NULL);")

        AesSocket.send(Message)  # Envoie la requête d'insertion au serveur.


# Point d'entrée de l'application.
if __name__ == "__main__":
    app = QApplication(sys.argv)  # Initialise l'application PyQt.
    formulaire = FormulaireTache()  # Crée une instance du formulaire.
    formulaire.show()  # Affiche le formulaire.
    sys.exit(app.exec())  # Exécute l'application.
