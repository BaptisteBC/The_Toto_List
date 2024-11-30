import sys
import pymysql.cursors  # Module pour gérer les connexions MySQL avec curseurs.
import pymysql  # Module pour interagir avec une base de données MySQL.
import socket  # Pour gérer les connexions réseau via des sockets.
from lib.custom import AEScipher, AESsocket  # Classes personnalisées pour gérer le chiffrement AES et les connexions sécurisées.
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QComboBox,
    QDateEdit, QVBoxLayout, QPushButton, QMessageBox
)  # Modules de PyQt5 pour créer l'interface graphique.
from PyQt5.QtCore import QDate  # Utilisé pour gérer les dates dans PyQt5.
from datetime import datetime  # Utilisé pour les opérations sur les dates/heures.

"""
Application PyQt5 pour interagir avec un serveur via un formulaire de création de tâches.
"""

class FormulaireTache(QWidget):
    """
    Classe représentant l'interface graphique pour créer une tâche.

    Attributes:
        groupes (list): Liste des groupes (optionnel pour extension future).
        listes (list): Liste des listes disponibles pour organiser les tâches.
        utilisateurs (list): Liste des utilisateurs assignables à une tâche.
        tags (list): Liste des tags disponibles pour catégoriser une tâche (future extension).
    """

    def __init__(self):
        """Initialise le formulaire, configure l'interface graphique et charge les données nécessaires."""
        super().__init__()

        # Configuration de la fenêtre principale
        self.setWindowTitle("Formulaire de Tâche")
        self.setGeometry(100, 100, 400, 600)  # Définit la taille et la position de la fenêtre.

        # Layout principal
        layout = QVBoxLayout()

        # Champ pour le nom de la tâche
        self.label_nom = QLabel("Nom de la tâche :")
        self.champ_nom = QLineEdit()
        layout.addWidget(self.label_nom)
        layout.addWidget(self.champ_nom)

        # Champ pour la description de la tâche
        self.label_description = QLabel("Description :")
        self.champ_description = QTextEdit()
        layout.addWidget(self.label_description)
        layout.addWidget(self.champ_description)

        # Sélecteur pour la date d'échéance
        self.label_date = QLabel("Date d'échéance :")
        self.champ_date = QDateEdit()
        self.champ_date.setDate(QDate.currentDate())  # Initialise avec la date actuelle.
        layout.addWidget(self.label_date)
        layout.addWidget(self.champ_date)

        # Sélecteur pour le statut de la tâche
        self.label_statut = QLabel("Statut de la tâche :")
        self.champ_statut = QComboBox()
        self.champ_statut.addItems(["à faire", "en cours", "terminé"])  # Options possibles.
        layout.addWidget(self.label_statut)
        layout.addWidget(self.champ_statut)

        # Menu déroulant pour sélectionner la liste
        self.label_liste = QLabel("Liste :")
        self.combo_box_listes = QComboBox()
        layout.addWidget(self.label_liste)
        layout.addWidget(self.combo_box_listes)

        # Menu déroulant pour sélectionner l'utilisateur assigné
        self.label_utilisateur = QLabel("Assigné à :")
        self.combo_box_utilisateurs = QComboBox()
        layout.addWidget(self.label_utilisateur)
        layout.addWidget(self.combo_box_utilisateurs)

        # Sélecteur pour la date de rappel
        self.label_date_rappel = QLabel("Date de rappel :")
        self.champ_date_rappel = QDateEdit()
        self.champ_date_rappel.setDate(QDate.currentDate())  # Initialise avec la date actuelle.
        layout.addWidget(self.label_date_rappel)
        layout.addWidget(self.champ_date_rappel)

        # Bouton pour soumettre le formulaire
        self.bouton_soumettre = QPushButton("Soumettre")
        self.bouton_soumettre.clicked.connect(self.Envoie)
        layout.addWidget(self.bouton_soumettre)

        self.setLayout(layout)  # Définit le layout pour la fenêtre.

        # Charger les utilisateurs et les listes disponibles
        self.ChargeUtilisateurs()
        self.ChargerListes()

    def conection(self):
        """
        Établit une connexion sécurisée avec le serveur via un socket.

        Returns:
            AESsocket: Socket sécurisé pour échanger des données chiffrées.
        """
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('localhost', 12345))  # Connexion au serveur local.
            return AESsocket(client_socket, is_server=False)  # Passe au socket sécurisé AES.
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur de connexion au serveur : {e}")

    def Deconnection(self):
        """
        Ferme la connexion avec le serveur.
        """
        client_socket = self.conection()
        if client_socket:
            client_socket.close()

    def ChargerListes(self):
        """
        Charge les listes disponibles depuis le serveur et les ajoute au menu déroulant.
        """
        try:
            requete_sql = "NOM_LISTE"  # Requête pour récupérer les noms des listes.
            resultats = self.envoyer_requete(requete_sql)  # Envoie la requête et récupère les résultats.

            if resultats:
                noms_listes = [liste['nom_liste'] for liste in resultats]
                self.combo_box_listes.addItems(noms_listes)
            else:
                QMessageBox.warning(self, "Aucune liste", "Aucune liste trouvée.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des listes : {e}")

    def ChargeUtilisateurs(self):
        """
        Charge les utilisateurs disponibles depuis le serveur et les ajoute au menu déroulant.
        """
        try:
            requete_sql = "PSUDO_UTILISATEUR"  # Requête pour récupérer les pseudos des utilisateurs.
            resultats = self.envoyer_requete(requete_sql)

            if resultats:
                noms_utilisateurs = [utilisateur['pseudo'] for utilisateur in resultats]
                self.combo_box_utilisateurs.addItems(noms_utilisateurs)
            else:
                QMessageBox.warning(self, "Aucun utilisateur", "Aucun utilisateur trouvé.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des utilisateurs : {e}")

    def Envoie(self):
        """
        Récupère les données du formulaire et les envoie au serveur pour créer une nouvelle tâche.
        """
        try:
            # Récupération des données du formulaire.
            titre_tache = self.champ_nom.text().strip()
            description = self.champ_description.toPlainText().strip()
            date_echeance = self.champ_date.date().toString("yyyy-MM-dd")
            statut = self.champ_statut.currentText().lower()
            date_rappel = self.champ_date_rappel.date().toString("yyyy-MM-dd")
            utilisateur_choisi = self.combo_box_utilisateurs.currentText()
            liste_choisie = self.combo_box_listes.currentText()

            # Connexion au serveur.
            aes_socket = self.conection()
            if not aes_socket:
                return

            # Récupération de l'ID utilisateur.
            message_utilisateur = f"ID_UTILISATEUR:{utilisateur_choisi}"
            aes_socket.send(message_utilisateur.encode('utf-8'))
            id_utilisateur = aes_socket.recv(1024).decode('utf-8')

            # Récupération de l'ID liste.
            message_liste = f"ID_LISTE:{liste_choisie}"
            aes_socket.send(message_liste.encode('utf-8'))
            id_liste = aes_socket.recv(1024).decode('utf-8')

            # Préparation et envoi du message pour créer la tâche.
            message = f"CREATION_TACHE:{id_utilisateur}:{id_liste}:{titre_tache}:{description}:{date_echeance}:{statut}:{date_rappel}"
            aes_socket.send(message.encode('utf-8'))
            QMessageBox.information(self, "Succès", "Tâche créée avec succès.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'envoi : {e}")


# Point d'entrée de l'application.
if __name__ == "__main__":
    app = QApplication(sys.argv)
    formulaire = FormulaireTache()
    formulaire.show()
    sys.exit(app.exec())
