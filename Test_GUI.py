from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QDateEdit, QMessageBox, QTreeWidgetItem, QTreeWidget, QMenu
)
from PyQt6.QtCore import Qt
import sys
from datetime import datetime


class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Paramètres")
        self.setGeometry(150, 150, 300, 200)

        # Layout pour les paramètres
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Réglages de l'application"))
        layout.addWidget(QLabel("Ici, vous pouvez configurer vos préférences."))

        # Bouton pour fermer la fenêtre de paramètres
        close_button = QPushButton("Fermer")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)


class HelpWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aide")
        self.setGeometry(150, 150, 400, 300)

        # Layout pour l'aide
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Aide de l'application"))
        layout.addWidget(QLabel(
            "Bienvenue dans l'aide de l'application To-Do List.\n\n"
            "Voici quelques instructions pour utiliser l'application :\n"
            "- Pour ajouter une tâche, utilisez le champ de saisie et cliquez sur 'Ajouter Tâche'.\n"
            "- Pour ajouter une sous-tâche, faites un clic droit sur une tâche et sélectionnez 'Ajouter Sous-Tâche'.\n"
            "- Pour supprimer ou modifier une tâche, sélectionnez-la et utilisez les boutons correspondants.\n"
            "- Utilisez les boutons de navigation en haut pour accéder à différents menus."
        ))

        # Bouton pour fermer la fenêtre de paramètres
        close_button = QPushButton("Fermer")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)

class CreditsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aide")
        self.setGeometry(150, 150, 400, 300)

        # Layout pour l'aide
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Crédits de l'application"))
        layout.addWidget(QLabel(
            "Bienvenue dans l'aide de l'application To-Do List.\n\n"
            "Voici quelques instructions pour utiliser l'application :\n"
            "- Pour ajouter une tâche, utilisez le champ de saisie et cliquez sur 'Ajouter Tâche'.\n"
            "- Pour ajouter une sous-tâche, faites un clic droit sur une tâche et sélectionnez 'Ajouter Sous-Tâche'.\n"
            "- Pour supprimer ou modifier une tâche, sélectionnez-la et utilisez les boutons correspondants.\n"
            "- Utilisez les boutons de navigation en haut pour accéder à différents menus."
        ))

        # Bouton pour fermer la fenêtre de paramètres
        close_button = QPushButton("Fermer")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)
        
class TodoListApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("To-Do List Application")
        self.setGeometry(100, 100, 800, 400)

        # Initialiser la variable pour la fenêtre de paramètres
        self.settings_window = None
        self.help_window = None
        self.credits_window = None

        # Layout principal
        main_layout = QVBoxLayout()  # Utiliser un QVBoxLayout pour le layout principal

        # Barre de navigation
        nav_layout = QHBoxLayout()

        self.login_button = QPushButton("Connexion")
        self.offline_button = QPushButton("Hors Ligne")
        self.home_button = QPushButton("Accueil")
        self.dashboard_button = QPushButton("Tableau de Bord")
        self.settings_button = QPushButton("Paramètres")
        self.help_button = QPushButton("Aide")
        self.credits_button = QPushButton("Crédits")

        # Connecter les boutons à la méthode d'ouverture
        self.settings_button.clicked.connect(self.open_settings)
        self.help_button.clicked.connect(self.open_help)
        self.credits_button.clicked.connect(self.open_credits)

        # Ajouter les boutons à la barre de navigation
        nav_layout.addWidget(self.login_button)
        nav_layout.addWidget(self.offline_button)
        nav_layout.addWidget(self.home_button)
        nav_layout.addWidget(self.dashboard_button)
        nav_layout.addWidget(self.settings_button)
        nav_layout.addWidget(self.help_button)
        nav_layout.addWidget(self.credits_button)

        # Ajouter la barre de navigation au layout principal
        main_layout.addLayout(nav_layout)

        # Arborescence des tâches
        self.task_tree = QTreeWidget()
        self.task_tree.setHeaderLabels(["Tâches"])
        self.task_tree.setMinimumWidth(300)

        # Connecter le clic droit pour le menu contextuel
        self.task_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.task_tree.customContextMenuRequested.connect(self.show_context_menu)

        # Formulaire pour ajouter une tâche
        self.task_label = QLabel("Nouvelle Tâche:")
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Ajouter une nouvelle tâche...")

        self.due_date_input = QDateEdit()
        self.due_date_input.setDate(datetime.now())

        self.add_task_button = QPushButton("Ajouter Tâche")
        self.add_task_button.clicked.connect(self.add_task)

        # Layout pour les éléments de tâche
        task_layout = QVBoxLayout()
        task_layout.addWidget(self.task_label)
        task_layout.addWidget(self.task_input)
        task_layout.addWidget(QLabel("Date d'Échéance:"))
        task_layout.addWidget(self.due_date_input)
        task_layout.addWidget(self.add_task_button)

        # Ajouter les éléments au layout principal
        main_layout.addWidget(self.task_tree)  # Placer l'arborescence des tâches à gauche
        main_layout.addLayout(task_layout)

        # Configuration des boutons pour supprimer et modifier
        delete_task_button = QPushButton("Supprimer Tâche")
        delete_task_button.clicked.connect(self.delete_task)

        modify_task_button = QPushButton("Modifier Tâche")
        modify_task_button.clicked.connect(self.modify_task)

        # Ajouter les boutons de modification et suppression
        main_layout.addWidget(delete_task_button)
        main_layout.addWidget(modify_task_button)

        # Appliquer le layout à la fenêtre
        self.setLayout(main_layout)

        # État de l'application
        self.is_subtask_mode = False  # Indicateur pour savoir si nous sommes en mode sous-tâche

    def open_settings(self):
        # Ouvrir la fenêtre des paramètres si elle n'est pas déjà ouverte
        if self.settings_window is None:
            self.settings_window = SettingsWindow()
        self.settings_window.show()

    def open_credits(self):
        # Ouvrir la fenêtre des paramètres si elle n'est pas déjà ouverte
        if self.credits_window is None:
            self.credits_window = CreditsWindow()
        self.credits_window.show()

    def open_help(self):
        # Ouvrir la fenêtre d'aide si elle n'est pas déjà ouverte
        if self.help_window is None:
            self.help_window = HelpWindow()
        self.help_window.show()

    def add_task(self):
        task_text = self.task_input.text()
        due_date = self.due_date_input.date().toString("dd/MM/yyyy")

        if task_text:
            selected_items = self.task_tree.selectedItems()
            if self.is_subtask_mode and selected_items:
                # Si nous sommes en mode sous-tâche, ajouter comme sous-tâche
                parent_item = selected_items[0]
                subtask_item = QTreeWidgetItem(parent_item)
                subtask_item.setText(0, f"{task_text} (Échéance: {due_date})")
            else:
                # Sinon, ajouter comme tâche principale
                task_item = QTreeWidgetItem(self.task_tree)
                task_item.setText(0, f"{task_text} (Échéance: {due_date})")
                self.task_tree.addTopLevelItem(task_item)

            self.task_input.clear()  # Réinitialiser le champ d'entrée
            self.reset_task_input()  # Réinitialiser le label et le mode
        else:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer une tâche.")

    def delete_task(self):
        selected_items = self.task_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une tâche à supprimer.")
            return
        for item in selected_items:
            index = self.task_tree.indexOfTopLevelItem(item)
            if index != -1:  # Si c'est une tâche principale
                self.task_tree.takeTopLevelItem(index)
            else:  # Si c'est une sous-tâche
                parent_item = item.parent()
                if parent_item:
                    parent_item.removeChild(item)

    def modify_task(self):
        selected_items = self.task_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une tâche à modifier.")
            return
        for item in selected_items:
            new_task_text = self.task_input.text()
            if new_task_text:
                due_date = self.due_date_input.date().toString("dd/MM/yyyy")
                item.setText(0, f"{new_task_text} (Échéance: {due_date})")
                self.task_input.clear()
                self.reset_task_input()  # Réinitialiser le label et le mode
            else:
                QMessageBox.warning(self, "Erreur", "Veuillez entrer une nouvelle tâche.")

    def show_context_menu(self, position):
        context_menu = QMenu(self)
        add_subtask_action = context_menu.addAction("Ajouter Sous-Tâche")
        action = context_menu.exec(self.task_tree.viewport().mapToGlobal(position))

        if action == add_subtask_action:
            self.prepare_for_subtask()

    def prepare_for_subtask(self):
        selected_items = self.task_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une tâche pour ajouter une sous-tâche.")
            return

        # Changer le texte de l'entrée pour indiquer l'ajout d'une sous-tâche
        self.is_subtask_mode = True  # Activer le mode sous-tâche
        self.task_label.setText("Ajouter Sous-Tâche:")
        self.task_input.clear()  # Effacer le texte de l'entrée pour permettre une nouvelle saisie
        self.task_input.setFocus()  # Mettre le focus sur le champ de saisie

    def reset_task_input(self):
        self.task_input.clear()
        self.task_label.setText("Nouvelle Tâche:")
        self.is_subtask_mode = False  # Réinitialiser le mode sous-tâche


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TodoListApp()
    window.show()
    sys.exit(app.exec())
