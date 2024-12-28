#!/bin/bash

# Fonction pour vérifier si un programme est installé
function check_and_install {
    local cmd=$1
    local pkg=$2

    if ! command -v "$cmd" &> /dev/null; then
        echo "$cmd n'est pas installé. Installation en cours..."
        sudo apt update && sudo apt install -y "$pkg"
        if [ $? -eq 0 ]; then
            echo "$cmd a été installé avec succès."
        else
            echo "Une erreur s'est produite pendant l'installation de $cmd."
            exit 1
        fi
    else
        echo "$cmd est déjà installé."
    fi
}

# Vérifier et installer ngrok
if ! command -v ngrok &> /dev/null; then
    echo "ngrok n'est pas installé. Installation en cours..."

    # Ajout de la clé GPG et dépôt ngrok
    curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
        | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null \
    && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" \
        | sudo tee /etc/apt/sources.list.d/ngrok.list >/dev/null \
    && sudo apt update \
    && sudo apt install -y ngrok

    if [ $? -eq 0 ]; then
        echo "Installation réussie. Configuration du token..."
        ngrok config add-authtoken [NGROK_AUTH_TOKEN]
        echo "ngrok est installé et configuré avec succès."
    else
        echo "Une erreur s'est produite pendant l'installation de ngrok."
        exit 1
    fi
else
    echo "ngrok est déjà installé."
fi

# Vérifier et installer Docker
check_and_install "docker" "docker.io"

# Vérifier et installer Docker Compose
check_and_install "docker-compose" "docker-compose"

# Lancer docker-compose et ngrok
echo "Lancement de docker-compose..."
docker-compose up --build -d

echo "Lancement de ngrok..."

# Créer un service systemd pour ngrok
echo "Création d'un service systemd pour ngrok..."
cat <<EOF > /etc/systemd/system/ngrok.service
[Unit]
Description=Ngrok
After=network.service

[Service]
Type=simple
User=root
WorkingDirectory=$PWD
ExecStart=/usr/local/bin/ngrok start --all --config="$PWD/config.yml"
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# Démarrer et activer le service ngrok
sudo systemctl daemon-reload
sudo systemctl enable ngrok
sudo systemctl start ngrok

echo "Service ngrok démarré et activé au démarrage."
