from PyQt5.QtCore import (Qt, QDate, QSize, QCoreApplication, QDateTime,
                          QPoint, QTimer, QTime, QUrl)
from PyQt5.QtGui import (QPalette, QColor, QIcon, QKeySequence, QPixmap,
                         QCursor, QFont, QDesktopServices)
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit,
                             QTextEdit, QComboBox, QDateEdit, QVBoxLayout,
                             QPushButton, QMessageBox, QGridLayout,
                             QListWidget, QListWidgetItem, QProgressBar,
                             QAction, QDialog, QHBoxLayout, QMainWindow,
                             QCheckBox, QMenu, QFormLayout, QDateTimeEdit,
                             QDialogButtonBox, QAbstractItemView, QSizePolicy,
                             QGraphicsDropShadowEffect, QFrame, QSpacerItem)
from lib.custom import AEScipher, AESsocket
from datetime import datetime
import requests
import socket
import bcrypt
import json
import time
import sys
import re
import os


# Création de la tâche (Yann)
class FormulaireTache(QWidget):
    """
    Classe représentant l'interface graphique pour créer une tâche.

    Attributes:
        listes (dict): Liste des listes disponibles pour organiser les tâches.
        utilisateurs (dict): Liste des utilisateurs assignables à une tâche.
        TodoListApp (object): Instance de l'application principale gérant les tâches.
        label_nom (QLabel): Étiquette pour le champ du nom de la tâche.
        champ_nom (QLineEdit): Champ de saisie pour le nom de la tâche.
        label_description (QLabel): Étiquette pour la description de la tâche.
        champ_description (QTextEdit): Champ de saisie pour la description de la tâche.
        label_date (QLabel): Étiquette pour la date d'échéance.
        champ_date (QDateEdit): Champ pour sélectionner la date d'échéance.
        label_liste (QLabel): Étiquette pour sélectionner la liste associée.
        combo_box_listes (QComboBox): Menu déroulant pour sélectionner une liste.
        label_utilisateur (QLabel): Étiquette pour sélectionner un utilisateur.
        combo_box_utilisateurs (QComboBox): Menu déroulant pour sélectionner un utilisateur assigné.
        label_date_rappel (QLabel): Étiquette pour sélectionner une date de rappel.
        champ_date_rappel (QDateEdit): Champ pour sélectionner la date de rappel.
        bouton_soumettre (QPushButton): Bouton pour soumettre le formulaire.
    """

    def __init__(self, todo_list_app):
        """Initialise le formulaire, configure l'interface graphique et charge les données nécessaires."""
        super().__init__()
        self.TodoListApp = todo_list_app
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
        self.label_date_fin = QLabel("Date d'échéance :")
        self.champ_date_fin = QDateEdit()
        self.champ_date_fin.setDate(QDate.currentDate())
        self.champ_date_fin.setCalendarPopup(True)
        layout.addWidget(self.label_date_fin)
        layout.addWidget(self.champ_date_fin)

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

    def connexionServeur(self):
        """
        Établit une connexion sécurisée avec le serveur via un socket.
        Returns:
            AESsocket: Socket sécurisé pour échanger des données chiffrées.
        """
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('85.10.235.60', 55555))
            return AESsocket(client_socket, is_server=False)
        except Exception as e:
            QMessageBox.critical(self, "Erreur de connexion", f"Erreur de connexion au serveur : {e}")
            return None

    def ChargerListes(self):
        """
        Charge les listes disponibles depuis le serveur et les ajoute au menu déroulant.

            :raises Exception: En cas d'erreur lors de la communication avec le serveur ou du traitement des données reçues.
            :return: Cette méthode ne retourne rien. Les listes sont chargées dans l'attribut `listes` et ajoutées au menu déroulant.
        """
        try:
            aes_socket = self.connexionServeur()
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
        """
        Charge les utilisateurs assignables à une tâche depuis le serveur et les ajoute au menu déroulant.

            :raises Exception: En cas d'erreur lors de la communication avec le serveur ou du traitement des données reçues.
            :return: Cette méthode ne retourne rien. Les utilisateurs sont chargés dans l'attribut `utilisateurs` et ajoutés au menu déroulant.
        """
        try:
            aes_socket = self.connexionServeur()
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
        """
        Récupère les données du formulaire et les envoie au serveur pour créer une nouvelle tâche.

            :raises Exception: En cas d'erreur lors de la communication avec le serveur ou du traitement des données.
            :return: Cette méthode ne retourne rien. Une tâche est créée sur le serveur si les données sont valides.
        """
        try:
            # Récupération des informations
            titre_tache = self.champ_nom.text().strip()
            description = self.champ_description.toPlainText().strip()
            date_echeance = self.champ_date_fin.date().toString("yyyy-MM-dd")
            date_rappel = self.champ_date_rappel.date().toString("yyyy-MM-dd")

            pseudo_choisi = self.combo_box_utilisateurs.currentText()
            nom_liste_choisie = self.combo_box_listes.currentText()

            id_utilisateur = self.utilisateurs.get(pseudo_choisi, None)
            id_liste = self.listes.get(nom_liste_choisie, None)

            if not id_utilisateur or not id_liste:
                QMessageBox.warning(self, "Erreur", "Utilisateur ou liste non sélectionné.")
                return

            aes_socket = self.connexionServeur()
            if not aes_socket:
                return

            message = f"CREATION_TACHE:{id_utilisateur}:{id_liste}:{titre_tache}:{description}:{date_echeance}:0:{date_rappel}"
            aes_socket.send(message)

            QMessageBox.information(self, "Succès", "Tâche créée avec succès.")
            self.TodoListApp.actualiser()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'envoi : {e}")


# GUI Principal (Thibaut)
class TodoListApp(QMainWindow):
    """
        Classe principale de l'application de gestion de tâches.

        :param pseudonyme_utilisateur: Pseudonyme de l'utilisateur pour l'authentification.
        :type pseudonyme_utilisateur: str
        :param motdepasse_utilisateur: Mot de passe de l'utilisateur pour l'authentification.
        :type motdepasse_utilisateur: str
        :ivar client_socket: Socket sécurisé pour la communication avec le serveur.
        :vartype client_socket: AESsocket
        :ivar formulaire: Formulaire pour créer de nouvelles tâches.
        :vartype formulaire: FormulaireTache
        :ivar taches: Liste affichant les tâches.
        :vartype taches: QListWidget
    """

    def __init__(self, pseudonyme_utilisateur, motdepasse_utilisateur):
        """
            Initialise la fenêtre principale de l'application, configure l'interface utilisateur,
            initialise la connexion au serveur, et configure les widgets et actions.

            :param pseudonyme_utilisateur: Le pseudonyme de l'utilisateur utilisé pour l'authentification.
            :type pseudonyme_utilisateur: str
            :param motdepasse_utilisateur: Le mot de passe de l'utilisateur utilisé pour l'authentification.
            :type motdepasse_utilisateur: str
            :raises Exception: En cas d'erreur lors de l'initialisation, de la connexion au serveur ou du chargement des widgets.
        """

        try:
            super().__init__()
            self.HOST = '127.0.0.1'
            self.PORT = 55555
            self.utilisateur = pseudonyme_utilisateur
            self.motdepasse = motdepasse_utilisateur
            self.initUI()
            self.formulaire = FormulaireTache(self)
            self.setWindowTitle("The Toto List")
            self.setGeometry(100, 100, 490, 603)
            self.setMinimumSize(490, 603)
            self.client_socket = socket.socket(socket.AF_INET,
                                               socket.SOCK_STREAM)
            self.client_socket.connect((self.HOST, self.PORT))
            self.client_socket = AESsocket(self.client_socket, is_server=False)
            time.sleep(0.5)
            self.client_socket.send(f"AUTH:{pseudonyme_utilisateur}:{motdepasse_utilisateur}")
            self.creerActions()
            self.creerMenu()
        except Exception as e:
            QMessageBox.critical(self, 'Erreur', f'Erreur lors du chargement de la fenetre {e}')

        self.repertoire_actuel = os.path.dirname(os.path.abspath(__file__))
        self.setWindowIcon(QIcon(OutilsCommuns.iconesDiverses("barre_titre")))
        self.icone_modifier_tache_noir = os.path.join(
            self.repertoire_actuel,
            "img/taches/",
            "MODIFIER_TACHE_SOUSTACHE_TRANSP_NOIR.png")
        self.icone_modifier_tache_blanc = os.path.join(
            self.repertoire_actuel,
            "img/taches/",
            "MODIFIER_TACHE_SOUSTACHE_TRANSP_BLANC.png")
        self.icone_supprimer_tache_noir = os.path.join(
            self.repertoire_actuel,
            "img/taches/",
            "SUPPRIMER_TACHE_SOUSTACHE_TRANSP_NOIR.png")
        self.icone_supprimer_tache_blanc = os.path.join(
            self.repertoire_actuel,
            "img/taches/",
            "SUPPRIMER_TACHE_SOUSTACHE_TRANSP_BLANC.png")
        self.icone_ajouter_soustache_noir = os.path.join(
            self.repertoire_actuel,
            "img/taches/",
            "AJOUTER_SOUSTACHE_NOIR_TRANSP.png"
        )
        self.icone_ajouter_soustache_blanc = os.path.join(
            self.repertoire_actuel,
            "img/taches/",
            "AJOUTER_SOUSTACHE_BLANC_TRANSP.png"
        )
        self.icone_barre_depliee_noir = os.path.join(
            self.repertoire_actuel,
            "img/barre_laterale/",
            "MASQUER_SIDEBAR_NOIR_TRANSP.png"
        )
        self.icone_barre_repliee_noir = os.path.join(
            self.repertoire_actuel,
            "img/barre_laterale/",
            "AFFICHER_SIDEBAR_NOIR_TRANSP.png"
        )

        self.icone_image_github = os.path.join(
            self.repertoire_actuel,
            "img/github/",
            "GITHUB_NOIR_TRANSP.png"
        )
        self.icone_dark_mode = os.path.join(
            self.repertoire_actuel,
            "img/theme/",
            "DARKMODE_NOIR_TRANSP.png"
        )
        self.icone_light_mode = os.path.join(
            self.repertoire_actuel,
            "img/theme/",
            "LIGHTMODE_BLANC_TRANSP.png"
        )

        central_widget = QWidget()
        layout_principal = QHBoxLayout(central_widget)

        self.barre_laterale = QWidget()
        self.barre_laterale.setFixedWidth(100)
        self.barre_laterale.setStyleSheet("""
            QWidget {
                border-radius: 10px;
            }
        """)
        self.layout_barre_laterale = QVBoxLayout(self.barre_laterale)

        effet_ombrage = QGraphicsDropShadowEffect()
        effet_ombrage.setBlurRadius(12)
        effet_ombrage.setXOffset(2)
        effet_ombrage.setYOffset(2)
        effet_ombrage.setColor(QColor(0, 0, 0, 128))

        self.label_horloge = QLabel()
        self.label_horloge.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.label_horloge.setFont(QFont("Arial", 14, QFont.Bold))
        self.label_horloge.setGraphicsEffect(effet_ombrage)
        self.label_horloge.setStyleSheet("""
            color: #333333;
            background: transparent;
            margin-top: 0;
            margin-bottom: 10;
            padding: 0;
        """)
        self.layout_barre_laterale.addWidget(self.label_horloge)
        self.layout_barre_laterale.addWidget(self.creerSeparateur())
        self.majHorloge()

        timer = QTimer(self)
        timer.timeout.connect(self.majHorloge)
        timer.start(1000)

        self.bouton_actualiser = QPushButton("Actualiser")
        self.bouton_actualiser.setFixedSize(90, 30)
        self.bouton_actualiser.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
        """)
        self.bouton_actualiser.clicked.connect(self.actualiser)

        image_thetotolist = QLabel()
        image_thetotolist.setPixmap(QPixmap(OutilsCommuns.iconesDiverses("barre_titre")).scaled(75, 75,
                                                                                                Qt.KeepAspectRatio))
        image_thetotolist.setAlignment(Qt.AlignHCenter)

        image_github = QPushButton()
        image_github.setIcon(QIcon(
            self.icone_image_github))
        image_github.setIconSize(QSize(25, 25))
        image_github.setFixedSize(40, 40)
        image_github.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: rgba(200, 200, 200, 0.5);
                border-radius: 20px;
            }
            QPushButton:pressed {
                background-color: rgba(150, 150, 150, 0.7);
            }
        """)
        image_github.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl("https://github.com/BaptisteBC/The_Toto_List/")))

        label_corbeille = QLabel("Corbeille")
        label_corbeille.setAlignment(Qt.AlignHCenter)
        label_corbeille.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #888888;
                text-shadow: 0px 1px 2px rgba(0, 0, 0, 0.3);
            }
        """)

        self.bouton_restaurer = QPushButton("Restaurer")
        self.bouton_restaurer.setFixedSize(90, 30)
        self.bouton_restaurer.setStyleSheet("""
                    QPushButton {
                        background-color: #333333;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 8px 16px;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #4d4d4d;
                    }
                """)
        self.bouton_restaurer.clicked.connect(self.restaurer)

        self.bouton_vider = QPushButton("Vider")
        self.bouton_vider.setFixedSize(90, 30)
        self.bouton_vider.setStyleSheet("""
                    QPushButton {
                        background-color: #333333;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 8px 16px;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #4d4d4d;
                    }
                """)
        self.bouton_vider.clicked.connect(self.vider)

        self.bouton_barre_laterale = QPushButton()
        self.bouton_barre_laterale.setIcon(QIcon(self.icone_barre_depliee_noir))
        self.bouton_barre_laterale.setIconSize(
            QSize(25, 25))
        self.bouton_barre_laterale.setFixedSize(40, 40)
        self.bouton_barre_laterale.setStyleSheet("""
            QPushButton 
                border: none;
                border-radius: 5px;
                background-color: transparent;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: rgba(200, 200, 200, 0.5);
            }
            QPushButton:pressed {
                background-color: rgba(150, 150, 150, 0.7);
            }
        """)
        self.bouton_barre_laterale.clicked.connect(self.switchBarreLaterale)

        self.layout_barre_laterale.addSpacing(20)
        self.layout_barre_laterale.addWidget(self.bouton_actualiser, alignment=Qt.AlignHCenter)
        self.layout_barre_laterale.addStretch()
        self.layout_barre_laterale.addWidget(image_thetotolist)
        self.layout_barre_laterale.addStretch()
        self.layout_barre_laterale.addWidget(label_corbeille, alignment=Qt.AlignHCenter)
        self.layout_barre_laterale.addSpacing(12)
        self.layout_barre_laterale.addWidget(self.bouton_restaurer, alignment=Qt.AlignBottom | Qt.AlignHCenter)
        self.layout_barre_laterale.addSpacing(7)
        self.layout_barre_laterale.addWidget(self.bouton_vider, alignment=Qt.AlignBottom | Qt.AlignHCenter)
        self.layout_barre_laterale.addSpacing(20)
        self.layout_barre_laterale.addWidget(self.creerSeparateur())
        self.layout_barre_laterale.addSpacing(6)
        self.layout_barre_laterale.addWidget(image_github, alignment=Qt.AlignBottom | Qt.AlignHCenter)

        self.main_widget = QWidget()
        layout_principal_vertical = QVBoxLayout(self.main_widget)

        self.bouton_formulaire = QPushButton("Nouvelle tâche")
        self.bouton_formulaire.clicked.connect(self.open_formulaire)
        self.bouton_formulaire.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.bouton_formulaire.setFixedSize(125, 45)
        self.bouton_formulaire.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
        """)

        self.bouton_theme = QPushButton()
        self.bouton_theme.setIcon(QIcon(self.icone_dark_mode))
        self.bouton_theme.setIconSize(QSize(25, 25))
        self.bouton_theme.setFixedSize(40, 40)
        self.bouton_theme.setStyleSheet("""
                    QPushButton 
                        border: none;
                        border-radius: 5px;
                        background-color: transparent;
                        margin-top: 10px;
                    }
                    QPushButton:hover {
                        background-color: rgba(200, 200, 200, 0.5);
                    }
                    QPushButton:pressed {
                        background-color: rgba(150, 150, 150, 0.7);
                    }
                """)
        self.bouton_theme.clicked.connect(self.switchTheme)

        # Barre de formulaire en bas
        layout_navigation_bas = QHBoxLayout()
        layout_navigation_bas.addWidget(self.bouton_barre_laterale,
                                        alignment=Qt.AlignLeft | Qt.AlignVCenter)
        layout_navigation_bas.addStretch()
        layout_navigation_bas.addWidget(self.bouton_formulaire)
        layout_navigation_bas.setAlignment(self.bouton_formulaire,
                                           Qt.AlignCenter)
        layout_navigation_bas.addStretch()
        layout_navigation_bas.addWidget(self.bouton_theme,
                                        alignment=Qt.AlignRight | Qt.AlignVCenter)

        # Liste des tâches (en dessous de la barre de navigation)
        self.taches = QListWidget()
        self.taches.setStyleSheet("""
            QListWidget {
                border: 1px solid #cccccc;
                border-radius: 10px;
                background: #f5f5f5;
                padding: 12px;
            }
            QListWidget::item:selected {
                background: transparent;
            }
            QListWidget::item {
                margin-bottom: 8px;
                margin-right: 14px;
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 12px;
                margin: 15px 0;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #cccccc;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: #cccccc;
                border-radius: 4px;
                height: 12px;
                subcontrol-origin: margin;
            }
            QScrollBar::add-line:vertical:hover, QScrollBar::sub-line:vertical:hover {
                background: #aaaaaa;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

        self.taches.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        layout_principal_vertical.addWidget(self.taches)
        layout_principal_vertical.addLayout(layout_navigation_bas)

        layout_principal.addWidget(self.main_widget)
        layout_principal.addWidget(self.barre_laterale)

        self.setCentralWidget(central_widget)
        self.actualiser()
        layout_principal.addWidget(self.main_widget)

        self.is_dark_mode = False

    def creerSeparateur(self):
        """
        Crée un divider pour la barre latérale.
        :return: QFrame configuré
        """
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        divider.setStyleSheet("""
            QFrame {
                background-color: #cccccc;
                height: 2px;
                margin-left: 5px;
            }
        """)
        return divider

    def majHorloge(self):
        temps = QTime.currentTime()
        self.label_horloge.setText(temps.toString("HH:mm:ss"))

    def switchBarreLaterale(self):
        """
        Bascule la visibilité de la barre latérale et met à jour l'icône du bouton.
        """
        self.barre_laterale.setVisible(not self.barre_laterale.isVisible())

        if self.barre_laterale.isVisible():
            self.bouton_barre_laterale.setIcon(QIcon(self.icone_barre_depliee_noir))
        else:
            self.bouton_barre_laterale.setIcon(QIcon(self.icone_barre_repliee_noir))

    def connexionServeur(self):
        """
        Établit une connexion sécurisée avec le serveur via un socket.
        :return: Socket sécurisé pour échanger des données chiffrées.
        :rtype: AESsocket
        :raises Exception: Si la connexion au serveur échoue.
        """
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('85.10.235.60', 55555))
            return AESsocket(client_socket, is_server=False)
        except Exception as e:
            QMessageBox.critical(self, "Erreur de connexion", f"Erreur de connexion au serveur : {e}")
            return None

    def actualiser(self):

        """
        Actualise la liste des tâches et sous-tâches depuis le serveur.

        :raises json.JSONDecodeError: Si les données reçues ne peuvent pas être décodées.
        :raises Exception: Pour toute autre erreur lors de la récupération ou du traitement des données.
        """
        try:
            aes_socket = self.connexionServeur()
            if not aes_socket:
                print("Erreur de connexion au serveur.")
                return
            aes_socket.send("GET_listeTache")
            tache_data = aes_socket.recv(1024)
            aes_socket.close()
            tache_j = json.loads(tache_data)

            if isinstance(tache_j, list) and tache_j:
                taches = [
                    tuple(
                        datetime.strptime(value, '%Y-%m-%d %H:%M:%S') if i == 3 and value else value
                        for i, value in enumerate(tache)
                    )
                    for tache in tache_j
                ]
            else:
                QMessageBox.information(self, "Info", "Aucune tâche trouvée.")
                return

            # Récupération des sous-tâches
            aes_socket = self.connexionServeur()
            if not aes_socket:
                print("Erreur de connexion au serveur.")
                return
            aes_socket.send("GET_listeSousTache")
            tache_data = aes_socket.recv(1024)
            aes_socket.close()

            try:
                tache_js = json.loads(tache_data)
                if isinstance(tache_js, list) and tache_js:
                    sousTaches = [
                        tuple(
                            datetime.strptime(value, '%Y-%m-%d %H:%M:%S') if i == 4 and value else value
                            for i, value in enumerate(sous_tache)
                        )
                        for sous_tache in tache_js
                    ]
                else:
                    sousTaches = []  # Aucune sous-tâche trouvée
            except json.JSONDecodeError:
                sousTaches = []  # Gérer une réponse mal formée ou vide

            self.taches.clear()
            for idTache, titreTache, statutTache, datesuppression_tache in taches:
                if datesuppression_tache:
                    continue
                self.ajouterTache(titreTache, idTache, statutTache)

                # Ajouter les sous-tâches associées si elles existent
                for idSousTache, titreSousTache, parentId, statutSousTache, datesuppression_soustache in sousTaches:
                    if datesuppression_soustache:
                        continue
                    if parentId == idTache:
                        self.ajouterSousTacheListe(titreSousTache, idSousTache, statutSousTache)

            self.taches.repaint()

        except Exception as e:
            print(f"Une erreur s'est produite : {e}")


        finally:
            if 'aes_socket' in locals() and aes_socket:
                aes_socket.close()

    def ajouterTache(self, titreTache, idTache, statutTache):
        """
        Ajoute une tâche à la liste des tâches affichée dans l'interface utilisateur.

        :param titreTache: Le titre de la tâche
        :type titreTache: str
        :param idTache: L'identifiant unique de la tâche
        :type idTache: int
        :param statutTache: Le statut de la tâche (1 si complétée, 0 sinon)
        :type statutTache: int
        """
        widgetTache = QWidget()
        widgetTache.setStyleSheet("""
            QWidget#TacheWidget {
                background-color: #f5f5f5;
                border: 1px solid #cccccc;
                border-radius: 10px;
                padding: 5px;
                height: 100%;
            }
            QWidget#TacheWidget:hover {
                background-color: #e0e0e0;
            }
        """)
        widgetTache.setObjectName("TacheWidget")

        layout = QHBoxLayout(widgetTache)

        caseCoche = QCheckBox()
        caseCoche.setStyleSheet("""
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #333;
                background: white;
            }
            QCheckBox::indicator:checked {
                background: #333;
            }
        """)
        caseCoche.setChecked(statutTache == 1)
        caseCoche.stateChanged.connect(lambda: self.mettreAJourStyle(labelTache, idTache, caseCoche.isChecked()))

        labelTache = QLabel(titreTache)

        if statutTache == 1:
            labelTache.setStyleSheet("""
                font-size: 13px;
                font-weight: bold; 
                color: #333333;
            """)
        else:
            labelTache.setStyleSheet("""
                font-size: 13px;
                font-weight: bold; 
                color: darkgray; 
            """)

        boutonModifier = QPushButton()
        boutonModifier.setIcon(QIcon(self.icone_modifier_tache_noir))
        boutonModifier.setFixedSize(24, 24)
        boutonModifier.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        boutonModifier.clicked.connect(lambda: self.modifierTache(idTache))

        boutonSupprimer = QPushButton()
        boutonSupprimer.setIcon(QIcon(self.icone_supprimer_tache_noir))
        boutonSupprimer.setFixedSize(24, 24)
        boutonSupprimer.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        boutonSupprimer.clicked.connect(lambda: self.supprimer(idTache))

        boutonAjouterSousTache = QPushButton()
        boutonAjouterSousTache.setIcon(QIcon(
            self.icone_ajouter_soustache_noir))
        boutonAjouterSousTache.setFixedSize(24, 24)
        boutonAjouterSousTache.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        boutonAjouterSousTache.clicked.connect(
            lambda: self.ajouterSousTache(idTache))

        layout.addWidget(caseCoche)
        layout.addWidget(labelTache)
        layout.addStretch()
        layout.addWidget(boutonAjouterSousTache)
        layout.addWidget(boutonModifier)
        layout.addWidget(boutonSupprimer)

        elementListe = QListWidgetItem()
        elementListe.setSizeHint(widgetTache.sizeHint())
        elementListe.setData(Qt.UserRole, {"type": "tache", "id": idTache})
        self.taches.addItem(elementListe)
        self.taches.setItemWidget(elementListe, widgetTache)

        widgetTache.mouseDoubleClickEvent = lambda \
                event: self.gestionEvenement(
            event, elementListe)
        widgetTache.setContextMenuPolicy(Qt.CustomContextMenu)
        widgetTache.customContextMenuRequested.connect(
            lambda pos: self.afficherMenuTache(idTache,
                                               widgetTache.mapToGlobal(pos))
        )

    def mettreAJourStyle(self, labelTache, idTache, coche):
        """
        Met à jour le style de la tâche et son statut de validation dans la base de données.

        :param labelTache: Widget QLabel représentant le titre de la tâche
        :type labelTache: QLabel
        :param idTache: Identifiant unique de la tâche
        :type idTache: int
        :param coche: Statut de la case cochée (True si cochée, False sinon)
        :type coche: bool
        """
        if coche:
            labelTache.setStyleSheet("""
                text-decoration: line-through;
                font-size: 13px;
                font-weight: bold;
                color: #333333;
            """)
            self.mettreAJourValidation(idTache, 1)
        else:
            labelTache.setStyleSheet("""
                font-size: 13px;
                font-weight: bold;
                color: darkgray;
            """)
            self.mettreAJourValidation(idTache, 0)

    def ajouterSousTacheListe(self, titreSousTache, idSousTache, statutSousTache):
        """
        Ajoute une sous-tâche associée à une tâche à la liste des tâches affichée dans l'interface utilisateur.

        :param titreSousTache: Le titre de la sous-tâche
        :type titreSousTache: str
        :param idSousTache: L'identifiant unique de la sous-tâche
        :type idSousTache: int
        :param statutSousTache: Le statut de la sous-tâche (1 si complétée, 0 sinon)
        :type statutSousTache: int
        """
        widgetSousTache = QWidget()
        widgetSousTache.setStyleSheet("""
            QWidget#SousTacheWidget {
                background-color: #ffffff;
                border: 1px solid #dddddd;
                border-radius: 10px;
                padding: 5px;
                height: 100%;
            }
            QWidget#SousTacheWidget:hover {
                background-color: #e0e0e0;
            }
        """)
        widgetSousTache.setObjectName("SousTacheWidget")

        layout = QHBoxLayout(widgetSousTache)

        espace = QWidget()
        espace.setFixedWidth(30)

        caseCocheSousTache = QCheckBox()
        caseCocheSousTache.setStyleSheet("""
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 1px solid #333;
                background: white;
            }
            QCheckBox::indicator:checked {
                background: #333;
            }
        """)
        caseCocheSousTache.setChecked(statutSousTache == 1)
        caseCocheSousTache.stateChanged.connect(
            lambda: self.mettreAJourStyleSousTache(labelSousTache, idSousTache, caseCocheSousTache.isChecked()))

        labelSousTache = QLabel(titreSousTache)

        if statutSousTache == 1:
            labelSousTache.setStyleSheet("text-decoration: line-through; "
                                         "color: darkgray;"
                                         "font-size: 13px;")
        else:
            labelSousTache.setStyleSheet("color: #333333; font-size: 13px;")

        # Bouton Modifier
        boutonModifier = QPushButton()
        boutonModifier.setIcon(QIcon(self.icone_modifier_tache_noir))
        boutonModifier.setFixedSize(24, 24)
        boutonModifier.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        boutonModifier.clicked.connect(
            lambda: self.modifierSousTache(idSousTache))

        boutonSupprimer = QPushButton()
        boutonSupprimer.setIcon(QIcon(self.icone_supprimer_tache_noir))
        boutonSupprimer.setFixedSize(24, 24)
        boutonSupprimer.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        boutonSupprimer.clicked.connect(
            lambda: self.supprimerSousTache(idSousTache))

        layout.addWidget(espace)
        layout.addWidget(caseCocheSousTache)
        layout.addWidget(labelSousTache)
        layout.addStretch()
        layout.addWidget(boutonModifier)
        layout.addWidget(boutonSupprimer)

        elementListe = QListWidgetItem()
        elementListe.setSizeHint(widgetSousTache.sizeHint())
        elementListe.setData(Qt.UserRole,
                             {"type": "sous-tache", "id": idSousTache})
        self.taches.addItem(elementListe)
        self.taches.setItemWidget(elementListe, widgetSousTache)

        widgetSousTache.mouseDoubleClickEvent = lambda \
                event: self.gestionEvenement(
            event, elementListe)
        widgetSousTache.setContextMenuPolicy(Qt.CustomContextMenu)
        widgetSousTache.customContextMenuRequested.connect(
            lambda pos: self.afficherMenuSousTache(idSousTache,
                                                   widgetSousTache.mapToGlobal(
                                                       pos))
        )

    def gestionEvenement(self, evenement, objet, clicDroit=False):
        """
        Gère un événement de clic (gauche ou droit) sur un objet en fonction de ses métadonnées.

        Si c'est un clic droit, affiche un menu contextuel. Sinon, affiche les détails de l'élément.

        :param evenement: L'événement déclencheur, soit un objet `QEvent`, soit un `QPoint`.
        :type evenement: :class:`QEvent` | :class:`QPoint`

        :param objet: L'objet auquel l'événement est associé, contenant les métadonnées.
        :type objet: :class:`QWidget`

        :param clicDroit: Indique si l'événement est un clic droit (par défaut `False`).
        :type clicDroit: bool, optionnel

        :return: Aucun retour.
        :rtype: None
        """

        metadonnees = objet.data(Qt.UserRole)
        if metadonnees is None:
            print("Erreur : pas de métadonnées associées à cet élément.")
            return

        if clicDroit:
            position = evenement if isinstance(evenement,
                                               QPoint) else evenement.globalPos()
            if metadonnees["type"] == "tache":
                self.afficherMenuTache(metadonnees["id"], position)
            elif metadonnees["type"] == "sous-tache":
                self.afficherMenuSousTache(metadonnees["id"], position)
        else:
            if metadonnees["type"] == "tache":
                self.detail(metadonnees["id"])
            elif metadonnees["type"] == "sous-tache":
                self.detailSousTache(metadonnees["id"])

    def afficherMenuSousTache(self, idSousTache, position=None):
        """
        Affiche un menu contextuel avec des options pour une tâche spécifique.

        :param idSousTache: Identifiant unique de la tâche
        :type idSousTache: int
        :param position: Position du curseur
        """
        menu = QMenu(self)
        actionDetailTache = QAction("Détails sous-tâche", self)
        actionDetailTache.triggered.connect(lambda: self.detailSousTache(idSousTache))
        actionModifierSousTache = QAction("Modifier sous-tâche", self)
        actionModifierSousTache.triggered.connect(lambda: self.modifierSousTache(idSousTache))
        actionSupprimerSousTache = QAction("Supprimer sous-tâche", self)
        actionSupprimerSousTache.triggered.connect(lambda: self.supprimerSousTache(idSousTache))
        menu.addAction(actionDetailTache)
        menu.addAction(actionModifierSousTache)
        menu.addAction(actionSupprimerSousTache)

        if position is None:
            position = QCursor.pos()
        menu.exec_(position)

    def mettreAJourStyleSousTache(self, labelSousTache, idSousTache, cocheSousTache):
        """
        Met à jour le style visuel de la sous-tâche et son statut de validation dans la base de données.

        :param labelSousTache: Widget QLabel représentant le titre de la sous-tâche
        :type labelSousTache: QLabel
        :param idSousTache: Identifiant unique de la sous-tâche
        :type idSousTache: int
        :param cocheSousTache: Statut de la case cochée (True si cochée, False sinon)
        :type cocheSousTache: bool
        """
        if cocheSousTache:
            labelSousTache.setStyleSheet("text-decoration: line-through; "
                                         "color: darkgray;"
                                         "font-size: 13px;")
            self.mettreAJourValidationSousTache(idSousTache, 1)
        else:
            labelSousTache.setStyleSheet("color: #333333; font-size: 13px;")
            self.mettreAJourValidationSousTache(idSousTache, 0)

    def afficherMenuTache(self, idTache, position=None):
        """
        Affiche un menu contextuel avec des options pour une tâche spécifique.

        :param idTache: Identifiant unique de la tâche
        :type idTache: int
        :param position: Position du curseur
        """
        menu = QMenu(self)
        actionAjouterSousTache = QAction("Ajouter sous-tâche", self)
        actionAjouterSousTache.triggered.connect(lambda: self.ajouterSousTache(idTache))
        actionDetailTache = QAction("Détails tâche", self)
        actionDetailTache.triggered.connect(lambda: self.detail(idTache))
        actionModifierTache = QAction("Modifier tâche", self)
        actionModifierTache.triggered.connect(lambda: self.modifierTache(idTache))
        actionSupprimerTache = QAction("Supprimer tâche", self)
        actionSupprimerTache.triggered.connect(lambda: self.supprimer(idTache))
        menu.addAction(actionAjouterSousTache)
        menu.addAction(actionDetailTache)
        menu.addAction(actionModifierTache)
        menu.addAction(actionSupprimerTache)

        if position is None:
            position = QCursor.pos()
        menu.exec_(position)

    def mettreAJourValidation(self, idTache, statutValidation):
        """
        Met à jour le champ de validation d'une tâche dans la base de données.

        :param idTache: Identifiant unique de la tâche
        :type idTache: int
        :param statutValidation: Nouveau statut de validation (0 ou 1)
        :type statutValidation: int
        :raises pymysql.MySQLError: En cas d'erreur lors de la mise à jour de la base de données
        """
        try:
            aes_socket = self.connexionServeur()
            if not aes_socket:
                print("Erreur de connexion au serveur.")
            message = f"validation:{idTache}:{statutValidation}"
            aes_socket.send(message)
        finally:
            aes_socket.close()

    def mettreAJourValidationSousTache(self, idSousTache, statutSousValidation):
        """
        Met à jour le champ de validation d'une sous-tâche dans la base de données.

        :param idSousTache: Identifiant unique de la sous-tâche
        :type idSousTache: int
        :param statutSousValidation: Nouveau statut de validation (0 ou 1)
        :type statutSousValidation: int
        :raises pymysql.MySQLError: En cas d'erreur lors de la mise à jour de la base de données
        """
        try:
            aes_socket = self.connexionServeur()
            if not aes_socket:
                print("Erreur de connexion au serveur.")
            message = f"validationSousTache:{idSousTache}:{statutSousValidation}"
            aes_socket.send(message)
        finally:
            aes_socket.close()

    def modifierTache(self, idTache):
        """
        Ouvre une fenêtre pour modifier les détails d'une tâche existante.

        :param idTache: Identifiant unique de la tâche
        :type idTache: int
        :raises json.JSONDecodeError: En cas d'erreur lors du décodage des données JSON de la tâche
        :raises Exception: En cas d'autres erreurs inattendues
        """
        try:
            aes_socket = self.connexionServeur()
            if not aes_socket:
                print("Erreur de connexion au serveur.")
                return
            aes_socket.send(f"GET_tache:{idTache}")
            tache_data = aes_socket.recv(1024)
            tache_j = json.loads(tache_data)
            if isinstance(tache_j, list) and tache_j:
                tache = tuple(
                    datetime.strptime(value, '%Y-%m-%d %H:%M:%S') if i in [2, 4] and value else value for i, value in
                    enumerate(tache_j[0]))
            else:
                QMessageBox.information(self, "Info", "Aucune tâche trouvée.")
                return
            dialog = QDialog(self)
            dialog.setWindowTitle("Modifier la Tâche")
            formulaire = QFormLayout(dialog)

            titreEdit = QLineEdit(tache[0] or "")
            descriptionEdit = QLineEdit(tache[1] or "")
            dateFinEdit = QDateTimeEdit(tache[2] or QDateTime.currentDateTime())
            dateFinEdit.setCalendarPopup(True)

            recurrenceEdit = QComboBox()
            recurrenceEdit.addItems(["Aucune", "Quotidienne", "Hebdomadaire", "Mensuelle"])
            recurrenceEdit.setCurrentText(tache[3] or "Aucune")

            dateRappelEdit = QDateTimeEdit(tache[4] or QDateTime.currentDateTime())
            dateRappelEdit.setCalendarPopup(True)

            rappelCheck = QCheckBox("Activer le rappel")
            rappelCheck.setChecked(tache[4] is not None)

            dateRappelEdit.setEnabled(rappelCheck.isChecked())
            rappelCheck.stateChanged.connect(lambda state: dateRappelEdit.setEnabled(state == Qt.Checked))

            formulaire.addRow("Titre:", titreEdit)
            formulaire.addRow("Description:", descriptionEdit)
            formulaire.addRow("Date de Fin:", dateFinEdit)
            formulaire.addRow("Récurrence:", recurrenceEdit)
            formulaire.addRow(rappelCheck, dateRappelEdit)

            boutons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            boutons.accepted.connect(
                lambda: self.sauvegarderModification(idTache, titreEdit.text(), descriptionEdit.text(),
                                                     dateFinEdit.dateTime(), recurrenceEdit.currentText(),
                                                     dateRappelEdit.dateTime() if rappelCheck.isChecked() else None,
                                                     dialog))
            boutons.rejected.connect(dialog.reject)
            formulaire.addWidget(boutons)
            dialog.exec_()

        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Erreur", f"Erreur de décodage JSON : {e}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur inattendue : {e}")
        finally:
            aes_socket.close()

    def sauvegarderModification(self, idTache, titre, description, dateFin, recurrence, dateRappel, dialog):
        """
        Sauvegarde les modifications d'une tâche.

        :param idTache: Identifiant de la tâche à modifier.
        :type idTache: str
        :param titre: Nouveau titre de la tâche.
        :type titre: str
        :param description: Nouvelle description de la tâche.
        :type description: str
        :param dateFin: Nouvelle date de fin de la tâche.
        :type dateFin: QDateTime
        :param recurrence: Récurrence de la tâche.
        :type recurrence: str
        :param dateRappel: Nouvelle date de rappel de la tâche, defaults to None.
        :type dateRappel: QDateTime, optional
        :param dialog: Fenêtre de dialogue associée.
        :type dialog: QDialog
        :raises pymysql.MySQLError: En cas d'erreur SQL lors de la modification.
        :return: None
        :rtype: None
        """
        try:

            aes_socket = self.connexionServeur()
            if not aes_socket:
                print("Erreur de connexion au serveur.")
            message = f"MODIF_TACHE|{idTache}|{titre}|{description}|{dateFin.toString('yyyy-MM-dd HH:mm:ss')}|{recurrence}|{dateRappel.toString('yyyy-MM-dd HH:mm:ss') if dateRappel else 'NULL'}"""
            aes_socket.send(message)
            dialog.accept()
            self.actualiser()
        except:
            print("Erreur sauvegarderModification")
        finally:
            aes_socket.close()

    def modifierSousTache(self, idSousTache):
        """
        Ouvre un formulaire pour modifier une sous-tâche.

        :param idSousTache: Identifiant de la sous-tâche à modifier.
        :type idSousTache: str
        :raises pymysql.MySQLError: En cas d'erreur SQL lors de la récupération des données de la sous-tâche.
        :return: None
        :rtype: None
        """
        try:
            aes_socket = self.connexionServeur()
            if not aes_socket:
                print("Erreur de connexion au serveur.")
                return
            aes_socket.send(f"GET_sousTache:{idSousTache}")
            tache_data = aes_socket.recv(1024)
            aes_socket.close()
            tache_j = json.loads(tache_data)
            if isinstance(tache_j, list) and tache_j:
                sousTache = tuple(
                    datetime.strptime(value, '%Y-%m-%d %H:%M:%S') if i in [2, 3] and value else value for i, value in
                    enumerate(tache_j[0]))
            else:
                QMessageBox.information(self, "Info", "Aucune tâche trouvée.")
                return

            if not sousTache:
                QMessageBox.critical(self, "Erreur", "Aucune sous-tâche trouvée avec cet ID.")
                return

            dialog = QDialog(self)
            dialog.setWindowTitle("Modifier la Sous-Tâche")
            formulaire = QFormLayout(dialog)

            titreEdit = QLineEdit(sousTache[0] or "")
            descriptionEdit = QLineEdit(sousTache[1] or "")
            dateFinEdit = QDateTimeEdit(sousTache[2] or QDateTime.currentDateTime())
            dateFinEdit.setCalendarPopup(True)

            dateRappelEdit = QDateTimeEdit(sousTache[3] or QDateTime.currentDateTime())
            dateRappelEdit.setCalendarPopup(True)
            rappelCheck = QCheckBox("Activer le rappel")
            rappelCheck.setChecked(sousTache[3] is not None)

            dateRappelEdit.setEnabled(rappelCheck.isChecked())
            rappelCheck.stateChanged.connect(lambda state: dateRappelEdit.setEnabled(state == Qt.Checked))

            formulaire.addRow("Titre:", titreEdit)
            formulaire.addRow("Description:", descriptionEdit)
            formulaire.addRow("Date de Fin:", dateFinEdit)
            formulaire.addRow(rappelCheck, dateRappelEdit)

            boutons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            boutons.accepted.connect(
                lambda: self.sauvegarderModificationSousTache(idSousTache, titreEdit.text(), descriptionEdit.text(),
                                                              dateFinEdit.dateTime(),
                                                              dateRappelEdit.dateTime() if rappelCheck.isChecked() else None,
                                                              dialog))
            boutons.rejected.connect(dialog.reject)
            formulaire.addWidget(boutons)

            dialog.exec_()
        except:
            print("Erreur modifierSousTache")
        finally:
            aes_socket.close()

    def sauvegarderModificationSousTache(self, idSousTache, titre, description, dateFin, dateRappel, dialog):
        """
        Sauvegarde les modifications d'une sous-tâche.

        :param idSousTache: Identifiant de la sous-tâche à modifier.
        :type idSousTache: str
        :param titre: Nouveau titre de la sous-tâche.
        :type titre: str
        :param description: Nouvelle description de la sous-tâche.
        :type description: str
        :param dateFin: Nouvelle date de fin de la sous-tâche.
        :type dateFin: QDateTime
        :param dateRappel: Nouvelle date de rappel de la sous-tâche, defaults to None.
        :type dateRappel: QDateTime, optional
        :param dialog: Fenêtre de dialogue associée.
        :type dialog: QDialog
        :raises pymysql.MySQLError: En cas d'erreur SQL lors de la modification.
        :return: None
        :rtype: None
        """
        try:
            aes_socket = self.connexionServeur()
            if not aes_socket:
                print("Erreur de connexion au serveur.")
            message = f"modifSousTache|{idSousTache}|{titre}|{description}|{dateFin.toString('yyyy-MM-dd HH:mm:ss')}|{dateRappel.toString('yyyy-MM-dd HH:mm:ss') if dateRappel else 'NULL'}"""
            aes_socket.send(message)
            dialog.accept()
            self.actualiser()
        except:
            print("Erreur SauvegarderModificationSousTache")
        finally:
            aes_socket.close()

    def ajouterSousTache(self, idTacheParent):
        """
        Ouvre un formulaire pour ajouter une nouvelle sous-tâche.

        :param idTacheParent: Identifiant de la tâche parent.
        :type idTacheParent: str
        :return: None
        :rtype: None
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajouter une sous-tâche")
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
                border-radius: 10px;
                padding: 10px;
            }
            QLabel {
                font-size: 14px;
                color: #333333;
                font-weight: bold;
            }
            QLineEdit, QDateTimeEdit {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            QDateTimeEdit::drop-down {
                border: none;
            }
            QDateTimeEdit::down-arrow {
                width: 10px;
                height: 10px;
            }
            QDateTimeEdit QAbstractItemView {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #333333;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
            QPushButton:pressed {
                background-color: #292929;
            }
            """)
        formulaire = QFormLayout(dialog)

        titreEdit = QLineEdit()
        descriptionEdit = QLineEdit()
        dateFinEdit = QDateTimeEdit(QDateTime.currentDateTime())
        dateFinEdit.setCalendarPopup(True)

        dateRappelEdit = QDateTimeEdit(QDateTime.currentDateTime())
        dateRappelEdit.setCalendarPopup(True)
        rappelCheck = QCheckBox("Activer le rappel")
        rappelCheck.setChecked(False)
        dateRappelEdit.setEnabled(rappelCheck.isChecked())
        rappelCheck.stateChanged.connect(lambda state: dateRappelEdit.setEnabled(state == Qt.Checked))

        formulaire.addRow("Titre:", titreEdit)
        formulaire.addRow("Description:", descriptionEdit)
        formulaire.addRow("Date de Fin:", dateFinEdit)
        formulaire.addRow(rappelCheck, dateRappelEdit)

        boutonsLayout = QHBoxLayout()

        boutonCancel = QPushButton("Cancel")
        boutonCancel.clicked.connect(dialog.reject)
        boutonsLayout.addWidget(boutonCancel, alignment=Qt.AlignLeft)

        boutonOk = QPushButton("Ok")
        boutonOk.clicked.connect(lambda: self.creerSousTache(
            idTacheParent,
            titreEdit.text(),
            descriptionEdit.text(),
            dateFinEdit.dateTime(),
            dateRappelEdit.dateTime() if rappelCheck.isChecked() else None,
            dialog
        ))
        boutonsLayout.addWidget(boutonOk, alignment=Qt.AlignRight)

        formulaire.addRow(boutonsLayout)

        dialog.exec_()

    def creerSousTache(self, idTacheParent, titre, description, dateFin, dateRappel, dialog):
        """
        Crée une nouvelle sous-tâche et l'enregistre dans la base de données.

        :param idTacheParent: Identifiant de la tâche parent.
        :type idTacheParent: str
        :param titre: Titre de la sous-tâche.
        :type titre: str
        :param description: Description de la sous-tâche.
        :type description: str
        :param dateFin: Date de fin de la sous-tâche.
        :type dateFin: QDateTime
        :param dateRappel: Date de rappel de la sous-tâche, defaults to None.
        :type dateRappel: QDateTime, optional
        :param dialog: Fenêtre de dialogue associée.
        :type dialog: QDialog
        :raises pymysql.MySQLError: En cas d'erreur SQL lors de la création.
        :return: None
        :rtype: None
        """
        try:
            aes_socket = self.connexionServeur()
            if not aes_socket:
                print("Erreur de connexion au serveur.")
            message = f"creationSousTache|{idTacheParent}|{titre}|{description}|{dateFin.toString('yyyy-MM-dd HH:mm:ss')}|{dateRappel.toString('yyyy-MM-dd HH:mm:ss') if dateRappel else 'NULL'}"""
            aes_socket.send(message)
            aes_socket.close()
            dialog.accept()
            self.actualiser()
        finally:
            aes_socket.close()

    def detailSousTache(self, idSousTache):
        """
        Affiche les détails d'une sous-tâche spécifique dans une fenêtre dédiée.

        :param idSousTache: Identifiant unique de la sous-tâche.
        :type idSousTache: int
        :raises json.JSONDecodeError: En cas d'erreur lors du décodage des données JSON de la sous-tâche.
        :raises Exception: Si la fenêtre de détail ne peut pas être affichée.
        """

        aes_socket = self.connexionServeur()
        if not aes_socket:
            print("Erreur de connexion au serveur.")
            return
        aes_socket.send(f"GET_sousTacheDetail:{idSousTache}")
        tache_data = aes_socket.recv(1024)
        tache_j = json.loads(tache_data)
        if isinstance(tache_j, list) and tache_j:
            tache = tuple(
                datetime.strptime(value, '%Y-%m-%d %H:%M:%S') if i in [2, 3, 5] and value else value for i, value in
                enumerate(tache_j[0]))
        else:
            QMessageBox.information(self, "Info", "Aucune tâche trouvée.")
            return

        try:
            FenetreDetail(tache[0], tache[1], tache[2], tache[3], tache[4], tache[5], tache[6], tache[7]).exec()

        except:
            print("problème d'execution de la fenetre de detail sous tache")

    def detail(self, idTache, ):
        """
        Affiche les détails d'une tâche spécifique dans une fenêtre dédiée.

        :param idTache: Identifiant unique de la tâche.
        :type idTache: int
        :raises json.JSONDecodeError: En cas d'erreur lors du décodage des données JSON de la tâche.
        :raises Exception: Si la fenêtre de détail ne peut pas être affichée.
        """
        aes_socket = self.connexionServeur()
        if not aes_socket:
            print("Erreur de connexion au serveur.")
            return
        aes_socket.send(f"GET_tacheDetail:{idTache}")
        tache_data = aes_socket.recv(1024)
        tache_j = json.loads(tache_data)
        if isinstance(tache_j, list) and tache_j:
            tache = tuple(
                datetime.strptime(value, '%Y-%m-%d %H:%M:%S') if i in [2, 3, 5] and value else value for i, value in
                enumerate(tache_j[0]))
        else:
            QMessageBox.information(self, "Info", "Aucune tâche trouvée.")
            return

        try:
            FenetreDetail(tache[0], tache[1], tache[2], tache[3], tache[4], tache[5]).exec()
        except:
            print("erreur execution detail")

    def restaurer(self):
        """
        Ouvre une fenêtre pour restaurer les tâches supprimées et actualise l'affichage des tâches.

        :return: None
        :rtype: None
        """

        Restaurer().exec()
        self.actualiser()

    def supprimer(self, id_tache):
        """
         Ouvre une fenêtre pour confirmer et supprimer une tâche.

         :param id_tache: Identifiant unique de la tâche à supprimer.
         :type id_tache: int
         :raises Exception: Si la fenêtre de suppression ne peut pas être ouverte.
         """

        try:
            SupprimerTache(id_tache, 0).exec()
            self.actualiser()
        except:
            print("erreur ouverture fenetre suppresion")

    def supprimerSousTache(self, id_tache):
        """
        Ouvre une fenêtre pour confirmer et supprimer une sous-tâche.

        :param id_tache: Identifiant unique de la sous-tâche à supprimer.
        :type id_tache: int
        :raises Exception: Si la fenêtre de suppression ne peut pas être ouverte.
        """

        try:
            SupprimerTache(id_tache, 1).exec()
            self.actualiser()
        except:
            print("erreur ouverture fenetre suppresion")

    def vider(self):
        """
        Vide la corbeille en ouvrant une fenêtre de confirmation.

        :return: None
        :rtype: None
        """
        ViderCorbeille().exec()

    def quitter(self):
        """
        Quitte l'application en fermant tous les processus.

        :return: None
        :rtype: None
        """
        QCoreApplication.exit(0)

    def creerMenu(self):
        """
        Crée un menu d'options et de crédits dans la barre de menu principale.

        :return: None
        :rtype: None
        """
        barre_menu = self.menuBar()
        self.menuBar().setStyleSheet("""
            QMenuBar {
                background-color: #333333;
                color: white;
                border: none;
                padding: 5px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 5px 10px;
                margin: 0px 5px;
                border-radius: 5px;
            }
            QMenuBar::item:selected {
                background-color: #4d4d4d;
                color: white;
            }
            QMenu {
                background-color: #444444;
                border: 1px solid #333333;
                padding: 5px;
                color: white;
                border-radius: 5px;
            }
            QMenu::item {
                background-color: transparent;
                padding: 5px 15px;
                margin: 3px;
                border-radius: 5px;
            }
            QMenu::item:selected {
                background-color: #555555;
                color: white;
            }
            QMenu::separator {
                height: 1px;
                background: #666666;
                margin: 5px 0;
            }
        """)

        menu_options = barre_menu.addMenu("Options")
        menu_options.addAction(self.action_changer_mdp)
        menu_options.addAction(self.action_quitter)

        menu_aide = barre_menu.addMenu("Aide")
        menu_aide.addAction(self.action_ouvrir_aide)

        menu_apropos = barre_menu.addMenu("À propos")
        menu_apropos.addAction(self.action_ouvrir_credits)

    def creerActions(self):
        """
        Définit les actions et raccourcis clavier pour le menu de l'application.

        :return: None
        :rtype: None
        """
        self.action_changer_mdp = QAction("Changer de mot de passe", self)
        self.action_changer_mdp.setShortcut(QKeySequence("Ctrl+P"))
        self.action_changer_mdp.triggered.connect(self.fenetreChangementMDP)

        self.action_quitter = QAction("Quitter", self)
        self.action_quitter.setShortcut(QKeySequence("Alt+F4"))
        self.action_quitter.setStatusTip("Quitter")
        self.action_quitter.triggered.connect(self.fermerApplication)

        self.action_ouvrir_credits = QAction("Crédits", self)
        self.action_ouvrir_credits.triggered.connect(self.ouvrirCredits)

        self.action_ouvrir_aide = QAction("Guide", self)
        self.action_ouvrir_aide.triggered.connect(self.ouvrirAide)

    def fermerApplication(self):
        """
        Ferme l'application et termine tous les processus en cours.

        :return: None
        :rtype: None
        """

        application.exit(0)
        sys.exit(0)

    def fenetreChangementMDP(self):
        """
        Ouvre une fenêtre pour permettre à l'utilisateur de modifier son mot de passe.

        :raises Exception: En cas d'erreur lors du processus de changement de mot de passe.
        :return: None
        :rtype: None
        """

        try:
            change_motDePasse_window = FenetreChangerMotDePasse(self.utilisateur, self.client_socket)
            if change_motDePasse_window.exec() == QDialog.Accepted:
                QMessageBox.information("Mot de passe changé avec succès !")

        except Exception as erreur:
            QMessageBox.critical("Erreur", f'Erreur lors du changement de mot de passe {erreur}')

    def initUI(self):
        """
        Méthode d'initialisation de l'interface utilisateur.
        Actuellement non implémentée.

        :return: None
        :rtype: None
        """

        pass

    def open_formulaire(self):
        """
        Ouvre une nouvelle fenêtre contenant le formulaire de création de tâche.

        :raises Exception: Si une erreur survient lors de l'ouverture de la fenêtre du formulaire.
        :return: None
        :rtype: None
        """

        print("Signal reçu : ouverture du formulaire en cours...")
        try:
            self.formulaire_window = FormulaireTache(self)
            self.formulaire_window.show()
        except Exception as e:
            print(f"Erreur lors de l'ouverture du formulaire : {e}")

    def switchTheme(self):
        """
        Bascule entre le mode clair et le mode sombre pour l'application.

        :return: None
        :rtype: None
        """

        if not self.is_dark_mode:
            self.set_dark_mode()
            self.bouton_theme.setIcon(QIcon(self.icone_light_mode))
            self.bouton_theme.setIconSize(QSize(25, 25))
            self.bouton_theme.setFixedSize(40, 40)
            self.bouton_theme.setStyleSheet("""
                QPushButton 
                    border: none;
                    border-radius: 5px;
                    background-color: transparent;
                    margin-top: 10px;
                }
                QPushButton:hover {
                    background-color: rgba(200, 200, 200, 0.5);
                }
                QPushButton:pressed {
                    background-color: rgba(150, 150, 150, 0.7);
                }
            """)
        else:
            self.set_light_mode()
            self.bouton_theme.setIcon(QIcon(self.icone_dark_mode))
            self.bouton_theme.setIconSize(QSize(25, 25))
            self.bouton_theme.setFixedSize(40, 40)
            self.bouton_theme.setStyleSheet("""
                QPushButton 
                    border: none;
                    border-radius: 5px;
                    background-color: transparent;
                    margin-top: 10px;
                }
                QPushButton:hover {
                    background-color: rgba(200, 200, 200, 0.5);
                }
                QPushButton:pressed {
                    background-color: rgba(150, 150, 150, 0.7);
                }
            """)
        self.is_dark_mode = not self.is_dark_mode

    def set_dark_mode(self):
        """
        Applique un thème sombre à l'application.

        :return: None
        :rtype: None
        """

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
        """
        Réinitialise le thème de l'application au mode clair par défaut.

        :return: None
        :rtype: None
        """
        QApplication.instance().setPalette(QApplication.style().standardPalette())
        self.setStyleSheet("")

    def ouvrirAide(self):
        """
        Affiche une fenêtre contenant des informations d'aide pour l'utilisateur.

        :return: None
        :rtype: None
        """

        fenetre_aide = QMessageBox(self)
        fenetre_aide.setWindowTitle("Aide")
        fenetre_aide.setText(
            "Besoin d'aide avec l'application ? <br><br>Le lien suivant pourra vous aider 😉 : <br><br>"
            '<a href="https://github.com/BaptisteBC/The_Toto_List">'
            "https://github.com/BaptisteBC/The_Toto_List</a>"
        )
        fenetre_aide.setStyleSheet("""
                    QDialog {
                        background-color: #f5f5f5;
                        border-radius: 10px;
                    }
                    QLabel {
                        font-size: 14px;
                        color: #333333;
                        font-weight: bold;
                    }
                    QLineEdit {
                        background-color: #ffffff;
                        border: 1px solid #cccccc;
                        border-radius: 5px;
                        padding: 5px;
                        font-size: 14px;
                    }
                    QPushButton {
                        background-color: #333333;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 8px 16px;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #4d4d4d;
                    }
                """)
        fenetre_aide.setIcon(QMessageBox.Information)
        fenetre_aide.exec()

    def ouvrirCredits(self):
        """
        Affiche une fenêtre contenant les crédits et informations sur les développeurs de l'application.

        :return: None
        :rtype: None
        """

        fenetre_credits = QMessageBox(self)
        fenetre_credits.setWindowTitle("Crédits")
        fenetre_credits.setText(
            "Application développée conjointement par : "
            "\n\n - BLANC-CARRIER Baptiste \n - BLANCK Yann "
            "\n - COSENZA Thibaut \n - DE AZEVEDO Kévin \n - GASSER Timothée "
            "\n - MARTIN Jean-Christophe \n - MERCKLE Florian "
            "\n - MOUROT Corentin \n - TRÉPIER Timothée\n\n © 2024 TheTotoList. "
            "Tous droits réservés. \n\n Élaboré par TheTotoGroup.")
        fenetre_credits.setStyleSheet("""
                            QDialog {
                                background-color: #f5f5f5;
                                border-radius: 10px;
                            }
                            QLabel {
                                font-size: 14px;
                                color: #333333;
                                font-weight: bold;
                            }
                            QLineEdit {
                                background-color: #ffffff;
                                border: 1px solid #cccccc;
                                border-radius: 5px;
                                padding: 5px;
                                font-size: 14px;
                            }
                            QPushButton {
                                background-color: #333333;
                                color: white;
                                border: none;
                                border-radius: 5px;
                                padding: 8px 16px;
                                font-size: 14px;
                            }
                            QPushButton:hover {
                                background-color: #4d4d4d;
                            }
                        """)
        fenetre_credits.setIcon(QMessageBox.Information)
        fenetre_credits.exec()


class SupprimerTache(QDialog):
    """
    Fenêtre de dialogue pour supprimer une tâche ou une sous-tâche.

    :param idTache: Identifiant de la tâche ou sous-tâche à supprimer.
    :type idTache: str
    :param typeTache: Type de tâche (0 pour une tâche, 1 pour une sous-tâche).
    :type typeTache: str
    """

    def __init__(self, idTache, typeTache):
        """
        Initialise la fenêtre de suppression d'une tâche.

        :param idTache: L'ID de la tâche à supprimer.
        :type idTache: str

        :param typeTache: Le type de la tâche à supprimer.
        :type typeTache: str

        :return: None
        :rtype: None
        """

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

        self.idTache: str = idTache
        self.typeTache: str = typeTache

        self.confirmer.clicked.connect(self.conf)
        self.annuler.clicked.connect(self.stop)

    def connexionServeur(self):
        """
        Établit une connexion sécurisée avec le serveur via un socket.
        :return: Socket sécurisé pour échanger des données chiffrées.
        :rtype: AESsocket
        :raises Exception: Si la connexion au serveur échoue.
        """
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('85.10.235.60', 55555))
            return AESsocket(client_socket, is_server=False)
        except Exception as e:
            QMessageBox.critical(self, "Erreur de connexion",
                                 f"Erreur de connexion au serveur : {e}")
            return None

    def conf(self):
        """
        Envoie une requête au serveur pour supprimer la tâche ou la sous-tâche.

        :raises Exception: En cas d'erreur de connexion ou d'envoi de la requête.
        """

        try:
            if self.typeTache == 0:
                aes_socket = self.connexionServeur()
                if not aes_socket:
                    print("Erreur de connexion au serveur.")
                    return
                aes_socket.send(f"SUP_Tache:{self.idTache}")

            else:
                aes_socket = self.connexionServeur()
                if not aes_socket:
                    print("Erreur de connexion au serveur.")
                    return
                aes_socket.send(f"SUP_sousTache:{self.idTache}")

            msg = QMessageBox()
            msg.setWindowTitle("Confirmation")
            msg.setText("Tache correctement supprimée")
            msg.exec()

            self.close()
        except Exception as E:
            print(E)

    def stop(self):
        """
        Ferme la fenêtre de dialogue sans effectuer d'action.

        :return: None
        :rtype: None
        """

        self.close()


class ViderCorbeille(QDialog):
    """
    Fenêtre de dialogue pour confirmer le vidage de la corbeille.

    :param None
    :return: None
    :rtype: None
    """

    def __init__(self):
        """
        Initialise la fenêtre de confirmation pour vider la corbeille.

        :return: None
        :rtype: None
        """

        super().__init__()

        self.setWindowTitle("Vider")

        grid = QGridLayout()
        self.setLayout(grid)
        self.resize(300, 150)

        self.titre = QLabel("!!! Attention : vider la corbeille ?!")
        self.confirmer = QPushButton("Confirmer")
        self.annuler = QPushButton("Annuler")

        grid.addWidget(self.titre)
        grid.addWidget(self.confirmer)
        grid.addWidget(self.annuler)

        self.confirmer.clicked.connect(self.conf)
        self.annuler.clicked.connect(self.stop)

    def connexionServeur(self):
        """
        Établit une connexion sécurisée avec le serveur via un socket.
        :return: Socket sécurisé pour échanger des données chiffrées.
        :rtype: AESsocket
        :raises Exception: Si la connexion au serveur échoue.
        """
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('85.10.235.60', 55555))
            return AESsocket(client_socket, is_server=False)
        except Exception as e:
            QMessageBox.critical(self, "Erreur de connexion", f"Erreur de connexion au serveur : {e}")
            return None

    def conf(self):
        """
        Envoie une requête au serveur pour vider la corbeille.

        :raises Exception: En cas d'erreur de connexion ou d'envoi de la requête.
        """

        aes_socket = self.connexionServeur()
        if not aes_socket:
            print("Erreur de connexion au serveur.")
            return
        aes_socket.send(f"viderCorbeille")

        msg = QMessageBox()
        msg.setWindowTitle("Confirmation")
        msg.setText("La corbeille a été vidée")
        msg.exec()

        self.close()

    def stop(self):
        """
        Ferme la fenêtre de dialogue sans effectuer d'action.

        :return: None
        :rtype: None
        """

        self.close()


class Restaurer(QDialog):
    """
    Fenêtre de dialogue pour confirmer la restauration des éléments supprimés de la corbeille.

    :param None
    :return: None
    :rtype: None
    """

    def __init__(self):
        """
        Initialise la fenêtre de confirmation pour restaurer les éléments de la corbeille.

        :return: None
        :rtype: None
        """

        super().__init__()

        self.setWindowTitle("Restaurer")

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

    def connexionServeur(self):
        """
        Établit une connexion sécurisée avec le serveur via un socket.

        :return: Socket sécurisé pour échanger des données chiffrées.
        :rtype: AESsocket
        :raises Exception: Si la connexion au serveur échoue.
        """
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('85.10.235.60', 55555))
            return AESsocket(client_socket, is_server=False)
        except Exception as e:
            QMessageBox.critical(self, "Erreur de connexion", f"Erreur de connexion au serveur : {e}")
            return None

    def conf(self):
        """
        Envoie une requête au serveur pour restaurer les éléments de la corbeille.

        :raises Exception: En cas d'erreur de connexion ou d'envoi de la requête.
        """

        aes_socket = self.connexionServeur()
        if not aes_socket:
            print("Erreur de connexion au serveur.")
            return
        aes_socket.send(f"restaurerCorbeille")

        msg = QMessageBox()
        msg.setWindowTitle("Confirmation")
        msg.setText("La corbeille a été restaurée !")
        msg.exec()

        self.close()

    def stop(self):
        """
        Ferme la fenêtre de dialogue sans effectuer d'action.

        :return: None
        :rtype: None
        """

        self.close()


class FenetreDetail(QDialog):
    """
    Fenêtre de dialogue affichant les détails d'une tâche ou d'une sous-tâche.

    :param titre: Titre de la tâche ou sous-tâche.
    :type titre: str
    :param description: Description de la tâche ou sous-tâche.
    :type description: str
    :param datecreation: Date de création de la tâche ou sous-tâche.
    :type datecreation: datetime
    :param datefin: Date de fin prévue de la tâche ou sous-tâche.
    :type datefin: datetime
    :param statut: Statut de la tâche ou sous-tâche (0 pour "En cours", 1 pour "Terminée").
    :type statut: int
    :param daterappel: Date de rappel associée à la tâche ou sous-tâche.
    :type daterappel: datetime
    :param soustache_id_tache: (Optionnel) Identifiant de la tâche parent si l'objet est une sous-tâche.
    :type soustache_id_tache: int, optional
    :param tache_parent: (Optionnel) Nom ou titre de la tâche parent si l'objet est une sous-tâche.
    :type tache_parent: str, optional
    """

    def __init__(self, titre, description, datecreation, datefin, statut, daterappel, soustache_id_tache=None,
                 tache_parent=None):
        """
        Initialise la fenêtre avec les détails d'une tâche ou sous-tâche.

        :param titre: Titre de la tâche ou sous-tâche.
        :type titre: str
        :param description: Description de la tâche ou sous-tâche.
        :type description: str
        :param datecreation: Date de création.
        :type datecreation: datetime
        :param datefin: Date de fin.
        :type datefin: datetime
        :param statut: Statut (0 pour "En cours", 1 pour "Terminée").
        :type statut: int
        :param daterappel: Date de rappel.
        :type daterappel: datetime
        :param soustache_id_tache: ID de la tâche parent (si sous-tâche).
        :type soustache_id_tache: int, optional
        :param tache_parent: Nom de la tâche parent (si sous-tâche).
        :type tache_parent: str, optional
        :return: None
        :rtype: None
        """

        super().__init__()

        self.setWindowTitle("Détail")
        self.repertoire_actuel = os.path.dirname(os.path.abspath(__file__))
        self.setWindowIcon(QIcon(OutilsCommuns.iconesDiverses("barre_titre")))
        grid = QGridLayout()
        self.setLayout(grid)
        self.resize(300, 250)

        self.titre = QLabel(f'Titre : {titre}')
        self.description = QLabel(f'Description : {description}')
        self.datecreation = QLabel(f'Date de création : {datecreation}')
        self.datefin = QLabel(f'Date de fin : {datefin}')

        if statut == 0:
            self.statut = QLabel("Statut : En cours")
        else:
            self.statut = QLabel("Statut : Terminée")

        self.daterappel = QLabel(f'Date de rappel : {daterappel}')
        self.confirmer = QPushButton("OK")

        grid.addWidget(self.titre)
        if soustache_id_tache:
            self.tache_parent = QLabel(f'Tache parent : {tache_parent}')
            grid.addWidget(self.tache_parent)
        grid.addWidget(self.statut)
        grid.addWidget(self.description)
        grid.addWidget(self.datecreation)
        grid.addWidget(self.datefin)

        grid.addWidget(self.daterappel)
        grid.addWidget(self.confirmer)

        self.confirmer.clicked.connect(self.stop)

    def stop(self):
        """
        Ferme la fenêtre de détail.

        :return: None
        :rtype: None
        """

        self.close()


# Fenêtre d'authentification
class FenetreAuthentification(QDialog):
    """
    Fenêtre d'authentification et d'inscription pour l'application.

    Cette classe gère la connexion et la création de comptes des utilisateurs.
    """

    def __init__(self):
        """
        Initialise la fenêtre d'authentification avec les paramètres par défaut.

        Définit les valeurs de connexion, le répertoire d'icônes et initialise l'interface utilisateur.

        :return: None
        :rtype: None
        """

        super().__init__()
        self.HOST = '127.0.0.1'
        self.PORT = 55555
        self.mode = "login"
        self.initUI()
        self.utilisateur = None

    def initUI(self):
        """
        Initialise l'interface utilisateur de la fenêtre d'authentification.

        :return: None
        :rtype: None
        """
        self.setWindowIcon(QIcon(OutilsCommuns.iconesDiverses("barre_titre")))
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
                border-radius: 10px;
            }
            QLabel {
                font-size: 14px;
                color: #333333;
                font-weight: bold;
            }
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #333333;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
        """)

        self.layout = QVBoxLayout()
        self.affichageFormulaireAuthentification()
        self.setLayout(self.layout)

    def effacerWidgets(self):
        """
        Supprime tous les widgets du formulaire en cours, utile lors du changement de mode (connexion/inscription).

        :return: None
        :rtype: None
        """
        while self.layout.count():
            enfant = self.layout.takeAt(0)
            if enfant.widget():
                enfant.widget().deleteLater()
            elif enfant.layout():
                self.effacerLayouts(enfant.layout())

    def effacerLayouts(self, layout):
        """
        Supprime les widgets et sous-layouts d'un layout.

        :param layout: Le layout à nettoyer.
        :type layout: QLayout
        :return: None
        :rtype: None
        """
        while layout.count():
            enfant = layout.takeAt(0)
            if enfant.widget():
                enfant.widget().deleteLater()
            elif enfant.layout():
                self.effacerLayouts(enfant.layout())

    def affichageFormulaireAuthentification(self):
        """
        Affiche le formulaire d'inscription pour les nouveaux utilisateurs.

        :return: None
        :rtype: None
        """
        self.effacerWidgets()

        self.setFixedSize(221, 280)
        self.setWindowTitle('Authentification')

        self.label_utilisateur = QLabel('Nom d\'utilisateur :', self)
        self.champ_utilisateur = QLineEdit(self)
        self.champ_utilisateur.setFixedWidth(200)

        self.label_motdepasse = QLabel('Mot de passe :', self)
        self.champ_motdepasse = QLineEdit(self)
        self.champ_motdepasse.setEchoMode(QLineEdit.Password)
        self.champ_motdepasse.setFixedWidth(200)

        self.action_afficher_motdepasse_auth = self.champ_motdepasse.addAction(
            QIcon(OutilsCommuns.calculDimensionsIcone(
                OutilsCommuns.iconesDiverses("afficher_motdepasse"),
                self.champ_motdepasse)),
            QLineEdit.TrailingPosition)
        self.action_afficher_motdepasse_auth.triggered.connect(
            lambda: OutilsCommuns.definirVisibiliteMotDePasse(
                self.champ_motdepasse, self.action_afficher_motdepasse_auth))

        self.bouton_connexion = QPushButton('Se connecter', self)
        self.bouton_connexion.setFixedSize(180, 30)
        self.bouton_connexion.clicked.connect(self.authentificationUtilisateur)
        self.bouton_connexion.setDefault(True)

        self.bouton_inscription = QPushButton('Inscription', self)
        self.bouton_inscription.setFixedSize(180, 30)
        self.bouton_inscription.clicked.connect(self.affichageFormulaireInscription)

        layout_utilisateur = QVBoxLayout()
        layout_utilisateur.setContentsMargins(0, 0, 0, 0)
        layout_utilisateur.setSpacing(5)
        layout_utilisateur.addWidget(self.label_utilisateur)
        layout_utilisateur.addWidget(self.champ_utilisateur)

        layout_motdepasse = QVBoxLayout()
        layout_motdepasse.setContentsMargins(0, 0, 0, 0)
        layout_motdepasse.setSpacing(5)
        layout_motdepasse.addWidget(self.label_motdepasse)
        layout_motdepasse.addWidget(self.champ_motdepasse)

        layout_formulaire = QVBoxLayout()
        layout_formulaire.setSpacing(15)
        layout_formulaire.addLayout(layout_utilisateur)
        layout_formulaire.addLayout(layout_motdepasse)
        layout_formulaire.addSpacing(20)

        layout_boutons = QVBoxLayout()
        layout_boutons.addWidget(self.bouton_connexion, alignment=Qt.AlignCenter)
        layout_boutons.addWidget(self.bouton_inscription, alignment=Qt.AlignCenter)
        layout_boutons.setSpacing(10)
        layout_boutons.addSpacing(8)

        layout_formulaire.addLayout(layout_boutons)

        self.layout.addLayout(layout_formulaire)

    def affichageFormulaireInscription(self):
        """
        Affiche le formulaire d'inscription pour un nouvel utilisateur.

        :return: None
        :rtype: None

        :raises Exception: Si une erreur survient lors du chargement du formulaire.
        """
        try:
            self.effacerWidgets()
            self.setFixedSize(221, 600)
            self.setWindowTitle('Inscription')

            self.label_email = QLabel('Email:', self)
            self.champ_email = QLineEdit(self)

            self.label_nom = QLabel('Nom:', self)
            self.champ_nom = QLineEdit(self)

            self.label_prenom = QLabel('Prénom:', self)
            self.champ_prenom = QLineEdit(self)

            self.label_pseudo = QLabel('Pseudo:', self)
            self.champ_pseudo = QLineEdit(self)

            self.label_motdepasse = QLabel('Mot de passe:', self)
            self.champ_motdepasse = QLineEdit(self)
            self.champ_motdepasse.setEchoMode(QLineEdit.Password)

            self.action_afficher_mdp = self.champ_motdepasse.addAction(
                QIcon(OutilsCommuns.calculDimensionsIcone(OutilsCommuns.iconesDiverses("afficher_motdepasse"),
                                                          self.champ_motdepasse)),
                QLineEdit.TrailingPosition)
            self.action_afficher_mdp.triggered.connect(
                lambda: OutilsCommuns.definirVisibiliteMotDePasse(self.champ_motdepasse,
                                                                  self.action_afficher_mdp)
            )

            self.label_confirmer_motdepasse = QLabel('Confirmer le mot de passe:', self)
            self.champ_confirmer_motdepasse = QLineEdit(self)
            self.champ_confirmer_motdepasse.setEchoMode(QLineEdit.Password)

            self.action_afficher_motdepasse_confirme = (
                self.champ_confirmer_motdepasse.addAction(QIcon(
                    OutilsCommuns.calculDimensionsIcone(OutilsCommuns.iconesDiverses("afficher_motdepasse"),
                                                        self.champ_confirmer_motdepasse)
                ), QLineEdit.TrailingPosition))
            self.action_afficher_motdepasse_confirme.triggered.connect(
                lambda: OutilsCommuns.definirVisibiliteMotDePasse(
                    self.champ_confirmer_motdepasse,
                    self.action_afficher_motdepasse_confirme)
            )

            self.barre_complexite_motdepasse = QProgressBar(self)
            self.barre_complexite_motdepasse.setRange(0, 100)
            self.barre_complexite_motdepasse.setTextVisible(False)

            self.label_complexite_motdepasse = QLabel("Complexité : Très faible", self)

            self.champ_motdepasse.textChanged.connect(self.MAJComplexiteMotDePasse)

            self.bouton_inscription = QPushButton('Créer un compte', self)
            self.bouton_inscription.clicked.connect(self.inscriptionUtilisateur)
            self.bouton_inscription.setDefault(True)

            self.bouton_retour = QPushButton('Retour à la connexion', self)
            self.bouton_retour.clicked.connect(self.affichageFormulaireAuthentification)

            self.champ_email.returnPressed.connect(self.bouton_inscription.click)
            self.champ_nom.returnPressed.connect(self.bouton_inscription.click)
            self.champ_prenom.returnPressed.connect(self.bouton_inscription.click)
            self.champ_pseudo.returnPressed.connect(self.bouton_inscription.click)
            self.champ_confirmer_motdepasse.returnPressed.connect(self.bouton_inscription.click)

            self.layout.addWidget(self.label_email)
            self.layout.addWidget(self.champ_email)
            self.layout.addWidget(self.label_nom)
            self.layout.addWidget(self.champ_nom)
            self.layout.addWidget(self.label_prenom)
            self.layout.addWidget(self.champ_prenom)
            self.layout.addWidget(self.label_pseudo)
            self.layout.addWidget(self.champ_pseudo)
            self.layout.addWidget(self.label_motdepasse)
            self.layout.addWidget(self.champ_motdepasse)
            self.layout.addWidget(self.label_confirmer_motdepasse)
            self.layout.addWidget(self.champ_confirmer_motdepasse)
            self.layout.addWidget(self.barre_complexite_motdepasse)
            self.layout.addWidget(self.label_complexite_motdepasse)
            self.layout.addWidget(self.bouton_inscription)
            self.layout.addWidget(self.bouton_retour)
        except Exception as erreur:
            QMessageBox.critical(self, 'Erreur', f"Erreur lors du chargement du formulaire : {erreur}")

    def authentificationUtilisateur(self):
        """
        Traite le formulaire de connexion et envoie les informations d'identification au serveur.

        :raises Exception: En cas d'échec de connexion ou d'erreur lors de l'authentification.
        :return: None
        :rtype: None
        """
        self.utilisateur = self.champ_utilisateur.text()
        self.motdepasse = self.champ_motdepasse.text()

        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((self.HOST, self.PORT))
            client_socket = AESsocket(client_socket, is_server=False)

            credentials = f"AUTH:{self.utilisateur}:{self.motdepasse}"  # AUTH -> signale au serveur une demande d'authentification

            print(credentials)
            client_socket.send(credentials)
            reponse = client_socket.recv(1024)

            if reponse.startswith("AUTHORIZED"):
                self.accept()
            else:
                QMessageBox.critical(self, 'Erreur', 'Nom d\'utilisateur ou mot de passe incorrect.')
            client_socket.close()
        except Exception as e:
            QMessageBox.critical(self, 'Erreur', f"Erreur lors de l'authentification: {e}")

    def inscriptionUtilisateur(self):
        """
        Traite le formulaire d'inscription et envoie les informations du compte au serveur.

        :raises Exception: En cas d'erreur lors de la création du compte ou de validation des données.
        :return: None
        :rtype: None
        """
        email = self.champ_email.text()
        nom = self.champ_nom.text()
        prenom = self.champ_prenom.text()
        pseudo = self.champ_pseudo.text()
        motdepasse = self.champ_motdepasse.text()
        motdepasse_confirme = self.champ_confirmer_motdepasse.text()

        # Vérifier les champs non vides
        if not (email and nom and prenom and pseudo and motdepasse and motdepasse_confirme):
            QMessageBox.critical(self, 'Erreur', 'Tous les champs sont obligatoires.')
            return
        # Vérification des mots de passe
        if motdepasse != motdepasse_confirme:
            QMessageBox.critical(self, 'Erreur', 'Les mots de passe ne correspondent pas.')
            return

        # Vérification de l'email
        if not self.validationDesEmail(email):
            QMessageBox.critical(self, 'Erreur', 'Adresse email invalide.')
            return

        # Vérification des caractères interdits
        if not all(self.validationDesEntrees(field) for field in [nom, prenom, pseudo, motdepasse]):
            QMessageBox.critical(self, 'Erreur', 'Les champs contiennent des caractères interdits.')
            return

        # Envoi des données au serveur
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((self.HOST, self.PORT))
            client_socket = AESsocket(client_socket, is_server=False)

            # generarion du sel et hashage du mot de passe
            salt = bcrypt.gensalt()
            motdepasse = motdepasse.encode('utf-8')
            motdepasse_hache = bcrypt.hashpw(motdepasse, salt)
            motdepasse_hache_decode = motdepasse_hache.decode('utf-8')

            message = f"CREATE_ACCOUNT:{email}:{nom}:{prenom}:{pseudo}:{motdepasse_hache_decode}"
            client_socket.send(message)
            reponse = client_socket.recv(1024)

            if reponse.startswith("ACCOUNT_CREATED"):
                QMessageBox.information(self, 'Succès', 'Compte créé avec succès !')
                self.affichageFormulaireAuthentification()
            elif reponse.startswith("EMAIL_TAKEN"):
                QMessageBox.critical(self, 'Erreur', 'Adresse email déjà utilisée.')
            elif reponse.startswith("PSEUDO_TAKEN"):
                QMessageBox.critical(self, 'Erreur', 'Le pseudo est déjà utilisé.')
            client_socket.close()
        except Exception as e:
            QMessageBox.critical(self, 'Erreur', f"Erreur lors de la création du compte : {e}")

    def MAJComplexiteMotDePasse(self):
        """
        Met à jour la barre de progression et l'indicateur de complexité du mot de passe.

        :return: None
        :rtype: None
        """
        try:
            motdepasse = self.champ_motdepasse.text()
            print(motdepasse)
            complexite = self.evaluerMotDePasse(motdepasse)

            niveaux = {
                "Très faible": (0, "red"),
                "Faible": (25, "orange"),
                "Moyen": (50, "yellow"),
                "Sécurisé": (75, "lightgreen"),
                "Inviolable": (100, "green")
            }
        except Exception as e:
            print(f'Echec lors du test de complexité: {e}')

        niveau, couleur = niveaux[complexite]
        self.barre_complexite_motdepasse.setValue(niveau)
        self.barre_complexite_motdepasse.setStyleSheet(f"QProgressBar::chunk {{ background-color: {couleur}; }}")
        self.label_complexite_motdepasse.setText(f"Complexité : {complexite}")

    def evaluerMotDePasse(self, MDP):
        """
        Évalue la complexité d'un mot de passe et renvoie une chaîne représentant son niveau.

        :param MDP: Le mot de passe à évaluer.
        :type MDP: str
        :return: Niveau de complexité du mot de passe.
        :rtype: str
        """
        try:
            # Initialiser les critères
            if len(MDP) >= 8 and len(MDP) < 14:
                longueurMotDePasse = 1
            elif len(MDP) >= 14 and len(MDP) < 20:
                longueurMotDePasse = 2
            elif len(MDP) >= 20:
                longueurMotDePasse = 3
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
                return "Inviolable"
            elif complexite == 4:
                return "Sécurisé"
            elif complexite == 3:
                return "Moyen"
            elif complexite == 2:
                return "Faible"
            else:
                return "Très faible"
        except Exception as e:
            print(f'Erreur lors de l\'évaluation de complexité : {e}')
            return "Très faible"

    def validationDesEntrees(self, input_text):
        """
        Vérifie la validité des champs de saisie selon un regex interdisant certains caractères.

        :param input_text: Texte à valider.
        :type input_text: str
        :return: True si valide, False sinon.
        :rtype: bool
        """
        # définission des caracteres interdits
        forbidden_pattern = r"[:;,']"
        return not re.search(forbidden_pattern, input_text)

    def validationDesEmail(self, email):
        """
        Vérifie si une adresse email est valide selon un regex.

        :param email: Adresse email à valider.
        :type email: str
        :return: True si valide, False sinon.
        :rtype: bool
        """
        email_regex = r'^[a-zA-Z0-9._+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None

    def getIdentifiants(self):
        """
        Renvoie les informations d'identification de l'utilisateur.

        :return: Un tuple contenant le nom d'utilisateur et le mot de passe.
        :rtype: tuple(str, str)
        """

        return self.utilisateur, self.motdepasse


# Fenêtre changement de mot de passe
class FenetreChangerMotDePasse(QDialog):
    """
    Fenêtre permettant à un utilisateur de changer son mot de passe.

    :param utilisateur: Nom d'utilisateur pour lequel le mot de passe doit être changé.
    :type utilisateur: str
    :param client_socket: Socket de communication avec le serveur.
    :type client_socket: AESsocket
    """

    def __init__(self, utilisateur, client_socket):
        """
        Initialise la fenêtre de changement de mot de passe.

        :param utilisateur: Nom d'utilisateur pour lequel le mot de passe doit être changé.
        :type utilisateur: str
        :param client_socket: Socket de communication avec le serveur.
        :type client_socket: AESsocket
        :raises Exception: Si la connexion au serveur échoue.
        """

        super().__init__()
        self.initUI()
        self.utilisateur = utilisateur
        try:
            self.HOST = '127.0.0.1'
            self.PORT = 55555
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.HOST, self.PORT))
            self.client_socket = AESsocket(self.client_socket, is_server=False)
        except Exception as e:
            QMessageBox.critical(self, 'Erreur',
                                 f'Erreur lors du chargement du formulaire de changement de mot de passse: {e}')

        self.motdepasse = None

    def initUI(self):
        """
        Initialise l'interface utilisateur de la fenêtre de changement de mot de passe.

        :raises Exception: En cas d'erreur lors de l'initialisation des widgets ou de la fenêtre.
        :return: None
        :rtype: None
        """
        try:
            self.setFixedSize(254, 240)
            self.setWindowTitle('Changer le mot de passe')
            self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
                border-radius: 10px;
            }
            QLabel {
                font-size: 14px;
                color: #333333;
                font-weight: bold;
            }
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #333333;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
            """)

            self.setWindowIcon(QIcon(OutilsCommuns.iconesDiverses("barre_titre")))
            self.label_nouveau_mdp = QLabel('Nouveau mot de passe :', self)
            self.champ_nouveau_mdp = QLineEdit(self)
            self.champ_nouveau_mdp.setEchoMode(QLineEdit.Password)

            self.action_afficher_nouveau_mdp = self.champ_nouveau_mdp.addAction(
                QIcon(OutilsCommuns.calculDimensionsIcone(
                    OutilsCommuns.iconesDiverses("afficher_motdepasse"),
                    self.champ_nouveau_mdp)),
                QLineEdit.TrailingPosition)
            self.action_afficher_nouveau_mdp.triggered.connect(
                lambda: OutilsCommuns.definirVisibiliteMotDePasse(
                    self.champ_nouveau_mdp,
                    self.action_afficher_nouveau_mdp))

            self.label_confirmer_mdp = QLabel('Confirmer le mot de passe :', self)
            self.champ_confirmer_mdp = QLineEdit(self)
            self.champ_confirmer_mdp.setEchoMode(QLineEdit.Password)

            self.action_afficher_confirmer_mdp = self.champ_confirmer_mdp.addAction(
                QIcon(OutilsCommuns.calculDimensionsIcone(
                    OutilsCommuns.iconesDiverses("afficher_motdepasse"),
                    self.champ_confirmer_mdp)),
                QLineEdit.TrailingPosition)
            self.action_afficher_confirmer_mdp.triggered.connect(
                lambda: OutilsCommuns.definirVisibiliteMotDePasse(
                    self.champ_confirmer_mdp,
                    self.action_afficher_confirmer_mdp))

            self.bouton_changer_mdp = QPushButton('Changer le mot de passe', self)
            self.bouton_changer_mdp.setFixedSize(190, 40)
            self.bouton_changer_mdp.clicked.connect(self.changerMotDePasse)

            layout_nouveau_mdp = QVBoxLayout()
            layout_nouveau_mdp.setContentsMargins(0, 0, 0, 0)
            layout_nouveau_mdp.setSpacing(5)
            layout_nouveau_mdp.addWidget(self.label_nouveau_mdp)
            layout_nouveau_mdp.addWidget(self.champ_nouveau_mdp)

            layout_confirmer_mdp = QVBoxLayout()
            layout_confirmer_mdp.setContentsMargins(0, 0, 0, 0)
            layout_confirmer_mdp.setSpacing(5)
            layout_confirmer_mdp.addWidget(self.label_confirmer_mdp)
            layout_confirmer_mdp.addWidget(self.champ_confirmer_mdp)

            layout = QVBoxLayout()
            layout.setSpacing(15)
            layout.addLayout(layout_nouveau_mdp)
            layout.addLayout(layout_confirmer_mdp)
            layout.addSpacing(10)

            layout_bouton = QVBoxLayout()
            layout_bouton.addWidget(self.bouton_changer_mdp, alignment=Qt.AlignCenter)
            layout_bouton.addSpacing(15)

            layout.addLayout(layout_bouton)

            self.setLayout(layout)

        except Exception as e:
            QMessageBox.critical(self, 'Erreur',
                                 f'Erreur lors du chargement du formulaire de changement de mot de passse: {e}')

    def changerMotDePasse(self):
        """
        Envoie une requête au serveur pour changer le mot de passe de l'utilisateur.

        Vérifie que les mots de passe saisis correspondent et les envoie au serveur après hashage.
        Affiche des messages pour indiquer le succès ou l'échec de l'opération.

        :raises Exception: En cas d'erreur lors de l'envoi ou de la réception des données avec le serveur.
        :return: None
        :rtype: None
        """
        new_motDePasse = self.champ_nouveau_mdp.text()
        confirm_motDePasse = self.champ_confirmer_mdp.text()

        # Vérifiez que les mots de passe correspondent
        if new_motDePasse == confirm_motDePasse:
            print(new_motDePasse)
            try:
                # generarion du sel et hashage du mot de passe
                salt = bcrypt.gensalt()
                motdepasse = new_motDePasse.encode('utf-8')
                motdepasse_hache = bcrypt.hashpw(motdepasse, salt)
                motdepasse_hache_decode = motdepasse_hache.decode('utf-8')
                print(motdepasse_hache_decode)

                message = f"CHANGE_PASSWORD:{self.utilisateur}:{motdepasse_hache_decode}"
                print(message)
                self.client_socket.send(message)

                reponse = self.client_socket.recv(1024)
                if reponse == "PASSWORD_CHANGED":
                    QMessageBox.information(self, 'Changement de mot de passe', 'Mot de passe changé avec succès!')
                    self.close()
                else:
                    QMessageBox.critical(self, 'Erreur', 'Échec du changement de mot de passe.')
            except Exception as e:
                print(f"Erreur lors du changement de mot de passe: {e}")
                QMessageBox.critical(self, 'Erreur', f'{e}\n')
        else:
            QMessageBox.critical(self, 'Erreur', f'Les mots de passe ne correspondent pas.\n')


class OutilsCommuns:
    @staticmethod
    def iconesDiverses(type_icone="barre_titre"):
        """
        Retourne le chemin complet de l'icône en fonction du type demandé.

        :param type_icone: Type d'icône à récupérer ("barre_titre", "afficher_motdepasse", "masquer_motdepasse").
        :type type_icone: str
        :return: Chemin absolu de l'icône.
        :rtype: str
        """
        repertoire_actuel = os.path.dirname(os.path.abspath(__file__))

        chemins_icones = {
            "barre_titre": os.path.join(
                repertoire_actuel,
                "img/barre_titre/",
                "ICONE_TITRE_TRANSP.png"
            ),
            "afficher_motdepasse": os.path.join(
                repertoire_actuel,
                "img/authentification/",
                "AFFICHER_MDP_TRANSP.png"
            ),
            "masquer_motdepasse": os.path.join(
                repertoire_actuel,
                "img/authentification/",
                "MASQUER_MDP_TRANSP.png"
            ),
        }
        return chemins_icones.get(type_icone, None)

    @staticmethod
    def calculDimensionsIcone(chemin_icone, champ):
        """
        Redimensionne l'icône en fonction de la taille du champ donné.
        :param chemin_icone: Chemin du fichier d'icône
        :param champ: QLineEdit cible
        :return: QPixmap redimensionné
        """
        taille_icone = champ.sizeHint().height()
        return QPixmap(chemin_icone).scaled(
            taille_icone, taille_icone, Qt.KeepAspectRatio,
            Qt.SmoothTransformation)

    @staticmethod
    def definirVisibiliteMotDePasse(champ, action):
        """
        Affiche ou masque le mot de passe pour le champ donné.
        :param champ: Champ de mot de passe ciblé (QLineEdit)
        :param action: Action associée au champ (QAction)
        """
        if champ.echoMode() == QLineEdit.Password:
            champ.setEchoMode(QLineEdit.Normal)
            action.setIcon(QIcon(OutilsCommuns.iconesDiverses("masquer_motdepasse")))
        else:
            champ.setEchoMode(QLineEdit.Password)
            action.setIcon(QIcon(OutilsCommuns.iconesDiverses("afficher_motdepasse")))


if __name__ == '__main__':
    application = QApplication(sys.argv)
    fenetre_authentification = FenetreAuthentification()
    if fenetre_authentification.exec() == QDialog.Accepted:
        pseudonyme_utilisateur, motdepasse_utilisateur = fenetre_authentification.getIdentifiants()
        fenetre_principale = TodoListApp(pseudonyme_utilisateur, motdepasse_utilisateur)
        fenetre_principale.show()
        sys.exit(application.exec_())