import sys
import pymysql.cursors
import pymysql
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QComboBox, QDateEdit, QVBoxLayout, QPushButton, QMessageBox)
from PyQt5.QtCore import QDate
from datetime import datetime

def creer_connexion_mysql(hote, utilisateur, mot_de_passe, nom_bd, port=3306):
    """Crée et retourne une connexion à la base de données MySQL.

    Parameters:
        hote (str): L'adresse de l'hôte de la base de données MySQL.
        utilisateur (str): Le nom d'utilisateur pour la connexion MySQL.
        mot_de_passe (str): Le mot de passe pour la connexion MySQL.
        nom_bd (str): Le nom de la base de données cible.
        port (int): Le port de la base de données (par défaut: 3306).

    Returns:
        connexion (pymysql.Connection): L'objet de connexion à la base de données MySQL.
    """
    try:
        connexion = pymysql.connect(
            host=hote,
            user=utilisateur,
            password=mot_de_passe,
            database=nom_bd,
            port=port
        )
        print("Connexion à la base de données réussie")
        return connexion
    except pymysql.MySQLError as e:
        print(f"Erreur lors de la connexion à MySQL : {e}")
        return None

def inserer_tache(connexion, titre, description, date_creation, date_echeance, type_recurrence, validation, id_groupe,
                  id_utilisateur, id_liste, id_tag, date_rappel=None):
    """Insère une nouvelle tâche dans la base de données.

    Parameters:
        connexion (pymysql.Connection): L'objet de connexion à la base de données.
        titre (str): Le titre de la tâche.
        description (str): La description de la tâche.
        date_creation (datetime): La date de création de la tâche.
        date_echeance (str): La date d'échéance de la tâche.
        type_recurrence (str): Type de récurrence de la tâche.
        validation (int): Statut de validation de la tâche (0 ou 1).
        id_groupe (int): ID du groupe auquel la tâche est affectée.
        id_utilisateur (int): ID de l'utilisateur affecté à la tâche.
        id_liste (int): ID de la liste dans laquelle se trouve la tâche.
        id_tag (int): ID du tag associé à la tâche.
        date_rappel (str): Date de rappel pour la tâche, optionnelle.

    """
    try:
        with connexion.cursor() as curseur:
            requete_insertion = """
            INSERT INTO taches (titre, description, dateCreation, dateFin, typeRecurence, validation, idGroupeAffecte, idUtilisateurAffecte, idListe, idTag, dateRappel)
            VALUES (%s, %s, CURRENT_TIMESTAMP, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            valeurs = (
                titre, description, date_echeance, type_recurrence, validation, id_groupe, id_utilisateur, id_liste, id_tag, date_rappel
            )
            curseur.execute(requete_insertion, valeurs)
            connexion.commit()
            print(f"Tâche '{titre}' ajoutée avec succès.")
    except pymysql.MySQLError as e:
        print(f"Erreur lors de l'insertion de la tâche : {e}")

def valider_date(date_str):
    """Valide que la date est au format AAAA-MM-JJ.

    Parameters:
        date_str (str): La date sous forme de chaîne.

    Returns:
        bool: True si la date est valide, sinon False.
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def obtenir_utilisateurs(connexion):
    """Récupère les utilisateurs depuis la base de données.

    Parameters:
        connexion (pymysql.Connection): L'objet de connexion à la base de données.

    Returns:
        list of tuple: Liste de tuples contenant l'ID et le nom des utilisateurs.
    """
    try:
        with connexion.cursor() as curseur:
            curseur.execute("SELECT idUtilisateur, pseudonyme FROM utilisateurs;")
            return curseur.fetchall()
    except pymysql.MySQLError as e:
        print(f"Erreur lors de la récupération des utilisateurs : {e}")
        return []

def obtenir_groupes(connexion):
    """Récupère les groupes depuis la base de données.

    Parameters:
        connexion (pymysql.Connection): L'objet de connexion à la base de données.

    Returns:
        list of tuple: Liste de tuples contenant l'ID et le nom des groupes.
    """
    try:
        with connexion.cursor() as curseur:
            curseur.execute("SELECT idGroupeAffecte, nom FROM groupes;")
            return curseur.fetchall()
    except pymysql.MySQLError as e:
        print(f"Erreur lors de la récupération des groupes : {e}")
        return []

def obtenir_listes(connexion):
    """Récupère les listes depuis la base de données.

    Parameters:
        connexion (pymysql.Connection): L'objet de connexion à la base de données.

    Returns:
        list of tuple: Liste de tuples contenant l'ID et le nom des listes.
    """
    try:
        with connexion.cursor() as curseur:
            curseur.execute("SELECT idListe, nom FROM listes;")
            return curseur.fetchall()
    except pymysql.MySQLError as e:
        print(f"Erreur lors de la récupération des listes : {e}")
        return []

def obtenir_tags(connexion):
    """Récupère les tags depuis la base de données.

    Parameters:
        connexion (pymysql.Connection): L'objet de connexion à la base de données.

    Returns:
        list of tuple: Liste de tuples contenant l'ID et le nom des tags.
    """
    try:
        with connexion.cursor() as curseur:
            curseur.execute("SELECT idTag, nomTag FROM tag;")
            return curseur.fetchall()
    except pymysql.MySQLError as e:
        print(f"Erreur lors de la récupération des tags : {e}")
        return []

class FormulaireTache(QWidget):
    """Interface graphique pour le formulaire de création de tâche.

    Attributes:
        connexion (pymysql.Connection): Connexion à la base de données MySQL.
        groupes (list): Liste des groupes.
        listes (list): Liste des listes.
        utilisateurs (list): Liste des utilisateurs.
        tags (list): Liste des tags.
    """

    def __init__(self):
        """Initialise le formulaire, la connexion MySQL et charge les données requises."""
        super().__init__()
        self.setWindowTitle("Formulaire de Tâche")
        self.setGeometry(100, 100, 400, 600)

        # Connexion à la base de données pour récupérer groupes, listes, utilisateurs, et tags
        self.connexion = creer_connexion_mysql("192.168.1.18", "toto", "toto", "thetotodb")

        if self.connexion is None:
            QMessageBox.critical(self, "Erreur", "Impossible de se connecter à la base de données.")
            return

        # Charger les groupes, listes, utilisateurs, et tags dans les combobox
        self.groupes = obtenir_groupes(self.connexion)
        self.listes = obtenir_listes(self.connexion)
        self.utilisateurs = obtenir_utilisateurs(self.connexion)
        self.tags = obtenir_tags(self.connexion)

        layout = QVBoxLayout()

        # Configuration du formulaire
        self.label_nom = QLabel("Nom de la tâche :")
        self.champ_nom = QLineEdit()
        layout.addWidget(self.label_nom)
        layout.addWidget(self.champ_nom)

        # Champ de description
        self.label_description = QLabel("Description :")
        self.champ_description = QTextEdit()
        layout.addWidget(self.label_description)
        layout.addWidget(self.champ_description)

        # Date d'échéance
        self.label_date = QLabel("Date d'échéance :")
        self.champ_date = QDateEdit()
        self.champ_date.setDate(QDate.currentDate())
        layout.addWidget(self.label_date)
        layout.addWidget(self.champ_date)

        # Statut de la tâche
        self.label_statut = QLabel("Statut de la tâche :")
        self.champ_statut = QComboBox()
        self.champ_statut.addItems(["à faire", "en cours", "terminé"])
        layout.addWidget(self.champ_statut)

        # Champs pour groupe, utilisateur, liste et tag
        self.label_groupe_affecte = QLabel("Groupe Affecté :")
        self.champ_groupe_affecte = QComboBox()
        for groupe in self.groupes:
            self.champ_groupe_affecte.addItem(groupe[1], groupe[0])
        layout.addWidget(self.label_groupe_affecte)
        layout.addWidget(self.champ_groupe_affecte)

        self.label_utilisateur_affecte = QLabel("Utilisateur Affecté :")
        self.champ_utilisateur_affecte = QComboBox()
        for utilisateur in self.utilisateurs:
            self.champ_utilisateur_affecte.addItem(utilisateur[1], utilisateur[0])
        layout.addWidget(self.label_utilisateur_affecte)
        layout.addWidget(self.champ_utilisateur_affecte)

        self.label_liste = QLabel("Liste :")
        self.champ_liste = QComboBox()
        for liste in self.listes:
            self.champ_liste.addItem(liste[1], liste[0])
        layout.addWidget(self.label_liste)
        layout.addWidget(self.champ_liste)

        self.label_tag = QLabel("Tag :")
        self.champ_tag = QComboBox()
        for tag in self.tags:
            self.champ_tag.addItem(tag[1], tag[0])
        layout.addWidget(self.label_tag)
        layout.addWidget(self.champ_tag)

        # Bouton pour soumettre
        self.bouton_soumettre = QPushButton("Soumettre")
        self.bouton_soumettre.clicked.connect(self.soumettre_formulaire)
        layout.addWidget(self.bouton_soumettre)

        self.setLayout(layout)

    def soumettre_formulaire(self):
        """Récupère les données saisies et les enregistre dans la base de données."""
        nom_tache = self.champ_nom.text().strip()
        description = self.champ_description.toPlainText().strip()
        date_echeance = self.champ_date.date().toString("yyyy-MM-dd")
        statut = self.champ_statut.currentText().lower()
        id_groupe = self.champ_groupe_affecte.currentData()
        id_utilisateur = self.champ_utilisateur_affecte.currentData()
        id_liste = self.champ_liste.currentData()
        id_tag = self.champ_tag.currentData()

        if not nom_tache or not description or not date_echeance or not statut:
            QMessageBox.warning(self, "Erreur", "Tous les champs sont obligatoires.")
            return

        if self.connexion:
            inserer_tache(self.connexion, nom_tache, description, date_echeance, statut, None, 0, id_groupe,
                          id_utilisateur, id_liste, id_tag)
            QMessageBox.information(self, "Succès", "La tâche a été ajoutée avec succès.")
        else:
            QMessageBox.critical(self, "Erreur", "Impossible de se connecter à la base de données.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    formulaire = FormulaireTache()
    formulaire.show()
    sys.exit(app.exec())
