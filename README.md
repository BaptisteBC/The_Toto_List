# The_Toto_List
# Résumé
Ce script Python implémente une application graphique pour créer et gérer des tâches. L'application utilise PyQt5 pour l'interface utilisateur et interagit avec une base de données MySQL via une connexion sécurisée avec chiffrement AES. Elle permet de saisir des informations sur une tâche, telles que son nom, sa description, la date d'échéance, le statut, l'utilisateur assigné, et la liste associée.

# Structure du script
## Importation des modules
Le script importe plusieurs bibliothèques :

- sys : pour interagir avec le système, notamment pour l'exécution de l'application.
- pymysql.cursors, pymysql : pour la connexion à la base de données MySQL.
- socket : pour la communication réseau.
- lib.custom : pour des outils personnalisés comme AEScipher et AESsocket, qui gèrent le chiffrement.
- PyQt5 : pour la création de l'interface utilisateur.
## Classe FormulaireTache
Cette classe hérite de QWidget et représente l'interface graphique du formulaire de création de tâche.

### Attributs
1. connexion : Connexion à la base de données MySQL.
2. groupes, listes, utilisateurs, tags : Listes contenant les groupes, listes, utilisateurs et tags respectifs.
### Constructeur (__init__)
Initialise les composants graphiques de l'application et charge les données nécessaires depuis le serveur.

### Éléments graphiques principaux
1. Nom de la tâche : Champ texte pour saisir le nom.
2. Description : Zone de texte pour détailler la tâche.
3. Date d'échéance : Sélecteur de date (QDateEdit) initialisé à la date actuelle.
4. Statut : Menu déroulant (QComboBox) pour choisir entre "à faire", "en cours", ou "terminé".
5. Liste : Menu déroulant pour sélectionner la liste associée à la tâche.
6. Utilisateur : Menu déroulant pour sélectionner l'utilisateur assigné.
7. Date de rappel : Sélecteur de date pour définir un rappel.
8. Bouton "Soumettre" : Déclenche l'envoi des données.
## Méthodes

1. conection
   
Établit une connexion réseau sécurisée avec le serveur via un socket standard, amélioré avec AES et Diffie-Hellman pour le chiffrement.

3. Deconnection
   
Ferme la connexion réseau.

4. ChargerListes
   
Charge les listes disponibles depuis le serveur et les affiche dans le QComboBox.

- Envoie une requête SQL : SELECT nom_liste FROM listes.
- Affiche un message d'erreur si aucun résultat n'est trouvé.
  
4. ChargeUtilisateurs
  
Charge les utilisateurs disponibles depuis le serveur et les affiche dans le QComboBox.

- Envoie une requête SQL : SELECT pseudo FROM utilisateurs.
- Affiche un message d'erreur si aucun résultat n'est trouvé.
5. Envoie
  
Récupère les données du formulaire, effectue les vérifications, puis les envoie au serveur.

  i. Récupération des données utilisateur et liste :
     
  - Identifie l'utilisateur assigné et la liste sélectionnée via des requêtes SQL.
  
  ii. Construction de la requête SQL :

  - Génère une requête d'insertion dans la table taches.
  
  iii. Transmission au serveur :

  - Utilise AESsocket pour envoyer les données de manière sécurisée.

