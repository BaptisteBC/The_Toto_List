import pymysql

#from testobfu import requetes

# Dictionnaire de mappage des tables
mtables = {
    "user": "xner1etn",
    "password":"frfrce",
}


def obfuscation(requete):
    # Connexion à la base de données MariaDB
    conn = pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='root',
        db='test'
    )
    

    cursor = conn.cursor()

    for table_orig in mtables.keys():
        if table_orig in requete:
            # Obtenir le nom de la table obfusquée
            table_obfusquee = mtables[table_orig]
            # Construire la nouvelle requête
            requete = requete.replace(table_orig, table_obfusquee)  # Ici, on remplace seulement la table
            break  # Sortir de la boucle après le premier remplacement
    # Exécution de la requête obfusquée sur la base de données
    cursor.execute(requete)
    resultats = cursor.fetchall()

    # Fermer la connexion
    conn.close()

    return resultats  # Retourner les résultats