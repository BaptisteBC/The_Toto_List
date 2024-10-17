import sys
import threading

import pymysql
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QWidget, QGridLayout, QTextEdit, QApplication, QLabel, QPushButton


class Principal(QWidget):
    def __init__(self, host:str='127.0.0.1', user:str='root', password='toto', database:str='thetotodb'):
        """

        :type user: str
        :type host: str
        :type password: str
        :type database: str
        """
        super().__init__()

        self.setWindowTitle("Page Prinicpale")

        grid = QGridLayout()
        self.setLayout(grid)
        self.resize(300, 150)

        self.titre = QLabel("Mes tâches")
        self.taches = QTextEdit()
        self.taches.setReadOnly(True)
        self.bouton_quitter = QPushButton("Quitter")
        self.bouton_actualiser = QPushButton("Actualiser")

        grid.addWidget(self.titre)
        grid.addWidget(self.taches)
        grid.addWidget(self.bouton_quitter)
        grid.addWidget(self.bouton_actualiser)

        self.bouton_quitter.clicked.connect(self.quitter)
        self.bouton_actualiser.clicked.connect(self.actualiser)

        self.host = host
        self.user = user
        self.password = password
        self.database = database

        self.cnx = pymysql.connect(host=host, user=user, password=password, database=database)

    def quitter(self):
        QCoreApplication.exit(0)

    def actualiser(self):
        curseur = self.cnx.cursor()
        curseur.execute("SELECT titre FROM taches;")
        resultat = curseur.fetchall()
        print(resultat[0][0])
        self.taches.append(resultat[0][0])






if __name__ == "__main__":
    app = QApplication(sys.argv)
    principal = Principal()
    principal.show()
    app.exec()