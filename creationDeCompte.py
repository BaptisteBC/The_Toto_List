import mysql.connector
import sys
'''
ATTENTION, ce programme est a modifier lors de la mise en production et lorsqu'on a le GUI
V0.1 BETA
'''

class CreerUtilisateur:
    '''
    Constructeur de la classe, permet d'initialiser toutes les variables propres à la création d'utilisateurs
    '''
    def __init__(self):
        try:
            self.db_connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='thetotodb'
            )
            self.cursor = self.db_connection.cursor()
        except mysql.connector.Error as err:
            print(f"Erreur de connexion à la base de données : {err}")
            sys.exit(1)

    def recevoirLesParametres(self):
        '''
        Récupère les paramètres de création des utilisateurs (GUI)
        '''
        email = input("Entrez un email : ")
        ####  Mettre la fonction de test de mail et de vérification de compte existant

        pseudo = input("Entrez un pseudo : ")
        nom = input("Entrez un nom : ")
        prenom = input("Entrez un prénom : ")
        #hasher le mot de passe
        motDePasse = input("Entrez un mot de passe : ")
        return email, pseudo, nom, prenom, motDePasse

    def creerUtilisateur(self):
        try:
            email, pseudo, nom, prenom, motDePasse = self.recevoirLesParametres() #recoit les parametres de la methode ci-dessus
            query = """
            INSERT INTO utilisateurs (email, pseudonyme, nom, prenom, motDePasse) 
            VALUES (%s, %s, %s, %s, %s)
            """
            # Exécution de la requête avec les paramètres sécurisés
            self.cursor.execute(query, (email, pseudo, nom, prenom, motDePasse))
            self.db_connection.commit()
            print("Utilisateur créé avec succès !")
        except mysql.connector.Error as err:
            print(f"Erreur lors de la création de l'utilisateur : {err}")
        finally:
            self.fermerConnexion()

    def fermerConnexion(self):
        '''
        Méthode pour fermer la connexion à la base de données
        '''
        if self.cursor:
            self.cursor.close()
        if self.db_connection:
            self.db_connection.close()

if __name__ == '__main__':
    utilisateur = CreerUtilisateur()
    utilisateur.creerUtilisateur()
