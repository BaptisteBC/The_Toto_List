from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
    QTreeWidgetItem, QTreeWidget, QDateEdit, QTextEdit, QComboBox, QMessageBox, QLineEdit, QDialog, QDialogButtonBox
)
from PyQt5.QtCore import Qt, QDate, QSize
from PyQt5.QtGui import QPalette, QColor, QIcon
import sys


class TaskDetailsDialog(QDialog):
    def __init__(self, task_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Détails de la tâche")
        self.setGeometry(150, 150, 400, 300)

        layout = QVBoxLayout()

        # Affichage des détails de la tâche
        self.label_nom = QLabel(f"Nom de la tâche : {task_data['nom']}")
        self.label_date = QLabel(f"Date : {task_data['date']}")
        self.label_categorie = QLabel(f"Catégorie : {task_data['categorie']}")
        self.label_statut = QLabel(f"Statut : {task_data['statut']}")
        self.label_priorite = QLabel(f"Priorité : {task_data['priorite']}")

        self.description_label = QLabel("Description :")
        self.description_text = QTextEdit()

        # Utilisation de HTML pour rendre les liens cliquables
        html_description = task_data['description']

        # Ici, vous pouvez détecter les liens et les convertir en balises HTML
        html_description = self.convert_links_to_html(html_description)

        self.description_text.setHtml(html_description)
        self.description_text.setReadOnly(True)  # Pour ne pas pouvoir modifier la description

        # Ajouter les widgets au layout
        layout.addWidget(self.label_nom)
        layout.addWidget(self.label_date)
        layout.addWidget(self.label_categorie)
        layout.addWidget(self.label_statut)
        layout.addWidget(self.label_priorite)
        layout.addWidget(self.description_label)
        layout.addWidget(self.description_text)

        # Boutons OK
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def convert_links_to_html(self, text):
        # Recherche de tous les liens dans la description et les transforme en liens HTML cliquables
        import re
        url_pattern = r'(https?://[^\s]+)'
        links = re.findall(url_pattern, text)

        for link in links:
            # Remplacer les liens par des balises HTML <a>
            text = text.replace(link, f'<a href="{link}" style="color: blue; text-decoration: underline;">{link}</a>')

        return text

class FormulaireTache(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Formulaire de Tâche")
        self.setGeometry(100, 100, 300, 300)

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
        priorite = self.champ_priorite.currentText()
        statut = self.champ_statut.currentText()

        # Vérifier que les champs obligatoires sont remplis
        if not nom_tache:
            QMessageBox.warning(self, "Erreur", "Le nom de la tâche est obligatoire.")
            return

        # Ajouter la tâche à la liste principale
        self.parent.add_task_to_tree(nom_tache, date, description, categorie, statut, priorite)
        self.close()

    def reset_form(self):
        """Réinitialiser les champs du formulaire"""
        self.champ_nom.clear()
        self.champ_description.clear()
        self.champ_date.setDate(QDate.currentDate())  # Réinitialiser la date à aujourd'hui
        self.champ_categorie.setCurrentIndex(0)  # Réinitialiser à la première catégorie
        self.champ_statut.setCurrentIndex(0)  # Réinitialiser au statut "À faire"
        self.champ_priorite.setCurrentIndex(0)  # Réinitialiser à la priorité "Basse"

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

        self.main_layout.addLayout(nav_layout)

        # Arborescence des tâches
        self.task_tree = QTreeWidget()
        self.task_tree.setHeaderLabels(["Tâches", "Échéance", "Description", "Catégorie", "Statut", "Priorité"])
        self.main_layout.addWidget(self.task_tree)

        # Connecter l'événement de clic sur une tâche
        self.task_tree.itemClicked.connect(self.show_task_details)
        self.main_layout.addWidget(self.task_tree)
        main_layout.addWidget(self.main_widget)

        # Définir le widget central pour QMainWindow
        self.setCentralWidget(central_widget)

        # Liste temporaire pour stocker les tâches
        self.tasks = []
        self.formulaire_window = None
        self.is_dark_mode = False

    def show_task_details(self, item, column):
        # Extraire les données de la tâche
        task_data = {
            'nom': item.text(0),
            'date': item.text(1),
            'description': item.text(2),
            'categorie': item.text(3),
            'statut': item.text(4),
            'priorite': item.text(5),
        }

        # Ouvrir une fenêtre pour afficher les détails
        dialog = TaskDetailsDialog(task_data, self)
        dialog.exec_()

    def toggle_sidebar(self):
        # Bascule de la visibilité de la colonne latérale
        self.sidebar.setVisible(not self.sidebar.isVisible())

    def open_formulaire(self):
        if self.formulaire_window is None:
            self.formulaire_window = FormulaireTache(parent=self)
        self.formulaire_window.show()
        # Réinitialiser les champs du formulaire avant de l'afficher
        self.formulaire_window.reset_form()

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