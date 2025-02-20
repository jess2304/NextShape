# Utiliser une image Node.js pour builder Vue.js
FROM node:18

# Définir le dossier de travail
WORKDIR /app

# Copier et installer les dépendances
COPY package.json package-lock.json ./
RUN npm install

# Copier le reste du projet
COPY . .

# Exposer le port Vue.js
EXPOSE 5173

# Démarrer le serveur
CMD ["npm", "run", "dev", "--", "--host"]
