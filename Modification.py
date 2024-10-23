import sys
import pymysql
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget,
    QHBoxLayout, QCheckBox, QAction, QMenu, QApplication, QListWidgetItem
)

class Principal(QWidget):
    def __init__(self, host: str = '127.0.0.1', user: str = 'root', password='toto', database: str = 'thetotodb'):
        super().__init__()

        self.setWindowTitle("Page Principale")

        self.layout = QVBoxLayout(self)
        self.resize(300, 150)

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
        curseur.execute("SELECT idTache, titre, validation FROM taches;")  # On récupère aussi le champ validation
        resultat = curseur.fetchall()
        self.taches.clear()
        for task_id, task_title, validation in resultat:
            task_widget = TaskWidget(task_title, task_id, validation, self)  # On passe le statut validation
            list_item = QListWidgetItem()  # Créez un QListWidgetItem vide
            list_item.setSizeHint(task_widget.sizeHint())  # Définir la taille du QListWidgetItem
            self.taches.addItem(list_item)  # Ajoutez le QListWidgetItem
            self.taches.setItemWidget(list_item, task_widget)  # Associez le widget à l'élément

    def delete_task(self, task_id):
        print(f"Tentative de suppression de la tâche avec ID: {task_id}")
        try:
            curseur = self.cnx.cursor()
            # Insérer l'ID de la tâche et la date de suppression dans la table corbeille
            curseur.execute("INSERT INTO corbeille (idTacheFini, dateSupression) VALUES (%s, NOW());", (task_id,))
            self.cnx.commit()  # Valider la transaction
            print(f"Tâche {task_id} déplacée vers la corbeille.")
        except pymysql.MySQLError as e:
            print(f"Erreur MySQL lors de la suppression de la tâche {task_id} : {e}")
        except Exception as e:
            print(f"Erreur générale lors de la suppression de la tâche {task_id} : {e}")
        finally:
            curseur.close()

    def update_validation(self, task_id, validation_status):
        """Met à jour le champ validation de la tâche dans la base de données."""
        try:
            curseur = self.cnx.cursor()
            curseur.execute("UPDATE taches SET validation = %s WHERE idTache = %s;", (validation_status, task_id))
            self.cnx.commit()
            print(f"Tâche {task_id} mise à jour avec validation = {validation_status}")
        except pymysql.MySQLError as e:
            print(f"Erreur MySQL lors de la mise à jour de la validation de la tâche {task_id} : {e}")
        finally:
            curseur.close()

class TaskWidget(QWidget):
    def __init__(self, task_title, task_id, validation, parent=None):
        super(TaskWidget, self).__init__(parent)
        self.task_id = task_id  # Stocker l'ID de la tâche
        self.parent_widget = parent  # Conserver une référence au parent

        layout = QHBoxLayout(self)

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(validation == 1)  # Définir la case en fonction de la validation
        self.checkbox.stateChanged.connect(self.update_style)  # Connecter l'état de la case à cocher

        self.task_label = QLabel(task_title)
        if validation == 1:
            self.task_label.setStyleSheet("text-decoration: line-through; color: gray;")  # Appliquer le style si déjà validé

        self.more_button = QPushButton("...")
        self.more_button.setFixedWidth(30)

        layout.addWidget(self.checkbox)
        layout.addWidget(self.task_label)
        layout.addWidget(self.more_button)

        layout.addStretch()

        self.more_button.clicked.connect(self.show_menu)

    def show_menu(self):
        menu = QMenu(self)

        modify_action = QAction("Modifier", self)
        delete_action = QAction("Supprimer", self)
        nouvEnf_action = QAction("Nouvelle tache enfant", self)

        delete_action.triggered.connect(self.delete_task)

        menu.addAction(modify_action)
        menu.addAction(delete_action)
        menu.addAction(nouvEnf_action)

        menu.exec_(self.mapToGlobal(self.more_button.pos()))

    def delete_task(self):
        if self.parent_widget:  # Vérifie si le parent est défini
            self.parent_widget.delete_task(self.task_id)  # Appeler delete_task sur le parent

    def update_style(self):
        if self.checkbox.isChecked():
            self.task_label.setStyleSheet("text-decoration: line-through; color: gray;")
            self.parent_widget.update_validation(self.task_id, 1)  # Marquer comme validée dans la DB
        else:
            self.task_label.setStyleSheet("")
            self.parent_widget.update_validation(self.task_id, 0)  # Marquer comme non validée dans la DB

if __name__ == "__main__":
    app = QApplication(sys.argv)
    principal = Principal()
    principal.show()
    sys.exit(app.exec_())
