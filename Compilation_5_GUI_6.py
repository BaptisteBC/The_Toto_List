from PyQt5.QtCore import Qt, QDate, QSize, QCoreApplication, QDateTime, QPoint
from PyQt5.QtGui import QPalette, QColor, QIcon, QKeySequence, QPixmap, QCursor
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, 
                             QTextEdit, QComboBox,QDateEdit, QVBoxLayout, 
                             QPushButton, QMessageBox, QGridLayout, 
                             QListWidget, QListWidgetItem, QProgressBar, 
                             QAction, QDialog, QHBoxLayout, QMainWindow, 
                             QCheckBox, QMenu, QFormLayout, QDateTimeEdit, 
                             QDialogButtonBox)
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

#Création de la tâche (Yann)
class FormulaireTache(QWidget):
    """
    Classe représentant l'interface graphique pour créer une tâche.

    Attributes:
        listes (dict): Liste des listes disponibles pour organiser les tâches.
        utilisateurs (dict): Liste des utilisateurs assignables à une tâche.
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
            self.TodoListApp.actualiser()
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
            self.motdepasse = motdepasse_utilisateur
            self.initUI()
            self.formulaire = FormulaireTache(self)
            self.setWindowTitle("The Toto List")
            self.setGeometry(100, 100, 500, 700)
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.HOST, self.PORT))
            self.client_socket = AESsocket(self.client_socket, is_server=False)
            time.sleep(0.5)
            self.client_socket.send(f"AUTH:{pseudonyme_utilisateur}:{motdepasse_utilisateur}")
            self.creerActions()
            self.creerMenu()
        except Exception as e:
            QMessageBox.critical(self, 'Erreur', f'Erreur lors du chargement de la fenetre {e}')

        self.repertoire_actuel = os.path.dirname(os.path.abspath(__file__))
        self.icone_barre_titre = os.path.join(
            self.repertoire_actuel,
            "img/barre_titre/",
            "ICONE_TITRE_TRANSP.png")
        self.setWindowIcon(QIcon(self.icone_barre_titre))
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

        # Widget central pour le contenu principal
        central_widget = QWidget()
        layout_principal = QHBoxLayout(central_widget)  # Layout principal horizontal (sidebar + contenu principal)

        # *** Sidebar ***
        self.sidebar = QWidget()
        layout_barre_laterale = QVBoxLayout(self.sidebar)

        # Boutons de la sidebar
        self.bouton_actualiser = QPushButton("Actualiser")
        self.bouton_restaurer = QPushButton("Restaurer la corbeille")
        self.bouton_vider = QPushButton("Vider la corbeille")
        self.bouton_quitter = QPushButton("Quitter")

        # Ajout des boutons dans la sidebar
        layout_barre_laterale.addWidget(self.bouton_actualiser)
        layout_barre_laterale.addWidget(self.bouton_restaurer)
        layout_barre_laterale.addWidget(self.bouton_vider)
        layout_barre_laterale.addWidget(self.bouton_quitter)

        # *** Zone principale ***
        self.main_widget = QWidget()
        layout_principal_vertical = QVBoxLayout(self.main_widget)

        #Barre de navigation (haut)
        layout_navigation = QHBoxLayout()
        self.bouton_barre_laterale = QPushButton()
        icon_url = "https://icons.veryicon.com/png/o/miscellaneous/we/sidebar-2.png"  # Remplacez par l'URL réelle
        self.set_icon_from_url(self.bouton_barre_laterale, icon_url)
        self.bouton_barre_laterale.setFixedSize(30, 30)  # Taille de l'icône
        self.bouton_barre_laterale.clicked.connect(self.toggle_sidebar)

        self.bouton_formulaire = QPushButton("Ouvrir Formulaire")
        self.bouton_formulaire.clicked.connect(self.open_formulaire)
        self.bouton_formulaire.setFixedSize(200, 30)

        self.bouton_theme = QPushButton()
        icon_url = "https://png.pngtree.com/png-clipart/20220812/ourmid/pngtree-shine-sun-light-effect-free-png-and-psd-png-image_6106445.png"  # Remplacez par l'URL réelle
        self.set_icon_from_url(self.bouton_theme, icon_url)
        self.bouton_theme.setIconSize(QSize(20, 20))  # Réduire la taille de l'icône à 20x20
        self.bouton_theme.setFixedSize(30, 30)  # Réduire la taille du bouton à 30x30
        self.bouton_theme.clicked.connect(self.toggle_theme)

        # Ajout des boutons dans la barre de navigation
        layout_navigation.addWidget(self.bouton_barre_laterale)
        layout_navigation.addWidget(self.bouton_formulaire)
        layout_navigation.addWidget(self.bouton_theme)
        layout_navigation.setContentsMargins(5, 0, 5, 0)
        layout_navigation.addStretch()

        # Liste des tâches (en dessous de la barre de navigation)
        self.taches = QListWidget()
        self.taches.setStyleSheet("""
            QListWidget::item:selected {
                background: transparent;  /* Supprime la couleur de surbrillance */
            }
            QListWidget::item {
                border: none;
                background: transparent;
                margin: 0px;  /* Supprime les marges par défaut */
                padding: 0px;
            }
        """)

        # Ajout des éléments dans le layout vertical principal
        layout_principal_vertical.addLayout(layout_navigation)
        layout_principal_vertical.addWidget(self.taches)

        # Ajout de la sidebar et de la zone principale dans le layout principal
        layout_principal.addWidget(self.sidebar)
        layout_principal.addWidget(self.main_widget)

        # Définir le widget central
        self.setCentralWidget(central_widget)

        # Connexion des signaux pour les boutons
        self.bouton_actualiser.clicked.connect(self.actualiser)
        self.bouton_restaurer.clicked.connect(self.restaurer)
        self.bouton_vider.clicked.connect(self.vider)
        self.bouton_quitter.clicked.connect(self.quitter)
        self.actualiser()

        layout_principal.addWidget(self.main_widget)

        self.is_dark_mode = False


    def actualiser(self):

        """
        Actualise la liste des tâches et sous-tâches depuis la base de données.

        :raises pymysql.MySQLError: Erreur lors de la connexion ou l'exécution des requêtes SQL sur la base de données.
        """
        try:
            aes_socket = self.conection()
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
            aes_socket = self.conection()
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

    def conection(self):
        """
        Établit une connexion sécurisée avec le serveur via un socket.

        :return: Socket sécurisé pour échanger des données chiffrées.
        :rtype: AESsocket
        :raises Exception: Si la connexion au serveur échoue.
        """
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('localhost', 55555))
            return AESsocket(client_socket, is_server=False)
        except Exception as e:
            QMessageBox.critical(self, "Erreur de connexion", f"Erreur de connexion au serveur : {e}")
            return None



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
                background-color: #f5f5f5;  /* Couleur de fond */
                border: 1px solid #cccccc; /* Bordure légère */
                border-radius: 10px;       /* Coins arrondis */
                padding: 5px;
                margin-bottom: 8px;        /* Espacement entre les widgets */
            }
            QWidget#TacheWidget:hover {
                background-color: #e0e0e0;  /* Change la couleur au survol */
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
            labelTache.setStyleSheet("text-decoration: line-through; color: gray;")
        else:
            labelTache.setStyleSheet("")

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
                background-color: #f0f0f0; /* Couleur au survol */
            }
        """)
        boutonModifier.clicked.connect(lambda: self.modifierTache(idTache))

        # Bouton Supprimer
        boutonSupprimer = QPushButton()
        boutonSupprimer.setIcon(QIcon(self.icone_supprimer_tache_noir))
        boutonSupprimer.setFixedSize(24, 24)
        boutonSupprimer.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: #f0f0f0; /* Couleur au survol */
            }
        """)
        boutonSupprimer.clicked.connect(lambda: self.supprimer(idTache))

        # Bouton Ajouter sous-tâche
        boutonAjouterSousTache = QPushButton()
        boutonAjouterSousTache.setIcon(QIcon(
            self.icone_ajouter_soustache_noir))  # Chemin de l'icône à définir
        boutonAjouterSousTache.setFixedSize(24, 24)
        boutonAjouterSousTache.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: #f0f0f0; /* Couleur au survol */
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

        # Gestion des événements (double-clic, clic droit)
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
            labelTache.setStyleSheet("text-decoration: line-through; color: gray;")
            self.mettreAJourValidation(idTache, 1)
        else:
            labelTache.setStyleSheet("")
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
                background-color: #ffffff;  /* Couleur de fond */
                border: 1px solid #dddddd;  /* Bordure légèrement plus claire */
                border-radius: 10px;        /* Coins arrondis */
                padding: 5px;
                margin-bottom: 6px;         /* Espacement réduit */
            }
            QWidget#SousTacheWidget:hover {
                background-color: #e0e0e0;  /* Change la couleur au survol */
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
        caseCocheSousTache.stateChanged.connect(lambda: self.mettreAJourStyleSousTache(labelSousTache, idSousTache, caseCocheSousTache.isChecked()))

        labelSousTache = QLabel(titreSousTache)

        if statutSousTache == 1:
            labelSousTache.setStyleSheet("text-decoration: line-through; color: gray;")
        else:
            labelSousTache.setStyleSheet("color: darkgray;")

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
                background-color: #f0f0f0; /* Couleur au survol */
            }
        """)
        boutonModifier.clicked.connect(
            lambda: self.modifierSousTache(idSousTache))

        # Bouton Supprimer
        boutonSupprimer = QPushButton()
        boutonSupprimer.setIcon(QIcon(self.icone_supprimer_tache_noir))
        boutonSupprimer.setFixedSize(24, 24)
        boutonSupprimer.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: #f0f0f0; /* Couleur au survol */
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

        # Gestion des événements (double-clic, clic droit)
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
        :param bouton: Bouton source qui déclenche l'affichage du menu
        :type bouton: QPushButton
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
            labelSousTache.setStyleSheet("text-decoration: line-through; color: gray;")
            self.mettreAJourValidationSousTache(idSousTache, 1)
        else:
            labelSousTache.setStyleSheet("")
            self.mettreAJourValidationSousTache(idSousTache, 0)

    def afficherMenuTache(self, idTache, position=None):
        """
        Affiche un menu contextuel avec des options pour une tâche spécifique.

        :param idTache: Identifiant unique de la tâche
        :type idTache: int
        :param bouton: Bouton source qui déclenche l'affichage du menu
        :type bouton: QPushButton
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
            aes_socket = self.conection()
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
            aes_socket = self.conection()
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
            aes_socket = self.conection()
            if not aes_socket:
                print("Erreur de connexion au serveur.")
                return
            aes_socket.send(f"GET_tache:{idTache}")
            tache_data = aes_socket.recv(1024)
            tache_j = json.loads(tache_data)
            if isinstance(tache_j, list) and tache_j:
                tache = tuple(datetime.strptime(value, '%Y-%m-%d %H:%M:%S') if i in [2, 4] and value else value for i, value in enumerate(tache_j[0]))
            else:
                QMessageBox.information(self, "Info", "Aucune tâche trouvée.")
                return
            dialog = QDialog(self)
            dialog.setWindowTitle("Modifier la Tâche")
            form = QFormLayout(dialog)

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

            form.addRow("Titre:", titreEdit)
            form.addRow("Description:", descriptionEdit)
            form.addRow("Date de Fin:", dateFinEdit)
            form.addRow("Récurrence:", recurrenceEdit)
            form.addRow(rappelCheck, dateRappelEdit)

            boutons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            boutons.accepted.connect(lambda: self.sauvegarderModification(idTache,titreEdit.text(),descriptionEdit.text(),dateFinEdit.dateTime(),recurrenceEdit.currentText(),dateRappelEdit.dateTime() if rappelCheck.isChecked() else None, dialog ))
            boutons.rejected.connect(dialog.reject)
            form.addWidget(boutons)
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

            aes_socket = self.conection()
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
        :type idSousTâche: str
        :raises pymysql.MySQLError: En cas d'erreur SQL lors de la récupération des données de la sous-tâche.
        :return: None
        :rtype: None
        """
        try:
            aes_socket = self.conection()
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
            form = QFormLayout(dialog)

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

            form.addRow("Titre:", titreEdit)
            form.addRow("Description:", descriptionEdit)
            form.addRow("Date de Fin:", dateFinEdit)
            form.addRow(rappelCheck, dateRappelEdit)

            boutons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            boutons.accepted.connect(lambda: self.sauvegarderModificationSousTache(idSousTache, titreEdit.text(), descriptionEdit.text(), dateFinEdit.dateTime(), dateRappelEdit.dateTime() if rappelCheck.isChecked() else None, dialog))
            boutons.rejected.connect(dialog.reject)
            form.addWidget(boutons)

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
            aes_socket = self.conection()
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
        form = QFormLayout(dialog)

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

        form.addRow("Titre:", titreEdit)
        form.addRow("Description:", descriptionEdit)
        form.addRow("Date de Fin:", dateFinEdit)
        form.addRow(rappelCheck, dateRappelEdit)

        boutons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        boutons.accepted.connect(lambda: self.creerSousTache(idTacheParent, titreEdit.text(), descriptionEdit.text(), dateFinEdit.dateTime(), dateRappelEdit.dateTime() if rappelCheck.isChecked() else None, dialog))
        boutons.rejected.connect(dialog.reject)
        form.addWidget(boutons)

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
            aes_socket = self.conection()
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
        aes_socket = self.conection()
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


    def detail(self, idTache,):

        aes_socket = self.conection()
        if not aes_socket:
            print("Erreur de connexion au serveur.")
            return
        aes_socket.send(f"GET_tacheDetail:{idTache}")
        tache_data = aes_socket.recv(1024)
        tache_j = json.loads(tache_data)
        if isinstance(tache_j, list) and tache_j:
            tache = tuple(
                datetime.strptime(value, '%Y-%m-%d %H:%M:%S') if i in [2, 3,5] and value else value for i, value in
                enumerate(tache_j[0]))
        else:
            QMessageBox.information(self, "Info", "Aucune tâche trouvée.")
            return

        try:
            FenetreDetail(tache[0],tache[1], tache[2],tache[3],tache[4], tache[5]).exec()
        except:
            print("erreur execution detail")


    def restaurer(self):
        Restaurer().exec()
        self.actualiser()

    def supprimer(self, id_tache):
        try:
            SupprimerTache(id_tache, 0).exec()
            self.actualiser()
        except:
            print("erreur ouverture fenetre suppresion")

    def supprimerSousTache(self, id_tache):
        try:
            SupprimerTache(id_tache, 1).exec()
            self.actualiser()
        except:
            print("erreur ouverture fenetre suppresion")


    def vider(self):
        Vider_corbeille().exec()

    def quitter(self):
        QCoreApplication.exit(0)

    def set_icon_from_url(self, button, url):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            reponse = requests.get(url, headers=headers, stream=True)
            reponse.raise_for_status()  # Vérifie les erreurs HTTP
            carte_pixels = QPixmap()
            if not carte_pixels.loadFromData(reponse.content):
                raise ValueError("Impossible de charger l'image à partir des données.")
            icone = QIcon(carte_pixels)
            button.setIcon(icone)
        except Exception as e:
            print(f"Erreur lors du chargement de l'image : {e}")
            QMessageBox.warning(self, "Erreur d'image", f"Impossible de charger l'image depuis {url} : {e}")

    def creerMenu(self):
        """
        permet de faire un menu d'actions
        :return:
        """
        menuBar = self.menuBar()

        # Menu Options
        optionsMenu = menuBar.addMenu("Options")
        optionsMenu.addAction(self.actChangemotDePasse)
        optionsMenu.addAction(self.actParametres)
        optionsMenu.addAction(self.actExit)

        # Menu Options
        creditsMenu = menuBar.addMenu("À propos")
        creditsMenu.addAction(self.actAide)
        creditsMenu.addAction(self.actCredits)

    def creerActions(self):
        """
        permet de définir les raccourci clavier afin de faire des actions
        :return:
        """
        self.actChangemotDePasse = QAction("Changer de mot de passe", self)
        self.actChangemotDePasse.setShortcut(QKeySequence("Ctrl+P"))
        self.actChangemotDePasse.triggered.connect(self.fenetreChangementMDP)

        self.actParametres = QAction("Paramètres", self)
        self.actParametres.triggered.connect(self.open_settings)

        self.actExit = QAction("Exit", self)
        self.actExit.setShortcut(QKeySequence("Alt+F4"))
        self.actExit.setStatusTip("Exit")
        self.actExit.triggered.connect(self.fermeture)

        # Action Crédits
        self.actCredits = QAction("Crédits", self)
        self.actCredits.triggered.connect(self.open_credits)

        self.actAide = QAction("Aide", self)
        self.actAide.triggered.connect(self.open_help)

    def fermeture(self):
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
            self.formulaire_window = FormulaireTache(self)
            self.formulaire_window.show()
        except Exception as e:
            print(f"Erreur lors de l'ouverture du formulaire : {e}")

    def toggle_theme(self):
        if not self.is_dark_mode:
            self.set_dark_mode()
            icon_url = "https://icones.pro/wp-content/uploads/2021/02/icone-de-la-lune-grise.png"  # Remplacez par l'URL réelle
            self.set_icon_from_url(self.bouton_theme, icon_url)  # Icône Lune pour le mode sombre
        else:
            self.set_light_mode()
            icon_url = "https://png.pngtree.com/png-clipart/20220812/ourmid/pngtree-shine-sun-light-effect-free-png-and-psd-png-image_6106445.png"  # Remplacez par l'URL réelle
            self.set_icon_from_url(self.bouton_theme, icon_url)  # Icône Soleil pour le mode clair
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

class SupprimerTache(QDialog):
    def __init__(self, idTache, typeTache):
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

        self.idTache:str = idTache
        self.typeTache: str = typeTache

        self.confirmer.clicked.connect(self.conf)
        self.annuler.clicked.connect(self.stop)

    def conection(self):
        """
        Établit une connexion sécurisée avec le serveur via un socket.

        :return: Socket sécurisé pour échanger des données chiffrées.
        :rtype: AESsocket
        :raises Exception: Si la connexion au serveur échoue.
        """
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('localhost', 55555))
            return AESsocket(client_socket, is_server=False)
        except Exception as e:
            QMessageBox.critical(self, "Erreur de connexion", f"Erreur de connexion au serveur : {e}")
            return None

    def conf(self):
        try :
            if self.typeTache == 0 :
                aes_socket = self.conection()
                if not aes_socket:
                    print("Erreur de connexion au serveur.")
                    return
                aes_socket.send(f"SUP_Tache:{self.idTache}")

            else:
                aes_socket = self.conection()
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
       self.close()

class Vider_corbeille(QDialog):
    def __init__(self):
        super().__init__()

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

    def conection(self):
        """
        Établit une connexion sécurisée avec le serveur via un socket.

        :return: Socket sécurisé pour échanger des données chiffrées.
        :rtype: AESsocket
        :raises Exception: Si la connexion au serveur échoue.
        """
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('localhost', 55555))
            return AESsocket(client_socket, is_server=False)
        except Exception as e:
            QMessageBox.critical(self, "Erreur de connexion", f"Erreur de connexion au serveur : {e}")
            return None

    def conf(self):
        aes_socket = self.conection()
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
       self.close()

class Restaurer(QDialog):
    def __init__(self):
        super().__init__()

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

    def conection(self):
        """
        Établit une connexion sécurisée avec le serveur via un socket.

        :return: Socket sécurisé pour échanger des données chiffrées.
        :rtype: AESsocket
        :raises Exception: Si la connexion au serveur échoue.
        """
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('localhost', 55555))
            return AESsocket(client_socket, is_server=False)
        except Exception as e:
            QMessageBox.critical(self, "Erreur de connexion", f"Erreur de connexion au serveur : {e}")
            return None

    def conf(self):
        aes_socket = self.conection()
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
       self.close()

class FenetreDetail(QDialog):
    def __init__(self, titre, description, datecreation, datefin, statut, daterappel, soustache_id_tache=None, tache_parent=None):
        super().__init__()

        self.setWindowTitle("Détail")

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
       self.close()

#Fenêtre d'authentification
class AuthWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.HOST = '127.0.0.1'
        self.PORT = 55555
        self.mode = "login"
        self.repertoire_actuel = os.path.dirname(os.path.abspath(__file__))
        self.icone_afficher_motdepasse = os.path.join(
            self.repertoire_actuel, 
            "img/authentification/", 
            "AFFICHER_MDP_TRANSP.png")
        self.icone_masquer_motdepasse = os.path.join(
            self.repertoire_actuel, 
            "img/authentification/", 
            "MASQUER_MDP_TRANSP.png")
        self.initUI()
        self.utilisateur = None


    def initUI(self):
        """
        Initialisation de la fenêtre.
        """
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "img/barre_titre/", "ICONE_TITRE_TRANSP.png")))
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;  /* Couleur de fond */
                border-radius: 10px;       /* Coins arrondis */
            }
            QLabel {
                font-size: 14px;
                color: #333333;            /* Texte sombre */
                font-weight: bold;         /* Texte en gras */
            }
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #333333; /* Gris anthracite */
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4d4d4d; /* Gris plus clair au survol */
            }
        """)

        self.layout = QVBoxLayout()
        self.affichageFormulaireAuthentification()
        self.setLayout(self.layout)

    def effacerWidgets(self):
        """
        cette methode efface tout les widgets du formulaire lors du switch
        entre "Se connecter" et "Inscription".
        :return:
        """
        while self.layout.count():
            enfant = self.layout.takeAt(0)
            if enfant.widget():
                enfant.widget().deleteLater()
            elif enfant.layout():
                self.effacerLayouts(enfant.layout())

    def effacerLayouts(self, layout):
        """
        Supprime les widgets et sous-layouts d'un layout donné.
        """
        while layout.count():
            enfant = layout.takeAt(0)
            if enfant.widget():
                enfant.widget().deleteLater()
            elif enfant.layout():
                self.effacerLayouts(enfant.layout())

    def calculDimensionsIcone(self, chemin_icone, champ):
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

    def affichageFormulaireAuthentification(self):
        """
        Cette méthode permet l'affichage du formulaire d'authentification 
        lors du lancement de l'application.
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
            QIcon(self.calculDimensionsIcone(self.icone_afficher_motdepasse,
                                             self.champ_motdepasse)),
            QLineEdit.TrailingPosition)
        self.action_afficher_motdepasse_auth.triggered.connect(
            lambda: self.definirVisibiliteMotDePasse(
                self.champ_motdepasse,self.action_afficher_motdepasse_auth))

        self.bouton_connexion = QPushButton('Se connecter', self)
        self.bouton_connexion.setFixedSize(180, 30)
        self.bouton_connexion.clicked.connect(self.authentificationUtilisateur)
        self.bouton_connexion.setDefault(True)

        self.bouton_inscription = QPushButton('Inscription', self)
        self.bouton_inscription.setFixedSize(180, 30)
        self.bouton_inscription.clicked.connect(self.affichageFormulaireInscription)

        layout_utilisateur = QVBoxLayout()
        layout_utilisateur.setContentsMargins(0, 0, 0,0)
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

    def definirVisibiliteMotDePasse(self, champ, action):
        """
        Affiche ou masque le mot de passe pour le champ donné.
        :param champ: Champ de mot de passe ciblé (QLineEdit)
        :param action: Action associée au champ (QAction)
        """
        if champ.echoMode() == QLineEdit.Password:
            champ.setEchoMode(QLineEdit.Normal)
            action.setIcon(QIcon(self.icone_masquer_motdepasse))
        else:
            champ.setEchoMode(QLineEdit.Password)
            action.setIcon(QIcon(self.icone_afficher_motdepasse))

    def affichageFormulaireInscription(self):
        """
    Cette méthode affiche le formulaire d'inscription pour les nouveaux utilisateurs.
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

            self.action_afficher_motdepasse = self.champ_motdepasse.addAction(
                QIcon(self.calculDimensionsIcone(self.icone_afficher_motdepasse,
                                               self.champ_motdepasse)),
                QLineEdit.TrailingPosition)
            self.action_afficher_motdepasse.triggered.connect(
                lambda: self.definirVisibiliteMotDePasse(self.champ_motdepasse,
                                                         self.action_afficher_motdepasse)
            )
            
            self.label_confirmer_motdepasse = QLabel('Confirmer le mot de passe:', self)
            self.champ_confirmer_motdepasse = QLineEdit(self)
            self.champ_confirmer_motdepasse.setEchoMode(QLineEdit.Password)

            self.action_afficher_motdepasse_confirme = (
                self.champ_confirmer_motdepasse.addAction(QIcon(
                    self.calculDimensionsIcone(self.icone_afficher_motdepasse,
                                               self.champ_confirmer_motdepasse)
                ),QLineEdit.TrailingPosition))
            self.action_afficher_motdepasse_confirme.triggered.connect(
                lambda: self.definirVisibiliteMotDePasse(
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
        except Exception as e:
            QMessageBox.critical(self, 'Erreur', f"Erreur lors du chargement du formulaire : {e}")


    def authentificationUtilisateur(self):
        """
        Fonction qui traite le formulaire de connexion et qui envoie les champs au serveur
        :return:
        """
        self.utilisateur = self.champ_utilisateur.text()
        self.motdepasse = self.champ_motdepasse.text()

        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((self.HOST, self.PORT))
            client_socket = AESsocket(client_socket, is_server=False)

            credentials = f"AUTH:{self.utilisateur}:{self.motdepasse}" #AUTH -> signale au serveur une demande d'authentification

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
        Fonction qui traite la création de compte.
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

            #generarion du sel et hashage du mot de passe
            salt=bcrypt.gensalt()
            motdepasse=motdepasse.encode('utf-8')
            motdepasse_hache = bcrypt.hashpw(motdepasse, salt)
            motdepasse_hache_decode=motdepasse_hache.decode('utf-8')

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
        Évalue la complexité du mot de passe et met à jour la barre et le label.
        """
        try :
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
        cette methode evalue la complexité du mot de passe et renvoie une chaine de caractere a la methode MAJComplexiteMotDePasse qui affichera le progrès sous forme de barre de progres
        :param MDP: string - mot de passe entré
        :return: srting - compléxité actuelle
        """
        try:
            # Initialiser les critères
            if len(MDP) >= 8 and len(MDP) <14 :
                longueurMotDePasse = 1
            elif len(MDP)>=14 and len(MDP) <20:
                longueurMotDePasse = 2
            elif len(MDP)>=20:
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
        return self.utilisateur, self.motdepasse

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

        self.motdepasse=None
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
                motdepasse = new_motDePasse.encode('utf-8')
                motdepasse_hache = bcrypt.hashpw(motdepasse, salt)
                motdepasse_hache_decode = motdepasse_hache.decode('utf-8')
                print(motdepasse_hache_decode)


                message = f"CHANGE_PASSWORD:{self.utilisateur}:{motdepasse_hache_decode}"
                print(message)
                self.client_socket.send(message)

                reponse = self.client_socket.recv(1024)
                if reponse=="PASSWORD_CHANGED":
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
        client_window = TodoListApp(pseudonyme_utilisateur, motdepasse_utilisateur)
        client_window.show()
        sys.exit(app.exec_())