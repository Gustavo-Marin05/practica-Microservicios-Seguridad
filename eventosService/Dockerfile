# Imagen base oficial de Node.js
FROM node:latest

# instalar netcat-openbsd (netcat) y limpiar cache apt
RUN apt-get update \
 && apt-get install -y netcat-openbsd \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

# Generar el cliente de Prisma (si lo necesitás en build)
RUN npx prisma generate

EXPOSE 3000

CMD ["npm", "run", "dev"]
