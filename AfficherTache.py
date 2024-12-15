import sys

import pymysql
from PyQt5.QtCore import QCoreApplication, Qt, QDate
from PyQt5.QtWidgets import QWidget, QGridLayout, QApplication, QLabel, QPushButton, \
    QListWidget, QLayout, QHBoxLayout, QListWidgetItem, QDialog, QFormLayout, QLineEdit, QDateTimeEdit, QCheckBox, \
    QComboBox, QDialogButtonBox, QDateEdit


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
        #self.taches = QTextBrowser()
        #self.taches.setOpenLinks(True)
        self.taches = QListWidget()
        #self.taches.setReadOnly(True)
        self.bouton_quitter = QPushButton("Quitter")
        self.bouton_actualiser = QPushButton("Actualiser")

        grid.addWidget(self.titre)
        grid.addWidget(self.bouton_actualiser)
        grid.addWidget(self.taches)
        grid.addWidget(self.bouton_quitter)


        self.bouton_quitter.clicked.connect(self.quitter)
        self.bouton_actualiser.clicked.connect(self.actualiser)
        #self.taches.itemClicked.connect(tache_cliquee)

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
        print(resultache)

        # Extraction de tous les titres des sous taches
        curseur.execute("SELECT id_soustache, titre_soustache, soustache_id_tache FROM soustaches;")
        sousresultache = curseur.fetchall()
        print(sousresultache)

        self.taches.clear()

        for id_tache, titre_tache in resultache:
        #for i in range(0, len(resultache)):
            #tache = resultache[i][1]

            #self.taches.append(tache)
            #self.taches.addItem(tache)

            self.afficherTache(id_tache, titre_tache)

            for id_soustache, titre_soustache, soustache_id_tache in sousresultache:
                if soustache_id_tache == id_tache :
                    #self.taches.addItem(f'|=> {sousresultache[j][1]}')
                    self.afficherTache(id_soustache, f'|=>{titre_soustache}', soustache_id_tache)
        curseur.close()


    def afficherTache(self, id_tache, titre_tache, soustache_id_tache=None):
        item = QListWidgetItem()
        tache = QWidget()
        layout = QHBoxLayout(tache)

        bouton = QPushButton(titre_tache)
        #bouton.setFixedWidth(70)
        layout.addWidget(bouton)
        bouton.clicked.connect(lambda : self.detail(id_tache, soustache_id_tache))

        suppr = QPushButton('X')
        suppr.setFixedWidth(30)
        layout.addWidget(suppr)
        suppr.clicked.connect(lambda : self.supprimer(id_tache, soustache_id_tache))

        layout.addStretch()
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
        print(f'Supprimer {id_tache}')


    def quitter(self):
        self.cnx.close()
        QCoreApplication.exit(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    principal = Principal()
    principal.show()
    app.exec()