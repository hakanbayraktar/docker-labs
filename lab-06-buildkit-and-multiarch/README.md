# LAB-DOC-06 — BuildKit ve Buildx: Cache, Gizli Bilgi ve Çoklu Mimari Image

| Profil / Araçlar | Açık Portlar |
|---|---|
| `docker buildx`, BuildKit, `python:3.12-slim`, `golang:1.26-alpine`, `registry:2` | 5000 (yalnızca 127.0.0.1) |

## Amaç

- `RUN --mount=type=cache` ile paket indirme cache'ini build'ler arasında korumak.
- Build sırasında gereken gizli bilgiyi (token) `ARG` yerine `--mount=type=secret` ile kullanıp image'a sızmasını engellemek.
- Tek komutla hem `linux/amd64` hem `linux/arm64` için image build etmek; emülasyon yerine çapraz derleme kullanmak.
- Çoklu mimari image'ın manifest listesini ve SBOM bilgisini incelemek.

## Ön Koşullar

- `docker buildx version` çalışmalıdır.
- Host üzerinde **5000** portu boş olmalıdır.

## Adım Adım Uygulama Rehberi

### 1. Buildx'i Tanıma

```bash
cd ~/docker-labs/lab-06-buildkit-and-multiarch
```

```bash
docker buildx version
```

```bash
docker buildx ls
```

BuildKit, Docker'ın build motorudur; `docker buildx` onu yöneten komuttur. Listedeki her satır bir builder'dır: `*` kullanılan builder'ı, `PLATFORMS` builder'ın kendi üzerinde çalıştırabildiği platformları gösterir. `default` builder'ı sunucunun mimarisini (`linux/amd64` ve aynı ailedeki birkaç varyantı) çalıştırır; listede `linux/arm64` yoktur. 5. adımda arm64 image'ını yine de nasıl ürettiğimizi göreceksiniz.

### 2. Cache Mount ile Paket Cache'i

```bash
cat cache-mount/Dockerfile.no-cache cache-mount/Dockerfile.cache-mount
```

İki Dockerfile da `numpy` ve `pandas` kurar; tek fark `RUN` satırıdır. Layer cache (LAB-04) ya hep ya hiç çalışır: `requirements.txt` değiştiğinde `pip install` yeniden çalışır ve bütün paketleri baştan indirir. `--mount=type=cache` ise BuildKit'in build'ler arasında sakladığı bir klasördür; yalnızca o `RUN` adımı sırasında `/root/.cache/pip` yoluna bağlanır ve image'a girmez. Layer cache bozulsa bile pip indirdiği paketleri orada bulur.

İlk build paketleri indirir ve cache mount'a yazar. `-q` build çıktısını gizler, yalnızca image kimliğini yazar:

```bash
docker build -q -f cache-mount/Dockerfile.cache-mount -t lab06-pip:cache-mount cache-mount/
```

Şimdi iki Dockerfile'ı da `--no-cache` ile build edin. `--no-cache` layer cache'ini kullanmaz, yani `pip install` iki build'de de yeniden çalışır; cache mount'a dokunmaz.

Cache mount olmadan paketler internetten yeniden indirilir (`Downloading`):

```bash
docker build --no-cache --progress=plain -f cache-mount/Dockerfile.no-cache -t lab06-pip:no-cache cache-mount/ 2>&1 | grep -E "Downloading (numpy|pandas)" | head -n 2
```

Cache mount ile pip aynı paketleri cache'ten alır (`Using cached`):

```bash
docker build --no-cache --progress=plain -f cache-mount/Dockerfile.cache-mount -t lab06-pip:cache-mount cache-mount/ 2>&1 | grep -E "Using cached (numpy|pandas)" | head -n 2
```

Image çalışır; cache klasörü image'da değildir:

```bash
docker run --rm lab06-pip:cache-mount
```

Çıktı: `pandas 2.2.3`

### 3. Gizli Bilgiyi ARG ile Vermenin Riski

```bash
echo -n "lab06-gizli-token-123456" > api_token.txt
```

```bash
cat secrets/Dockerfile.secret-bad
```

```bash
docker build -q -f secrets/Dockerfile.secret-bad --build-arg API_TOKEN="$(cat api_token.txt)" -t lab06-secret:bad secrets/
```

`--build-arg` ile verilen değer, onu kullanan `RUN` satırıyla birlikte image'ın geçmişine yazılır. Image'ı çeken herkes token'ı açık metin olarak görebilir:

```bash
docker history --no-trunc lab06-secret:bad | grep -o "API_TOKEN=[^ ]*"
```

Çıktıda `API_TOKEN=lab06-gizli-token-123456` görünür. Image registry'ye gönderildiyse token sızmış demektir; değiştirilmesi gerekir.

### 4. Secret Mount ile Güvenli Kullanım

```bash
cat secrets/Dockerfile.secret-good
```

`--mount=type=secret`, token dosyasını yalnızca o `RUN` adımı sürerken `/run/secrets/api_token` yolunda gösterir. Adım bitince dosya kaldırılır; ne layer'a ne geçmişe yazılır.

```bash
docker build -q -f secrets/Dockerfile.secret-good --secret id=api_token,src=api_token.txt -t lab06-secret:good secrets/
```

Build sırasında token okundu; uzunluğu (`24`) log dosyasına yazıldı:

```bash
docker run --rm lab06-secret:good
```

Token image'ın geçmişinde yoktur:

```bash
docker history --no-trunc lab06-secret:good | grep -q "lab06-gizli-token" && echo "Token gecmiste VAR" || echo "Token gecmiste yok"
```

Dosya sisteminde de yoktur; komut `ls: /run/secrets: No such file or directory` yazar:

```bash
docker run --rm lab06-secret:good ls /run/secrets 2>&1 || true
```

### 5. Çoklu Mimari Build

Çoklu mimari image, tek tag altında her mimari için ayrı bir image taşır ve registry üzerinden paylaşılır. Yerel bir registry başlatın:

```bash
docker run -d --name lab06-registry -p 127.0.0.1:5000:5000 registry:2
```

Build'i ayrı bir builder'da yapın. `docker-container` sürücüsü builder'ı kendi container'ında çalıştırır; sonucu `--push` ile doğrudan registry'ye gönderir ve iş bitince cache'iyle birlikte silinir. `network=host`, builder container'ının `localhost:5000` adresine ulaşmasını sağlar:

```bash
docker buildx create --name lab06-builder --driver docker-container --driver-opt network=host
```

`--bootstrap` builder container'ını başlatır (ilk seferde `moby/buildkit` image'ını indirir):

```bash
docker buildx inspect lab06-builder --bootstrap | grep -E "Driver|Platforms"
```

`Platforms` satırında yine `linux/arm64` yoktur. Sunucuda arm64 programı çalıştıracak emülatör (QEMU) kurulu değildir; bu labda gerek de yoktur:

```bash
cat multiarch/Dockerfile
```

- `FROM --platform=$BUILDPLATFORM`: derleme aşaması her zaman sunucunun kendi mimarisinde (amd64) çalışır.
- `GOARCH=$TARGETARCH`: Go, amd64 üzerinde arm64 için binary üretir (çapraz derleme). `TARGETARCH` değerini BuildKit her platform için doldurur.
- `FROM scratch` + `COPY`: son aşamada hiçbir komut çalışmaz, yalnızca binary kopyalanır. Bu yüzden arm64 kodu sunucuda hiç çalıştırılmaz.

İki mimari için build edip registry'ye gönderin. `--sbom` image'daki paket listesini, `--provenance` image'ın nasıl build edildiğini (Dockerfile, build argümanları, kaynak) image'a ek kayıt olarak koyar:

```bash
docker buildx build --builder lab06-builder \
  --platform linux/amd64,linux/arm64 \
  --sbom=true --provenance=mode=max \
  -t localhost:5000/lab06-multiarch:1.0 \
  --push multiarch/
```

Çıktıdaki `[linux/amd64->arm64 builder 4/4] RUN ... GOARCH=arm64 go build` satırı, arm64 binary'sinin amd64 üzerinde derlendiğini gösterir.

### 6. Manifest Listesi ve Çalıştırma

```bash
docker buildx imagetools inspect localhost:5000/lab06-multiarch:1.0
```

Tag, bir **manifest listesini** (`image.index`) gösterir. Listede dört kayıt vardır:

- `Platform: linux/amd64` ve `Platform: linux/arm64`: iki mimarinin image'ları.
- `Platform: unknown/unknown`: her image'ın SBOM ve provenance kaydı (attestation). `vnd.docker.reference.digest` hangi image'a ait olduğunu gösterir.

Docker, listeden sunucunun mimarisine uygun image'ı çeker. arm64 bir sunucuda (ör. AWS Graviton) aynı komut arm64 image'ını çeker:

```bash
docker run --rm localhost:5000/lab06-multiarch:1.0
```

Çıktı: `Merhaba! Bu binary linux/amd64 icin derlendi.`

### 7. SBOM'u İnceleme

SBOM (Software Bill of Materials), image'daki paketlerin listesidir. Bir paketin açığı duyurulduğunda hangi image'ların etkilendiği SBOM'dan bulunur. Aşağıdaki komut SBOM içindeki adları listeler; image'da yalnızca tek bir Go binary'si olduğu için liste kısadır:

```bash
docker buildx imagetools inspect localhost:5000/lab06-multiarch:1.0 --format '{{json .SBOM}}' | grep -o '"name":"[^"]*"' | sort -u | head -n 10
```

### 8. Builder Cache'i

Builder, layer'ları ve indirdiği image'ları kendi cache'inde tutar. `Reclaimable` silinebilir alanı, `Total` toplamı gösterir:

```bash
docker buildx du --builder lab06-builder | tail -n 2
```

Bu cache builder'a aittir; builder silinince cache de silinir.

## Temizlik

```bash
docker buildx rm lab06-builder
```

Builder container'ı için indirilen BuildKit image'ını da silin:

```bash
docker rmi moby/buildkit:buildx-stable-1 2>/dev/null || true
```

`-v`, registry image'ının oluşturduğu anonim volume'ü de siler:

```bash
docker rm -f -v lab06-registry
```

```bash
docker rmi lab06-pip:no-cache lab06-pip:cache-mount lab06-secret:bad lab06-secret:good localhost:5000/lab06-multiarch:1.0 registry:2 2>/dev/null || true
```

```bash
rm -f api_token.txt
```
