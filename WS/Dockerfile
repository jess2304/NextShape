# Image Python
FROM python:3.11

# Dossier de travail
WORKDIR /app

# Copier et installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le projet
COPY . .

# Exposer le port de Django
EXPOSE 8000

# Commande de démarrage
CMD ["python", "manage.py","runserver", "0.0.0.0:8000"]
