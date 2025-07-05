# Utiliser une image Node.js pour builder Vue.js
FROM node:18 AS builder

# Définir le dossier de travail
WORKDIR /app

# Copier et installer les dépendances
COPY package.json package-lock.json ./
RUN npm install

# Copier le reste du projet
COPY . .
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}

RUN npm run build

# Étape de prod : utiliser Nginx pour servir l'app
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html

# Exposer le port attendu par Render
EXPOSE 80

# Démarrer le serveur
CMD ["nginx", "-g", "daemon off;"]
