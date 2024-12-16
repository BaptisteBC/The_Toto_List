import sys

import pymysql

from PyQt5.QtCore import QCoreApplication, Qt, QDate
from PyQt5.QtWidgets import QWidget, QGridLayout, QApplication, QLabel, QPushButton, \
    QListWidget, QLayout, QHBoxLayout, QListWidgetItem, QDialog, QFormLayout, QLineEdit, QDateTimeEdit, QCheckBox, \
    QComboBox, QDialogButtonBox, QDateEdit, QMessageBox


def tache_cliquee():
    print("ça fonctionne !")



class Principal(QWidget):
    """Fenêtre principale d'affichage des tâches.
    Prends en argument les infos de connexion à la BDD"""

    def __init__(self, host:str='127.0.0.1', user:str='root', password='toto', database:str='thetotodb'):
        super().__init__()

        self.setWindowTitle("Page Prinicpale")

        grid = QGridLayout()
        self.setLayout(grid)
        self.resize(500, 550)

        self.titre = QLabel("Mes tâches")
        self.bouton_actualiser = QPushButton("Actualiser")
        self.taches = QListWidget()
        self.bouton_quitter = QPushButton("Quitter")

        grid.addWidget(self.titre)
        grid.addWidget(self.bouton_actualiser)
        grid.addWidget(self.taches)
        grid.addWidget(self.bouton_quitter)

        self.bouton_actualiser.clicked.connect(self.actualiser)
        self.bouton_quitter.clicked.connect(self.quitter)

        self.cnx = pymysql.connect(host=host, user=user, password=password, database=database)

        self.actualiser()

    def actualiser(self):
        """Fonction d'actualisation des tâches.
        Lorsque le bouton est cliqué, effectue une requête dans la table tâche et récupère le champ 'titre_tache' pour \
        l'afficher dans la fenêtre principale."""

        curseur = self.cnx.cursor()

        # Extraction de tous les titres des taches principales
        curseur.execute("SELECT id_tache, titre_tache, datesuppression_tache FROM taches;")
        resultache = curseur.fetchall()

        # Extraction de tous les titres des sous taches
        curseur.execute("SELECT id_soustache, titre_soustache, soustache_id_tache FROM soustaches;")
        sousresultache = curseur.fetchall()

        self.taches.clear()

        for id_tache, titre_tache, datesuppression_tache in resultache:
            if datesuppression_tache :
                pass
            else:
                self.afficherTache(id_tache, titre_tache)

                for id_soustache, titre_soustache, soustache_id_tache in sousresultache:
                    if soustache_id_tache == id_tache :
                        self.afficherTache(id_soustache, f'|=>{titre_soustache}', soustache_id_tache)

        curseur.close()

    def afficherTache(self, id_tache, titre_tache, soustache_id_tache=None):
        item = QListWidgetItem()
        tache = QWidget()

        bouton = QPushButton(titre_tache)
        suppr = QPushButton('X')
        suppr.setFixedWidth(30)

        layout = QHBoxLayout(tache)
        layout.addWidget(bouton)
        layout.addWidget(suppr)
        layout.addStretch()

        bouton.clicked.connect(lambda: self.detail(id_tache, soustache_id_tache))
        suppr.clicked.connect(lambda : self.supprimer(id_tache, soustache_id_tache))

        item.setSizeHint(tache.sizeHint())

        self.taches.addItem(item)
        self.taches.setItemWidget(item, tache)

    def detail(self, id_tache, soustache_id_tache):
        curseur = self.cnx.cursor()

        if soustache_id_tache:
            curseur.execute("SELECT titre_soustache, description_soustache, datecreation_soustache, "
                            "datefin_soustache, statut_soustache, daterappel_soustache FROM soustaches;")
        else:
            curseur.execute("SELECT titre_tache, description_tache, datecreation_tache, datefin_tache,  "
                            "recurrence_tache, statut_tache, daterappel_tache, datesuppression_tache FROM taches;")

        curseur.close()

    def supprimer(self, id_tache, soustache_id_tache):
        if not soustache_id_tache: #Tache
            Supprimer(id_tache, self.cnx).exec()
            self.actualiser()

        else: #Sous-tache
            print(f'Sous tache')

    def quitter(self):
        self.cnx.close()
        QCoreApplication.exit(0)

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