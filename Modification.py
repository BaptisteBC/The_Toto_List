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
    Classe principale gérant l'interface pour la gestion des tâches et sous-tâches.
    Fusion des fonctionnalités des deux scripts fournis.
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
        QCoreApplication.exit(0)

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

    def actualiser(self):
        """ Actualise la liste des tâches et sous-tâches depuis la base de données. """
        try:

            curseur = self.cnx.cursor()
            curseur.execute("SELECT id_tache, titre_tache, statut_tache FROM taches;")
            taches = curseur.fetchall()


            curseur.execute("SELECT id_soustache, titre_soustache, soustache_id_tache FROM soustaches;")
            sousTaches = curseur.fetchall()

            self.listeTaches.clear()

            for idTache, titreTache, statutTache in taches:
                self.ajouterTache(titreTache, idTache, statutTache)
                for idSousTache, titreSousTache, parentId in sousTaches:
                    if parentId == idTache:
                        self.ajouterSousTacheListe(titreSousTache, idSousTache)

        except pymysql.MySQLError as e:
            QMessageBox.critical(self, 'Erreur', f'Erreur MySQL : {e}')
        finally:
            if 'curseur' in locals():
                curseur.close()

    def ajouterTache(self, titreTache, idTache, statutTache):
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

        caseCoche.stateChanged.connect(lambda state: self.mettreAJourValidation(idTache, state, labelTache))
        boutonPlus.clicked.connect(lambda: self.afficherMenuTache(idTache, boutonPlus))

        elementListe = QListWidgetItem()
        elementListe.setSizeHint(widgetTache.sizeHint())
        self.listeTaches.addItem(elementListe)
        self.listeTaches.setItemWidget(elementListe, widgetTache)

    def ajouterSousTacheListe(self, titreSousTache, idSousTache):
        widgetSousTache = QWidget()
        layout = QHBoxLayout(widgetSousTache)

        labelSousTache = QLabel(f"  ↳ {titreSousTache}")
        labelSousTache.setStyleSheet("color: darkgray;")

        boutonModifier = QPushButton("Modifier")
        boutonModifier.setFixedWidth(60)
        layout.addWidget(labelSousTache)
        layout.addWidget(boutonModifier)
        layout.addStretch()

        boutonModifier.clicked.connect(lambda: self.modifierSousTache(idSousTache))

        elementListe = QListWidgetItem()
        elementListe.setSizeHint(widgetSousTache.sizeHint())
        self.listeTaches.addItem(elementListe)
        self.listeTaches.setItemWidget(elementListe, widgetSousTache)

    def afficherMenuTache(self, idTache, bouton):
        menu = QMenu(self)
        actionModifier = QAction("Modifier", self)
        actionAjouterSousTache = QAction("Ajouter sous-tâche", self)
        actionModifier.triggered.connect(lambda: self.modifierTache(idTache))
        actionAjouterSousTache.triggered.connect(lambda: self.ajouterSousTache(idTache))
        menu.addAction(actionModifier)
        menu.addAction(actionAjouterSousTache)
        position = bouton.mapToGlobal(bouton.rect().bottomLeft())
        menu.exec_(position)

    def modifierTache(self, idTache):
        try:
            aes_socket = self.conection()  # Tentative de connexion
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
        try:

            aes_socket = self.conection()
            if not aes_socket:
                print("Erreur de connexion au serveur.")
            message = f"MODIF_TACHE|{idTache}|{titre}|{description}|{dateFin.toString('yyyy-MM-dd HH:mm:ss')}|{recurrence}|{dateRappel.toString('yyyy-MM-dd HH:mm:ss') if dateRappel else 'NULL'}"""
            print(message)
            aes_socket.send(message)
            print("message ennvoyer")
            dialog.accept()
            self.actualiser()
        except pymysql.MySQLError as e:
            QMessageBox.critical(self, "Erreur", f"Erreur MySQL lors de la modification : {e}")
        finally:
            aes_socket.close()

    def modifierSousTache(self, idSousTache):
        try:
            curseur = self.cnx.cursor()
            curseur.execute("SELECT titre_soustache, description_soustache, datefin_soustache, daterappel_soustache FROM soustaches WHERE id_soustache = %s;", (idSousTache,))
            sousTache = curseur.fetchone()

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
            if 'curseur' in locals():
                curseur.close()

    def sauvegarderModificationSousTache(self, idSousTache, titre, description, dateFin, dateRappel, dialog):
        try:
            curseur = self.cnx.cursor()
            curseur.execute("""
                UPDATE soustaches SET titre_soustache = %s, description_soustache = %s, datefin_soustache = %s, daterappel_soustache = %s
                WHERE id_soustache = %s;
            """, (titre, description, dateFin.toString("yyyy-MM-dd HH:mm:ss"), dateRappel.toString("yyyy-MM-dd HH:mm:ss") if dateRappel else None, idSousTache))
            self.cnx.commit()
            dialog.accept()
            self.actualiser()
        except pymysql.MySQLError as e:
            QMessageBox.critical(self, "Erreur", f"Erreur MySQL lors de la modification : {e}")
        finally:
            if 'curseur' in locals():
                curseur.close()

    def ajouterSousTache(self, idTacheParent):
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
        try:
            curseur = self.cnx.cursor()
            curseur.execute("""
                INSERT INTO soustaches (soustache_id_tache, titre_soustache, description_soustache, datefin_soustache, daterappel_soustache, datecreation_soustache)
                VALUES (%s, %s, %s, %s, %s, NOW());
            """, (idTacheParent, titre, description, dateFin.toString("yyyy-MM-dd HH:mm:ss"), dateRappel.toString("yyyy-MM-dd HH:mm:ss") if dateRappel else None))
            self.cnx.commit()
            dialog.accept()
            self.actualiser()
        except pymysql.MySQLError as e:
            QMessageBox.critical(self, "Erreur", f"Erreur MySQL lors de la création de la sous-tâche : {e}")
        finally:
            if 'curseur' in locals():
                curseur.close()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = PagePrincipale()
    fenetre.show()
    sys.exit(app.exec_())
