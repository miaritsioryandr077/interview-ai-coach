FROM node:20-alpine

WORKDIR /app

ENV CI=true

# npm ci exige package.json + package-lock.json
COPY package.json package-lock.json ./
RUN npm ci

COPY . .

EXPOSE 3000

# Mode dev actuel du projet : Vite sur le port 3000 (voir vite.config.ts).
# --host 0.0.0.0 est requis pour rendre le serveur accessible hors du conteneur.
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]
