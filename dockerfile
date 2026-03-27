FROM python:3.9-slim
WORKDIR /app
# On ne réinstalle pas build-essential si ça a marché sans, pour gagner du temps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# CRUCIAL : Indique le script à lancer par défaut
CMD ["python", "train_phone.py"]
