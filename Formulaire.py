# Importation des modules nécessaires pour l'interface graphique, la gestion de la connexion réseau,
# et le chiffrement des données.
import sys
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QTextEdit, QDateEdit, QVBoxLayout, QComboBox,
                             QPushButton, QApplication, QMessageBox)
from PyQt5.QtCore import QDate
import socket
import json
from lib.custom import AESsocket  # Importation d'un socket personnalisé qui gère le chiffrement AES


class FormulaireTache(QWidget):
    """
    Classe représentant l'interface graphique pour créer une tâche.

    Attributes:
        listes (dict): Liste des listes disponibles pour organiser les tâches.
        utilisateurs (dict): Liste des utilisateurs assignables à une tâche.
    """

    def __init__(self):
        """Initialise le formulaire, configure l'interface graphique et charge les données nécessaires."""
        super().__init__()

        # Configuration de la fenêtre principale : titre et dimensions de la fenêtre
        self.setWindowTitle("Formulaire de Tâche")
        self.setGeometry(100, 100, 400, 600)

        # Layout principal : Utilisation d'un QVBoxLayout pour organiser les widgets verticalement
        layout = QVBoxLayout()

        # Champ pour le nom de la tâche
        self.label_nom = QLabel("Nom de la tâche :")  # Etiquette pour le champ du nom
        self.champ_nom = QLineEdit()  # Champ de saisie du nom
        layout.addWidget(self.label_nom)
        layout.addWidget(self.champ_nom)

        # Champ pour la description de la tâche
        self.label_description = QLabel("Description :")  # Etiquette pour la description
        self.champ_description = QTextEdit()  # Champ de texte pour la description
        layout.addWidget(self.label_description)
        layout.addWidget(self.champ_description)

        # Sélecteur pour la date d'échéance
        self.label_date = QLabel("Date d'échéance :")  # Etiquette pour la date d'échéance
        self.champ_date = QDateEdit()  # Sélecteur de date
        self.champ_date.setDate(QDate.currentDate())  # Date initiale : date actuelle
        self.champ_date.setCalendarPopup(True)  # Affichage d'un calendrier au clic
        layout.addWidget(self.label_date)
        layout.addWidget(self.champ_date)

        # Menu déroulant pour sélectionner la liste
        self.label_liste = QLabel("Liste :")  # Etiquette pour le menu déroulant de liste
        self.combo_box_listes = QComboBox()  # Menu déroulant pour les listes
        layout.addWidget(self.label_liste)
        layout.addWidget(self.combo_box_listes)

        # Menu déroulant pour sélectionner l'utilisateur assigné
        self.label_utilisateur = QLabel("Assigné à :")  # Etiquette pour le menu déroulant des utilisateurs
        self.combo_box_utilisateurs = QComboBox()  # Menu déroulant pour les utilisateurs
        layout.addWidget(self.label_utilisateur)
        layout.addWidget(self.combo_box_utilisateurs)

        # Sélecteur pour la date de rappel
        self.label_date_rappel = QLabel("Date de rappel :")  # Etiquette pour la date de rappel
        self.champ_date_rappel = QDateEdit()  # Sélecteur de date pour le rappel
        self.champ_date_rappel.setDate(QDate.currentDate())  # Date initiale : date actuelle
        self.champ_date_rappel.setCalendarPopup(True)  # Affichage d'un calendrier au clic
        layout.addWidget(self.label_date_rappel)
        layout.addWidget(self.champ_date_rappel)

        # Bouton pour soumettre le formulaire
        self.bouton_soumettre = QPushButton("Soumettre")  # Bouton pour soumettre le formulaire
        self.bouton_soumettre.clicked.connect(self.Envoie)  # Connexion de l'action du bouton à la méthode Envoie
        layout.addWidget(self.bouton_soumettre)

        self.setLayout(layout)  # Applique le layout à la fenêtre

        # Variables pour stocker les données récupérées des utilisateurs et des listes
        self.listes = {}
        self.utilisateurs = {}

        # Charger les utilisateurs et les listes disponibles depuis le serveur
        self.ChargerUtilisateurs()
        self.ChargerListes()

    def conection(self):
        """
        Établit une connexion sécurisée avec le serveur via un socket.

        Returns:
            AESsocket: Socket sécurisé pour échanger des données chiffrées.
        """
        try:
            # Création du socket pour la connexion avec le serveur (adresse locale et port 12345)
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('localhost', 12345))  # Connexion au serveur local
            return AESsocket(client_socket, is_server=False)  # Retourne un socket sécurisé
        except Exception as e:
            # Affichage d'un message d'erreur si la connexion échoue
            QMessageBox.critical(self, "Erreur de connexion", f"Erreur de connexion au serveur : {e}")
            return None

    def ChargerListes(self):
        """Charge les listes disponibles depuis le serveur et les ajoute au menu déroulant."""
        try:
            aes_socket = self.conection()  # Tentative de connexion
            if not aes_socket:
                return  # Si la connexion échoue, on retourne sans charger les listes

            aes_socket.send("GET_LISTES")  # Envoi de la requête pour obtenir les listes
            reponse_listes = aes_socket.recv(1024)  # Réception de la réponse du serveur
            resultats_listes = json.loads(reponse_listes)  # Décodage des données JSON reçues

            if "error" in resultats_listes:  # Si une erreur est retournée, on l'affiche
                QMessageBox.warning(self, "Erreur", resultats_listes["error"])
            else:
                # Remplir le dictionnaire des listes et ajouter les options au menu déroulant
                self.listes = {liste['nom_liste']: liste['id'] for liste in resultats_listes}
                self.combo_box_listes.addItems(self.listes.keys())  # Ajout des noms des listes au combo box
        except Exception as e:
            # Affichage d'un message d'erreur en cas de problème lors du chargement des listes
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des listes : {e}")

    def ChargerUtilisateurs(self):
        """Charge les utilisateurs assignables à une tâche depuis le serveur et les ajoute au menu déroulant."""
        try:
            aes_socket = self.conection()  # Tentative de connexion
            if not aes_socket:
                return  # Si la connexion échoue, on retourne sans charger les utilisateurs

            aes_socket.send("GET_UTILISATEURS")  # Envoi de la requête pour obtenir les utilisateurs
            reponse_utilisateurs = aes_socket.recv(1024)  # Réception de la réponse du serveur
            resultats_utilisateurs = json.loads(reponse_utilisateurs)  # Décodage des données JSON reçues

            if resultats_utilisateurs:
                # Remplir le dictionnaire des utilisateurs et ajouter les options au menu déroulant
                self.utilisateurs = {utilisateur['pseudo']: utilisateur['id'] for utilisateur in resultats_utilisateurs}
                self.combo_box_utilisateurs.addItems(self.utilisateurs.keys())  # Ajout des pseudos des utilisateurs
            else:
                # Affichage d'un message si aucun utilisateur n'est trouvé
                QMessageBox.information(self, "Information", "Aucun utilisateur trouvé.")
        except Exception as e:
            # Affichage d'un message d'erreur en cas de problème lors du chargement des utilisateurs
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des utilisateurs : {e}")

    def Envoie(self):
        """Récupère les données du formulaire et les envoie au serveur pour créer une nouvelle tâche."""
        try:
            # Récupération des informations du formulaire
            titre_tache = self.champ_nom.text().strip()
            description = self.champ_description.toPlainText().strip()
            date_echeance = self.champ_date.date().toString("yyyy-MM-dd")  # Format de la date
            date_rappel = self.champ_date_rappel.date().toString("yyyy-MM-dd")

            pseudo_choisi = self.combo_box_utilisateurs.currentText()
            nom_liste_choisie = self.combo_box_listes.currentText()

            # Récupération des ID associés à l'utilisateur et à la liste choisis
            id_utilisateur = self.utilisateurs.get(pseudo_choisi, None)
            id_liste = self.listes.get(nom_liste_choisie, None)

            # Vérification si l'utilisateur ou la liste n'a pas été sélectionné
            if not id_utilisateur or not id_liste:
                QMessageBox.warning(self, "Erreur", "Utilisateur ou liste non sélectionné.")
                return

            # Envoi des informations au serveur pour créer la tâche
            aes_socket = self.conection()
            if not aes_socket:
                return  # Si la connexion échoue, on retourne sans envoyer les données

            message = f"CREATION_TACHE:{id_utilisateur}:{id_liste}:{titre_tache}:{description}:{date_echeance}:0:{date_rappel}"
            aes_socket.send(message)  # Envoi des données de création de la tâche au serveur

            # Affichage d'un message de succès
            QMessageBox.information(self, "Succès", "Tâche créée avec succès.")
        except Exception as e:
            # Affichage d'un message d'erreur si un problème survient lors de l'envoi
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'envoi : {e}")


# Point d'entrée de l'application.
if __name__ == "__main__":
    # Création de l'application PyQt et lancement de l'interface graphique
    app = QApplication(sys.argv)
    formulaire = FormulaireTache()  # Création de la fenêtre du formulaire
    formulaire.show()  # Affichage de la fenêtre
    sys.exit(app.exec_())  # Exécution de l'application
