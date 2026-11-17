# Taban image: Node.js kurulu hafif Alpine Linux
FROM node:22-alpine

# Container içindeki çalışma dizini
WORKDIR /app

# Önce bağımlılık listesini kopyala ve paketleri kur
COPY package.json .
RUN npm install

# Sonra uygulama kodunu kopyala
COPY server.js .

# Uygulamanın dinlediği port
EXPOSE 3000

# Container başlayınca çalışacak komut
CMD ["node", "server.js"]
