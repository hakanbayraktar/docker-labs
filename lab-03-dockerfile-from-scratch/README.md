# LAB-DOC-03 — Sıfırdan Dockerfile Yazma ve Image Build

| Profil / Araçlar | Açık Portlar |
|---|---|
| `docker build`, `python:3.12-slim`, `node:22-alpine`, `curl` | 3000, 3001 |

## Amaç

- Bir Python ve bir Node.js uygulaması için Dockerfile yazmak.
- Build sırasında bağımlılıkların kurulduğunu görmek (`pip install`, `npm install`).
- Image'ı çalıştırıp uygulamayı test etmek.

## Ön Koşullar

- Host üzerinde **3000** ve **3001** portları boş olmalıdır.

## Adım Adım Uygulama Rehberi

### Bölüm 1: Python Uygulaması

#### 1. Dosyaları İnceleme

```bash
cd ~/docker-labs/lab-03-dockerfile-from-scratch/python-app
```

```bash
cat app.py
```

```bash
cat requirements.txt
```

```bash
cat Dockerfile
```

#### 2. Image'ı Build Etme

```bash
docker build -t python-app:1.0 .
```

Çıktıda `RUN pip install` adımında Flask ve bağımlılıklarının kurulduğunu görün:

```text
Successfully installed Flask-3.1.2 blinker-1.9.0 click-8.5.1 itsdangerous-2.2.0 jinja2-3.1.6 markupsafe-3.0.4 werkzeug-3.1.9
```

```bash
docker images python-app
```

```bash
docker history python-app:1.0
```

Her Dockerfile satırı bir layer'dır. `RUN pip install` layer'ı kurulan paketler kadar yer kaplar.

#### 3. Çalıştırma ve Test

Host'un 3000 portunu container'ın 5000 portuna bağlayın:

```bash
docker run -d --name python-app -p 3000:5000 python-app:1.0
```

```bash
curl -s http://localhost:3000
```

Beklenen çıktı: `{"dil":"python","mesaj":"Merhaba Docker"}`

```bash
docker logs python-app
```

Loglardaki `WARNING: This is a development server` satırı Flask'ın geliştirme sunucusu uyarısıdır; lab için normaldir.

Kurulan paketi container içinde görün:

```bash
docker exec python-app pip list
```

Tarayıcıdan `http://<SUNUCU-IP>:3000` adresini de açabilirsiniz.

<details>
<summary><strong>İsteğe bağlı: CMD ile ENTRYPOINT farkı</strong></summary>

Dockerfile'ın son satırı `CMD ["python", "app.py"]`, container başlayınca çalışacak **varsayılan** komuttur. `docker run`'da image adından sonra bir komut yazarsanız CMD'nin yerine o çalışır; uygulama başlamaz, yalnızca Python sürümü yazılır:

```bash
docker run --rm python-app:1.0 python --version
```

Image'ın ayarlarına bakın:

```bash
docker image inspect --format 'CMD={{.Config.Cmd}} ENTRYPOINT={{.Config.Entrypoint}}' python-app:1.0
```

| | `CMD` | `ENTRYPOINT` |
|---|---|---|
| `docker run <image> <komut>` yazılınca | Yerine yazılan komut çalışır | Yazılanlar ENTRYPOINT'e argüman olarak eklenir |
| Ne zaman? | Değiştirilebilir varsayılan komut | Image'ın her zaman çalışması gereken asıl programı |

İkisi birlikte de kullanılabilir: `ENTRYPOINT` programı, `CMD` onun varsayılan argümanlarını verir.

</details>

### Bölüm 2: Node.js Uygulaması

#### 4. Dosyaları İnceleme

```bash
cd ~/docker-labs/lab-03-dockerfile-from-scratch/node-app
```

```bash
cat server.js
```

```bash
cat package.json
```

```bash
cat Dockerfile
```

#### 5. Image'ı Build Etme

```bash
docker build -t node-app:1.0 .
```

Çıktıda `RUN npm install` adımında Express ve bağımlılıklarının kurulduğunu görün:

```text
added 69 packages, and audited 70 packages in 4s
```

```bash
docker images node-app
```

#### 6. Çalıştırma ve Test

Host'un 3001 portunu container'ın 3000 portuna bağlayın:

```bash
docker run -d --name node-app -p 3001:3000 node-app:1.0
```

```bash
curl -s http://localhost:3001
```

Beklenen çıktı: `{"dil":"nodejs","mesaj":"Merhaba Docker"}`

```bash
docker logs node-app
```

Kurulan paketi container içinde görün:

```bash
docker exec node-app npm ls
```

Tarayıcıdan `http://<SUNUCU-IP>:3001` adresini de açabilirsiniz.

## Temizlik

```bash
docker rm -f python-app node-app 2>/dev/null || true
```

```bash
docker rmi python-app:1.0 node-app:1.0 2>/dev/null || true
```
