import pymysql
from datetime import datetime

def journalisation(utilisateurId: int, typeEvenement: str):
    """Enregistre un événement dans la table de journalisation.

    :param utilisateurId: Identifiant de l'utilisateur.
    :type utilisateurId: int
    :param typeEvenement: Chaine d'evenement, il est conseiller d'utiliser la fonction "creerChaineEvenement".
    :type typeEvenement: str
    :raises pymysql.MySQLError: Erreur lors de l'insertion dans la base de données.
    :return: None
    :rtype: None
    """
    try:
        connexion = pymysql.connect(
            host="127.0.0.1",
            user="totodb-admin",
            password="&TotoDB$IUT!2024%Ad",
            database="thetotodb"
        )

        curseur = connexion.cursor()
        dateEvenement = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        requete = """
        INSERT INTO journalisation (journalisation_id_utilisateur, type_evenement, date_evenement)
        VALUES (%s, %s, %s)
        """
        valeurs = (utilisateurId, typeEvenement, dateEvenement)
        curseur.execute(requete, valeurs)
        connexion.commit()
        print("Informations insérées dans la table 'journalisation'.")

    except pymysql.MySQLError as erreur:
        print(f"Erreur d'insertion : {erreur}")

    finally:
        if curseur is not None:
            curseur.close()
        if connexion is not None:
            connexion.close()

def creerChaineEvenement(premierX: int, deuxiemeX: int, troisiemeX: int, listeY, listeZ):
    """Crée une chaîne d'événements formatée pour la fonction journalisation.

    :param premierX: Type d'évènement : 0 Ajout ; 1 Modification ; 2 Suppression.
    :type premierX: int
    :param deuxiemeX:  Objet affecter par l'évènement : 0 Utilisateur ; 1 Tache ; 2 Sous tache ; 3 Liste ; 4 Group ; 5 Groupes_utilisateurs ; 6 Etiquettes  ; 7 Etiquettes_elements
    :type deuxiemeX: int
    :param troisiemeX: Id de l'entrée affecter.
    :type troisiemeX: int
    :param listeY: Liste de noms ou d'indices de colonnes, selon le cas.
    :type listeY: list | str
    :param listeZ: Liste valeur modifier dans l'ordre des N° de colonne.
    :type listeZ: list
    :raises pymysql.MySQLError: Erreur lors de la connexion à la base de données.
    :raises ValueError: Si certaines colonnes dans listeY ne correspondent pas.
    :return: Chaîne d’événements formatée.
    :rtype: str | None
    """
    try:
        connexion = pymysql.connect(
            host="127.0.0.1",
            user="totodb-admin",
            password="&TotoDB$IUT!2024%Ad",
            database="thetotodb"
        )

        curseur = connexion.cursor()

        if isinstance(listeY, list):
            if all(isinstance(element, str) for element in listeY):
                tables = [
                    "utilisateurs", "taches", "soustaches", "listes", "groupes",
                    "groupes_utilisateurs", "etiquettes", "etiquettes_elements"
                ]
                nomTable = tables[deuxiemeX]
                colonnesValides = []
                for colonne in listeY:
                    requete = f"SHOW COLUMNS FROM {nomTable} LIKE %s"
                    curseur.execute(requete, (colonne,))
                    resultat = curseur.fetchone()
                    if resultat:
                        colonnesValides.append(resultat[0])
                if len(colonnesValides) != len(listeY):
                    print("Certaines colonnes ne correspondent pas, annulation de l'opération.")
                    return None
                listeY = [colonnesValides.index(colonne) + 1 for colonne in colonnesValides]

        listeYStr = ".".join(map(str, listeY)) if isinstance(listeY, list) else str(listeY)
        zStr = ".".join(map(str, listeZ))
        chaineEvenement = f"{premierX}.{deuxiemeX}.{troisiemeX}.{{{listeYStr}}}.{{{zStr}}}"

        return chaineEvenement

    except pymysql.MySQLError as erreur:
        print(f"Erreur de connexion : {erreur}")

    finally:
        if curseur is not None:
            curseur.close()
        if connexion is not None:
            connexion.close()

if __name__ == "__main__":
    chaineEvenement = creerChaineEvenement(1, 1, 326, ["titre_tache", "daterappel_tache"], ["nouveauNom", "2024-11-16 15:14:00"])
    if chaineEvenement:
        print(chaineEvenement)
        journalisation(1, chaineEvenement)
