import sys
import pymysql
from PyQt5.QtCore import QCoreApplication, Qt, QDate, QDateTime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget,
    QHBoxLayout, QCheckBox, QAction, QMenu, QApplication, QListWidgetItem, QDialog,
    QLineEdit, QDialogButtonBox, QFormLayout, QDateEdit, QComboBox, QDateTimeEdit
)

class Principal(QWidget):
    def __init__(self, host: str = '127.0.0.1', user: str = 'root', password='toto', database: str = 'thetotodb'):
        super().__init__()

        self.setWindowTitle("Page Principale")
        self.layout = QVBoxLayout(self)
        self.resize(400, 300)  # Augmenter la taille pour plus d'espace

        self.titre = QLabel("Mes tâches")
        self.bouton_actualiser = QPushButton("Actualiser")
        self.bouton_quitter = QPushButton("Quitter")

        self.taches = QListWidget()

        self.layout.addWidget(self.titre)
        self.layout.addWidget(self.bouton_actualiser)
        self.layout.addWidget(self.taches)
        self.layout.addWidget(self.bouton_quitter)

        self.bouton_quitter.clicked.connect(self.quitter)
        self.bouton_actualiser.clicked.connect(self.actualiser)

        self.host = host
        self.user = user
        self.password = password
        self.database = database

        self.cnx = pymysql.connect(host=host, user=user, password=password, database=database)

        self.actualiser()  # Charger les tâches au démarrage

    def quitter(self):
        QCoreApplication.exit(0)

    def actualiser(self):
        curseur = self.cnx.cursor()
        curseur.execute("SELECT idTache, titre, validation FROM taches;")
        resultat = curseur.fetchall()
        self.taches.clear()
        for task_id, task_title, validation in resultat:
            self.ajouter_tache(task_title, task_id, validation)

    def ajouter_tache(self, task_title, task_id, validation):
        """Ajoute une tâche sous forme de widget personnalisé dans la liste"""
        task_widget = QWidget()
        layout = QHBoxLayout(task_widget)

        checkbox = QCheckBox()
        checkbox.setChecked(validation == 1)  # Définir la case en fonction de la validation
        task_label = QLabel(task_title)

        if validation == 1:
            task_label.setStyleSheet("text-decoration: line-through; color: gray;")

        more_button = QPushButton("...")
        more_button.setFixedWidth(30)

        layout.addWidget(checkbox)
        layout.addWidget(task_label)
        layout.addWidget(more_button)
        layout.addStretch()

        # Connexion des signaux
        checkbox.stateChanged.connect(lambda: self.update_style(task_label, task_id, checkbox.isChecked()))
        more_button.clicked.connect(lambda: self.show_menu(task_id, task_title, task_widget))

        list_item = QListWidgetItem()
        list_item.setSizeHint(task_widget.sizeHint())
        self.taches.addItem(list_item)
        self.taches.setItemWidget(list_item, task_widget)

    def update_style(self, task_label, task_id, checked):
        """Mise à jour du style visuel et de la validation dans la base de données"""
        if checked:
            task_label.setStyleSheet("text-decoration: line-through; color: gray;")
            self.update_validation(task_id, 1)
        else:
            task_label.setStyleSheet("")
            self.update_validation(task_id, 0)

    def update_validation(self, task_id, validation_status):
        """Met à jour le champ validation de la tâche dans la base de données"""
        try:
            curseur = self.cnx.cursor()
            curseur.execute("UPDATE taches SET validation = %s WHERE idTache = %s;", (validation_status, task_id))
            self.cnx.commit()
            print(f"Tâche {task_id} mise à jour avec validation = {validation_status}")
        except pymysql.MySQLError as e:
            print(f"Erreur MySQL lors de la mise à jour de la validation de la tâche {task_id} : {e}")
        finally:
            curseur.close()

    def show_menu(self, task_id, task_title, task_widget):
        """Affiche un menu contextuel pour la tâche"""
        menu = QMenu(task_widget)

        modify_action = QAction("Modifier", task_widget)
        delete_action = QAction("Supprimer", task_widget)
        nouvEnf_action = QAction("Nouvelle tâche enfant", task_widget)

        modify_action.triggered.connect(lambda: self.modifier_tache(task_id))  # Ouvre la popup de modification
        delete_action.triggered.connect(lambda: self.delete_task(task_id))

        menu.addAction(modify_action)
        menu.addAction(delete_action)
        menu.addAction(nouvEnf_action)

        menu.exec_(self.mapToGlobal(task_widget.pos()))

    def modifier_tache(self, task_id):
        """Ouvre la boîte de dialogue de modification avec des champs datetime et prise en charge des valeurs NULL"""
        try:
            # Récupérer les données de la tâche depuis la base de données
            curseur = self.cnx.cursor()
            curseur.execute("""
                SELECT titre, description, dateFin, recurence, typeRecurence, idUtilisateurAffecte, idTag, dateRappel 
                FROM taches 
                WHERE idTache = %s
            """, (task_id,))
            tache = curseur.fetchone()

            if tache:
                # Gestion des dates et des heures - Détecter les NULL
                date_fin_str = tache[2].strftime("%Y-%m-%d %H:%M:%S") if tache[2] else None
                date_rappel_str = tache[7].strftime("%Y-%m-%d %H:%M:%S") if tache[7] else None

                # Si les dates sont NULL, définir les QDateTime avec des valeurs par défaut
                date_fin = QDateTime.fromString(date_fin_str,
                                                "yyyy-MM-dd HH:mm:ss") if date_fin_str else QDateTime.currentDateTime()
                date_rappel = QDateTime.fromString(date_rappel_str,
                                                   "yyyy-MM-dd HH:mm:ss") if date_rappel_str else QDateTime.currentDateTime()

                # Lancer la boîte de dialogue de modification avec les données récupérées
                dialog = ModificationDialog(task_id, tache, date_fin, date_rappel, self)

                # Cocher les cases "Mettre la date à NULL" si la date est NULL dans la base de données
                if not date_fin_str:
                    dialog.date_fin_null_checkbox.setChecked(True)
                    dialog.date_fin_edit.setEnabled(False)  # Désactiver le champ date si NULL
                if not date_rappel_str:
                    dialog.date_rappel_null_checkbox.setChecked(True)
                    dialog.date_rappel_edit.setEnabled(False)  # Désactiver le champ date si NULL

                # Si l'utilisateur valide la boîte de dialogue
                if dialog.exec_() == QDialog.Accepted:
                    # Récupérer les nouvelles données du formulaire
                    nouveau_donnees = dialog.get_task_data()

                    # Mettre à jour la tâche dans la base de données avec les nouvelles données
                    self.update_tache(task_id, *nouveau_donnees)

        except Exception as e:
            print(f"Erreur lors de la récupération des données de la tâche : {e}")
        finally:
            curseur.close()

    def update_tache(self, task_id, titre, description, date_fin, recurence, type_recurence, utilisateur, tag,
                     date_rappel):
        """Met à jour la tâche dans la base de données"""
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
            """, (titre, description, date_fin, recurence, type_recurence, utilisateur, tag, date_rappel, task_id))
            self.cnx.commit()
            print(f"Tâche {task_id} mise à jour avec succès.")
            self.actualiser()  # Rafraîchir la liste des tâches
        except pymysql.MySQLError as e:
            print(f"Erreur MySQL lors de la mise à jour de la tâche {task_id} : {e}")
        finally:
            curseur.close()

    def get_utilisateurs(self):
        """Récupère tous les utilisateurs (idUtilisateur, pseudonyme) depuis la table utilisateurs"""
        try:
            curseur = self.cnx.cursor()
            curseur.execute("SELECT idUtilisateur, pseudonyme FROM utilisateurs;")
            utilisateurs = curseur.fetchall()
            return utilisateurs
        except pymysql.MySQLError as e:
            print(f"Erreur MySQL lors de la récupération des utilisateurs : {e}")
            return []
        finally:
            curseur.close()

    def get_tags(self):
        """Récupère tous les tags (idTag, nomTag) depuis la table tag"""
        try:
            curseur = self.cnx.cursor()
            curseur.execute("SELECT idTag, nomTag FROM tag;")
            tags = curseur.fetchall()
            return tags
        except pymysql.MySQLError as e:
            print(f"Erreur MySQL lors de la récupération des tags : {e}")
            return []
        finally:
            curseur.close()

    def delete_task(self, task_id):
        """Supprime une tâche et l'ajoute à la corbeille uniquement si elle n'est pas déjà supprimée"""
        print(f"Tentative de suppression de la tâche avec ID: {task_id}")
        try:
            curseur = self.cnx.cursor()

            # Vérifier si la tâche est déjà dans la corbeille
            curseur.execute("SELECT COUNT(*) FROM corbeille WHERE idTacheFini = %s;", (task_id,))
            result = curseur.fetchone()

            if result[0] > 0:
                print(f"Tâche {task_id} déjà dans la corbeille, suppression impossible.")
            else:
                # Insérer l'ID de la tâche et la date de suppression dans la table corbeille
                curseur.execute("INSERT INTO corbeille (idTacheFini, dateSupression) VALUES (%s, NOW());", (task_id,))
                self.cnx.commit()
                print(f"Tâche {task_id} déplacée vers la corbeille.")
                self.actualiser()  # Rafraîchir la liste des tâches
        except pymysql.MySQLError as e:
            print(f"Erreur MySQL lors de la suppression de la tâche {task_id} : {e}")
        finally:
            curseur.close()


class ModificationDialog(QDialog):
    def __init__(self, task_id, tache_data, date_fin, date_rappel, parent=None):
        super(ModificationDialog, self).__init__(parent)
        self.task_id = task_id
        self.setWindowTitle(f"Modification de '{tache_data[0]}'")

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QFormLayout(self)

        # Champs du formulaire
        self.titre_edit = QLineEdit(tache_data[0])
        self.description_edit = QLineEdit(tache_data[1])

        # Gestion de la date de fin
        self.date_fin_edit = QDateTimeEdit()
        self.date_fin_edit.setCalendarPopup(True)
        self.date_fin_edit.setDateTime(date_fin)

        # Case à cocher pour mettre la date de fin à NULL
        self.date_fin_null_checkbox = QCheckBox("Mettre la date de fin à NULL")
        self.date_fin_null_checkbox.stateChanged.connect(self.toggle_date_fin_edit)

        # Gestion de la récurrence
        self.recurrence_checkbox = QCheckBox("Récurrence")
        self.recurrence_checkbox.setChecked(tache_data[3] == 1)

        self.type_recurrence_combo = QComboBox()
        self.type_recurrence_combo.addItems(["Tous les jours", "Toutes les semaines", "Tous les mois", "Jours spécifiques"])
        self.type_recurrence_combo.setEnabled(tache_data[3] == 1)

        self.recurrence_checkbox.stateChanged.connect(
            lambda: self.type_recurrence_combo.setEnabled(self.recurrence_checkbox.isChecked())
        )

        # Liste déroulante pour les utilisateurs affectés
        self.utilisateur_combo = QComboBox()
        self.populate_utilisateur_combo(tache_data[5])  # Passe l'utilisateur actuel pour le sélectionner

        # Liste déroulante pour les tags
        self.tag_combo = QComboBox()
        self.populate_tag_combo(tache_data[6])  # Passe le tag actuel pour le sélectionner

        # Gestion de la date de rappel
        self.date_rappel_edit = QDateTimeEdit()
        self.date_rappel_edit.setCalendarPopup(True)
        self.date_rappel_edit.setDateTime(date_rappel)

        # Case à cocher pour mettre la date de rappel à NULL
        self.date_rappel_null_checkbox = QCheckBox("Mettre la date de rappel à NULL")
        self.date_rappel_null_checkbox.stateChanged.connect(self.toggle_date_rappel_edit)

        # Ajout des champs dans le layout
        layout.addRow("Titre", self.titre_edit)
        layout.addRow("Description", self.description_edit)
        layout.addRow("Date de fin", self.date_fin_edit)
        layout.addRow(self.date_fin_null_checkbox)  # Checkbox pour mettre la date de fin à NULL
        layout.addRow("Récurrence", self.recurrence_checkbox)
        layout.addRow("Type de récurrence", self.type_recurrence_combo)
        layout.addRow("Utilisateur affecté", self.utilisateur_combo)  # Utilisation de la QComboBox pour les utilisateurs
        layout.addRow("Tag", self.tag_combo)  # Utilisation de la QComboBox pour les tags
        layout.addRow("Date de rappel", self.date_rappel_edit)
        layout.addRow(self.date_rappel_null_checkbox)  # Checkbox pour mettre la date de rappel à NULL

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        layout.addRow(self.buttons)

    def populate_tag_combo(self, selected_tag_id):
        """Remplit la liste déroulante avec les tags et sélectionne celui de la tâche"""
        self.tag_combo.addItem("Aucun", None)

        # Récupérer les tags depuis la base de données
        tags = self.parent().get_tags()

        # Ajouter chaque tag dans la QComboBox
        for tag_id, tag_name in tags:
            self.tag_combo.addItem(tag_name, tag_id)

        # Sélectionner le tag actuel de la tâche
        index = self.tag_combo.findData(selected_tag_id)
        if index >= 0:
            self.tag_combo.setCurrentIndex(index)

    def populate_utilisateur_combo(self, selected_utilisateur_id):
        """Remplit la liste déroulante avec les utilisateurs et sélectionne celui de la tâche"""
        self.utilisateur_combo.addItem("Aucun", 0)

        # Récupérer les utilisateurs depuis la base de données
        utilisateurs = self.parent().get_utilisateurs()

        # Ajouter chaque utilisateur dans la QComboBox
        for utilisateur_id, pseudonyme in utilisateurs:
            self.utilisateur_combo.addItem(pseudonyme, utilisateur_id)

        # Sélectionner l'utilisateur actuel de la tâche
        index = self.utilisateur_combo.findData(selected_utilisateur_id)
        if index >= 0:
            self.utilisateur_combo.setCurrentIndex(index)

    def toggle_date_fin_edit(self, state):
        """Active ou désactive le champ de la date de fin selon l'état de la case à cocher."""
        self.date_fin_edit.setEnabled(state == 0)  # désactiver si coché

    def toggle_date_rappel_edit(self, state):
        """Active ou désactive le champ de la date de rappel selon l'état de la case à cocher."""
        self.date_rappel_edit.setEnabled(state == 0)  # désactiver si coché

    def get_task_data(self):
        """Retourne les données modifiées sous forme de tuple"""
        return (
            self.titre_edit.text(),
            self.description_edit.text(),
            None if self.date_fin_null_checkbox.isChecked() else self.date_fin_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss"),
            1 if self.recurrence_checkbox.isChecked() else 0,
            self.type_recurrence_combo.currentIndex(),
            self.utilisateur_combo.currentData(),  # Récupérer l'idUtilisateur sélectionné
            self.tag_combo.currentData(),  # Récupérer l'idTag sélectionné
            None if self.date_rappel_null_checkbox.isChecked() else self.date_rappel_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Principal()
    window.show()
    sys.exit(app.exec_())
