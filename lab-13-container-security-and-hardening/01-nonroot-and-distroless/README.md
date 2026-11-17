# LAB-DOC-13-01 — Non-Root Kullanıcı ve Distroless Image

| Profil / Araçlar | Açık Portlar |
|---|---|
| `docker build`, `python:3.12-alpine`, `golang:1.26-alpine`, `gcr.io/distroless/static-debian12:nonroot` | 8080 |

## Amaç

- `USER` direktifi olmayan image'ların root (UID 0) olarak çalıştığını görmek.
- Root çalışan bir container'ın bağlanan host dizinine root sahipli dosyalar yazabildiğini görmek.
- `USER 10001` ile aynı işlemin engellendiğini doğrulamak.
- Shell, paket yöneticisi ve araç içermeyen distroless image'la saldırı yüzeyini küçültmek.

## Ön Koşullar

- Host üzerinde **8080** portu boş olmalıdır.

## Adım Adım Uygulama Rehberi

### 1. Root Çalışan Image

```bash
cd ~/docker-labs/lab-13-container-security-and-hardening/app
```

```bash
cat Dockerfile.bad
```

```bash
docker build -f Dockerfile.bad -t sec-demo:root .
```

```bash
docker run --rm sec-demo:root id
```

### 2. Root Container'ın Host Dizinine Etkisi

```bash
mkdir -p ./shared
```

```bash
docker run --rm -v "$(pwd)/shared:/shared" sec-demo:root touch /shared/root-dosyasi
```

```bash
ls -l ./shared
```

Dosyanın sahibi host'ta `root`'tur. Container, host'ta sizin yetkinizin üzerinde bir işlem yaptı.

### 3. Root Olmayan Kullanıcı

```bash
cat Dockerfile.hardened
```

```bash
docker build -f Dockerfile.hardened -t sec-demo:hardened .
```

```bash
docker run --rm sec-demo:hardened id
```

```bash
docker run --rm -v "$(pwd)/shared:/shared" sec-demo:hardened touch /shared/deneme || echo "ENGELLENDI: UID 10001 host dizinine yazamaz"
```

### 4. Distroless Image

```bash
cat Dockerfile.distroless
```

```bash
docker build -f Dockerfile.distroless -t sec-demo:distroless .
```

```bash
docker run -d --name test-distroless -p 8080:8080 sec-demo:distroless
```

```bash
curl -s http://localhost:8080
```

Container'da shell yoktur:

```bash
docker exec test-distroless sh || echo "KABUK YOK: distroless imajda sh bulunmuyor"
```

Kullanıcıyı ve image boyutlarını karşılaştırın:

```bash
docker inspect -f '{{.Config.User}}' sec-demo:distroless
```

```bash
docker images sec-demo --format '{{.Tag}} {{.Size}}'
```

Distroless image'da hata ayıklamak için shell açılamaz. Teşhis, uygulama logları (`docker logs`) ve aynı ağa bağlanan ayrı bir araç container'ıyla yapılır.

## Temizlik

```bash
docker rm -f test-distroless 2>/dev/null || true
```

```bash
docker run --rm -v "$(pwd)/shared:/shared" alpine:3.20 rm -f /shared/root-dosyasi
```

```bash
rm -rf ./shared
```

```bash
docker rmi sec-demo:root sec-demo:hardened sec-demo:distroless 2>/dev/null || true
```
