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


---------------------------------------------------------------------------------------------------------------------



# Formulaire.py

L'application permet à l'utilisateur de saisir une tâche avec un titre, une description, une date d'échéance, une date de rappel, une liste à laquelle la tâche appartient et un utilisateur assigné. L'interface envoie ensuite ces informations au serveur via une connexion réseau sécurisée, utilisant un socket AES.

## Fonctionnalités principales :
- Création de tâches : Permet à l'utilisateur de spécifier un titre, une description, une date d'échéance et une date de rappel pour la tâche.
- Assignation à une liste et un utilisateur : L'utilisateur peut sélectionner la liste de tâches à laquelle la tâche appartient ainsi que l'utilisateur assigné.
- Chiffrement AES : Les données échangées entre l'application et le serveur sont chiffrées à l'aide de l'AES (Advanced Encryption Standard).
- Connexion au serveur : Le formulaire récupère les listes et utilisateurs disponibles sur le serveur via une connexion réseau sécurisée.

## Prérequis
Avant d'exécuter ce projet, assurez-vous d'avoir installé Python 3 ainsi que les dépendances nécessaires :

- PyQt5 : Pour l'interface graphique.
- socket : Pour la gestion de la connexion réseau.
- json : Pour l'échange de données en format JSON.
- lib.custom.AESsocket : Classe personnalisée pour la gestion du chiffrement AES des données réseau.

### Installation des dépendances
Si vous n'avez pas encore installé PyQt5, vous pouvez le faire via pip :

`pip install PyQt5`

### Structure du projet
Voici un aperçu de la structure du projet :

- Nom de la tâche : Champ pour spécifier le titre de la tâche.
- Description : Champ pour entrer une description détaillée de la tâche.
- Date d'échéance : Sélecteur de date pour choisir la date limite de la tâche.
- Liste : Menu déroulant pour sélectionner la liste à laquelle la tâche appartient (récupérée depuis le serveur).
- Assigné à : Menu déroulant pour sélectionner l'utilisateur à qui la tâche est assignée (récupéré depuis le serveur).
- Date de rappel : Sélecteur de date pour définir une date de rappel.
- Connexion au serveur : Lorsque vous soumettez le formulaire, l'application se connecte au serveur pour récupérer les utilisateurs et les listes disponibles, puis envoie la tâche créée au serveur via un socket sécurisé.

## Détails techniques
Fonctionnalités principales
1. Connexion au serveur
La fonction conection() établit une connexion sécurisée avec le serveur via un socket AES. Si la connexion échoue, un message d'erreur est affiché.

2. Charger les listes et utilisateurs
Les fonctions ChargerListes() et ChargerUtilisateurs() récupèrent respectivement les listes et les utilisateurs disponibles sur le serveur. Ces informations sont ensuite affichées dans les menus déroulants de l'interface.

3. Envoi des données de la tâche
La fonction Envoie() récupère les données du formulaire et les envoie au serveur sous forme de message chiffré, après avoir vérifié que toutes les informations nécessaires (utilisateur, liste) sont sélectionnées.

Format du message envoyé au serveur
Le message envoyé au serveur lors de la création d'une tâche a le format suivant :

`CREATION_TACHE:<id_utilisateur>:<id_liste>:<titre_tache>:<description>:<date_echeance>:0:<date_rappel>`
- id_utilisateur : L'ID de l'utilisateur assigné à la tâche.
- id_liste : L'ID de la liste à laquelle la tâche appartient.
- titre_tache : Le titre de la tâche.
- description : La description détaillée de la tâche.
- date_echeance : La date d'échéance de la tâche.
- date_rappel : La date du rappel pour la tâche.

## Chiffrement AES
Le chiffrement des données est géré par un socket personnalisé AESsocket, qui crypte les messages avant de les envoyer et les décrypte après les avoir reçus. Cela garantit la sécurité des échanges entre l'application et le serveur.

