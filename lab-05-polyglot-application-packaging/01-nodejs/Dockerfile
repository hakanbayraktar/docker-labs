FROM node:24-alpine

WORKDIR /app
ENV NODE_ENV=production \
    PORT=3000

# 1. Önce yalnızca bağımlılık tanımları (layer cache için)
COPY package*.json ./

# 2. Kilitli sürümleri kur, geliştirme bağımlılıklarını dışarıda bırak
RUN npm ci --omit=dev

# 3. Sık değişen uygulama kodu en son kopyalanır
COPY . .

# 4. Root yerine image'daki hazır node kullanıcısı
USER node

EXPOSE 3000
CMD ["node", "server.js"]
