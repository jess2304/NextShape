# Étape 1 : Build Vue frontend
FROM node:20 AS frontend
WORKDIR /app
COPY UI/ ./UI/
RUN cd UI && npm install && npm run build

# Étape 2 : Django backend avec frontend intégré
FROM python:3.11
WORKDIR /app

RUN apt-get update && apt-get install -y postgresql-client

COPY WS/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY WS/ .

COPY --from=frontend /app/UI/dist /app/UI/dist

RUN chmod +x wait.sh entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["bash", "entrypoint.sh"]
