from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
    QTreeWidgetItem, QTreeWidget, QDateEdit, QTextEdit, QComboBox, QMessageBox, QLineEdit
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QPalette, QColor
import sys

class FormulaireTache(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

        self.setWindowTitle("Formulaire de Tâche")
        self.setGeometry(100, 100, 300, 400)

        layout = QVBoxLayout()

        # Champ pour le nom de la tâche
        self.label_nom = QLabel("Nom de la tâche :")
        self.champ_nom = QLineEdit()
        layout.addWidget(self.label_nom)
        layout.addWidget(self.champ_nom)

        # Champ pour la description
        self.label_description = QLabel("Description :")
        self.champ_description = QTextEdit()
        layout.addWidget(self.label_description)
        layout.addWidget(self.champ_description)

        # Champ pour la date
        self.label_date = QLabel("Date :")
        self.champ_date = QDateEdit()
        self.champ_date.setDate(QDate.currentDate())
        layout.addWidget(self.label_date)
        layout.addWidget(self.champ_date)

        # Champ pour la catégorie
        self.label_categorie = QLabel("Catégorie :")
        self.champ_categorie = QComboBox()
        self.champ_categorie.addItems(["Travail", "Personnel", "Urgent", "Autre"])
        layout.addWidget(self.label_categorie)
        layout.addWidget(self.champ_categorie)

        # Champ pour le statut
        self.label_statut = QLabel("Statut :")
        self.champ_statut = QComboBox()
        self.champ_statut.addItems(["À faire", "En cours", "Terminé"])
        layout.addWidget(self.label_statut)
        layout.addWidget(self.champ_statut)

        # Champ pour la priorité
        self.label_priorite = QLabel("Priorité :")
        self.champ_priorite = QComboBox()
        self.champ_priorite.addItems(["Basse", "Moyenne", "Haute"])
        layout.addWidget(self.label_priorite)
        layout.addWidget(self.champ_priorite)

        # Bouton pour soumettre
        self.bouton_soumettre = QPushButton("Soumettre")
        self.bouton_soumettre.clicked.connect(self.SoumettreFormulaire)
        layout.addWidget(self.bouton_soumettre)

        self.setLayout(layout)

    def SoumettreFormulaire(self):
        # Récupérer les données du formulaire
        nom_tache = self.champ_nom.text()
        description = self.champ_description.toPlainText()
        date = self.champ_date.date().toString("dd/MM/yyyy")
        categorie = self.champ_categorie.currentText()
        statut = self.champ_statut.currentText()
        priorite = self.champ_priorite.currentText()

        # Vérifier que les champs obligatoires sont remplis
        if not nom_tache:
            QMessageBox.warning(self, "Erreur", "Le nom de la tâche est obligatoire.")
            return

        # Ajouter la tâche à la liste principale
        self.parent.add_task_to_tree(nom_tache, date, description, categorie, statut, priorite)
        self.close()


class TodoListApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("The ToDo List")
        self.setGeometry(100, 100, 800, 400)

        self.tasks = []
        self.formulaire_window = None
        self.settings_window = None
        self.help_window = None
        self.credits_window = None
        self.is_dark_mode = False

        main_layout = QVBoxLayout()

        # Barre de navigation
        nav_layout = QHBoxLayout()

        self.home_button = QPushButton("Accueil")
        self.form_button = QPushButton("Ouvrir Formulaire")
        self.theme_button = QPushButton("Mode Sombre")
        self.settings_button = QPushButton("Paramètres")
        self.help_button = QPushButton("Aide")
        self.credits_button = QPushButton("Crédits")

        self.home_button.clicked.connect(self.show_home_message)
        self.form_button.clicked.connect(self.open_formulaire)
        self.theme_button.clicked.connect(self.toggle_theme)
        self.settings_button.clicked.connect(self.open_settings)
        self.help_button.clicked.connect(self.open_help)
        self.credits_button.clicked.connect(self.open_credits)

        nav_layout.addWidget(self.home_button)
        nav_layout.addWidget(self.form_button)
        nav_layout.addWidget(self.theme_button)
        nav_layout.addWidget(self.settings_button)
        nav_layout.addWidget(self.help_button)
        nav_layout.addWidget(self.credits_button)

        main_layout.addLayout(nav_layout)

        # Arborescence des tâches
        self.task_tree = QTreeWidget()
        self.task_tree.setHeaderLabels(["Tâches", "Échéance", "Description", "Catégorie", "Statut", "Priorité"])
        self.task_tree.setMinimumWidth(300)
        main_layout.addWidget(self.task_tree)

        self.setLayout(main_layout)

    def show_home_message(self):
        QMessageBox.information(self, "Accueil", "Vous êtes sur la page d'accueil.")
        self.task_tree.clearSelection()

    def open_formulaire(self):
        if self.formulaire_window is None:
            self.formulaire_window = FormulaireTache(parent=self)
        self.formulaire_window.show()

    def toggle_theme(self):
        if not self.is_dark_mode:
            self.set_dark_mode()
            self.theme_button.setText("Mode Clair")
        else:
            self.set_light_mode()
            self.theme_button.setText("Mode Sombre")
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
        dark_palette.setColor(QPalette.PlaceholderText, Qt.lightGray)

        QApplication.instance().setPalette(dark_palette)

    def set_light_mode(self):
        light_palette = QPalette()
        light_palette.setColor(QPalette.Window, Qt.white)
        light_palette.setColor(QPalette.WindowText, Qt.black)
        light_palette.setColor(QPalette.Base, Qt.white)
        light_palette.setColor(QPalette.AlternateBase, QColor(240, 240, 240))
        light_palette.setColor(QPalette.ToolTipBase, Qt.black)
        light_palette.setColor(QPalette.ToolTipText, Qt.black)
        light_palette.setColor(QPalette.Text, Qt.black)
        light_palette.setColor(QPalette.Button, Qt.white)
        light_palette.setColor(QPalette.ButtonText, Qt.black)
        light_palette.setColor(QPalette.BrightText, Qt.red)
        light_palette.setColor(QPalette.Link, QColor(0, 0, 255))
        light_palette.setColor(QPalette.Highlight, QColor(100, 150, 200))
        light_palette.setColor(QPalette.HighlightedText, Qt.black)
        light_palette.setColor(QPalette.PlaceholderText, Qt.darkGray)

        QApplication.instance().setPalette(light_palette)

    def add_task_to_tree(self, nom_tache, date, description, categorie, statut, priorite):
        task_item = QTreeWidgetItem([nom_tache, date, description, categorie, statut, priorite])
        self.task_tree.addTopLevelItem(task_item)
        self.tasks.append({
            "nom": nom_tache,
            "date": date,
            "description": description,
            "categorie": categorie,
            "statut": statut,
            "priorite": priorite
        })

    def open_settings(self):
        if self.settings_window is None:
            self.settings_window = SettingsWindow()
        self.settings_window.show()

    def open_help(self):
        if self.help_window is None:
            self.help_window = HelpWindow()
        self.help_window.show()

    def open_credits(self):
        if self.credits_window is None:
            self.credits_window = CreditsWindow()
        self.credits_window.show()


class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Paramètres")
        self.setGeometry(150, 150, 300, 200)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Réglages de l'application"))
        layout.addWidget(QLabel("Ici, vous pouvez configurer vos préférences."))

        close_button = QPushButton("Fermer")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)


class HelpWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aide")
        self.setGeometry(150, 150, 400, 300)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Aide de l'application"))

        close_button = QPushButton("Fermer")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)


class CreditsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Crédits")
        self.setGeometry(150, 150, 400, 300)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Crédits de l'application"))

        close_button = QPushButton("Fermer")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TodoListApp()
    window.show()
    sys.exit(app.exec())
