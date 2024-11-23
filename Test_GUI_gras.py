from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
    QTreeWidgetItem, QTreeWidget, QDateEdit, QTextEdit, QComboBox, QMessageBox, QLineEdit, QCheckBox
)
from PyQt5.QtCore import Qt, QDate, QSize
from PyQt5.QtGui import QPalette, QColor, QIcon
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

        # Options pour le formatage du nom
        self.label_format = QLabel("Format du texte :")
        self.checkbox_bold = QCheckBox("Gras")
        self.checkbox_italic = QCheckBox("Italique")
        self.checkbox_underline = QCheckBox("Souligné")
        format_layout = QHBoxLayout()
        format_layout.addWidget(self.checkbox_bold)
        format_layout.addWidget(self.checkbox_italic)
        format_layout.addWidget(self.checkbox_underline)
        layout.addWidget(self.label_format)
        layout.addLayout(format_layout)

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
        layout.addWidget(self.champ_categorie)

        # Champ pour le statut
        self.label_statut = QLabel("Statut :")
        self.champ_statut = QComboBox()
        self.champ_statut.addItems(["À faire", "En cours", "Terminé"])
        layout.addWidget(self.champ_statut)

        # Champ pour la priorité
        self.label_priorite = QLabel("Priorité :")
        self.champ_priorite = QComboBox()
        self.champ_priorite.addItems(["Basse", "Moyenne", "Haute"])
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
        priorite = self.champ_priorite.currentText()
        statut = self.champ_statut.currentText()

        # Déterminer le formatage
        format_style = ""
        if self.checkbox_bold.isChecked():
            format_style += "<b>"
        if self.checkbox_italic.isChecked():
            format_style += "<i>"
        if self.checkbox_underline.isChecked():
            format_style += "<u>"

        formatted_nom = f"{format_style}{nom_tache}</b></i></u>"

        # Vérifier que les champs obligatoires sont remplis
        if not nom_tache:
            QMessageBox.warning(self, "Erreur", "Le nom de la tâche est obligatoire.")
            return

        # Ajouter la tâche à la liste principale
        self.parent.add_task_to_tree(formatted_nom, date, description, categorie, statut, priorite)
        self.close()

    def reset_form(self):
        """Réinitialiser les champs du formulaire"""
        self.champ_nom.clear()
        self.champ_description.clear()
        self.champ_date.setDate(QDate.currentDate())  # Réinitialiser la date à aujourd'hui
        self.champ_categorie.setCurrentIndex(0)  # Réinitialiser à la première catégorie
        self.champ_statut.setCurrentIndex(0)  # Réinitialiser au statut "À faire"
        self.champ_priorite.setCurrentIndex(0)  # Réinitialiser à la priorité "Basse"
        self.checkbox_bold.setChecked(False)
        self.checkbox_italic.setChecked(False)
        self.checkbox_underline.setChecked(False)


class TodoListApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("The ToDo List")
        self.setGeometry(100, 100, 1000, 400)

        # Widget central pour le contenu principal
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)

        # Création de la colonne latérale (sidebar)
        self.sidebar = QWidget()
        sidebar_layout = QVBoxLayout(self.sidebar)

        # Boutons déplacés vers la colonne latérale
        self.theme_button = QPushButton()
        self.theme_button.setIcon(QIcon("sun.png"))  # Icône par défaut (Soleil pour le mode clair)
        self.theme_button.setIconSize(QSize(30, 30))  # Taille de l'icône
        self.settings_button = QPushButton("Paramètres")
        self.help_button = QPushButton("Aide")
        self.credits_button = QPushButton("Crédits")

        # Connexion des boutons de la colonne latérale
        self.theme_button.clicked.connect(self.toggle_theme)
        self.settings_button.clicked.connect(self.open_settings)
        self.help_button.clicked.connect(self.open_help)
        self.credits_button.clicked.connect(self.open_credits)

        # Ajout des boutons à la colonne latérale
        sidebar_layout.addWidget(self.theme_button)
        sidebar_layout.addWidget(self.settings_button)
        sidebar_layout.addWidget(self.help_button)
        sidebar_layout.addWidget(self.credits_button)

        main_layout.addWidget(self.sidebar)

        # Zone principale de l'application
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)

        # Barre de navigation avec le bouton pour afficher/cacher la colonne latérale
        nav_layout = QHBoxLayout()
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

        self.main_layout.addLayout(nav_layout)

        # Arborescence des tâches
        self.task_tree = QTreeWidget()
        self.task_tree.setHeaderLabels(["Tâches", "Échéance", "Description", "Catégorie", "Statut", "Priorité"])
        self.main_layout.addWidget(self.task_tree)

        main_layout.addWidget(self.main_widget)

        # Définir le widget central pour QMainWindow
        self.setCentralWidget(central_widget)

        # Liste temporaire pour stocker les tâches
        self.tasks = []
        self.formulaire_window = None
        self.is_dark_mode = False

    def toggle_sidebar(self):
        self.sidebar.setVisible(not self.sidebar.isVisible())

    def open_formulaire(self):
        if self.formulaire_window is None:
            self.formulaire_window = FormulaireTache(parent=self)
        self.formulaire_window.show()
        self.formulaire_window.reset_form()

    def toggle_theme(self):
        if not self.is_dark_mode:
            self.set_dark_mode()
            self.theme_button.setIcon(QIcon("moon.png"))
        else:
            self.set_light_mode()
            self.theme_button.setIcon(QIcon("sun.png"))
        self.is_dark_mode = not self.is_dark_mode

    def set_dark_mode(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        QApplication.instance().setPalette(dark_palette)

    def set_light_mode(self):
        QApplication.instance().setPalette(QApplication.style().standardPalette())
        self.setStyleSheet("")

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
