from PyQt5.QtCore import Qt, QDate, QSize, QCoreApplication, QDateTime
from PyQt5.QtGui import QPalette, QColor, QIcon, QKeySequence, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QComboBox,
    QDateEdit, QVBoxLayout, QPushButton, QMessageBox, QGridLayout, QListWidget, QListWidgetItem, QProgressBar, QAction, QDialog, QHBoxLayout, QMainWindow, QCheckBox, QMenu, QFormLayout, QDateTimeEdit, QDialogButtonBox
)
from lib.custom import AESsocket
import socket
import json
import bcrypt
import time
import re
import requests
from datetime import datetime
import sys


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
        self.setWindowTitle("Formulaire de Tâche")
        self.setGeometry(100, 100, 400, 600)

        layout = QVBoxLayout()

        self.label_nom = QLabel("Nom de la tâche :")
        self.champ_nom = QLineEdit()
        layout.addWidget(self.label_nom)
        layout.addWidget(self.champ_nom)

        self.label_description = QLabel("Description :")
        self.champ_description = QTextEdit()
        layout.addWidget(self.label_description)
        layout.addWidget(self.champ_description)

        self.label_date = QLabel("Date d'échéance :")
        self.champ_date = QDateEdit()
        self.champ_date.setDate(QDate.currentDate())
        self.champ_date.setCalendarPopup(True)
        layout.addWidget(self.label_date)
        layout.addWidget(self.champ_date)

        self.label_liste = QLabel("Liste :")
        self.combo_box_listes = QComboBox()
        layout.addWidget(self.label_liste)
        layout.addWidget(self.combo_box_listes)

        self.label_utilisateur = QLabel("Assigné à :")
        self.combo_box_utilisateurs = QComboBox()
        layout.addWidget(self.label_utilisateur)
        layout.addWidget(self.combo_box_utilisateurs)

        self.label_date_rappel = QLabel("Date de rappel :")
        self.champ_date_rappel = QDateEdit()
        self.champ_date_rappel.setDate(QDate.currentDate())
        self.champ_date_rappel.setCalendarPopup(True)
        layout.addWidget(self.label_date_rappel)
        layout.addWidget(self.champ_date_rappel)

        self.bouton_soumettre = QPushButton("Soumettre")
        self.bouton_soumettre.clicked.connect(self.Envoie)
        layout.addWidget(self.bouton_soumettre)

        self.setLayout(layout)

        self.listes = {}
        self.utilisateurs = {}

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
        """
        Charge les listes disponibles depuis le serveur et les ajoute au menu déroulant.

            :raises Exception: En cas d'erreur lors de la communication avec le serveur ou du traitement des données reçues.
            :return: Cette méthode ne retourne rien. Les listes sont chargées dans l'attribut `listes` et ajoutées au menu déroulant.
        """
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
        """
        Charge les utilisateurs assignables à une tâche depuis le serveur et les ajoute au menu déroulant.

            :raises Exception: En cas d'erreur lors de la communication avec le serveur ou du traitement des données reçues.
            :return: Cette méthode ne retourne rien. Les utilisateurs sont chargés dans l'attribut `utilisateurs` et ajoutés au menu déroulant.
        """
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
        """
        Récupère les données du formulaire et les envoie au serveur pour créer une nouvelle tâche.

            :raises Exception: En cas d'erreur lors de la communication avec le serveur ou du traitement des données.
            :return: Cette méthode ne retourne rien. Une tâche est créée sur le serveur si les données sont valides.
        """
        try:
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
        try :
            super().__init__()
            self.HOST = '127.0.0.1'
            self.PORT = 55555
            self.utilisateur = pseudonyme_utilisateur
            self.motDePasse = motdepasse_utilisateur
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

        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)  # Layout principal horizontal (sidebar + contenu principal)

        # *** Sidebar ***
        self.sidebar = QWidget()
        sidebar_layout = QVBoxLayout(self.sidebar)

        # Boutons de la sidebar
        self.settings_button = QPushButton("Paramètres")
        self.help_button = QPushButton("Aide")
        self.bouton_actualiser = QPushButton("Actualiser")
        self.bouton_restaurer_corb = QPushButton("Restaurer la corbeille")
        self.bouton_vider_corb = QPushButton("Vider la corbeille")
        self.bouton_quitter = QPushButton("Quitter")

        # Ajout des boutons dans la sidebar
        sidebar_layout.addWidget(self.settings_button)
        sidebar_layout.addWidget(self.help_button)
        sidebar_layout.addWidget(self.bouton_actualiser)
        sidebar_layout.addWidget(self.bouton_restaurer_corb)
        sidebar_layout.addWidget(self.bouton_vider_corb)
        sidebar_layout.addWidget(self.bouton_quitter)

        # *** Zone principale ***
        self.main_widget = QWidget()
        main_layout_vertical = QVBoxLayout(self.main_widget)

        #Barre de navigation (haut)
        nav_layout = QHBoxLayout()
        self.toggle_sidebar_button = QPushButton()
        icon_url = "https://icons.veryicon.com/png/o/miscellaneous/we/sidebar-2.png"  # Remplacez par l'URL réelle
        self.set_icon_from_url(self.toggle_sidebar_button, icon_url)
        self.toggle_sidebar_button.setFixedSize(30, 30)  # Taille de l'icône
        self.toggle_sidebar_button.clicked.connect(self.toggle_sidebar)

        self.form_button = QPushButton("Ouvrir Formulaire")
        self.form_button.clicked.connect(self.open_formulaire)
        self.form_button.setFixedSize(200, 30)

        self.theme_button = QPushButton()
        icon_url = "https://png.pngtree.com/png-clipart/20220812/ourmid/pngtree-shine-sun-light-effect-free-png-and-psd-png-image_6106445.png"
        self.set_icon_from_url(self.theme_button, icon_url)
        self.theme_button.setIconSize(QSize(20, 20))
        self.theme_button.setFixedSize(30, 30)
        self.theme_button.clicked.connect(self.toggle_theme)

        # Ajout des boutons dans la barre de navigation
        nav_layout.addWidget(self.toggle_sidebar_button)
        nav_layout.addWidget(self.form_button)
        nav_layout.addWidget(self.theme_button)
        nav_layout.setContentsMargins(5, 0, 5, 0)
        nav_layout.addStretch()

        # Liste des tâches (en dessous de la barre de navigation)
        self.taches = QListWidget()

        # Ajout des éléments dans le layout vertical principal
        main_layout_vertical.addLayout(nav_layout)
        main_layout_vertical.addWidget(self.taches)

        # Ajout de la sidebar et de la zone principale dans le layout principal
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.main_widget)

        # Définir le widget central
        self.setCentralWidget(central_widget)

        # Connexion des signaux pour les boutons
        self.settings_button.clicked.connect(self.open_settings)
        self.help_button.clicked.connect(self.open_help)
        self.bouton_actualiser.clicked.connect(self.actualiser)
        self.bouton_restaurer_corb.clicked.connect(self.restaurer)
        self.bouton_vider_corb.clicked.connect(self.vider)
        self.bouton_quitter.clicked.connect(self.quitter)
        self.actualiser()

        main_layout.addWidget(self.main_widget)

        self.is_dark_mode = False


    def actualiser(self):

        """
        Actualise la liste des tâches et sous-tâches depuis le serveur.

        :raises json.JSONDecodeError: Si les données reçues ne peuvent pas être décodées.
        :raises Exception: Pour toute autre erreur lors de la récupération ou du traitement des données.
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
                    sousTaches = []
            except json.JSONDecodeError:
                sousTaches = []

            self.taches.clear()
            for idTache, titreTache, statutTache, datesuppression_tache in taches:
                if datesuppression_tache:
                    continue
                self.ajouterTache(titreTache, idTache, statutTache)


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
        Établit une connexion sécurisée avec le serveur.

        :return: Socket sécurisé pour l'échange de données chiffrées.
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
        Ajoute une tâche à la liste affichée dans l'interface utilisateur.

        :param titreTache: Le titre de la tâche.
        :type titreTache: str
        :param idTache: Identifiant unique de la tâche.
        :type idTache: int
        :param statutTache: Statut de la tâche (1 pour complétée, 0 sinon).
        :type statutTache: int
        """
        widgetTache = QWidget()
        layout = QHBoxLayout(widgetTache)

        caseCoche = QCheckBox()
        caseCoche.setChecked(statutTache == 1)
        labelTache = QLabel(titreTache)

        if statutTache == 1:
            labelTache.setStyleSheet("text-decoration: line-through; color: gray;")
        else:
            labelTache.setStyleSheet("")

        boutonPlus = QPushButton("...")
        boutonPlus.setFixedWidth(30)

        layout.addWidget(caseCoche)
        layout.addWidget(labelTache)
        layout.addWidget(boutonPlus)
        layout.addStretch()

        caseCoche.stateChanged.connect(lambda: self.mettreAJourStyle(labelTache, idTache, caseCoche.isChecked()))
        boutonPlus.clicked.connect(lambda: self.afficherMenuTache(idTache, boutonPlus))

        elementListe = QListWidgetItem()
        elementListe.setSizeHint(widgetTache.sizeHint())
        self.taches.addItem(elementListe)
        self.taches.setItemWidget(elementListe, widgetTache)

    def mettreAJourStyle(self, labelTache, idTache, coche):
        """
        Met à jour le style de la tâche et son statut de validation dans la base de données.

        :param labelTache: Widget QLabel représentant le titre de la tâche.
        :type labelTache: QLabel
        :param idTache: Identifiant unique de la tâche.
        :type idTache: int
        :param coche: Statut de validation de la tâche (True si cochée, False sinon).
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
        Ajoute une sous-tâche à la liste des tâches affichée dans l'interface utilisateur.

        :param titreSousTache: Le titre de la sous-tâche.
        :type titreSousTache: str
        :param idSousTache: Identifiant unique de la sous-tâche.
        :type idSousTache: int
        :param statutSousTache: Statut de la sous-tâche (1 pour complétée, 0 sinon).
        :type statutSousTache: int
        """
        widgetSousTache = QWidget()
        layout = QHBoxLayout(widgetSousTache)
        caseCocheSousTache = QCheckBox()
        caseCocheSousTache.setChecked(statutSousTache == 1)

        labelSousTache = QLabel(f"  ↳ {titreSousTache}")
        labelSousTache.setStyleSheet("color: darkgray;")

        if statutSousTache == 1:
            labelSousTache.setStyleSheet("text-decoration: line-through; color: gray;")
        else:
            labelSousTache.setStyleSheet("")

        boutonPlus = QPushButton("...")
        boutonPlus.setFixedWidth(30)

        layout.addWidget(caseCocheSousTache)
        layout.addWidget(labelSousTache)
        layout.addWidget(boutonPlus)
        layout.addStretch()

        caseCocheSousTache.stateChanged.connect(lambda: self.mettreAJourStyleSousTache(labelSousTache, idSousTache, caseCocheSousTache.isChecked()))
        boutonPlus.clicked.connect(lambda: self.afficherMenuSousTache(idSousTache, boutonPlus))

        elementListe = QListWidgetItem()
        elementListe.setSizeHint(widgetSousTache.sizeHint())
        self.taches.addItem(elementListe)
        self.taches.setItemWidget(elementListe, widgetSousTache)

    def afficherMenuSousTache(self, idSousTache, bouton):
        """
        Affiche un menu contextuel pour une sous-tâche.

        :param idSousTache: Identifiant unique de la sous-tâche.
        :type idSousTache: int
        :param bouton: Bouton source déclenchant le menu.
        :type bouton: QPushButton
        """
        menu = QMenu(self)
        actionModifier = QAction("Modifier sous tache", self)
        actionSupprimerTache = QAction("Supprimer la sous tâche", self)
        actionDetailTache = QAction("Détails sous tache", self)
        actionModifier.triggered.connect(lambda: self.modifierSousTache(idSousTache))
        actionSupprimerTache.triggered.connect(lambda: self.supprimerSousTache(idSousTache))
        actionDetailTache.triggered.connect(lambda: self.detailSousTache(idSousTache))
        menu.addAction(actionDetailTache)
        menu.addAction(actionSupprimerTache)
        menu.addAction(actionModifier)
        position = bouton.mapToGlobal(bouton.rect().bottomLeft())
        menu.exec_(position)

    def mettreAJourStyleSousTache(self, labelSousTache, idSousTache, cocheSousTache):
        """
        Met à jour le style visuel et le statut de validation d'une sous-tâche.

        :param labelSousTache: Widget QLabel représentant le titre de la sous-tâche.
        :type labelSousTache: QLabel
        :param idSousTache: Identifiant unique de la sous-tâche.
        :type idSousTache: int
        :param cocheSousTache: Statut de la case cochée (True si cochée, False sinon).
        :type cocheSousTache: bool
        """
        if cocheSousTache:
            labelSousTache.setStyleSheet("text-decoration: line-through; color: gray;")
            self.mettreAJourValidationSousTache(idSousTache, 1)
        else:
            labelSousTache.setStyleSheet("")
            self.mettreAJourValidationSousTache(idSousTache, 0)

    def afficherMenuTache(self, idTache, bouton):
        """
        Affiche un menu contextuel pour une tâche.

        :param idTache: Identifiant unique de la tâche.
        :type idTache: int
        :param bouton: Bouton source déclenchant le menu.
        :type bouton: QPushButton
        """
        menu = QMenu(self)
        actionModifier = QAction("Modifier", self)
        actionAjouterSousTache = QAction("Ajouter sous-tâche", self)
        actionSupprimerTache = QAction("Supprimer la tâche", self)
        actionDetailTache = QAction("Détails", self)
        actionModifier.triggered.connect(lambda: self.modifierTache(idTache))
        actionAjouterSousTache.triggered.connect(lambda: self.ajouterSousTache(idTache))
        actionSupprimerTache.triggered.connect(lambda: self.supprimer(idTache))
        actionDetailTache.triggered.connect(lambda: self.detail(idTache))
        menu.addAction(actionDetailTache)
        menu.addAction(actionSupprimerTache)
        menu.addAction(actionModifier)
        menu.addAction(actionAjouterSousTache)
        position = bouton.mapToGlobal(bouton.rect().bottomLeft())
        menu.exec_(position)

    def mettreAJourValidation(self, idTache, statutValidation):
        """
        Met à jour le statut de validation d'une tâche dans la base de données.

        :param idTache: Identifiant unique de la tâche.
        :type idTache: int
        :param statutValidation: Nouveau statut de validation (0 ou 1).
        :type statutValidation: int
        :raises pymysql.MySQLError: Erreur lors de la mise à jour de la base de données.
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
        Met à jour le statut de validation d'une sous-tâche dans la base de données.

        :param idSousTache: Identifiant unique de la sous-tâche.
        :type idSousTache: int
        :param statutSousValidation: Nouveau statut de validation (0 ou 1).
        :type statutSousValidation: int
        :raises pymysql.MySQLError: Erreur lors de la mise à jour de la base de données.
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
        """
        Affiche les détails d'une sous-tâche spécifique dans une fenêtre dédiée.

        :param idSousTache: Identifiant unique de la sous-tâche.
        :type idSousTache: int
        :raises json.JSONDecodeError: En cas d'erreur lors du décodage des données JSON de la sous-tâche.
        :raises Exception: Si la fenêtre de détail ne peut pas être affichée.
        """
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
        """
        Affiche les détails d'une tâche spécifique dans une fenêtre dédiée.

        :param idTache: Identifiant unique de la tâche.
        :type idTache: int
        :raises json.JSONDecodeError: En cas d'erreur lors du décodage des données JSON de la tâche.
        :raises Exception: Si la fenêtre de détail ne peut pas être affichée.
        """
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
        Vider_corbeille().exec()

    def quitter(self):
        """
        Quitte l'application en fermant tous les processus.

        :return: None
        :rtype: None
        """
        QCoreApplication.exit(0)

    def set_icon_from_url(self, button, url):
        """
        Définit une icône pour un bouton à partir d'une URL d'image.

        :param button: Le bouton auquel l'icône sera appliquée.
        :type button: QPushButton
        :param url: URL de l'image à utiliser comme icône.
        :type url: str
        :raises Exception: En cas d'erreur lors du téléchargement ou du chargement de l'image.
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers, stream=True)
            response.raise_for_status()
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
        Crée un menu d'options et de crédits dans la barre de menu principale.

        :return: None
        :rtype: None
        """
        menuBar = self.menuBar()


        optionsMenu = menuBar.addMenu("Options")
        optionsMenu.addAction(self.actChangemotDePasse)
        optionsMenu.addAction(self.actExit)


        creditsMenu = menuBar.addMenu("À propos")
        creditsMenu.addAction(self.actCredits)

    def creerActions(self):
        """
        Définit les actions et raccourcis clavier pour le menu de l'application.

        :return: None
        :rtype: None
        """
        self.actChangemotDePasse = QAction("Changer de mot de passe", self)
        self.actChangemotDePasse.setShortcut(QKeySequence("Ctrl+P"))
        self.actChangemotDePasse.triggered.connect(self.fenetreChangementMDP)

        self.actExit = QAction("Exit", self)
        self.actExit.setShortcut(QKeySequence("Alt+F4"))
        self.actExit.setStatusTip("Exit")
        self.actExit.triggered.connect(self.fermeture)


        self.actCredits = QAction("Crédits", self)
        self.actCredits.triggered.connect(self.open_credits)

    def fermeture(self):
        """
        Ferme l'application et termine tous les processus en cours.

        :return: None
        :rtype: None
        """
        app.exit(0)
        sys.exit(0)

    def fenetreChangementMDP(self):
        """
        Ouvre une fenêtre pour permettre à l'utilisateur de modifier son mot de passe.

        :raises Exception: En cas d'erreur lors du processus de changement de mot de passe.
        :return: None
        :rtype: None
        """
        try:
            change_motDePasse_window = ChangemotDePasseWindow(self.utilisateur, self.client_socket)
            if change_motDePasse_window.exec() == QDialog.Accepted:
                QMessageBox.information("Mot de passe changé avec succès!")
                #print("Mot de passe changé avec succès!")
        except Exception as e:
            QMessageBox.critical("Erreur",f'Erreur lors du changement de mot de passe {e}')

    def initUI(self):
        """
        Méthode d'initialisation de l'interface utilisateur.
        Actuellement non implémentée.

        :return: None
        :rtype: None
        """
        pass

    def toggle_sidebar(self):
        """
        Affiche ou masque la barre latérale.

        :return: None
        :rtype: None
        """
        self.sidebar.setVisible(not self.sidebar.isVisible())

    def open_formulaire(self):
        """
        Ouvre une nouvelle fenêtre contenant le formulaire de création de tâche.

        :raises Exception: Si une erreur survient lors de l'ouverture de la fenêtre du formulaire.
        :return: None
        :rtype: None
        """
        try:
            self.formulaire_window = FormulaireTache(self)
            self.formulaire_window.show()
        except Exception as e:
            print(f"Erreur lors de l'ouverture du formulaire : {e}")

    def toggle_theme(self):
        """
        Bascule entre le mode clair et le mode sombre pour l'application.

        :return: None
        :rtype: None
        """
        if not self.is_dark_mode:
            self.set_dark_mode()
            icon_url = "https://icones.pro/wp-content/uploads/2021/02/icone-de-la-lune-grise.png"
            self.set_icon_from_url(self.theme_button, icon_url)
        else:
            self.set_light_mode()
            icon_url = "https://png.pngtree.com/png-clipart/20220812/ourmid/pngtree-shine-sun-light-effect-free-png-and-psd-png-image_6106445.png"
            self.set_icon_from_url(self.theme_button, icon_url)
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

    def open_settings(self):
        """
        Ouvre une fenêtre d'information pour afficher les paramètres.

        :return: None
        :rtype: None
        """
        QMessageBox.information(self, "Paramètres", "Ouvrir les paramètres")

    def open_help(self):
        """
        Affiche une fenêtre contenant des informations d'aide pour l'utilisateur.

        :return: None
        :rtype: None
        """
        QMessageBox.information(self, "Aide", "Besoin d'aide ? \n \nSuivez ce lien pour comprendre comment utiliser votre application de ToDoList 😉 : https://github.com/BaptisteBC/The_Toto_List")

    def open_credits(self):
        """
        Affiche une fenêtre contenant les crédits et informations sur les développeurs de l'application.

        :return: None
        :rtype: None
        """
        QMessageBox.information(self, "Crédits","Application développée par les personnes suivantes : \n\n - BLANC-CARRIER Baptiste \n - BLANCK Yann \n - COSENZA Thibaut \n - DE AZEVEDO Kévin \n - GASSER Timothée \n - MARTIN Jean-Christophe \n - MERCKLE Florian \n - MOUROT Corentin \n - TRÉPIER Timothée\n\n © 2024 TheTotoList. Tous droits réservés. Développé par TheTotoGroup.")

class SupprimerTache(QDialog):
    """
    Fenêtre de dialogue pour supprimer une tâche ou une sous-tâche.

    :param idTache: Identifiant de la tâche ou sous-tâche à supprimer.
    :type idTache: str
    :param typeTache: Type de tâche (0 pour une tâche, 1 pour une sous-tâche).
    :type typeTache: str
    """
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
        """
        Envoie une requête au serveur pour supprimer la tâche ou la sous-tâche.

        :raises Exception: En cas d'erreur de connexion ou d'envoi de la requête.
        """
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
        """
        Ferme la fenêtre de dialogue sans effectuer d'action.

        :return: None
        :rtype: None
        """
        self.close()

class Vider_corbeille(QDialog):
    """
    Fenêtre de dialogue pour vider la corbeille.

    Cette classe permet de confirmer l'action de suppression définitive de toutes les tâches et sous-tâches dans la corbeille.
    """
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
        """
        Envoie une requête au serveur pour vider la corbeille.

        :raises Exception: En cas d'erreur de connexion ou d'envoi de la requête.
        """
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
        """
        Ferme la fenêtre de dialogue sans effectuer d'action.

        :return: None
        :rtype: None
        """
        self.close()

class Restaurer(QDialog):
    """
        Fenêtre de dialogue pour restaurer les éléments supprimés de la corbeille.
    """
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
        """
        Envoie une requête au serveur pour restaurer les éléments de la corbeille.

        :raises Exception: En cas d'erreur de connexion ou d'envoi de la requête.
        """
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
        """
        Ferme la fenêtre de détail.

        :return: None
        :rtype: None
        """
        self.close()

class AuthWindow(QDialog):
    """
    Fenêtre d'authentification et d'inscription pour l'application.

    Cette classe gère la connexion et la création de comptes des utilisateurs.
    """
    def __init__(self):
        super().__init__()
        self.HOST = '127.0.0.1'
        self.PORT = 55555
        self.mode = "login"
        self.initUI()
        self.utilisateur= None

    def initUI(self):
        """
        Initialise l'interface utilisateur de la fenêtre d'authentification.

        :return: None
        :rtype: None
        """
        self.setGeometry(300, 300, 300, 300)
        self.setWindowTitle('Authentification')

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
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def affichageFormulaireAuthentification(self):
        """
        Affiche le formulaire d'authentification pour les utilisateurs existants.

        :return: None
        :rtype: None
        """
        self.effacerWidgets()

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

        self.layout.addWidget(self.lblUtilisateur)
        self.layout.addWidget(self.tbxUtilisateur)
        self.layout.addWidget(self.lblmotDePasse)
        self.layout.addWidget(self.tbxmotDePasse)
        self.layout.addWidget(self.btnLogin)
        self.layout.addWidget(self.btnSwitch)

    def affichageFormulaireInscription(self):
        """
        Affiche le formulaire d'inscription pour les nouveaux utilisateurs.

        :return: None
        :rtype: None
        """
        try:
            self.effacerWidgets()
            self.setWindowTitle('Inscription')

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

            self.password_strength_bar = QProgressBar(self)
            self.password_strength_bar.setRange(0, 100)
            self.password_strength_bar.setTextVisible(False)

            self.password_strength_label = QLabel("Complexité : Très faible", self)

            self.tbxmotDePasse.textChanged.connect(self.MAJComplexiteMotDePasse)

            self.btnInscription = QPushButton('Créer un compte', self)
            self.btnInscription.clicked.connect(self.inscriptionUtilisateur)
            self.btnInscription.setDefault(True)

            self.btnSwitch = QPushButton('Retour à la connexion', self)
            self.btnSwitch.clicked.connect(self.affichageFormulaireAuthentification)

            self.tbxEmail.returnPressed.connect(self.btnInscription.click)
            self.tbxNom.returnPressed.connect(self.btnInscription.click)
            self.tbxPrenom.returnPressed.connect(self.btnInscription.click)
            self.tbxPseudo.returnPressed.connect(self.btnInscription.click)
            self.tbxmotDePasseConfirm.returnPressed.connect(self.btnInscription.click)

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
        Traite le formulaire de connexion et envoie les informations d'identification au serveur.

        :raises Exception: En cas d'échec de connexion ou d'erreur lors de l'authentification.
        :return: None
        :rtype: None
        """
        self.utilisateur = self.tbxUtilisateur.text()
        self.motDePasse = self.tbxmotDePasse.text()

        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((self.HOST, self.PORT))
            client_socket = AESsocket(client_socket, is_server=False)

            credentials = f"AUTH:{self.utilisateur}:{self.motDePasse}"

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
        Traite le formulaire d'inscription et envoie les informations du compte au serveur.

        :raises Exception: En cas d'erreur lors de la création du compte ou de validation des données.
        :return: None
        :rtype: None
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
        Met à jour la barre de progression et l'indicateur de complexité du mot de passe.

        :return: None
        :rtype: None
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
        Évalue la complexité d'un mot de passe et renvoie une chaîne représentant son niveau.

        :param MDP: Le mot de passe à évaluer.
        :type MDP: str
        :return: Niveau de complexité du mot de passe.
        :rtype: str
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
        return self.utilisateur, self.motDePasse

#Fenêtre changement de mot de passe
class ChangemotDePasseWindow(QDialog):
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
        Initialise l'interface utilisateur de la fenêtre de changement de mot de passe.

        :raises Exception: En cas d'erreur lors de l'initialisation des widgets ou de la fenêtre.
        :return: None
        :rtype: None
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
        Envoie une requête au serveur pour changer le mot de passe de l'utilisateur.

        Vérifie que les mots de passe saisis correspondent et les envoie au serveur après hashage.
        Affiche des messages pour indiquer le succès ou l'échec de l'opération.

        :raises Exception: En cas d'erreur lors de l'envoi ou de la réception des données avec le serveur.
        :return: None
        :rtype: None
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
        client_window = TodoListApp(pseudonyme_utilisateur, motdepasse_utilisateur)
        client_window.show()
        sys.exit(app.exec_())