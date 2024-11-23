import sys
import pymysql.cursors
import pymysql
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QComboBox, QDateEdit, QVBoxLayout, QPushButton, QMessageBox)
from PyQt5.QtCore import QDate
from datetime import datetime

# Fonction pour créer une connexion avec la base de données MySQL
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
        # Création de la connexion à la base de données
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

# Fonction pour insérer une tâche dans la base de données
def inserer_tache(connexion, titre, description, date_creation, date_echeance, type_recurrence, statut, id_groupe,
                  id_utilisateur, id_liste, id_tag, date_rappel=None):
    """Insère une nouvelle tâche dans la base de données, selon le format requis."""

    try:
        with connexion.cursor() as curseur:
            # Nouvelle requête d'insertion avec les noms de colonnes mis à jour
            requete_insertion = f"""
            INSERT INTO taches (id_tache, taches_id_groupe, taches_id_utilisateur, taches_id_liste, 
                titre_tache, description_tache, datecreation_tache, datefin_tache, recurrence_tache, 
                statut_tache, daterappel_tache, datesuppression_tache) 
            VALUES (NULL, NULL, {id_utilisateur}, '{id_liste}', '{titre}', '{description}', 
                CURRENT_TIMESTAMP, '{date_echeance}', '', '{statut}', {date_rappel if date_rappel else 'NULL'}, NULL);
            """
            curseur.execute(requete_insertion)  # Exécution de la requête
            connexion.commit()  # Validation de l'insertion
            print(f"Tâche '{titre}' ajoutée avec succès.")
    except pymysql.MySQLError as e:
        print(f"Erreur lors de l'insertion de la tâche : {e}")

# Fonction pour valider si une date est au format 'AAAA-MM-JJ'
def valider_date(date_str):
    """Valide que la date est au format AAAA-MM-JJ.

    Parameters:
        date_str (str): La date sous forme de chaîne.

    Returns:
        bool: True si la date est valide, sinon False.
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")  # Tentative de conversion de la chaîne en datetime
        return True
    except ValueError:
        return False

# Fonction pour obtenir les utilisateurs à partir de la base de données
def obtenir_utilisateurs(connexion):
    """Récupère les utilisateurs depuis la base de données.

    Parameters:
        connexion (pymysql.Connection): L'objet de connexion à la base de données.

    Returns:
        list of tuple: Liste de tuples contenant l'ID et le nom des utilisateurs.
    """
    try:
        with connexion.cursor() as curseur:
            curseur.execute("SELECT idUtilisateur, pseudonyme FROM utilisateurs;")  # Requête pour obtenir les utilisateurs
            return curseur.fetchall()  # Retourne tous les résultats
    except pymysql.MySQLError as e:
        print(f"Erreur lors de la récupération des utilisateurs : {e}")
        return []

# Fonction pour obtenir les groupes à partir de la base de données
def obtenir_groupes(connexion):
    """Récupère les groupes depuis la base de données.

    Parameters:
        connexion (pymysql.Connection): L'objet de connexion à la base de données.

    Returns:
        list of tuple: Liste de tuples contenant l'ID et le nom des groupes.
    """
    try:
        with connexion.cursor() as curseur:
            curseur.execute("SELECT idGroupeAffecte, nom FROM groupes;")  # Requête pour obtenir les groupes
            return curseur.fetchall()  # Retourne tous les résultats
    except pymysql.MySQLError as e:
        print(f"Erreur lors de la récupération des groupes : {e}")
        return []

# Fonction pour obtenir les listes à partir de la base de données
def obtenir_listes(connexion):
    """Récupère les listes depuis la base de données.

    Parameters:
        connexion (pymysql.Connection): L'objet de connexion à la base de données.

    Returns:
        list of tuple: Liste de tuples contenant l'ID et le nom des listes.
    """
    try:
        with connexion.cursor() as curseur:
            curseur.execute("SELECT idListe, nom FROM listes;")  # Requête pour obtenir les listes
            return curseur.fetchall()  # Retourne tous les résultats
    except pymysql.MySQLError as e:
        print(f"Erreur lors de la récupération des listes : {e}")
        return []

# Fonction pour obtenir les tags à partir de la base de données
def obtenir_tags(connexion):
    """Récupère les tags depuis la base de données.

    Parameters:
        connexion (pymysql.Connection): L'objet de connexion à la base de données.

    Returns:
        list of tuple: Liste de tuples contenant l'ID et le nom des tags.
    """
    try:
        with connexion.cursor() as curseur:
            curseur.execute("SELECT idTag, nomTag FROM tag;")  # Requête pour obtenir les tags
            return curseur.fetchall()  # Retourne tous les résultats
    except pymysql.MySQLError as e:
        print(f"Erreur lors de la récupération des tags : {e}")
        return []

# Classe représentant le formulaire de création de tâche dans l'interface graphique
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

        # Layout principal pour organiser les widgets
        layout = QVBoxLayout()

        # Ajout des champs de saisie pour la tâche
        self.label_nom = QLabel("Nom de la tâche :")
        self.champ_nom = QLineEdit()
        layout.addWidget(self.label_nom)
        layout.addWidget(self.champ_nom)

        # Champ pour la description
        self.label_description = QLabel("Description :")
        self.champ_description = QTextEdit()
        layout.addWidget(self.label_description)
        layout.addWidget(self.champ_description)

        # Champ pour la date d'échéance
        self.label_date = QLabel("Date d'échéance :")
        self.champ_date = QDateEdit()
        self.champ_date.setDate(QDate.currentDate())  # La date par défaut est la date actuelle
        layout.addWidget(self.label_date)
        layout.addWidget(self.champ_date)

        # Choix du statut de la tâche
        self.label_statut = QLabel("Statut de la tâche :")
        self.champ_statut = QComboBox()
        self.champ_statut.addItems(["à faire", "en cours", "terminé"])  # Statuts disponibles
        layout.addWidget(self.label_statut)
        layout.addWidget(self.champ_statut)

        # Sélection du groupe affecté
        self.label_groupe_affecte = QLabel("Groupe Affecté :")
        self.champ_groupe_affecte = QComboBox()
        for groupe in self.groupes:
            self.champ_groupe_affecte.addItem(groupe[1], groupe[0])  # Ajouter le groupe au combobox
        layout.addWidget(self.label_groupe_affecte)
        layout.addWidget(self.champ_groupe_affecte)

        # Sélection de l'utilisateur affecté
        self.label_utilisateur_affecte = QLabel("Utilisateur Affecté :")
        self.champ_utilisateur_affecte = QComboBox()
        for utilisateur in self.utilisateurs:
            self.champ_utilisateur_affecte.addItem(utilisateur[1], utilisateur[0])  # Ajouter l'utilisateur
        layout.addWidget(self.label_utilisateur_affecte)
        layout.addWidget(self.champ_utilisateur_affecte)

        # Sélection de la liste
        self.label_liste = QLabel("Liste :")
        self.champ_liste = QComboBox()
        for liste in self.listes:
            self.champ_liste.addItem(liste[1], liste[0])  # Ajouter la liste
        layout.addWidget(self.label_liste)
        layout.addWidget(self.champ_liste)

        # Sélection des tags
        self.label_tag = QLabel("Tag :")
        self.champ_tag = QComboBox()
        for tag in self.tags:
            self.champ_tag.addItem(tag[1], tag[0])  # Ajouter le tag
        layout.addWidget(self.label_tag)
        layout.addWidget(self.champ_tag)

        # Bouton de soumission
        self.bouton_submit = QPushButton("Soumettre")
        self.bouton_submit.clicked.connect(self.on_submit)  # Connexion de l'action du bouton à la fonction on_submit
        layout.addWidget(self.bouton_submit)

        # Définir le layout du formulaire
        self.setLayout(layout)

    def on_submit(self):
        """Valide et soumet les données du formulaire pour insertion dans la base de données."""
        titre = self.champ_nom.text()
        description = self.champ_description.toPlainText()
        date_echeance = self.champ_date.date().toString("yyyy-MM-dd")
        statut = self.champ_statut.currentText()
        id_groupe = self.champ_groupe_affecte.currentData()
        id_utilisateur = self.champ_utilisateur_affecte.currentData()
        id_liste = self.champ_liste.currentData()
        id_tag = self.champ_tag.currentData()
        date_rappel = None  # Pour cet exemple, la date de rappel est laissée vide (à gérer par l'utilisateur si besoin)

        # Vérification de la validité des données
        if not titre or not description:
            QMessageBox.warning(self, "Erreur", "Tous les champs obligatoires doivent être remplis.")
            return

        if not valider_date(date_echeance):
            QMessageBox.warning(self, "Erreur", "La date d'échéance est invalide.")
            return

        # Insérer la tâche dans la base de données
        inserer_tache(self.connexion, titre, description, datetime.now(), date_echeance, "", statut, id_groupe,
                      id_utilisateur, id_liste, id_tag, date_rappel)

        QMessageBox.information(self, "Succès", "Tâche ajoutée avec succès!")

# Point d'entrée de l'application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = FormulaireTache()  # Crée l'instance du formulaire
    form.show()  # Affiche le formulaire
    sys.exit(app.exec_())  # Démarre l'application
