import sys
from datetime import datetime
import pymysql
import json
import socket
from lib.custom import AESsocket
from PyQt5.QtCore import QCoreApplication, Qt, QDateTime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget,
    QHBoxLayout, QCheckBox, QAction, QMenu, QApplication, QListWidgetItem, QDialog,
    QLineEdit, QDialogButtonBox, QFormLayout, QDateTimeEdit, QComboBox, QMessageBox
)

class PagePrincipale(QWidget):
    """
        Classe représentant la page principale de l'application, contenant une interface graphique
    pour afficher et gérer des tâches et sous-tâches.

        :param hote: Adresse de l'hôte de la base de données, defaults to '127.0.0.1'
        :type hote: str, optional
        :param utilisateur: Nom d'utilisateur pour la connexion à la base de données, defaults to 'root'
        :type utilisateur: str, optional
        :param motDePasse: Mot de passe pour la connexion à la base de données, defaults to 'toto'
        :type motDePasse: str, optional
        :param baseDeDonnees: Nom de la base de données à utiliser, defaults to 'thetotodb'
        :type baseDeDonnees: str, optional

        :raises pymysql.MySQLError: Si la connexion à la base de données échoue.
        """

    def __init__(self, hote: str = '127.0.0.1', utilisateur: str = 'root', motDePasse='toto', baseDeDonnees: str = 'thetotodb'):
        super().__init__()
        self.setWindowTitle("Page Principale")
        self.layout = QVBoxLayout(self)
        self.resize(400, 300)

        self.titre = QLabel("Mes Tâches et Sous-Tâches")
        self.boutonActualiser = QPushButton("Actualiser")
        self.boutonQuitter = QPushButton("Quitter")
        self.listeTaches = QListWidget()

        self.layout.addWidget(self.titre)
        self.layout.addWidget(self.boutonActualiser)
        self.layout.addWidget(self.listeTaches)
        self.layout.addWidget(self.boutonQuitter)

        self.boutonQuitter.clicked.connect(self.quitter)
        self.boutonActualiser.clicked.connect(self.actualiser)

        try:
            self.cnx = pymysql.connect(host=hote, user=utilisateur, password=motDePasse, database=baseDeDonnees)
            self.actualiser()
        except pymysql.MySQLError as e:
            QMessageBox.critical(self, "Erreur", f"Erreur de connexion à la base de données : {e}")

    def quitter(self):
        """
            Quitte l'application en fermant la session actuelle.

            :return: None
            :rtype: NoneType
        """
        QCoreApplication.exit(0)

    def conection(self):
        """
        Établit une connexion sécurisée avec le serveur via un socket.

        :return: Socket sécurisé pour échanger des données chiffrées.
        :rtype: AESsocket
        :raises Exception: Si la connexion au serveur échoue.
        """
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('localhost', 12345))
            return AESsocket(client_socket, is_server=False)
        except Exception as e:
            QMessageBox.critical(self, "Erreur de connexion", f"Erreur de connexion au serveur : {e}")
            return None

    def actualiser(self):
        """
        Actualise la liste des tâches et sous-tâches depuis la base de données.

        :raises pymysql.MySQLError: Erreur lors de la connexion ou l'exécution des requêtes SQL sur la base de données.
        """
        try:
            curseur = self.cnx.cursor()
            curseur.execute("SELECT id_tache, titre_tache, statut_tache FROM taches;")
            taches = curseur.fetchall()


            curseur.execute("SELECT id_soustache, titre_soustache, soustache_id_tache, statut_soustache FROM soustaches;")
            sousTaches = curseur.fetchall()

            self.listeTaches.clear()
            for idTache, titreTache, statutTache in taches:
                self.ajouterTache(titreTache, idTache, statutTache)
                for idSousTache, titreSousTache, parentId, statutSousTache in sousTaches:
                    if parentId == idTache:
                        self.ajouterSousTacheListe(titreSousTache, idSousTache, statutSousTache)
            self.listeTaches.repaint()
        except pymysql.MySQLError as e:
            QMessageBox.critical(self, 'Erreur', f'Erreur MySQL : {e}')
        finally:
            if 'curseur' in locals():
                curseur.close()

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
        self.listeTaches.addItem(elementListe)
        self.listeTaches.setItemWidget(elementListe, widgetTache)


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
        layout = QHBoxLayout(widgetSousTache)
        caseCocheSousTache = QCheckBox()
        caseCocheSousTache.setChecked(statutSousTache == 1)

        labelSousTache = QLabel(f"  ↳ {titreSousTache}")
        labelSousTache.setStyleSheet("color: darkgray;")

        if statutSousTache == 1:
            labelSousTache.setStyleSheet("text-decoration: line-through; color: gray;")
        else:
            labelSousTache.setStyleSheet("")

        boutonModifier = QPushButton("Modifier")
        boutonModifier.setFixedWidth(60)

        layout.addWidget(caseCocheSousTache)
        layout.addWidget(labelSousTache)
        layout.addWidget(boutonModifier)
        layout.addStretch()

        caseCocheSousTache.stateChanged.connect(lambda: self.mettreAJourStyleSousTache(labelSousTache, idSousTache, caseCocheSousTache.isChecked()))
        boutonModifier.clicked.connect(lambda: self.modifierSousTache(idSousTache))

        elementListe = QListWidgetItem()
        elementListe.setSizeHint(widgetSousTache.sizeHint())
        self.listeTaches.addItem(elementListe)
        self.listeTaches.setItemWidget(elementListe, widgetSousTache)

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

    def afficherMenuTache(self, idTache, bouton):
        """
        Affiche un menu contextuel avec des options pour une tâche spécifique.

        :param idTache: Identifiant unique de la tâche
        :type idTache: int
        :param bouton: Bouton source qui déclenche l'affichage du menu
        :type bouton: QPushButton
        """
        menu = QMenu(self)
        actionModifier = QAction("Modifier", self)
        actionAjouterSousTache = QAction("Ajouter sous-tâche", self)
        actionModifier.triggered.connect(lambda: self.modifierTache(idTache))
        actionAjouterSousTache.triggered.connect(lambda: self.ajouterSousTache(idTache))
        menu.addAction(actionModifier)
        menu.addAction(actionAjouterSousTache)
        position = bouton.mapToGlobal(bouton.rect().bottomLeft())
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
        except pymysql.MySQLError as e:
            QMessageBox.critical(self, 'Erreur', f'Erreur MySQL lors de la mise à jour de la validation de la tâche {idTache} : {e}')
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
        except pymysql.MySQLError as e:
            QMessageBox.critical(self, 'Erreur', f'Erreur MySQL lors de la mise à jour de la validation de la sous tâche {idSousTache} : {e}')
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
            aes_socket.close()
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
        except pymysql.MySQLError as e:
            QMessageBox.critical(self, "Erreur", f"Erreur MySQL lors de la modification : {e}")
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
        except pymysql.MySQLError as e:
            QMessageBox.critical(self, "Erreur", f"Erreur MySQL : {e}")
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
        except pymysql.MySQLError as e:
            QMessageBox.critical(self, "Erreur", f"Erreur MySQL lors de la modification : {e}")
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
        except pymysql.MySQLError as e:
            QMessageBox.critical(self, "Erreur", f"Erreur MySQL lors de la création de la sous-tâche : {e}")
        finally:
            aes_socket.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = PagePrincipale()
    fenetre.show()
    sys.exit(app.exec_())