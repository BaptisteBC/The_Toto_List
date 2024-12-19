from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
    QTreeWidgetItem, QTreeWidget, QDateEdit, QTextEdit, QComboBox, QMessageBox, QLineEdit, QDialog, QDialogButtonBox
)
from PyQt5.QtCore import Qt, QDate, QSize, QCoreApplication, pyqtSignal
from PyQt5.QtGui import QPalette, QColor, QIcon, QKeySequence, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QComboBox,
    QDateEdit, QVBoxLayout, QPushButton, QMessageBox, QGridLayout, QListWidget, QListWidgetItem, QProgressBar, QAction
)  # Modules de PyQt5 pour créer l'interface graphique.
from lib.custom import AEScipher, AESsocket # Classes personnalisées pour gérer le chiffrement AES et les connexions sécurisées.
import sys
import pymysql.cursors  # Module pour gérer les connexions MySQL avec curseurs.
import pymysql  # Module pour interagir avec une base de données MySQL.
import socket  # Pour gérer les connexions réseau via des sockets.
from datetime import datetime  # Utilisé pour les opérations sur les dates/heures.
import json
import hashlib
import bcrypt
import time
from bcrypt import gensalt
from statsmodels.distributions import ECDFDiscrete
import re
import requests
from typing import Tuple

#Création de la tâche (Yann)
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

        # Configuration de la fenêtre principale
        self.setWindowTitle("Formulaire de Tâche")
        self.setGeometry(100, 100, 400, 600)

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
        self.champ_date.setDate(QDate.currentDate())
        self.champ_date.setCalendarPopup(True)
        layout.addWidget(self.label_date)
        layout.addWidget(self.champ_date)

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
        self.champ_date_rappel.setDate(QDate.currentDate())
        self.champ_date_rappel.setCalendarPopup(True)
        layout.addWidget(self.label_date_rappel)
        layout.addWidget(self.champ_date_rappel)

        # Bouton pour soumettre le formulaire
        self.bouton_soumettre = QPushButton("Soumettre")
        self.bouton_soumettre.clicked.connect(self.Envoie)
        layout.addWidget(self.bouton_soumettre)

        self.setLayout(layout)

        # Variables pour stocker les données récupérées
        self.listes = {}
        self.utilisateurs = {}

        # Charger les utilisateurs et les listes disponibles
        self.ChargerUtilisateurs()
        self.ChargerListes()

    def conection(self):
        """
        Établit une connexion sécurisée avec le serveur via un socket.

        Returns:
            AESsocket: Socket sécurisé pour échanger des données chiffrées.
        """
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('localhost', 55555))
            return AESsocket(client_socket, is_server=False)
        except Exception as e:
            QMessageBox.critical(self, "Erreur de connexion", f"Erreur de connexion au serveur : {e}")
            return None

    def ChargerListes(self):
        """Charge les listes disponibles depuis le serveur et les ajoute au menu déroulant."""
        try:
            aes_socket = self.conection()
            if not aes_socket:
                return

            aes_socket.send("GET_LISTES")
            reponse_listes = aes_socket.recv(1024)
            resultats_listes = json.loads(reponse_listes)

            if "error" in resultats_listes:
                QMessageBox.warning(self, "Erreur", resultats_listes["error"])
            else:
                self.listes = {liste['nom_liste']: liste['id'] for liste in resultats_listes}
                self.combo_box_listes.addItems(self.listes.keys())
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des listes : {e}")

    def ChargerUtilisateurs(self):
        """Charge les utilisateurs assignables à une tâche depuis le serveur et les ajoute au menu déroulant."""
        try:
            aes_socket = self.conection()
            if not aes_socket:
                return

            aes_socket.send("GET_UTILISATEURS")
            reponse_utilisateurs = aes_socket.recv(1024)
            resultats_utilisateurs = json.loads(reponse_utilisateurs)

            if resultats_utilisateurs:
                self.utilisateurs = {utilisateur['pseudo']: utilisateur['id'] for utilisateur in resultats_utilisateurs}
                self.combo_box_utilisateurs.addItems(self.utilisateurs.keys())
            else:
                QMessageBox.information(self, "Information", "Aucun utilisateur trouvé.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des utilisateurs : {e}")

    def Envoie(self):
        """Récupère les données du formulaire et les envoie au serveur pour créer une nouvelle tâche."""
        try:
            # Récupération des informations
            titre_tache = self.champ_nom.text().strip()
            description = self.champ_description.toPlainText().strip()
            date_echeance = self.champ_date.date().toString("yyyy-MM-dd")
            date_rappel = self.champ_date_rappel.date().toString("yyyy-MM-dd")

            pseudo_choisi = self.combo_box_utilisateurs.currentText()
            nom_liste_choisie = self.combo_box_listes.currentText()

            id_utilisateur = self.utilisateurs.get(pseudo_choisi, None)
            id_liste = self.listes.get(nom_liste_choisie, None)

            if not id_utilisateur or not id_liste:
                QMessageBox.warning(self, "Erreur", "Utilisateur ou liste non sélectionné.")
                return

            aes_socket = self.conection()
            if not aes_socket:
                return

            message = f"CREATION_TACHE:{id_utilisateur}:{id_liste}:{titre_tache}:{description}:{date_echeance}:0:{date_rappel}"
            aes_socket.send(message)

            QMessageBox.information(self, "Succès", "Tâche créée avec succès.")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'envoi : {e}")

#GUI Principal (Thibaut)
class TodoListApp(QMainWindow):
    def __init__(self, pseudonyme_utilisateur, motdepasse_utilisateur):
        try :
            super().__init__()
            self.HOST = '127.0.0.1'
            self.PORT = 55555
            self.utilisateur = pseudonyme_utilisateur
            self.motDePasse = motdepasse_utilisateur
            self.initUI()
            self.formulaire = FormulaireTache()
            self.setWindowTitle("The ToDo List")
            self.setGeometry(100, 100, 1000, 400)
            grid = QGridLayout()
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.HOST, self.PORT))
            self.client_socket = AESsocket(self.client_socket, is_server=False)
            time.sleep(0.5)
            self.client_socket.send(f"AUTH:{pseudonyme_utilisateur}:{motdepasse_utilisateur}")

            self.creerActions()
            self.creerMenu()
        except Exception as e:
            QMessageBox.critical(self, 'Erreur', f'Erreur lors du chargement de la fenetre {e}')

        # Widget central pour le contenu principal
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)

        # Création de la colonne latérale (sidebar)
        self.sidebar = QWidget()
        sidebar_layout = QVBoxLayout(self.sidebar)

        # Boutons déplacés vers la colonne latérale
        self.settings_button = QPushButton("Paramètres")
        self.help_button = QPushButton("Aide")
        self.credits_button = QPushButton("Crédits")

        # Connexion des boutons de la colonne latérale
        self.settings_button.clicked.connect(self.open_settings)
        self.help_button.clicked.connect(self.open_help)
        self.credits_button.clicked.connect(self.open_credits)

        # Ajout des boutons à la colonne latérale
        sidebar_layout.addWidget(self.settings_button)
        sidebar_layout.addWidget(self.help_button)
        sidebar_layout.addWidget(self.credits_button)

        main_layout.addWidget(self.sidebar)

        # Zone principale de l'application
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)

        # Barre de navigation avec le bouton pour afficher/cacher la colonne latérale
        nav_layout = QHBoxLayout()
        # Utilisation d'une icône pour le bouton d'affichage de la colonne
        self.toggle_sidebar_button = QPushButton()
        icon_url = "https://icons.veryicon.com/png/o/miscellaneous/we/sidebar-2.png"  # Remplacez par l'URL réelle
        self.set_icon_from_url(self.toggle_sidebar_button, icon_url)
        self.toggle_sidebar_button.setFixedSize(30, 30)  # Taille de l'icône
        self.toggle_sidebar_button.clicked.connect(self.toggle_sidebar)

        self.bouton_actualiser = QPushButton("Actualiser")
        self.bouton_restaurer_corb = QPushButton("Restaurer la corbeille")
        self.taches = QListWidget()
        self.bouton_vider_corb = QPushButton("Vider la corbeille")
        self.bouton_quitter = QPushButton("Quitter")

        sidebar_layout.addWidget(self.bouton_actualiser)
        sidebar_layout.addWidget(self.bouton_restaurer_corb)
        sidebar_layout.addWidget(self.taches)
        sidebar_layout.addWidget(self.bouton_vider_corb)
        sidebar_layout.addWidget(self.bouton_quitter)

        self.bouton_actualiser.clicked.connect(self.actualiser)
        self.bouton_restaurer_corb.clicked.connect(self.restaurer)
        self.bouton_vider_corb.clicked.connect(self.vider)
        self.bouton_quitter.clicked.connect(self.quitter)

        self.cnx = pymysql.connect(host="127.0.0.1", user="root", password="toto", database="TheTotoDB")
        self.actualiser()

        # Ajout du bouton icône en haut à gauche
        nav_layout.addWidget(self.toggle_sidebar_button)

        # Bouton "Ouvrir Formulaire"
        self.form_button = QPushButton("Ouvrir Formulaire")
        self.form_button.clicked.connect(self.open_formulaire)

        nav_layout.addWidget(self.form_button)

        nav_layout.setContentsMargins(5, 0, 5, 0)

        # Bouton mode sombre déplacé vers la droite
        self.theme_button = QPushButton()
        icon_url = "https://png.pngtree.com/png-clipart/20220812/ourmid/pngtree-shine-sun-light-effect-free-png-and-psd-png-image_6106445.png"  # Remplacez par l'URL réelle
        self.set_icon_from_url(self.theme_button, icon_url)
        self.theme_button.setIconSize(QSize(20, 20))  # Réduire la taille de l'icône à 20x20
        self.theme_button.setFixedSize(30, 30)  # Réduire la taille du bouton à 30x30
        self.theme_button.clicked.connect(self.toggle_theme)
        nav_layout.addWidget(self.theme_button)
        self.main_layout.addLayout(nav_layout)

        #Arborescence des tâches
        self.task_tree = QTreeWidget()
        self.task_tree.setHeaderLabels(["Nom tâche", "Échéance", "Description", "Liste", "Statut", "Priorité"])
        self.main_layout.addWidget(self.task_tree)

        # Connecter l'événement de clic sur une tâche
        self.main_layout.addWidget(self.task_tree)
        main_layout.addWidget(self.main_widget)

        # Définir le widget central pour QMainWindow
        self.setCentralWidget(central_widget)

        self.is_dark_mode = False

    def actualiser(self):
        """Fonction d'actualisation des tâches.
        Lorsque le bouton est cliqué, effectue une requête dans la table tâche et récupère le champ 'titre_tache' pour \
        l'afficher dans la fenêtre principale."""

        curseur = self.cnx.cursor()

        # Extraction de tous les titres des taches principales
        curseur.execute("SELECT id_tache, titre_tache, datesuppression_tache FROM taches;")
        resultache = curseur.fetchall()

        # Extraction de tous les titres des sous taches
        curseur.execute("SELECT id_soustache, titre_soustache, soustache_id_tache, datesuppression_soustache FROM "
                        "soustaches;")
        sousresultache = curseur.fetchall()

        self.taches.clear()

        for id_tache, titre_tache, datesuppression_tache in resultache:
            if datesuppression_tache:
                pass
            else:
                self.afficherTache(id_tache, titre_tache)

                for id_soustache, titre_soustache, soustache_id_tache, datesuppression_tache in sousresultache:
                    if datesuppression_tache:
                        pass
                    elif soustache_id_tache == id_tache:
                        self.afficherTache(id_soustache, f'|=>{titre_soustache}', soustache_id_tache)

        curseur.close()

    def afficherTache(self, id_tache, titre_tache, soustache_id_tache=None):
        item = QListWidgetItem()
        tache = QWidget()

        bouton = QPushButton(titre_tache)
        suppr = QPushButton('X')
        suppr.setFixedWidth(30)

        layout = QHBoxLayout(tache)
        layout.addWidget(bouton)
        layout.addWidget(suppr)
        layout.addStretch()

        bouton.clicked.connect(lambda: self.detail(id_tache, soustache_id_tache))
        suppr.clicked.connect(lambda: self.supprimer(id_tache, soustache_id_tache))

        item.setSizeHint(tache.sizeHint())

        self.taches.addItem(item)
        self.taches.setItemWidget(item, tache)

    def detail(self, id_tache, soustache_id_tache):
        curseur = self.cnx.cursor()

        if soustache_id_tache:
            curseur.execute("SELECT titre_soustache, description_soustache, datecreation_soustache, "
                            "datefin_soustache, statut_soustache, daterappel_soustache FROM soustaches;")
        else:
            curseur.execute("SELECT titre_tache, description_tache, datecreation_tache, datefin_tache,  "
                            "recurrence_tache, statut_tache, daterappel_tache, datesuppression_tache FROM taches;")

        curseur.close()

    def restaurer(self):
        Restaurer(self.cnx).exec()
        self.actualiser()

    def supprimer(self, id_tache, soustache_id_tache):
        if not soustache_id_tache:  # Tache
            Supprimer(id_tache, soustache_id_tache, self.cnx).exec()
            self.actualiser()

        else:  # Sous-tache
            Supprimer(id_tache, soustache_id_tache, self.cnx).exec()
            self.actualiser()

    def vider(self):
        Vider_corbeille(self.cnx).exec()

    def quitter(self):
        self.cnx.close()
        QCoreApplication.exit(0)

    def set_icon_from_url(self, button, url):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers, stream=True)
            response.raise_for_status()  # Vérifie les erreurs HTTP
            pixmap = QPixmap()
            if not pixmap.loadFromData(response.content):
                raise ValueError("Impossible de charger l'image à partir des données.")
            icon = QIcon(pixmap)
            button.setIcon(icon)
        except Exception as e:
            print(f"Erreur lors du chargement de l'image : {e}")
            QMessageBox.warning(self, "Erreur d'image", f"Impossible de charger l'image depuis {url} : {e}")

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

    def toggle_sidebar(self):
        # Bascule de la visibilité de la colonne latérale
        self.sidebar.setVisible(not self.sidebar.isVisible())

    def open_formulaire(self):
        print("Signal reçu : ouverture du formulaire en cours...")
        try:
            self.formulaire_window = FormulaireTache()
            self.formulaire_window.show()
        except Exception as e:
            print(f"Erreur lors de l'ouverture du formulaire : {e}")

    def toggle_theme(self):
        if not self.is_dark_mode:
            self.set_dark_mode()
            icon_url = "https://icones.pro/wp-content/uploads/2021/02/icone-de-la-lune-grise.png"  # Remplacez par l'URL réelle
            self.set_icon_from_url(self.theme_button, icon_url)  # Icône Lune pour le mode sombre
        else:
            self.set_light_mode()
            icon_url = "https://png.pngtree.com/png-clipart/20220812/ourmid/pngtree-shine-sun-light-effect-free-png-and-psd-png-image_6106445.png"  # Remplacez par l'URL réelle
            self.set_icon_from_url(self.theme_button, icon_url)  # Icône Soleil pour le mode clair
        self.is_dark_mode = not self.is_dark_mode

    def set_dark_mode(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.white)
        QApplication.instance().setPalette(dark_palette)
        # Appliquer les styles en mode sombre pour les autres widgets
        dark_style = """
            QWidget {
                background-color: #353535;
                color: white;
            }
            QLabel {
                color: white;
            }
            QLineEdit, QTextEdit, QComboBox, QDateEdit {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #555555;
            }
            QPushButton {
                background-color: #444444;
                color: white;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QPushButton:pressed {
                background-color: #333333;
            }
            QTreeWidget {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #555555;
            }
            QHeaderView::section {
                background-color: #444444;
                color: white;
                padding: 4px;
                border: 1px solid #222222;
            }
        """
        self.setStyleSheet(dark_style)
    def set_light_mode(self):
        # Réinitialiser le style de l'application au style par défaut
        QApplication.instance().setPalette(QApplication.style().standardPalette())
        self.setStyleSheet("")  # Supprimer les styles personnalisés

    def open_settings(self):
        QMessageBox.information(self, "Paramètres", "Ouvrir les paramètres")

    def open_help(self):
        QMessageBox.information(self, "Aide", "Besoin d'aide ? \n \nSuivez ce lien pour comprendre comment utiliser votre application de ToDoList 😉 : https://github.com/BaptisteBC/The_Toto_List")

    def open_credits(self):
        QMessageBox.information(self, "Crédits","Application développée par les personnes suivantes : \n\n - BLANC-CARRIER Baptiste \n - BLANCK Yann \n - COSENZA Thibaut \n - DE AZEVEDO Kévin \n - GASSER Timothée \n - MARTIN Jean-Christophe \n - MERCKLE Florian \n - MOUROT Corentin \n - TRÉPIER Timothée\n\n © 2024 TheTotoList. Tous droits réservés. Développé par TheTotoGroup.")

class Supprimer(QDialog):
    def __init__(self, id_tache, soustache_id_tache, cnx):
        super().__init__()

        self.setWindowTitle("Supprimer")

        grid = QGridLayout()
        self.setLayout(grid)
        self.resize(300, 150)

        self.titre = QLabel("Supprimer la tâche")
        self.confirmer = QPushButton("Confirmer")
        self.annuler = QPushButton("Annuler")

        grid.addWidget(self.titre)
        grid.addWidget(self.confirmer)
        grid.addWidget(self.annuler)

        self.id_tache:str = id_tache
        self.cnx = cnx
        self.soustache_id_tache = soustache_id_tache

        self.confirmer.clicked.connect(self.conf)
        self.annuler.clicked.connect(self.stop)

    def conf(self):
        try :
            curseur = self.cnx.cursor()
            if not self.soustache_id_tache:
                curseur.execute(f'UPDATE taches SET datesuppression_tache = NOW() WHERE id_tache = "{self.id_tache}";')
                curseur.execute(f'UPDATE soustaches SET datesuppression_soustache = NOW() '
                                f'WHERE soustache_id_tache = "{self.id_tache}";')
            else:
                curseur.execute(f'UPDATE soustaches SET datesuppression_soustache = NOW() '
                            f'WHERE id_soustache = "{self.id_tache}";')
            self.cnx.commit()
            curseur.close()

            msg = QMessageBox()
            msg.setWindowTitle("Confirmation")
            msg.setText("Tache correctement supprimée")
            msg.exec()

            self.close()
        except Exception as E:
            print(E)

    def stop(self):
       self.close()

class Vider_corbeille(QDialog):
    def __init__(self, cnx):
        super().__init__()

        self.cnx = cnx

        self.setWindowTitle("Vider la corbeille")

        grid = QGridLayout()
        self.setLayout(grid)
        self.resize(300, 150)

        self.titre = QLabel("!!! Attention : Vider la corbeille !!!")
        self.confirmer = QPushButton("Confirmer")
        self.annuler = QPushButton("Annuler")

        grid.addWidget(self.titre)
        grid.addWidget(self.confirmer)
        grid.addWidget(self.annuler)

        self.confirmer.clicked.connect(self.conf)
        self.annuler.clicked.connect(self.stop)

    def conf(self):
        curseur = self.cnx.cursor()
        curseur.execute(f'DELETE FROM soustaches WHERE datesuppression_soustache is not NULL;')
        curseur.execute(f'DELETE FROM taches WHERE datesuppression_tache is not NULL;')

        self.cnx.commit()
        curseur.close()

        msg = QMessageBox()
        msg.setWindowTitle("Confirmation")
        msg.setText("La corbeille a été vidée")
        msg.exec()

        self.close()

    def stop(self):
       self.close()

class Restaurer(QDialog):
    def __init__(self, cnx):
        super().__init__()

        self.cnx = cnx

        self.setWindowTitle("Restaurer la corbeille")

        grid = QGridLayout()
        self.setLayout(grid)
        self.resize(300, 150)

        self.titre = QLabel("Restaurer la corbeille ?")
        self.confirmer = QPushButton("Confirmer")
        self.annuler = QPushButton("Annuler")

        grid.addWidget(self.titre)
        grid.addWidget(self.confirmer)
        grid.addWidget(self.annuler)

        self.confirmer.clicked.connect(self.conf)
        self.annuler.clicked.connect(self.stop)

    def conf(self):
        curseur = self.cnx.cursor()
        curseur.execute('UPDATE taches SET datesuppression_tache = NULL WHERE datesuppression_tache IS NOT NULL;')
        curseur.execute('UPDATE soustaches SET datesuppression_soustache = NULL WHERE datesuppression_soustache '
                        'IS NOT NULL;')
        self.cnx.commit()
        curseur.close()

        msg = QMessageBox()
        msg.setWindowTitle("Confirmation")
        msg.setText("La corbeille a été restaurée !")
        msg.exec()

        self.close()

    def stop(self):
       self.close()

#Fenêtre d'authentification
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
    Cette méthode affiche le formulaire d'inscription pour les nouveaux utilisateurs.
    """
        try:
            self.effacerWidgets()
            self.setWindowTitle('Inscription')

            # Champs d'inscription
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

            self.lblmotDePasseConfirm = QLabel('Confirmer le mot de passe:', self)
            self.tbxmotDePasseConfirm = QLineEdit(self)
            self.tbxmotDePasseConfirm.setEchoMode(QLineEdit.Password)

            # Barre de progression et label pour la complexité
            self.password_strength_bar = QProgressBar(self)
            self.password_strength_bar.setRange(0, 100)
            self.password_strength_bar.setTextVisible(False)

            self.password_strength_label = QLabel("Complexité : Très faible", self)

            # Connecter les événements pour la validation en temps réel
            self.tbxmotDePasse.textChanged.connect(self.MAJComplexiteMotDePasse)

            # Boutons
            self.btnInscription = QPushButton('Créer un compte', self)
            self.btnInscription.clicked.connect(self.inscriptionUtilisateur)
            self.btnInscription.setDefault(True)

            self.btnSwitch = QPushButton('Retour à la connexion', self)
            self.btnSwitch.clicked.connect(self.affichageFormulaireAuthentification)

            # Gestion de la touche "Entrée"
            self.tbxEmail.returnPressed.connect(self.btnInscription.click)
            self.tbxNom.returnPressed.connect(self.btnInscription.click)
            self.tbxPrenom.returnPressed.connect(self.btnInscription.click)
            self.tbxPseudo.returnPressed.connect(self.btnInscription.click)
            self.tbxmotDePasseConfirm.returnPressed.connect(self.btnInscription.click)

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
            self.layout.addWidget(self.lblmotDePasseConfirm)
            self.layout.addWidget(self.tbxmotDePasseConfirm)
            self.layout.addWidget(self.password_strength_bar)
            self.layout.addWidget(self.password_strength_label)
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
        Fonction qui traite la création de compte.
        """
        email = self.tbxEmail.text()
        nom = self.tbxNom.text()
        prenom = self.tbxPrenom.text()
        pseudo = self.tbxPseudo.text()
        motDePasse = self.tbxmotDePasse.text()
        motDePasseConfirm = self.tbxmotDePasseConfirm.text()

        # Vérifier les champs non vides
        if not (email and nom and prenom and pseudo and motDePasse and motDePasseConfirm):
            QMessageBox.critical(self, 'Erreur', 'Tous les champs sont obligatoires.')
            return
        # Vérification des mots de passe
        if motDePasse != motDePasseConfirm:
            QMessageBox.critical(self, 'Erreur', 'Les mots de passe ne correspondent pas.')
            return

        # Vérification de l'email
        if not self.validationDesEmail(email):
            QMessageBox.critical(self, 'Erreur', 'Adresse email invalide.')
            return


        # Vérification des caractères interdits
        if not all(self.validationDesEntrees(field) for field in [nom, prenom, pseudo, motDePasse]):
            QMessageBox.critical(self, 'Erreur', 'Les champs contiennent des caractères interdits.')
            return

        # Envoi des données au serveur
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((self.HOST, self.PORT))
            client_socket = AESsocket(client_socket, is_server=False)

            #generarion du sel et hashage du mot de passe
            salt=bcrypt.gensalt()
            motDePasse=motDePasse.encode('utf-8')
            motDePasseHache = bcrypt.hashpw(motDePasse, salt)
            motDePasseHacheDecode=motDePasseHache.decode('utf-8')

            message = f"CREATE_ACCOUNT:{email}:{nom}:{prenom}:{pseudo}:{motDePasseHacheDecode}"
            client_socket.send(message)
            response = client_socket.recv(1024)

            if response.startswith("ACCOUNT_CREATED"):
                QMessageBox.information(self, 'Succès', 'Compte créé avec succès !')
                self.affichageFormulaireAuthentification()
            elif response.startswith("EMAIL_TAKEN"):
                QMessageBox.critical(self, 'Erreur', 'Adresse email déjà utilisée.')
            elif response.startswith("PSEUDO_TAKEN"):
                QMessageBox.critical(self, 'Erreur', 'Le pseudo est déjà utilisé.')
            client_socket.close()
        except Exception as e:
            QMessageBox.critical(self, 'Erreur', f"Erreur lors de la création du compte : {e}")

    def MAJComplexiteMotDePasse(self):
        """
        Évalue la complexité du mot de passe et met à jour la barre et le label.
        """
        try :
            motDePasse = self.tbxmotDePasse.text()
            print(motDePasse)
            complexite = self.evaluerMotDePasse(motDePasse)

            niveaux = {
                "Très faible": (0, "red"),
                "Faible": (25, "orange"),
                "Moyennement sécurisé": (50, "yellow"),
                "Sécurisé": (75, "lightgreen"),
                "Très sécurisé": (100, "green")
            }
        except Exception as e:
            print(f'Echec lors du test de complexité: {e}')

        niveau, couleur = niveaux[complexite]
        self.password_strength_bar.setValue(niveau)
        self.password_strength_bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {couleur}; }}")
        self.password_strength_label.setText(f"Complexité : {complexite}")

    def evaluerMotDePasse(self, MDP):
        """
        cette methode evalue la complexité du mot de passe et renvoie une chaine de caractere a la methode MAJComplexiteMotDePasse qui affichera le progrès sous forme de barre de progres
        :param MDP: string - mot de passe entré
        :return: srting - compléxité actuelle
        """
        try:
            # Initialiser les critères
            if len(MDP) >= 8 and len(MDP) <14 :
                longueurMotDePasse = 1
            elif len(MDP)>=14 and len(MDP) <20:
                longueurMotDePasse=2
            elif len(MDP)>=20:
                longueurMotDePasse=3
            else:
                longueurMotDePasse = -1
            critereMinuscule = bool(re.search(r'[a-z]', MDP))
            critereMajuscule = bool(re.search(r'[A-Z]', MDP))
            critereChiffre = bool(re.search(r'\d', MDP))
            critereCaractereSpecial = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', MDP))

            # Compter combien de critères sont respectés
            complexite = sum(
                [longueurMotDePasse, critereMinuscule, critereMajuscule, critereChiffre, critereCaractereSpecial]
            )
            print(complexite)
            # Déterminer le niveau de complexité
            if complexite >= 5:
                return "Très sécurisé"
            elif complexite == 4:
                return "Sécurisé"
            elif complexite == 3:
                return "Moyennement sécurisé"
            elif complexite == 2:
                return "Faible"
            else:
                return "Très faible"
        except Exception as e:
            print(f'Erreur lors de l\'évaluation de complexité : {e}')
            return "Très faible"

    def validationDesEntrees(self, input_text):
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

#Fenêtre changement de mot de passe
class ChangemotDePasseWindow(QDialog):
    '''
    cette classe va ouvrir une fenetre afin que l'utilisateur puisse changer son mot de passe
    '''
    def __init__(self, utilisateur, client_socket):
        super().__init__()
        self.initUI()
        self.utilisateur = utilisateur
        try :
            self.HOST = '127.0.0.1'
            self.PORT = 55555
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.HOST, self.PORT))
            self.client_socket = AESsocket(self.client_socket, is_server=False)
        except Exception as e:
            QMessageBox.critical(self, 'Erreur',
                                 f'Erreur lors du chargement du formulaire de changement de mot de passse: {e}')

        self.motDePasse=None
    def initUI(self):
        """
        initialisation et affichage du formulaire de changement de mot de Passe
        :return: void
        """
        try :
            self.setGeometry(300, 300, 300, 200)
            self.setWindowTitle('Changer le mot de passe')

            self.lblNouvMDP = QLabel('Nouveau mot de passe:', self)
            self.tbxNouvMDP = QLineEdit(self)
            self.tbxNouvMDP.setEchoMode(QLineEdit.Password)

            self.lblConfirm = QLabel('Confirmer le mot de passe:', self)
            self.tbxConfirm = QLineEdit(self)
            self.tbxConfirm.setEchoMode(QLineEdit.Password)

            self.btnChangerMDP = QPushButton('Changer le mot de passe', self)
            self.btnChangerMDP.clicked.connect(self.change_motDePasse)

            layout = QVBoxLayout()
            layout.addWidget(self.lblNouvMDP)
            layout.addWidget(self.tbxNouvMDP)
            layout.addWidget(self.lblConfirm)
            layout.addWidget(self.tbxConfirm)
            layout.addWidget(self.btnChangerMDP)

            self.setLayout(layout)
        except Exception as e :
            QMessageBox.critical(self, 'Erreur', f'Erreur lors du chargement du formulaire de changement de mot de passse: {e}')

    def change_motDePasse(self):
        """
        NON FONCTIONNEL
        :return:
        """
        new_motDePasse = self.tbxNouvMDP.text()
        confirm_motDePasse = self.tbxConfirm.text()

        # Vérifiez que les mots de passe correspondent
        if new_motDePasse == confirm_motDePasse:
            print(new_motDePasse)
            try:
                # generarion du sel et hashage du mot de passe
                salt = bcrypt.gensalt()
                motDePasse = new_motDePasse.encode('utf-8')
                motDePasseHache = bcrypt.hashpw(motDePasse, salt)
                motDePasseHacheDecode = motDePasseHache.decode('utf-8')
                print(motDePasseHacheDecode)


                message = f"CHANGE_PASSWORD:{self.utilisateur}:{motDePasseHacheDecode}"
                print(message)
                self.client_socket.send(message)

                response = self.client_socket.recv(1024)
                if response=="PASSWORD_CHANGED":
                    QMessageBox.information(self, 'Changement de mot de passe', 'Mot de passe changé avec succès!')
                    self.close()
                else:
                    QMessageBox.critical(self, 'Erreur', 'Échec du changement de mot de passe.')
            except Exception as e:
                print(f"Erreur lors du changement de mot de passe: {e}")
                QMessageBox.critical(self, 'Erreur', f'{e}\n')
        else:
            QMessageBox.critical(self, 'Erreur', f'Les mots de passe ne correspondent pas.\n')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    auth_window = AuthWindow()
    if auth_window.exec() == QDialog.Accepted:
        pseudonyme_utilisateur, motdepasse_utilisateur = auth_window.getIdentifiants()
        #print(f"username :{pseudonyme_utilisateur} | motDePasse :{motdepasse_utilisateur}")
        client_window = TodoListApp(pseudonyme_utilisateur, motdepasse_utilisateur)
        client_window.show()
        sys.exit(app.exec_())

