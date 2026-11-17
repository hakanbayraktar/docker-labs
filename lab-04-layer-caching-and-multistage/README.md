# LAB-DOC-04 — Dockerfile Optimizasyonu: Layer Cache ve Multi-Stage Build

| Profil / Araçlar | Açık Portlar |
|---|---|
| `docker build`, `node:22-alpine`, `golang:1.26`, `alpine:3.20` | 8080 |

## Amaç

- `COPY` ve `RUN` sıralamasının layer cache'i nasıl etkilediğini ölçmek.
- `.dockerignore` ile gereksiz dosyaları build context dışında tutmak.
- İki build'in layer'larını karşılaştırıp hangisinin cache'ten geldiğini görmek.
- Multi-stage build ile derleyiciyi nihai image'dan ayırıp Go image'ını yaklaşık 850 MB'tan 20 MB civarına indirmek.

## Ön Koşullar

- Host üzerinde **8080** portu boş olmalıdır.
- İlk build'de npm paketleri ve Go image'ı indirildiği için internet erişimi gerekir.

## Adım Adım Uygulama Rehberi

### Bölüm 1: Layer Cache ve .dockerignore

#### 1. İki Dockerfile'ı Karşılaştırma

```bash
cd ~/docker-labs/lab-04-layer-caching-and-multistage/caching
```

```bash
diff Dockerfile.slow Dockerfile.optimized
```

Docker, Dockerfile'daki her satırın sonucunu bir layer olarak cache'te saklar. Tekrar build ederken satırları yukarıdan aşağı kontrol eder: satır ve kopyaladığı dosyalar değişmediyse layer'ı cache'ten alır (`CACHED`). Bir satırda değişiklik bulduğu anda o satırı ve **altındaki tüm satırları** yeniden çalıştırır.

Bu yüzden `npm install`'ın yeri önemlidir. `server.js` değiştiğinde:

```text
Dockerfile.slow                     Dockerfile.optimized
COPY . .          -> değişti         COPY package*.json ./  -> aynı, CACHED
RUN npm install   -> yeniden çalışır RUN npm install        -> CACHED
                                     COPY . .               -> değişti, yeniden çalışır
```

- `Dockerfile.slow`: `COPY . .` kodu da kopyaladığı için tek satırlık kod değişikliği bu satırı değiştirir. Altındaki `npm install` her build'de paketleri baştan indirir.
- `Dockerfile.optimized`: `npm install`'ın üstünde yalnızca `package*.json` vardır. Kod değişince bu dosyalar aynı kaldığı için paketler cache'ten gelir; yalnızca son `COPY . .` çalışır. Paketler ancak `package.json` değişince yeniden kurulur.

Kural: az değişen satırlar (bağımlılık tanımı) üste, sık değişenler (kaynak kod) alta yazılır.

```bash
cat .dockerignore
```

`.dockerignore`'daki dosyalar build context'e gönderilmez ve `COPY . .` ile image'a girmez. Host'taki `node_modules` image'da kurulan paketlerin üzerine yazılmaz; `*.md` gibi koda ait olmayan bir dosya değişince de `COPY . .` cache'i boşuna bozulmaz.

#### 2. Kötü Sıralı Image'ı Build Etme

```bash
time docker build -f Dockerfile.slow -t cache-demo:slow-v1 .
```

Kaynak kodda küçük bir değişiklik yapın:

```bash
echo '// LAB-DOC-04 degisiklik 1' >> server.js
```

Tekrar build edin ve süreyi karşılaştırın:

```bash
time docker build -f Dockerfile.slow -t cache-demo:slow-v2 .
```

Çıktıda `RUN npm install` adımı yeniden çalışır. Paketler değişmediği hâlde `COPY . .` satırı kod değişikliği yüzünden cache'i geçersiz kıldı.

#### 3. Doğru Sıralı Image'ı Build Etme

```bash
time docker build -f Dockerfile.optimized -t cache-demo:opt-v1 .
```

```bash
echo '// LAB-DOC-04 degisiklik 2' >> server.js
```

```bash
time docker build -f Dockerfile.optimized -t cache-demo:opt-v2 .
```

Çıktıda `RUN npm install` satırının yanında `CACHED` yazar ve build saniyeler içinde biter.

#### 4. Layer'ları Karşılaştırma

`docker history`, image'ın her layer'ını hangi Dockerfile satırının ürettiğini ve boyutunu gösterir:

```bash
docker history cache-demo:opt-v2 --format '{{.CreatedBy}} | {{.Size}}' | head -n 6
```

En büyük layer `RUN npm install`'dır; cache'ten gelmesi bu yüzden build'i hızlandırır.

Cache'ten gelip gelmediğini görmek için aynı Dockerfile'ın iki build'ini karşılaştırın. Her layer'ın içeriğinden hesaplanan bir kimliği (`sha256:...`) vardır; iki image'da aynı kimlik, aynı layer'ın yeniden kullanıldığını gösterir. Aşağıdaki komutlar her image'ın son üç layer'ını listeler.

Kötü sıralı build'ler:

```bash
docker image inspect -f '{{join .RootFS.Layers "\n"}}' cache-demo:slow-v1 | tail -n 3
```

```bash
docker image inspect -f '{{join .RootFS.Layers "\n"}}' cache-demo:slow-v2 | tail -n 3
```

İlk satır aynı, son iki satır farklıdır: kod değişince `COPY . .` layer'ı ve altındaki `npm install` layer'ı yeniden oluştu.

Doğru sıralı build'ler:

```bash
docker image inspect -f '{{join .RootFS.Layers "\n"}}' cache-demo:opt-v1 | tail -n 3
```

```bash
docker image inspect -f '{{join .RootFS.Layers "\n"}}' cache-demo:opt-v2 | tail -n 3
```

İlk iki satır (`COPY package*.json` ve `npm install`) aynıdır; yalnızca son satır (`COPY . .`) farklıdır. Kod değişikliği yalnızca kodun layer'ını yeniledi.

### Bölüm 2: Multi-Stage Build

#### 5. Go Uygulamasını İnceleme

```bash
cd ~/docker-labs/lab-04-layer-caching-and-multistage/go-app
```

```bash
cat Dockerfile.single-stage
```

```bash
cat Dockerfile.multi-stage
```

#### 6. Tek Aşamalı Image'ı Build Etme

```bash
docker build -f Dockerfile.single-stage -t go-app:heavy .
```

#### 7. Çok Aşamalı Image'ı Build Etme

```bash
docker build -f Dockerfile.multi-stage -t go-app:light .
```

#### 8. Boyutları Karşılaştırma

```bash
docker images go-app --format '{{.Repository}}:{{.Tag}} {{.Size}}'
```

`go-app:heavy` yaklaşık 850 MB, `go-app:light` yaklaşık 20 MB'dır (Alpine tabanı + tek Go binary). Hafif image'da Go derleyicisi yoktur:

```bash
docker run --rm --entrypoint sh go-app:light -c 'command -v go || echo "go derleyicisi yok"'
```

#### 9. Hafif Image'ı Çalıştırma

```bash
docker run -d --name go-service -p 8080:8080 go-app:light
```

```bash
curl -s http://localhost:8080
```

Container root ile değil, Dockerfile'daki `USER 10001` kullanıcısıyla çalışır:

```bash
docker exec go-service id -u
```

## Temizlik

```bash
docker rm -f go-service 2>/dev/null || true
```

```bash
docker rmi go-app:heavy go-app:light cache-demo:slow-v1 cache-demo:slow-v2 cache-demo:opt-v1 cache-demo:opt-v2 2>/dev/null || true
```

```bash
sed -i '/LAB-DOC-04 degisiklik/d' ~/docker-labs/lab-04-layer-caching-and-multistage/caching/server.js
```
