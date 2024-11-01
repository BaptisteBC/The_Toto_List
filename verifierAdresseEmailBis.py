from dotenv import load_dotenv
from typing import Tuple, Dict
import pymysql
import os
import re

def chargerEnvironnement() -> Dict[str, str | int]:
    """
    Cette méthode est à usage unique et a pour objectif de :
        Charger les variables d'environnement pour la connexion à la BDD.

    Returns:
        → Dict[str, str | int]: Dictionnaire de configuration de la BDD avec :
            ▪ Les paramètres de connexion sous forme de chaînes.
            ▪ Les paramètres numériques sous forme d'entiers.
    """

    # On charge les variables d'environnement depuis le fichier .env
    load_dotenv("identifiantsBDD.env.exemple")

    # -------------------------------------------------------------------------
    # Assemblage des paramètres de connexion à la base de données.
    # -------------------------------------------------------------------------
    return {
        'host': os.getenv('BDD_HOTE'),
        'port': int(os.getenv('BDD_PORT')),
        'user': os.getenv('BDD_UTIL'),
        'password': os.getenv('BDD_MDP'),
        'database': os.getenv('BDD_NOM'),
        'charset': os.getenv('BDD_JDC'),
        'connect_timeout': int(os.getenv('BDD_DELAI'))
    }


def verifierAdresseEmail(adresseEmailSaisie: str,
                         BDD_CONFIG: Dict[str, str | int]) -> Tuple[str, bool]:
    """
    Cette méthode est à usage unique et a pour objectifs de :

        1. Vérifier le bon format de l'adresse e-mail saisie par l'utilisateur.
        2. Vérifier si ladite adresse e-mail est déjà présente dans la BDD.

    Args:
        → adresseEmailSaisie (str): L'adresse e-mail qui doit être vérifiée.
            ▪ Celle-ci est récupérée depuis un champ de saisie utilisateur.
        → BDD_CONFIG (Dict[str, str | int]): Paramètres de connexion à la BDD.
            ▪ Ils sont stockés sous forme de dictionnaire dans le fichier .env.

    Raises:
        → pymysql.err.OperationalError : Erreur opérationnelle avec la BDD.
            ▪ Code 2013 : Connexion perdue avec la BDD.
            ▪ Code 2003 : Connexion refusée par la BDD.
            ▪ Code 2006 : Serveur de BDD indisponible.
        → pymysql.err.InterfaceError : Erreur d'interfaçage avec la BDD.
        → pymysql.err.Error : Erreur globale non gérée avec la BDD.

    Returns:
        → Tuple[str, bool]:
        (adresseEmailSaisie, True) : l'adresse e-mail est valide et disponible.
        (adresseEmailSaisie, False) : l'adresse e-mail est inutilisable car :
            ▪ Son format est invalide.
            ▪ Elle est déjà existante dans la BDD.
            ▪ Une erreur a été levée lors des vérifications.
    """

    # -------------------------------------------------------------------------
    # Définition des constantes des codes d'erreur MySQL.
    # -------------------------------------------------------------------------
    MYSQL_ERROR_CONNECTION_LOST = 2013
    MYSQL_ERROR_CONNECTION_REFUSED = 2003
    MYSQL_ERROR_SERVER_GONE = 2006

    # -------------------------------------------------------------------------
    # Initialisation REGEX du format standard d'une adresse e-mail.
    # Sont permis les caractères suivants : (a-z), (A-Z), (0-9), (.), (-), (_).
    # -------------------------------------------------------------------------
    adresseEmailFormat = (r'^[a-zA-Z0-9][a-zA-Z0-9._-]*'
                          r'@[a-zA-Z0-9][a-zA-Z0-9._-]*'
                          r'\.[a-zA-Z]{2,}$')

    # -------------------------------------------------------------------------
    # Logique de vérification du bon formatage de l'adresse e-mail.
    # -------------------------------------------------------------------------
    if not re.match(adresseEmailFormat, adresseEmailSaisie):
        # ---------------------------------------------------------------------
        # Insérer ici une fonction qui affiche une pop-up d'erreur.
        print(f"Le format de l'adresse e-mail saisie est invalide : "
              f"{adresseEmailSaisie}")
        # ---------------------------------------------------------------------
        return adresseEmailSaisie, False

    # -------------------------------------------------------------------------
    # Logique de vérification de la disponibilité de l'adresse e-mail.
    # -------------------------------------------------------------------------
    try:

        # On établit une connexion vers la base de données MySQL.
        with pymysql.connect(**BDD_CONFIG) as connexionMySQL:

            with connexionMySQL.cursor() as curseurMySQL:

                # On prépare la requête de recherche de l'adresse e-mail.
                requeteMySQL = ("SELECT COUNT(*) "
                              "FROM utilisateurs "
                              "WHERE email_utilisateur = %s")

                # On exécute la requête de recherche dans la base de données.
                curseurMySQL.execute(requeteMySQL, (adresseEmailSaisie,))

                # On compte le nombre de correspondances existantes.
                adresseEmailExistante = curseurMySQL.fetchone()[0]

                # Si le compteur > 0, alors l'adresse e-mail existe déjà.
                if adresseEmailExistante > 0:
                    # ---------------------------------------------------------
                    # Insérer ici une fonction qui affiche une pop-up d'erreur.
                    print(f"L'adresse e-mail saisie existe déjà : "
                          f"{adresseEmailSaisie}")
                    # ---------------------------------------------------------
                    return adresseEmailSaisie, False

                return adresseEmailSaisie, True

    # -------------------------------------------------------------------------
    # Gestion des diverses exceptions relatives à la base de données.
    # -------------------------------------------------------------------------
    except pymysql.err.OperationalError as erreur:

        if erreur.args[0] == MYSQL_ERROR_CONNECTION_LOST:
            # -----------------------------------------------------------------
            # Insérer ici une fonction qui affiche une pop-up d'erreur.
            print(f"Connexion perdue avec la base de données : {erreur}")
            # -----------------------------------------------------------------
            return adresseEmailSaisie, False

        elif erreur.args[0] == MYSQL_ERROR_CONNECTION_REFUSED:
            # -----------------------------------------------------------------
            # Insérer ici une fonction qui affiche une pop-up d'erreur.
            print(f"Connexion refusée par la base de données : {erreur}")
            # -----------------------------------------------------------------
            return adresseEmailSaisie, False

        elif erreur.args[0] == MYSQL_ERROR_SERVER_GONE:
            # -----------------------------------------------------------------
            # Insérer ici une fonction qui affiche une pop-up d'erreur.
            print(f"Le serveur de base de données est indisponible : {erreur}")
            # -----------------------------------------------------------------
            return adresseEmailSaisie, False

        else:
            # -----------------------------------------------------------------
            # Insérer ici une fonction qui affiche une pop-up d'erreur.
            print(f"Erreur opérationnelle MySQL non gérée : {erreur}")
            # -----------------------------------------------------------------
            return adresseEmailSaisie, False

    except pymysql.err.InterfaceError as erreur:
        # ---------------------------------------------------------------------
        # Insérer ici une fonction qui affiche une pop-up d'erreur.
        print(f"Erreur d'interfaçage avec la base de données : {erreur}")
        # ---------------------------------------------------------------------
        return adresseEmailSaisie, False

    except pymysql.err.Error as erreur:
        # ---------------------------------------------------------------------
        # Insérer ici une fonction qui affiche une pop-up d'erreur.
        print(f"Erreur générale relative à la base de données : {erreur}")
        # ---------------------------------------------------------------------
        return adresseEmailSaisie, False


# -----------------------------------------------------------------------------
# Logique d'exécution principale du programme.
# -----------------------------------------------------------------------------
if __name__ == "__main__":

    # On définit l'adresse e-mail comme étant invalide par défaut.
    adresseEmailValide = False

    # -------------------------------------------------------------------------
    # Initialisation des paramètres de connexion à la base de données.
    # -------------------------------------------------------------------------
    BDD_CONFIG = chargerEnvironnement()

    # On boucle dans la fonction tant que l'adresse e-mail n'est pas validée.
    while not adresseEmailValide:

        # On redemande la saisie d'une adresse e-mail.
        adresseEmailSaisie = input("Entrez une adresse e-mail : ")

        # On récupère l'adresse e-mail saisie et le résultat des vérifications.
        adresseEmailVerifiee, resultatVerifications = (
            verifierAdresseEmail(adresseEmailSaisie, BDD_CONFIG))

        adresseEmailValide = resultatVerifications

    print(f"Adresse e-mail valide et disponible : {adresseEmailVerifiee}")
