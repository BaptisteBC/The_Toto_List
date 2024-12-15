from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
    QTreeWidgetItem, QTreeWidget, QDateEdit, QTextEdit, QComboBox, QMessageBox, QLineEdit, QDialog, QDialogButtonBox
)
from PyQt5.QtCore import Qt, QDate, QSize, QCoreApplication, pyqtSignal
from PyQt5.QtGui import QPalette, QColor, QIcon
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QComboBox,
    QDateEdit, QVBoxLayout, QPushButton, QMessageBox, QGridLayout, QListWidget, QListWidgetItem
)  # Modules de PyQt5 pour créer l'interface graphique.
from lib.custom import AEScipher, AESsocket # Classes personnalisées pour gérer le chiffrement AES et les connexions sécurisées.
import sys
import pymysql.cursors  # Module pour gérer les connexions MySQL avec curseurs.
import pymysql  # Module pour interagir avec une base de données MySQL.
import socket  # Pour gérer les connexions réseau via des sockets.
from datetime import datetime  # Utilisé pour les opérations sur les dates/heures.
import json

#Création de la tâche (Yann)
class FormulaireTache(QWidget):
    """
       Classe représentant l'interface graphique pour créer une tâche.

       Attributes:
           groupes (list): Liste des groupes (optionnel pour extension future).
           listes (list): Liste des listes disponibles pour organiser les tâches.
           utilisateurs (list): Liste des utilisateurs assignables à une tâche.
           tags (list): Liste des tags disponibles pour catégoriser une tâche (future extension).
       """
    tache_ajoutee = pyqtSignal()
    def __init__(self, parent=None):
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
        #self.ChargeUtilisateurs()
        self.ChargerListes()

    def reset_form(self):
        """Réinitialise les champs du formulaire."""
        self.champ_nom.clear()
        self.champ_description.clear()
        self.champ_date.setDate(QDate.currentDate())
        self.champ_statut.setCurrentIndex(0)
        self.combo_box_listes.setCurrentIndex(0)
        self.combo_box_utilisateurs.setCurrentIndex(0)
        self.champ_date_rappel.setDate(QDate.currentDate())

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
            # Connexion au serveur
            aes_socket = self.conection()
            if not aes_socket:
                return  # Arrête si la connexion a échoué

            # Préparation et envoi du message pour demander les listes
            message_listes = "GET_LISTES"
            aes_socket.send(message_listes)

            # Réception des données du serveur
            reponse_listes = aes_socket.recv(1024)

            # Fermeture de la connexion
            aes_socket.close()

            # Traitement des résultats
            resultats_listes = json.loads(reponse_listes)
            #resultats_listes = eval(reponse_listes)  # Convertit la réponse en structure Python (ou json.loads si JSON)
            if resultats_listes:
                # Ajoute les noms des listes au menu déroulant
                noms_listes = [liste['nom_liste'] for liste in resultats_listes]
                self.combo_box_listes.clear()  # Efface les anciennes options
                self.combo_box_listes.addItems(noms_listes)
            else:
                QMessageBox.warning(self, "Aucune liste", "Aucune liste trouvée.")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des listes : {e}")
    """
    def ChargeUtilisateurs(self):

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
    """
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
            aes_socket.send(message_utilisateur)
            id_utilisateur = aes_socket.recv(1024)

            # Récupération de l'ID liste.
            message_liste = f"ID_LISTE:{liste_choisie}"
            aes_socket.send(message_liste)
            id_liste = aes_socket.recv(1024)

            # Préparation et envoi du message pour créer la tâche.
            message = f"CREATION_TACHE:{id_utilisateur}:{id_liste}:{titre_tache}:{description}:{date_echeance}:{statut}:{date_rappel}"
            aes_socket.send(message)
            QMessageBox.information(self, "Succès", "Tâche créée avec succès.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'envoi : {e}")

#Affichage de la tâche (Baptiste)
class Principal(QWidget):
    """Fenêtre principale d'affichage des tâches.
    Prends en argument les infos de connexion à la BDD"""

    def __init__(self, host:str='85.10.235.60', user:str='totodb-admin', password='&TotoDB$IUT!2024%Ad', database:str='TheTotoDB', port=50000):
        super().__init__()

        self.setWindowTitle("Page Principale")
        grid = QGridLayout()
        self.setLayout(grid)
        self.resize(500, 550)

        self.titre = QLabel("Mes tâches")
        #self.taches = QTextBrowser()
        #self.taches.setOpenLinks(True)
        self.taches = QListWidget()
        #self.taches.setReadOnly(True)
        self.bouton_quitter = QPushButton("Quitter")
        self.bouton_actualiser = QPushButton("Actualiser")

        grid.addWidget(self.titre)
        grid.addWidget(self.bouton_actualiser)
        grid.addWidget(self.taches)
        grid.addWidget(self.bouton_quitter)

        self.bouton_quitter.clicked.connect(self.quitter)
        self.bouton_actualiser.clicked.connect(self.actualiser)
        #self.taches.itemClicked.connect(tache_cliquee)

        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port

        self.actualiser()

    def actualiser(self):
        """Fonction d'actualisation des tâches.
        Lorsue le bouton est cliqué, effectue une requête dans la table tâche et récupère le champ 'titre_tache' pour \
        l'afficher dans la fenêtre principale."""

        self.cnx = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database, port=self.port)
        curseur = self.cnx.cursor()

        # Extraction de tous les titres des taches principales
        curseur.execute("SELECT id_tache, titre_tache FROM taches;")
        resultache = curseur.fetchall()
        print(resultache)

        # Extraction de tous les titres des sous taches
        curseur.execute("SELECT id_soustache, titre_soustache, soustache_id_tache FROM soustaches;")
        sousresultache = curseur.fetchall()
        print(sousresultache)

        self.taches.clear()

        for id_tache, titre_tache in resultache:
        #for i in range(0, len(resultache)):
            #tache = resultache[i][1]

            #self.taches.append(tache)
            #self.taches.addItem(tache)

            self.afficherTache(id_tache, titre_tache)

            for id_soustache, titre_soustache, soustache_id_tache in sousresultache:
                if soustache_id_tache == id_tache :
                    #self.taches.addItem(f'|=> {sousresultache[j][1]}')
                    self.afficherTache(id_soustache, f'|=>{titre_soustache}', soustache_id_tache)
        curseur.close()

    def afficherTache(self, id_tache, titre_tache, soustache_id_tache=None):
        tache = QListWidgetItem()
        bouton = QPushButton(titre_tache)
        #layout = QHBoxLayout(tache)
        #label = QLabel(titre_tache)
        #layout.addWidget(label)
        bouton.clicked.connect(lambda : self.detail(id_tache, soustache_id_tache))

        #elementListe = QListWidgetItem()
        #elementListe.setSizeHint(tache.sizeHint())
        self.taches.addItem(tache)
        self.taches.setItemWidget(tache, bouton)

    def detail(self, id_tache, soustache_id_tache):
        curseur = self.cnx.cursor()
        if soustache_id_tache:
            curseur.execute("SELECT titre_soustache, description_soustache, datecreation_soustache, "
                            "datefin_soustache, statut_soustache, daterappel_soustache FROM soustaches;")
        else:
            curseur.execute("SELECT titre_tache, description_tache, datecreation_tache, datefin_tache,  "
                            "recurrence_tache, statut_tache, daterappel_tache, datesuppression_tache FROM taches;")
        curseur.close()

    def quitter(self):
        self.cnx.close()
        QCoreApplication.exit(0)

#GUI Principal (Thibaut)
class TodoListApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.principal = Principal()
        self.formulaire = FormulaireTache()
        self.setWindowTitle("The ToDo List")
        self.setGeometry(100, 100, 1000, 400)

        # Connecter le signal tache_ajoutee de Formulairetache à la méthode actualiser de Principal
        self.formulaire.tache_ajoutee.connect(self.principal.actualiser)

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
        self.toggle_sidebar_button.setIcon(QIcon("sidebar-2.png"))  # Utilise une icône par défaut
        self.toggle_sidebar_button.setFixedSize(30, 30)  # Taille de l'icône
        self.toggle_sidebar_button.clicked.connect(self.toggle_sidebar)

        # Ajout du bouton icône en haut à gauche
        nav_layout.addWidget(self.toggle_sidebar_button)

        # Bouton "Ouvrir Formulaire"
        self.form_button = QPushButton("Ouvrir Formulaire")
        self.form_button.clicked.connect(self.open_formulaire)
        nav_layout.addWidget(self.form_button)

        nav_layout.setContentsMargins(5, 0, 5, 0)

        # Bouton mode sombre déplacé vers la droite
        self.theme_button = QPushButton()
        self.theme_button.setIcon(QIcon("sun.png"))  # Icône par défaut (Soleil pour le mode clair)
        self.theme_button.setIconSize(QSize(20, 20))  # Réduire la taille de l'icône à 20x20
        self.theme_button.setFixedSize(30, 30)  # Réduire la taille du bouton à 30x30
        self.theme_button.clicked.connect(self.toggle_theme)
        nav_layout.addWidget(self.theme_button)
        self.main_layout.addLayout(nav_layout)

        # Arborescence des tâches
        self.task_tree = QTreeWidget()
        self.task_tree.setHeaderLabels(["Tâches", "Échéance", "Description", "Catégorie", "Statut", "Priorité"])
        self.main_layout.addWidget(self.task_tree)

        # Connecter l'événement de clic sur une tâche
        self.main_layout.addWidget(self.task_tree)
        main_layout.addWidget(self.main_widget)

        # Définir le widget central pour QMainWindow
        self.setCentralWidget(central_widget)

        # Liste temporaire pour stocker les tâches
        #self.tasks = []
        #self.formulaire_window = None
        self.is_dark_mode = False

    def toggle_sidebar(self):
        # Bascule de la visibilité de la colonne latérale
        self.sidebar.setVisible(not self.sidebar.isVisible())

    def open_formulaire(self):
        print("Signal reçu : ouverture du formulaire en cours...")
        try:
            self.formulaire_window = FormulaireTache(parent=self)
            self.formulaire_window.show()
        except Exception as e:
            print(f"Erreur lors de l'ouverture du formulaire : {e}")

    def toggle_theme(self):
        if not self.is_dark_mode:
            self.set_dark_mode()
            self.theme_button.setIcon(QIcon("moon.png"))  # Icône Lune pour le mode sombre
        else:
            self.set_light_mode()
            self.theme_button.setIcon(QIcon("sun.png"))  # Icône Soleil pour le mode clair
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

    def add_task_to_tree(self, nom, date, description, categorie, statut, priorite):
        task_item = QTreeWidgetItem([nom, date, description, categorie, statut, priorite])
        self.task_tree.addTopLevelItem(task_item)

    def open_settings(self):
        QMessageBox.information(self, "Paramètres", "Ouvrir les paramètres")

    def open_help(self):
        QMessageBox.information(self, "Aide", "Ouvrir l'aide")

    def open_credits(self):
        QMessageBox.information(self, "Crédits", "Ouvrir les crédits")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TodoListApp()
    window.show()
    sys.exit(app.exec())