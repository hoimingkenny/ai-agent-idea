# Dockerfile for Offline SLM Chat Sync Server
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
# RUN npm install

COPY . .

EXPOSE 3000

CMD ["node", "server/sync_server.js"]
