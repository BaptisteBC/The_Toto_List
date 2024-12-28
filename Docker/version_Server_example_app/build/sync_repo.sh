#!/bin/bash

# Fichier contenant vos identifiants GitHub (sous forme token)
ENV_FILE="/app/.env"

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

if [ -z "$WEBHOOK_URL" ]; then
    echo "Erreur : L'URL du webhook Discord n'est pas définie."
    exit 1
fi

# Fonction pour envoyer un message au webhook Discord
send_discord_notification() {
    local status="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    curl -H "Content-Type: application/json" -X POST -d "{
        \"embeds\": [{
            \"title\": \"Statut de la mise à jour\",
            \"description\": \"$status\",
            \"color\": 5814783,
            \"footer\": {
                \"text\": \"Mise à jour effectuée\",
                \"icon_url\": \"https://cdn.discordapp.com/icons/1292737459003719751/4942fa21779e1aa5c5172ecc3ea0028e.webp?size=512&format=webp\"
            },
            \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
        }]
    }" "$WEBHOOK_URL"
}

# Vérifier si le projet existe déjà localement
if [ ! -d "$PROJECT_DEST" ]; then
    echo "Clonage initial du projet..."
    git clone https://$GITHUB_TOKEN@${REPO_URL#https://} "$PROJECT_DEST"

    cd "$PROJECT_DEST" || exit 1
    git config pull.rebase false
    send_discord_notification "Le projet a été cloné avec succès le $(date '+%Y-%m-%d %H:%M:%S')."
else
    echo "Mise à jour du projet existant..."
    cd "$PROJECT_DEST" || exit 1

    output=$(git pull)
    echo $output
    if [[ $output == *"Already up to date."* ]]; then
        true # Pour rendre valide
    else
        send_discord_notification "Le projet a été mis à jour avec succès au $(date '+%Y-%m-%d %H:%M:%S')."
    fi
fi
