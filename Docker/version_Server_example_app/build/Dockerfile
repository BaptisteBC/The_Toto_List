# Utilise une image de base Python
FROM python:3.10-slim

# Définit le répertoire de travail
WORKDIR /app

# Copie les fichiers nécessaires
COPY requirements.txt ./
COPY .env ./
COPY sync_repo.sh ./
COPY update_cron ./

# Installe les dépendances système nécessaires
RUN apt-get update -y && \
    apt-get install -y git curl cron nano && \
    rm -rf /var/lib/apt/lists/*

# Donne les droits nécessaires aux scripts
RUN chmod 0777 /app/sync_repo.sh /app/update_cron

# Copie la tâche cron dans le répertoire approprié
RUN cp /app/update_cron /etc/cron.d/update_cron

# Donne les permissions nécessaires à la tâche cron
RUN chmod 0644 /etc/cron.d/update_cron

# Ajoute la tâche cron au démon cron
RUN crontab /etc/cron.d/update_cron

# Crée un fichier de log pour `cron`
RUN touch /var/log/cron.log

# Initialise le répertoire via le script de synchronisation
RUN ./sync_repo.sh

# Installe les dépendances Python
RUN pip3 install --no-cache-dir -r requirements.txt

# Copie le code de l'application
COPY app.py ./

# Définit la variable d'environnement pour Flask
ENV FLASK_APP=app.py

# Commande pour démarrer `cron` et Flask
CMD ["bash", "-c", "cron && flask run --host=0.0.0.0 --port=80"]
