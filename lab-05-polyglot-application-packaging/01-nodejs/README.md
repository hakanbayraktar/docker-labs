# LAB-DOC-05-01 — Node.js (Express) API Paketleme

| Profil / Araçlar | Açık Portlar |
|---|---|
| `node:24-alpine`, `npm ci`, `curl` | 19001 |

## Amaç

- Express tabanlı bir Node.js API'sini bağımlılıklarıyla birlikte image'a paketlemek.
- `package*.json` dosyalarını koddan önce kopyalayarak layer cache'ini korumak.
- Uygulamayı image'daki hazır `node` kullanıcısıyla (root olmadan) çalıştırmak.

## Ön Koşullar

- Host üzerinde **19001** portu boş olmalıdır. Aynı portu kullanan başka bir alt lab çalışıyorsa önce onu silin.
- Host'a programlama dili veya SDK kurmayın; build ortamı image'ın içindedir.

## Adım Adım Uygulama Rehberi

### 1. Dosyaları İnceleme

```bash
cd ~/docker-labs/lab-05-polyglot-application-packaging/01-nodejs
```

```bash
ls -la
```

```bash
cat Dockerfile
```

### 2. Image'ı Build Etme

```bash
docker build -t app-node:1.0 .
```

```bash
docker images app-node:1.0
```

### 3. Container'ı Çalıştırma

```bash
docker run -d --name test-node -p 19001:3000 app-node:1.0
```

### 4. Uç Noktaları Test Etme

```bash
curl -s http://localhost:19001/api/info
```

```bash
curl -s http://localhost:19001/health
```

Tarayıcıdan `http://<SUNUCU-IP>:19001` adresini de açabilirsiniz.

### 5. Çalışan Kullanıcıyı Doğrulama

```bash
docker exec test-node id
```

UID değeri `1000` olmalıdır; uygulama root ile çalışmıyor.

## Temizlik

```bash
docker rm -f test-node
```

```bash
docker rmi app-node:1.0
```
