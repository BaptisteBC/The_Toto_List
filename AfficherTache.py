import sys

import pymysql
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QWidget, QGridLayout, QApplication, QLabel, QPushButton, \
    QListWidget, QHBoxLayout, QListWidgetItem, QDialog, QDateTimeEdit, QDateEdit


class Principal(QWidget):
    """
    Client d'affichage principal qui contient les fonctions principales d'affichage des tâches


    """
    def __init__(self, host:str='127.0.0.1', user:str='root', password='toto', database:str='thetotodb'):
        super().__init__()

        self.setWindowTitle("Page Prinicpale")

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

        self.actualiser()

    def actualiser(self):
        """Fonction d'actualisation des tâches.
        Lorsue le bouton est cliqué, effectue une requête dans la table tâche et récupère le champ 'titre_tache' pour \
        l'afficher dans la fenêtre principale."""

        self.cnx = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database)
        curseur = self.cnx.cursor()

        # Extraction de tous les titres des taches principales
        curseur.execute("SELECT id_tache, titre_tache FROM taches;")
        resultache = curseur.fetchall()

        # Extraction de tous les titres des sous taches
        curseur.execute("SELECT id_soustache, titre_soustache, soustache_id_tache FROM soustaches;")
        sousresultache = curseur.fetchall()

        curseur.close()

        self.taches.clear()

        for id_tache, titre_tache in resultache:

            self.afficherTache(id_tache, titre_tache)

            for id_soustache, titre_soustache, soustache_id_tache in sousresultache:
                if soustache_id_tache == id_tache :
                    self.afficherTache(id_soustache, titre_soustache, soustache_id_tache)

    def afficherTache(self, id_tache, titre_tache, soustache_id_tache=None):
        item = QListWidgetItem()
        tache = QWidget()

        detail = QPushButton(titre_tache)
        suppr = QPushButton('X')
        suppr.setFixedWidth(30)

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
        self.cnx.close()
        QCoreApplication.exit()

class Detail(QDialog):
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
       self.close()


class Supprimer(QDialog):
    def __init__(self, id_tache, cnx):
        super().__init__()

        self.setWindowTitle("Supprimer")

        grid = QGridLayout()
        self.setLayout(grid)
        self.resize(300, 350)

        self.titre = QLabel("Supprimer la tâche")
        self.confirmer = QPushButton("Confirmer")

        grid.addWidget(self.titre)
        grid.addWidget(self.confirmer)

        self.id_tache:str = id_tache
        self.cnx = cnx

        self.confirmer.clicked.connect(self.conf)

    def conf(self):
        try :
            curseur = self.cnx.cursor()
            curseur.execute(f'UPDATE taches SET datesuppression_tache = NOW() WHERE id_tache = "{self.id_tache}";')
            self.cnx.commit()
            curseur.close()
            self.close()
        except Exception as E:
            print(E)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    principal = Principal()
    principal.show()
    app.exec()