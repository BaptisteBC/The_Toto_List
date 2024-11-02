## 🅰️ - Informations générales<br><br>
<br>

▶️ Ce référentiel contient deux méthodes principales de vérification des adresses e-mail, qui sont les suivantes :
<br>
<br>
| Méthode | Description |
| --------------| ----------------------------|
| methode_A | La méthode utilise des variables **statiques** définies dans le code. |
| methode_B | La méthode **charge** des variables depuis un fichier environnement. |  
<br>
<br>

▶️ Ces deux méthodes ont une variante `_SSL` qui force la connexion à la base de données via **SSL/TLS** :
<br>
<br>
| Variante | Description |
| --------------| ----------------------------|
| methode_A_SSL | Variante de la méthode A, force une connexion chiffrée via SSL/TLS. |
| methode_B_SSL | Variante de la méthode B, force une connexion chiffrée via SSL/TLS. |
<br>

---
## 🅱️ - Hiérarchie du référentiel<br><br>
<br>

▶️ Les dossiers du référentiel sont structurés de la manière suivante :  
<br>
<br>
📁 [methode_A](methode_A)  
‎ |  
└── 📄 [verifierAdresseEmailSemel.py](methode_A/verifierAdresseEmailSemel.py)  
‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ |  
‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ └── Version avec variables statiques, sans chiffrement SSL/TLS.  
<br>
📁 [methode_A_SSL](methode_A_SSL)  
‎ |  
└── 📄 [verifierAdresseEmailBis.py](methode_A_SSL/verifierAdresseEmailBis.py)  
‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ |  
‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ └── Version avec variables statiques et chiffrement SSL/TLS.  
<br>
📁 [methode_B](methode_B)  
‎ |  
├── 📄 [variablesBDD.env.exemple](methode_B/variablesBDD.env.exemple)  
‎ |‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎|  
‎ ‎| ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎‎└── Variables d'environnement sans le paramètre SSL/TLS.  
‎ |  
└── 📄 [verifierAdresseEmailTer.py](methode_B/verifierAdresseEmailTer.py)  
‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ |  
‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ └── Version avec variables d'environnement, sans chiffrement SSL/TLS.  
<br>
📁 [methode_B_SSL](methode_B_SSL)  
‎ |  
├── 📄 [variablesBDD_SSL.env.exemple](methode_B_SSL/variablesBDD_SSL.env.exemple)  
‎ |‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎|  
‎ ‎| ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎‎└── Variables d'environnement avec le paramètre SSL/TLS.  
‎ |  
└── 📄 [verifierAdresseEmailQuater.py](methode_B_SSL/verifierAdresseEmailQuater.py)  
‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ |  
‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ └── Version avec variables d'environnement et chiffrement SSL/TLS.
<br><br>

---
## ⚠️ - Important<br><br>
<br>

> [!WARNING]
> Il faut modifier les paramètres de connexion à la base de données, selon la méthode utilisée.
<br>

📁 [methode_A](methode_A) et [methode_A_SSL](methode_A_SSL) → directement dans **le code**.
<br>
<br>
| Paramètre | Description |
| --------------| ----------------------------|
| `host` | Adresse IP ou nom d'hôte du serveur de base de données |
| `port` | Port utilisé pour la connexion au serveur de base de données |
| `user` | Utilisateur de connexion au serveur de base de données |
| `password` | Mot de passe de connexion au serveur de base de données |
| `database` | Nom de la base de données. |  
<br>
<br>

📁 [methode_B](methode_B) et [methode_B_SSL](methode_B_SSL) → dans les fichiers `.env.exemple` fournis.
<br>
<br>
| Paramètre | Description |
| --------------| ----------------------------|
| `BDD_HOTE` | Adresse IP ou nom d'hôte du serveur de base de données |
| `BDD_PORT` | Port utilisé pour la connexion au serveur de base de données |
| `BDD_UTIL` | Utilisateur de connexion au serveur de base de données |
| `BDD_MDP` | Mot de passe de connexion au serveur de base de données |
| `BDD_NOM` | Nom de la base de données. |  
<br>
<br>

> [!IMPORTANT]
> Il sera nécessaire de supprimer l'ensemble des fonctions `print` présentes dans les codes.  
> Celles-ci pourront être remplacées par des fonctions d'affichage de pop-up correspondantes.
