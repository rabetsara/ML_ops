FROM python:3.9-slim

WORKDIR /app

# Installation des dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copie des fichiers de configuration
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du reste du code
COPY . .

# Création du dossier data si nécessaire
RUN mkdir -p data

# Par défaut, on ne fait rien, Jenkins lancera les scripts spécifiques
CMD ["python"]