import sys

import pymysql
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QWidget, QGridLayout, QApplication, QLabel, QPushButton, \
    QListWidget


def tache_cliquee():
    print("ça fonctionne !")

def quitter():
    QCoreApplication.exit(0)

class Principal(QWidget):
    """Fenêtre principale d'affichage des tâches.
    Prends en argument les infos de connexion à la BDD"""

    def __init__(self, host:str='127.0.0.1', user:str='root', password='toto', database:str='thetotodb'):
        super().__init__()

        self.setWindowTitle("Page Prinicpale")

        grid = QGridLayout()
        self.setLayout(grid)
        self.resize(300, 150)

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


        self.bouton_quitter.clicked.connect(quitter)
        self.bouton_actualiser.clicked.connect(self.actualiser)
        self.taches.itemClicked.connect(tache_cliquee)

        self.host = host
        self.user = user
        self.password = password
        self.database = database





    def actualiser(self):
        """Fonction d'actualisation des tâches.
        Lorsue le bouton est cliqué, effectue une requête dans la table tâche et récupère le champ 'titre_tache' pour \
        l'afficher dans la fenêtre principale."""

        self.cnx = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database)
        curseur = self.cnx.cursor()

        # Extraction de tous les titres des taches principales
        curseur.execute("SELECT id_tache,titre_tache FROM taches;")
        resultache = curseur.fetchall()
        print(resultache)

        # Extraction de tous les titres des sous taches
        curseur.execute("SELECT soustache_id_tache,titre_soustache FROM soustaches;")
        sousresultache = curseur.fetchall()
        print(sousresultache)

        self.taches.clear()

        for i in range(0, len(resultache)):
            tache = resultache[i][1]

            #self.taches.append(tache)
            self.taches.addItem(tache)

            for j in range(0, len(sousresultache)):
                if sousresultache[j][0] == resultache[i][0] :
                    self.taches.addItem(f'|=> {sousresultache[j][1]}')
        curseur.close()
        self.cnx.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    principal = Principal()
    principal.show()
    app.exec()