# LAB-DOC-01 — Container Yaşam Döngüsü ve Temel Docker CLI

| Profil / Araçlar | Açık Portlar |
|---|---|
| `docker`, `nginx:alpine`, `alpine:3.20`, `curl` | 8080 |

## Amaç

- Image ile container farkını uygulamalı görmek.
- `pull`, `run` ve `-d`, `--name`, `-p`, `-it`, `--rm` bayraklarını kullanmak.
- Container'ı yaşam döngüsü boyunca yönetmek: `stop`, `start`, `restart`, `pause`, `kill`, `rm`.

## Ön Koşullar

- Host üzerinde **8080** portu boş olmalıdır.

## Adım Adım Uygulama Rehberi

### 1. Docker Engine'i Doğrulama

```bash
cd ~/docker-labs/lab-01-container-lifecycle-and-cli
```

```bash
docker version
```

İstemci (Client) ve sunucu (Server / Engine) bölümlerinin ikisi de görünmelidir. Server bölümü yoksa Docker servisi çalışmıyordur.

```bash
docker info | grep -E "Server Version|Storage Driver|Cgroup"
```

```bash
docker ps
```

### 2. Image Çekme ve İnceleme

```bash
docker pull nginx:alpine
```

```bash
docker images nginx
```

```bash
docker image inspect nginx:alpine --format '{{.Os}}/{{.Architecture}} {{.Size}} bayt'
```

`nginx` image'ın adı, `alpine` tag'idir. Tag yazılmazsa Docker `latest` tag'ini kullanır.

### 3. Tek Seferlik ve Etkileşimli Container

`--rm`, container işi bitince otomatik silinmesini sağlar:

```bash
docker run --rm alpine:3.20 echo "Merhaba konteyner"
```

`-it`, container içinde etkileşimli bir terminal açar. İçeride birkaç komut çalıştırıp `exit` ile çıkın:

```bash
docker run --rm -it alpine:3.20 sh
```

```bash
cat /etc/os-release
```

```bash
ps
```

```bash
exit
```

`ps` çıktısında yalnızca `sh` ve `ps` görünür: container kendi izole süreç ağacına sahiptir.

### 4. Arka Planda Web Container'ı Başlatma

`-d` arka planda (detached) çalıştırır, `--name` container'a isim verir, `-p` port eşler:

```bash
docker run -d --name web-life -p 8080:80 nginx:alpine
```

```bash
docker ps
```

```bash
curl -s http://localhost:8080 | grep "<title>"
```

### 5. Durdurma, Başlatma ve Yeniden Başlatma

`stop`, ana sürece önce SIGTERM gönderir; 10 saniye içinde kapanmazsa SIGKILL gönderir:

```bash
docker stop web-life
```

```bash
docker ps -a --filter name=web-life
```

```bash
docker start web-life
```

```bash
docker restart web-life
```

### 6. Pause ve Unpause

`pause`, Linux cgroup **freezer** mekanizmasıyla container'daki tüm süreçleri dondurur; bellek korunur, CPU kullanılmaz. Sinyal gönderilmez.

```bash
docker pause web-life
```

```bash
curl --max-time 2 http://localhost:8080 || echo "Konteyner donduruldu, yanit vermiyor"
```

```bash
docker unpause web-life
```

```bash
curl -s http://localhost:8080 | grep "<title>"
```

### 7. Kill ile Zorla Kapatma

`kill`, beklemeden SIGKILL gönderir. Uygulamaya kapanış işlemleri için süre tanımaz:

```bash
docker kill web-life
```

```bash
docker ps -a --filter name=web-life --format '{{.Names}} {{.Status}}'
```

Çıkış kodu `137` olur (128 + 9 = SIGKILL).

### 8. Container Silme ve Disk Kullanımı

```bash
docker rm web-life
```

`prune`, durmuş container'ları toplu siler. Paylaşılan bir sunucuda başkalarının container'larına dokunmamak için yalnızca bu labın label'ıyla sınırlayın. Önce label'lı iki kısa ömürlü container oluşturun:

```bash
docker run --label lab=lab01 alpine:3.20 true
```

```bash
docker run --label lab=lab01 alpine:3.20 true
```

```bash
docker ps -a --filter label=lab=lab01
```

```bash
docker container prune -f --filter label=lab=lab01
```

```bash
docker system df
```

## Temizlik

```bash
docker rm -f web-life 2>/dev/null || true
```
