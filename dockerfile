# Utilisation d'une image Python légère
FROM python:3.9-slim

# Définition du répertoire de travail
WORKDIR /app

# Installation des dépendances système minimales pour éviter les erreurs
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copie et installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copie de tout le projet (scripts + dataset)
COPY . .

# Création du dossier data s'il n'existe pas (pour éviter l'erreur dans train_phone.py)
RUN mkdir -p data

# Par défaut, on lance l'entraînement
CMD ["python", "train_phone.py"]
