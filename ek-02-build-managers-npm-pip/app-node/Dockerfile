# ---------- 1. aşama: build -------------------------------------------------
# Bölüm 1'deki adımların aynısı: bağımlılık, lint, test, paket.
# Bu aşamada ESLint, testler ve npm cache vardır; son image'a girmezler.
FROM node:24-alpine AS build
WORKDIR /app

# Önce yalnızca manifest ve lockfile: bağımlılık layer'ı cache'te kalır
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund

COPY . .
RUN npm run lint
RUN npm test
RUN npm pack

# ---------- 2. aşama: çalışma -----------------------------------------------
# Yalnızca artifact (.tgz) alınır ve üretim bağımlılıklarıyla kurulur.
FROM node:24-alpine
WORKDIR /app
COPY --from=build /app/sepet-hesaplama-1.0.0.tgz /tmp/
RUN npm install --omit=dev --no-audit --no-fund /tmp/sepet-hesaplama-1.0.0.tgz \
    && rm /tmp/sepet-hesaplama-1.0.0.tgz \
    && npm cache clean --force

USER node
CMD ["node", "node_modules/sepet-hesaplama/src/index.js"]
