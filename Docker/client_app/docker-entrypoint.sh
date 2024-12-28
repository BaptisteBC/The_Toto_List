 #!/bin/bash


# Fichier contenant vos identifiants GitHub (sous forme token)
ENV_FILE="/app/config.env"

# Chargement des variables d'ENV
if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"
else
    echo "Erreur : Le fichier $ENV_FILE est introuvable."
    exit 1
fi

if [ -z "$GITHUB_TOKEN" ]; then
    echo "Erreur : Le token GitHub n'est pas défini dans $ENV_FILE."
    exit 1
fi

if [ -z "$APP_NAME" ]; then
    echo "Erreur : Le nom du script client n'est pas défini dans $ENV_FILE."
    exit 1
fi

if [ -z "$PROJECT_DIR" ]; then
    echo "Erreur : La variable PROJECT_DIR n'est pas définie dans $ENV_FILE."
    exit 1
fi

# Effectuer la première requête
result1=$(curl -s https://version.pnoutlet.site/version --connect-timeout 5)

echo "$result1"

# Vérifier la taille de la réponse
if [ ${#result1} -ne 32 ]; then
    echo "Il n\'est pas possible d\'atteindre le site de versionnage, veuillez vérifier votre connectivité"
    exit 1
fi

if [[ ! -d "$PROJECT_DIR" || ! "$(ls -A $PROJECT_DIR)" ]]; then
   echo "Premier lancement : Récupération du projet..."

   git clone https://$GITHUB_TOKEN@${REPO_URL#https://} "$PROJECT_DIR"

   cd "$PROJECT_DIR" || exit 1
   git config pull.rebase false
   python "${PROJECT_DIR}/${APP_NAME}"
else
   echo "Vérification de la version actuelle..."
   result2=$(find "$PROJECT_DIR" -type f ! -path '*/.git/*' ! -path '*/__pycache__/*' -exec md5sum {} \; | awk '{print $1}' | sort | md5sum | cut -d " " -f 1)
   echo "$result2"
   if [[ "$result1" == "$result2" ]]; then
       echo "Version à jour ! Lancement de l'application..."
       python "${PROJECT_DIR}/${APP_NAME}"
   else
       echo "Version obsolète ! Obtention de la dernière version..."
       cd "$PROJECT_DIR" || exit 1
       git pull && python "${PROJECT_DIR}/${APP_NAME}"
   fi
fi
