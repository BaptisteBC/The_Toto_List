import sys
import pymysql
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QApplication, QLabel, QPushButton,
    QListWidget, QHBoxLayout, QListWidgetItem, QDialog
)


class Principal(QWidget):
    """
    Interface principale de gestion des tâches.
    Cette classe interagit avec GestionTemp pour gérer les rappels et les tâches proches de l'échéance.
    """

    def __init__(self, host: str = '127.0.0.1', user: str = 'root', password='toto', database: str = 'thetotodb'):
        super().__init__()

        self.setWindowTitle("Page Principale")

        grid = QGridLayout()
        self.setLayout(grid)
        self.resize(500, 550)

        self.titre = QLabel("Mes tâches")
        self.taches = QListWidget()
        self.bouton_quitter = QPushButton("Quitter")
        self.bouton_actualiser = QPushButton("Actualiser")

        grid.addWidget(self.titre)
        grid.addWidget(self.bouton_actualiser)
        grid.addWidget(self.taches)
        grid.addWidget(self.bouton_quitter)

        self.bouton_quitter.clicked.connect(self.quitter)
        self.bouton_actualiser.clicked.connect(self.actualiser)

        self.host = host
        self.user = user
        self.password = password
        self.database = database


        self.actualiser()  # Mise à jour initiale

    def actualiser(self):
        """
        Récupérer les tâches et sous-tâches, appliquer les rappels et gestion des échéances.
        """
        curseur = self.cnx.cursor()

        # Récupération des tâches principales
        curseur.execute("SELECT id_tache, titre_tache FROM taches WHERE datesuppression_tache IS NULL;")
        resultache = curseur.fetchall()

        # Récupération des sous-tâches
        curseur.execute(
            "SELECT id_soustache, titre_soustache, soustache_id_tache FROM soustaches WHERE datesuppression_soustache IS NULL;")
        sousresultache = curseur.fetchall()

        self.taches.clear()

        # Obtenez les tâches nécessitant des rappels et celles proches de leur échéance
        taches_rappel = self.gestion_temps.get_taches_pour_rappel()
        taches_presque_terminees = self.gestion_temps.get_taches_presque_terminees()

        curseur.close()

        # Affichez toutes les tâches tout en attribuant des couleurs aux boutons
        for id_tache, titre_tache in resultache:
            color = None
            if id_tache in taches_rappel:
                color = "yellow"  # Couleur jaune : tâche nécessite un rappel
            elif id_tache in taches_presque_terminees:
                color = "red"  # Couleur rouge : tâche proche de son échéance

            self.afficherTache(id_tache, titre_tache, color=color)

            # Affichez les sous-tâches associées
            for id_soustache, titre_soustache, soustache_id_tache in sousresultache:
                if soustache_id_tache == id_tache:
                    self.afficherTache(id_soustache, titre_soustache, soustache_id_tache, color)

    def afficherTache(self, id_tache, titre_tache, soustache_id_tache=None, color=None):
        """
        Affiche une tâche dans le GUI avec une couleur (optionnelle).
        """
        item = QListWidgetItem()
        tache = QWidget()

        detail = QPushButton(titre_tache)
        suppr = QPushButton('X')
        suppr.setFixedWidth(30)

        # Appliquez une couleur au bouton, si spécifié
        if color:
            detail.setStyleSheet(f"background-color: {color}")

        layout = QHBoxLayout(tache)
        layout.addWidget(detail)
        layout.addWidget(suppr)
        layout.addStretch()

        detail.clicked.connect(lambda: self.detail(id_tache, soustache_id_tache))
        suppr.clicked.connect(lambda: self.supprimer(id_tache, soustache_id_tache))

        item.setSizeHint(tache.sizeHint())

        self.taches.addItem(item)
        self.taches.setItemWidget(item, tache)

    def detail(self, id_tache, soustache_id_tache):
        """
        Affiche les détails d'une tâche ou sous-tâche.
        """
        curseur = self.cnx.cursor()
        if soustache_id_tache:
            curseur.execute(f'SELECT titre_soustache, description_soustache, datecreation_soustache, '
                            f'datefin_soustache, statut_soustache, daterappel_soustache FROM soustaches '
                            f'WHERE id_soustache = {id_tache};')
            soustache = curseur.fetchall()
            curseur.execute(f'SELECT titre_tache FROM taches WHERE id_tache = {soustache_id_tache};')
            tache_parent = curseur.fetchone()

            for (titre_soustache, description_soustache, datecreation_soustache, datefin_soustache, statut_soustache,
                 daterappel_soustache) in soustache:
                Detail(titre_soustache, description_soustache, datecreation_soustache, datefin_soustache,
                       statut_soustache, daterappel_soustache, soustache_id_tache, tache_parent[0]).exec()

        else:
            curseur.execute(f'SELECT titre_tache, description_tache, datecreation_tache, '
                            f'datefin_tache, statut_tache, daterappel_tache FROM taches '
                            f'WHERE id_tache = {id_tache};')
            tache = curseur.fetchall()

            for (titre_tache, description_tache, datecreation_tache, datefin_tache, statut_tache,
                 daterappel_tache) in tache:
                Detail(titre_tache, description_tache, datecreation_tache, datefin_tache,
                       statut_tache, daterappel_tache).exec()

        curseur.close()

    def quitter(self):
        """
        Quitte l'application.
        """
        self.cnx.close()
        QCoreApplication.exit()


class Detail(QDialog):
    """
    Fenêtre de détails d'une tâche.
    """

    def __init__(self, titre, description, datecreation, datefin, statut, daterappel, soustache_id_tache=None,
                 tache_parent=None):
        super().__init__()

        self.setWindowTitle("Détail")

        grid = QGridLayout()
        self.setLayout(grid)
        self.resize(300, 250)

        self.titre = QLabel(f'Titre : {titre}')
        self.description = QLabel(f'Description : {description}')
        self.datecreation = QLabel(f'Date de création : {datecreation}')
        self.datefin = QLabel(f'Date de fin : {datefin}')

        if statut == 1:
            self.statut = QLabel("Statut : En cours")
        else:
            self.statut = QLabel("Statut : Terminée")

        self.daterappel = QLabel(f'Date de rappel : {daterappel}')
        self.confirmer = QPushButton("OK")

        grid.addWidget(self.titre)
        if soustache_id_tache:
            self.tache_parent = QLabel(f'Tache parent : {tache_parent}')
            grid.addWidget(self.tache_parent)
        grid.addWidget(self.statut)
        grid.addWidget(self.description)
        grid.addWidget(self.datecreation)
        grid.addWidget(self.datefin)
        grid.addWidget(self.daterappel)
        grid.addWidget(self.confirmer)

        self.confirmer.clicked.connect(self.stop)

    def stop(self):
        """
        Fermer la fenêtre.
        """
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    principal = Principal()
    principal.show()
    sys.exit(app.exec())
