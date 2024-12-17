# Serveur.py

**Serveur.py** est un serveur de gestion des tâches qui permet aux clients de gérer des utilisateurs, des listes et des tâches via des commandes. Il utilise des sockets sécurisés avec un chiffrement AES pour la communication. Les données des utilisateurs et des tâches sont stockées dans une base de données MySQL.

## Fonctionnalités principales
- Récupérer la liste des utilisateurs (`GET_UTILISATEURS`).
- Récupérer les listes de tâches disponibles (`GET_LISTES`).
- Créer une nouvelle tâche (`CREATION_TACHE`).
- Obtenir les détails d'une liste de tâches spécifique (`ID_LISTE`).

## Prérequis

Avant de pouvoir utiliser le serveur, assurez-vous que les éléments suivants sont installés :

- **Python 3.x** : Assurez-vous que Python 3 est installé sur votre machine.
- **MySQL** : Un serveur MySQL fonctionnel, avec une base de données contenant les tables appropriées (`utilisateurs`, `listes`, `taches`).
- **Librairies Python** :
  - `pymysql`
  - `socket`
  - `json`

Vous pouvez installer les dépendances Python en exécutant la commande suivante :
`pip install pymysql`

## Variables de connexion à la base de données
Le serveur utilise les informations de connexion à MySQL définies dans le code :
```
host : 127.0.0.1 (ou l'adresse IP de votre serveur MySQL)
user : root (nom d'utilisateur MySQL)
password : toto (mot de passe MySQL)
database : TheTotoDB
port : 3306 (port MySQL)
```


### Structure du code
## TaskServer
La classe principale qui implémente le serveur. Elle est responsable de :

- Écouter les connexions entrantes via un socket sécurisé avec AES.
- Interpréter les commandes reçues des clients.
- Interagir avec la base de données MySQL pour récupérer des informations ou insérer de nouvelles données.

## Méthodes principales :
- start() : Démarre le serveur et attend les connexions des clients.
- interpretCommand(command) : Interprète la commande reçue du client et appelle la méthode appropriée pour y répondre.
- getUserId() : Récupère les utilisateurs enregistrés dans la base de données.
- getListId() : Récupère les listes disponibles.
- createTask(userId, listId, taskTitle, taskDescription, dueDate, status, reminderDate) : Crée une nouvelle tâche dans la base de données.

## Exemple de commandes
Voici quelques exemples de commandes que le client peut envoyer au serveur :

### Obtenir la liste des utilisateurs :

`GET_UTILISATEURS `
Cette commande renvoie une liste JSON contenant les ID et pseudonymes des utilisateurs.

### Obtenir les listes de tâches :

`GET_LISTES`
Cette commande renvoie une liste JSON contenant les ID et noms des listes de tâches disponibles.

### Créer une nouvelle tâche :

`CREATION_TACHE:1:1:Tâche test:Une description de la tâche:2024-12-31:à faire:2024-12-25`
Cette commande crée une nouvelle tâche pour l'utilisateur avec l'ID 1 dans la liste avec l'ID 1.

### Obtenir les tâches d'une liste spécifique :

`ID_LISTE:1`
Cette commande renvoie les tâches associées à la liste avec l'ID 1.

## Gestion des erreurs
Si une commande est mal formulée ou non reconnue, le serveur renverra un message indiquant "Commande inconnue".
En cas d'erreur de connexion à la base de données ou d'échec d'exécution d'une requête, le serveur renverra un message d'erreur spécifique.
