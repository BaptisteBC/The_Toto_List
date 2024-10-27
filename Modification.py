import sys
import pymysql
from PyQt5.QtCore import QCoreApplication, Qt, QDate, QDateTime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget,
    QHBoxLayout, QCheckBox, QAction, QMenu, QApplication, QListWidgetItem, QDialog,
    QLineEdit, QDialogButtonBox, QFormLayout, QDateEdit, QComboBox, QDateTimeEdit, QMessageBox
)

class PagePrincipale(QWidget):
    """
    Classe principale gérant l'interface de dev pour la gestion des modifications.

    :param hote: Adresse de l'hôte de la base de données, défaut '127.0.0.1'
    :type hote: str, optional
    :param utilisateur: Nom d'utilisateur pour la base de données, défaut 'root'
    :type utilisateur: str, optional
    :param motDePasse: Mot de passe pour la base de données, défaut 'toto'
    :type motDePasse: str, optional
    :param baseDeDonnees: Nom de la base de données, défaut 'thetotodb'
    :type baseDeDonnees: str, optional
    """
    def __init__(self, hote: str = '127.0.0.1', utilisateur: str = 'root', motDePasse='toto', baseDeDonnees: str = 'thetotodb'):
        super().__init__()

        self.setWindowTitle("Page Principale")
        self.layout = QVBoxLayout(self)
        self.resize(400, 300)

        self.titre = QLabel("Mes Tâches")
        self.boutonActualiser = QPushButton("Actualiser")
        self.boutonQuitter = QPushButton("Quitter")

        self.listeTaches = QListWidget()

        self.layout.addWidget(self.titre)
        self.layout.addWidget(self.boutonActualiser)
        self.layout.addWidget(self.listeTaches)
        self.layout.addWidget(self.boutonQuitter)

        self.boutonQuitter.clicked.connect(self.quitter)
        self.boutonActualiser.clicked.connect(self.actualiser)

        self.hote = hote
        self.utilisateur = utilisateur
        self.motDePasse = motDePasse
        self.baseDeDonnees = baseDeDonnees

        self.cnx = pymysql.connect(host=hote, user=utilisateur, password=motDePasse, database=baseDeDonnees)

        self.actualiser()

    def quitter(self):
        """
        Quitte l'application.
        """
        QCoreApplication.exit(0)

    def actualiser(self):
        """
        Actualise la liste des tâches depuis la base de données.
        """
        curseur = self.cnx.cursor()
        curseur.execute("SELECT idTache, titre, validation FROM taches;")
        resultat = curseur.fetchall()
        self.listeTaches.clear()
        for idTache, titreTache, validation in resultat:
            self.ajouterTache(titreTache, idTache, validation)

    def ajouterTache(self, titreTache, idTache, validation):
        """
        Ajoute une tâche à la liste des tâches (graphique).

        :param titreTache: Titre de la tâche à ajouter
        :type titreTache: str
        :param idTache: Identifiant unique de la tâche
        :type idTache: int
        :param validation: Statut de validation de la tâche (0 ou 1)
        :type validation: int
        """
        widgetTache = QWidget()
        layout = QHBoxLayout(widgetTache)

        caseCoche = QCheckBox()
        caseCoche.setChecked(validation == 1)
        labelTache = QLabel(titreTache)

        if validation == 1:
            labelTache.setStyleSheet("text-decoration: line-through; color: gray;")

        boutonPlus = QPushButton("...")
        boutonPlus.setFixedWidth(30)

        layout.addWidget(caseCoche)
        layout.addWidget(labelTache)
        layout.addWidget(boutonPlus)
        layout.addStretch()

        caseCoche.stateChanged.connect(lambda: self.mettreAJourStyle(labelTache, idTache, caseCoche.isChecked()))
        boutonPlus.clicked.connect(lambda: self.afficherMenu(idTache, titreTache, widgetTache))

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

    def mettreAJourValidation(self, idTache, statutValidation):
        """
        Met à jour le champ validation de la tâche dans la base de données.

        :param idTache: Identifiant unique de la tâche
        :type idTache: int
        :param statutValidation: Nouveau statut de validation (0 ou 1)
        :type statutValidation: int
        :raises pymysql.MySQLError: En cas d'erreur lors de la mise à jour de la base de données
        """
        try:
            curseur = self.cnx.cursor()
            curseur.execute("UPDATE taches SET validation = %s WHERE idTache = %s;", (statutValidation, idTache))
            self.cnx.commit()
        except pymysql.MySQLError as e:
            QMessageBox.critical(self, 'Erreur', f'Erreur MySQL lors de la mise à jour de la validation de la tâche {idTache} : {e}')
        finally:
            curseur.close()

    def afficherMenu(self, idTache, titreTache, widgetTache):
        """
        Affiche un menu contextuel pour une tâche.

        :param idTache: Identifiant unique de la tâche
        :type idTache: int
        :param titreTache: Titre de la tâche
        :type titreTache: str
        :param widgetTache: Widget représentant la tâche dans l'interface
        :type widgetTache: QWidget
        """
        menu = QMenu(widgetTache)

        actionModifier = QAction("Modifier", widgetTache)
        actionSupprimer = QAction("Supprimer", widgetTache)
        actionNouvelleSousTache = QAction("Nouvelle tâche enfant", widgetTache)

        actionModifier.triggered.connect(lambda: self.modifierTache(idTache))
        actionSupprimer.triggered.connect(lambda: self.supprimerTache(idTache))
        actionNouvelleSousTache.triggered.connect(lambda: self.ajouterSousTache(idTache))

        menu.addAction(actionModifier)
        menu.addAction(actionSupprimer)
        menu.addAction(actionNouvelleSousTache)

        menu.exec_(self.mapToGlobal(widgetTache.pos()))

    def modifierTache(self, idTache):
        """
        Modifie les détails d'une tâche existante.

        :param idTache: Identifiant unique de la tâche à modifier
        :type idTache: int
        """
        try:
            curseur = self.cnx.cursor()
            curseur.execute("""
                SELECT titre, description, dateFin, recurence, typeRecurence, idUtilisateurAffecte, idTag, dateRappel 
                FROM taches 
                WHERE idTache = %s
            """, (idTache,))
            tache = curseur.fetchone()

            if tache:
                dateFinStr = tache[2].strftime("%Y-%m-%d %H:%M:%S") if tache[2] else None
                dateRappelStr = tache[7].strftime("%Y-%m-%d %H:%M:%S") if tache[7] else None

                dateFin = QDateTime.fromString(dateFinStr, "yyyy-MM-dd HH:mm:ss") if dateFinStr else QDateTime.currentDateTime()
                dateRappel = QDateTime.fromString(dateRappelStr, "yyyy-MM-dd HH:mm:ss") if dateRappelStr else QDateTime.currentDateTime()

                dialog = DialogueModification(idTache, tache, dateFin, dateRappel, self)

                if not dateFinStr:
                    dialog.caseDateFinNull.setChecked(True)
                    dialog.dateFinEdit.setEnabled(False)
                if not dateRappelStr:
                    dialog.caseDateRappelNull.setChecked(True)
                    dialog.dateRappelEdit.setEnabled(False)

                if dialog.exec_() == QDialog.Accepted:
                    nouvellesDonnees = dialog.getDonneesTache()
                    self.mettreAJourTache(idTache, *nouvellesDonnees)

        except Exception as e:
            QMessageBox.critical(self, 'Erreur', f'Erreur lors de la récupération des données de la tâche : {e}')
        finally:
            curseur.close()

    def mettreAJourTache(self, idTache, titre, description, dateFin, recurence, typeRecurence, utilisateur, tag, dateRappel):
        """
        Met à jour les détails d'une tâche existante dans la base de données.

        :param idTache: Identifiant unique de la tâche
        :type idTache: int
        :param titre: Nouveau titre de la tâche
        :type titre: str
        :param description: Nouvelle description de la tâche
        :type description: str
        :param dateFin: Nouvelle date de fin de la tâche
        :type dateFin: str ou None
        :param recurence: Indicateur de récurrence (0 ou 1)
        :type recurence: int
        :param typeRecurence: Type de récurrence
        :type typeRecurence: int
        :param utilisateur: Identifiant de l'utilisateur assigné à la tâche
        :type utilisateur: int
        :param tag: Identifiant du tag associé à la tâche
        :type tag: int
        :param dateRappel: Nouvelle date de rappel de la tâche
        :type dateRappel: str ou None
        :raises pymysql.MySQLError: En cas d'erreur lors de la mise à jour de la base de données
        """
        try:
            curseur = self.cnx.cursor()
            curseur.execute("""
                UPDATE taches SET 
                    titre = %s, 
                    description = %s, 
                    dateFin = %s, 
                    recurence = %s,
                    typeRecurence = %s, 
                    idUtilisateurAffecte = %s, 
                    idTag = %s, 
                    dateRappel = %s
                WHERE idTache = %s;
            """, (titre, description, dateFin, recurence, typeRecurence, utilisateur, tag, dateRappel, idTache))
            self.cnx.commit()
        except pymysql.MySQLError as e:
            QMessageBox.critical(self, 'Erreur', f'Erreur MySQL lors de la mise à jour de la tâche {idTache} : {e}')
        finally:
            curseur.close()

    def getUtilisateurs(self):
        """
        Récupère tous les utilisateurs (idUtilisateur, pseudonyme) depuis la table utilisateurs.

        :return: Liste des utilisateurs (idUtilisateur, pseudonyme)
        :rtype: list of tuple
        :raises pymysql.MySQLError: En cas d'erreur lors de la récupération des utilisateurs
        """
        try:
            curseur = self.cnx.cursor()
            curseur.execute("SELECT idUtilisateur, pseudonyme FROM utilisateurs;")
            utilisateurs = curseur.fetchall()
            return utilisateurs
        except pymysql.MySQLError as e:
            QMessageBox.critical(self, 'Erreur', f'Erreur MySQL lors de la récupération des utilisateurs : {e}')
            return []
        finally:
            curseur.close()

    def getTags(self):
        """
        Récupère tous les tags (idTag, nomTag) depuis la table tag.

        :return: Liste des tags (idTag, nomTag)
        :rtype: list of tuple
        :raises pymysql.MySQLError: En cas d'erreur lors de la récupération des tags
        """
        try:
            curseur = self.cnx.cursor()
            curseur.execute("SELECT idTag, nomTag FROM tag;")
            tags = curseur.fetchall()
            return tags
        except pymysql.MySQLError as e:
            QMessageBox.critical(self, 'Erreur', f'Erreur MySQL lors de la récupération des tags : {e}')
            return []
        finally:
            curseur.close()

    def supprimerSousTache(self, idSousTache):
        """
        Supprime une sous-tâche en fonction de son ID depuis la base de données.

        :param idSousTache: Identifiant unique de la sous-tâche à supprimer
        :type idSousTache: int
        :raises pymysql.MySQLError: En cas d'erreur lors de la suppression de la sous-tâche
        """
        try:
            curseur = self.cnx.cursor()
            curseur.execute("DELETE FROM sous_taches WHERE idSousTache = %s;", (idSousTache,))
            self.cnx.commit()
        except pymysql.MySQLError as e:
            QMessageBox.critical(self, 'Erreur', f'Erreur MySQL lors de la suppression de la sous-tâche {idSousTache} : {e}')
        finally:
            curseur.close()

    def supprimerTache(self, idTache):
        """
        Supprime une tâche et l'ajoute à la corbeille uniquement si elle n'est pas déjà supprimée.

        :param idTache: Identifiant unique de la tâche à supprimer
        :type idTache: int
        :raises pymysql.MySQLError: En cas d'erreur lors de la suppression de la tâche
        """
        try:
            curseur = self.cnx.cursor()

            curseur.execute("SELECT COUNT(*) FROM corbeille WHERE idTacheFini = %s;", (idTache,))
            resultat = curseur.fetchone()

            if resultat[0] > 0:
                self.actualiser()
        except pymysql.MySQLError as e:
            QMessageBox.critical(self, 'Erreur', f'Erreur MySQL lors de la suppression de la tâche {idTache} : {e}')
        finally:
            curseur.close()

    def ajouterSousTache(self, idTacheParent):
        """
        Ouvre une boîte de dialogue pour ajouter une sous-tâche.

        :param idTacheParent: Identifiant de la tâche parente à laquelle ajouter une sous-tâche
        :type idTacheParent: int
        """
        dialog = DialogueSousTache(idTacheParent, self)
        if dialog.exec_() == QDialog.Accepted:
            donneesSousTache = dialog.getDonneesSousTache()
            self.insererSousTache(donneesSousTache)

    def insererSousTache(self, donneesSousTache):
        """
        Insère une sous-tâche dans la base de données avec 'validation' par défaut à 0.

        :param donneesSousTache: Tuple contenant les informations de la sous-tâche à insérer
        :type donneesSousTache: tuple
        :raises pymysql.MySQLError: En cas d'erreur lors de l'insertion de la sous-tâche
        """
        try:
            curseur = self.cnx.cursor()
            curseur.execute("""
                INSERT INTO soustaches (titre, description, idTacheParent, dateFinSousTache, dateRappel, etiquette, validation)
                VALUES (%s, %s, %s, %s, %s, %s, 0);
            """, donneesSousTache)
            self.cnx.commit()
        except pymysql.MySQLError as e:
            QMessageBox.critical(self, 'Erreur', f"Erreur MySQL lors de l'insertion de la sous-tâche : {e}")
        finally:
            curseur.close()

class DialogueModification(QDialog):
    """
    Boîte de dialogue pour modifier les détails d'une tâche existante.

    :param idTache: Identifiant unique de la tâche à modifier
    :type idTache: int
    :param donneesTache: Détails de la tâche existante
    :type donneesTache: tuple
    :param dateFin: Date de fin de la tâche
    :type dateFin: QDateTime
    :param dateRappel: Date de rappel de la tâche
    :type dateRappel: QDateTime
    :param parent: Widget parent
    :type parent: QWidget, optional
    """
    def __init__(self, idTache, donneesTache, dateFin, dateRappel, parent=None):
        super(DialogueModification, self).__init__(parent)
        self.idTache = idTache
        self.setWindowTitle(f"Modification de '{donneesTache[0]}'")

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QFormLayout(self)

        self.titreEdit = QLineEdit(donneesTache[0])
        self.descriptionEdit = QLineEdit(donneesTache[1])

        self.dateFinEdit = QDateTimeEdit()
        self.dateFinEdit.setCalendarPopup(True)
        self.dateFinEdit.setDateTime(dateFin)

        self.caseDateFinNull = QCheckBox("Mettre la date de fin à NULL")
        self.caseDateFinNull.stateChanged.connect(self.cacheDateFinEdit)

        self.caseRecurrence = QCheckBox("Récurrence")
        self.caseRecurrence.setChecked(donneesTache[3] == 1)

        self.comboTypeRecurrence = QComboBox()
        self.comboTypeRecurrence.addItems(["Tous les jours", "Toutes les semaines", "Tous les mois", "Jours spécifiques"])
        self.comboTypeRecurrence.setEnabled(donneesTache[3] == 1)

        self.caseRecurrence.stateChanged.connect(
            lambda: self.comboTypeRecurrence.setEnabled(self.caseRecurrence.isChecked())
        )

        self.comboUtilisateur = QComboBox()
        self.remplirComboUtilisateur(donneesTache[5])

        self.comboTag = QComboBox()
        self.remplirComboTag(donneesTache[6])

        self.dateRappelEdit = QDateTimeEdit()
        self.dateRappelEdit.setCalendarPopup(True)
        self.dateRappelEdit.setDateTime(dateRappel)

        self.caseDateRappelNull = QCheckBox("Mettre la date de rappel à NULL")
        self.caseDateRappelNull.stateChanged.connect(self.cacheDateRappelEdit)

        layout.addRow("Titre", self.titreEdit)
        layout.addRow("Description", self.descriptionEdit)
        layout.addRow("Date de fin", self.dateFinEdit)
        layout.addRow(self.caseDateFinNull)
        layout.addRow("Récurrence", self.caseRecurrence)
        layout.addRow("Type de récurrence", self.comboTypeRecurrence)
        layout.addRow("Utilisateur affecté", self.comboUtilisateur)
        layout.addRow("Tag", self.comboTag)
        layout.addRow("Date de rappel", self.dateRappelEdit)
        layout.addRow(self.caseDateRappelNull)

        self.boutons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.boutons.accepted.connect(self.accept)
        self.boutons.rejected.connect(self.reject)

        layout.addRow(self.boutons)

    def remplirComboTag(self, idTagSelectionne):
        """
        Remplit la liste déroulante avec les tags et sélectionne celui de la tâche.

        :param idTagSelectionne: Identifiant du tag à sélectionner
        :type idTagSelectionne: int
        """
        self.comboTag.addItem("Aucun", None)
        tags = self.parent().getTags()
        for idTag, nomTag in tags:
            self.comboTag.addItem(nomTag, idTag)
        index = self.comboTag.findData(idTagSelectionne)
        if index >= 0:
            self.comboTag.setCurrentIndex(index)

    def remplirComboUtilisateur(self, idUtilisateurSelectionne):
        """
        Remplit la liste déroulante avec les utilisateurs et sélectionne celui de la tâche.

        :param idUtilisateurSelectionne: Identifiant de l'utilisateur à sélectionner
        :type idUtilisateurSelectionne: int
        """
        self.comboUtilisateur.addItem("Aucun", 0)
        utilisateurs = self.parent().getUtilisateurs()
        for idUtilisateur, pseudonyme in utilisateurs:
            self.comboUtilisateur.addItem(pseudonyme, idUtilisateur)
        index = self.comboUtilisateur.findData(idUtilisateurSelectionne)
        if index >= 0:
            self.comboUtilisateur.setCurrentIndex(index)

    def cacheDateFinEdit(self, etat):
        """
        Active ou désactive le champ de la date de fin selon l'état de la case à cocher.

        :param etat: État de la case à cocher (True si coché, False sinon)
        :type etat: bool
        """
        self.dateFinEdit.setEnabled(etat == 0)

    def cacheDateRappelEdit(self, etat):
        """
        Active ou désactive le champ de la date de rappel selon l'état de la case à cocher.

        :param etat: État de la case à cocher (True si coché, False sinon)
        :type etat: bool
        """
        self.dateRappelEdit.setEnabled(etat == 0)

    def getDonneesTache(self):
        """
        Retourne les données modifiées sous forme de tuple.

        :return: Tuple contenant les nouvelles données de la tâche
        :rtype: tuple
        """
        return (
            self.titreEdit.text(),
            self.descriptionEdit.text(),
            None if self.caseDateFinNull.isChecked() else self.dateFinEdit.dateTime().toString("yyyy-MM-dd HH:mm:ss"),
            1 if self.caseRecurrence.isChecked() else 0,
            self.comboTypeRecurrence.currentIndex(),
            self.comboUtilisateur.currentData(),
            self.comboTag.currentData(),
            None if self.caseDateRappelNull.isChecked() else self.dateRappelEdit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        )

class DialogueSousTache(QDialog):
    """
    Boîte de dialogue pour ajouter une nouvelle sous-tâche.

    :param idTacheParent: Identifiant de la tâche parente
    :type idTacheParent: int
    :param parent: Widget parent
    :type parent: QWidget, optional
    """
    def __init__(self, idTacheParent, parent=None):
        super(DialogueSousTache, self).__init__(parent)
        self.idTacheParent = idTacheParent
        self.setWindowTitle("Nouvelle Sous-Tâche")

        layout = QFormLayout(self)

        self.titreEdit = QLineEdit()
        self.descriptionEdit = QLineEdit()

        self.dateFinEdit = QDateEdit()
        self.dateFinEdit.setCalendarPopup(True)
        self.dateFinEdit.setDate(QDate.currentDate())

        self.caseDateFinNull = QCheckBox("Mettre la date de fin à NULL")
        self.caseDateFinNull.stateChanged.connect(self.cacherDateFinEdit)

        self.dateRappelEdit = QDateEdit()
        self.dateRappelEdit.setCalendarPopup(True)
        self.dateRappelEdit.setDate(QDate.currentDate())

        self.caseDateRappelNull = QCheckBox("Mettre la date de rappel à NULL")
        self.caseDateRappelNull.stateChanged.connect(self.cacherDateRappelEdit)

        self.comboEtiquette = QComboBox()
        self.remplirComboEtiquette()

        layout.addRow("Titre", self.titreEdit)
        layout.addRow("Description", self.descriptionEdit)
        layout.addRow("Date de fin", self.dateFinEdit)
        layout.addRow(self.caseDateFinNull)
        layout.addRow("Date de rappel", self.dateRappelEdit)
        layout.addRow(self.caseDateRappelNull)
        layout.addRow("Étiquette", self.comboEtiquette)

        self.boutons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.boutons.accepted.connect(self.accept)
        self.boutons.rejected.connect(self.reject)

        layout.addRow(self.boutons)

    def remplirComboEtiquette(self):
        """
        Remplit la liste déroulante avec les étiquettes disponibles.
        """
        self.comboEtiquette.addItem("Aucun", None)
        etiquettes = self.parent().getTags()
        for idTag, nomTag in etiquettes:
            self.comboEtiquette.addItem(nomTag, idTag)

    def cacherDateFinEdit(self, etat):
        """
        Active ou désactive le champ de la date de fin selon l'état de la case à cocher.

        :param etat: État de la case à cocher (True si coché, False sinon)
        :type etat: bool
        """
        self.dateFinEdit.setEnabled(etat == 0)

    def cacherDateRappelEdit(self, etat):
        """
        Active ou désactive le champ de la date de rappel selon l'état de la case à cocher.

        :param etat: État de la case à cocher (True si coché, False sinon)
        :type etat: bool
        """
        self.dateRappelEdit.setEnabled(etat == 0)

    def getDonneesSousTache(self):
        """
        Retourne les données de la sous-tâche sous forme de tuple.

        :return: Tuple contenant les informations de la sous-tâche
        :rtype: tuple
        """
        return (
            self.titreEdit.text(),
            self.descriptionEdit.text(),
            self.idTacheParent,
            None if self.caseDateFinNull.isChecked() else self.dateFinEdit.date().toString("yyyy-MM-dd"),
            None if self.caseDateRappelNull.isChecked() else self.dateRappelEdit.date().toString("yyyy-MM-dd"),
            self.comboEtiquette.currentData()
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = PagePrincipale()
    fenetre.show()
    sys.exit(app.exec_())
