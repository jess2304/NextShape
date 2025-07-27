# Image Python
FROM python:3.11

# Dossier de travail
WORKDIR /app

RUN apt-get update && apt-get install -y postgresql-client

# Copier et installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le projet
COPY . .
COPY wait.sh entrypoint.sh ./

# Ajouter le certificat Brevo
COPY brevo.pem /usr/local/share/ca-certificates/brevo.crt
RUN update-ca-certificates

# Donner les droits d'exécution au script d'entrée
RUN apt-get update && apt-get install -y dos2unix \
  && dos2unix wait.sh entrypoint.sh \
  && chmod +x wait.sh entrypoint.sh
RUN chmod +x ./wait.sh ./entrypoint.sh

# Exposer le port de Django
EXPOSE 8000

# Définir le script comme point d'entrée
ENTRYPOINT ["bash", "entrypoint.sh"]
