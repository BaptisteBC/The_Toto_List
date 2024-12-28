FROM continuumio/miniconda3:latest

WORKDIR /app

# Mise à jour et installation des dépendances système nécessaires pour Qt
RUN apt-get update && apt-get install -y \
    curl \
    git \
    x11-apps \
    libx11-6 \
    libxext-dev \
    libxrender-dev \
    libxinerama-dev \
    libxi-dev \
    libxrandr-dev \
    libxcursor-dev \
    libxtst-dev \
    libglib2.0-0 \
    libfontconfig1 \
    libdbus-1-3 \
    libxcomposite-dev \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-render0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-shm0 \
    libxcb-xfixes0 \
    libxcb-xinerama0 \
    libxcb-randr0 \
    libxcb-util1 \
    libegl1 \
    tk-dev \
    qtbase5-dev && rm -rf /var/lib/apt/lists/*


COPY config.env .

# Ajouter les channels et créer un environnement Conda
COPY environment.yml /tmp/environment.yml

# Installation des dépendances et configuration de l'environnement Conda
RUN conda config --add channels conda-forge
RUN conda env create -f /tmp/environment.yml
RUN conda clean -afy
RUN echo "conda activate TOTO_LIST" >> ~/.bashrc

# Activer l'environnement par défaut
ENV PATH=/opt/conda/envs/TOTO_LIST/bin:$PATH

# Copier le script d'entrée
COPY docker-entrypoint.sh /app/docker-entrypoint.sh

# Rendre le script exécutable
RUN chmod +x /app/docker-entrypoint.sh

# Définir le script d'entrée
CMD ["bash","/app/docker-entrypoint.sh"]
