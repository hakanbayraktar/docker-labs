# LAB-DOC-05-06 — PHP 8.3 API Paketleme

| Profil / Araçlar | Açık Portlar |
|---|---|
| `php:8.3-cli-alpine`, `composer:2`, `curl` | 19001 |

## Amaç

- PHP uygulamasını Composer bağımlılıklarıyla image'a paketlemek.
- `docker-php-ext-install` ile PHP eklentisi (OPcache) kurmak.
- Composer'ı ayrı bir image'dan `COPY --from` ile almak ve uygulamayı `www-data` kullanıcısıyla çalıştırmak.

## Ön Koşullar

- Host üzerinde **19001** portu boş olmalıdır. Aynı portu kullanan başka bir alt lab çalışıyorsa önce onu silin.
- Host'a programlama dili veya SDK kurmayın; build ortamı image'ın içindedir.

## Adım Adım Uygulama Rehberi

### 1. Dosyaları İnceleme

```bash
cd ~/docker-labs/lab-05-polyglot-application-packaging/06-php
```

```bash
ls -la
```

```bash
cat Dockerfile
```

### 2. Image'ı Build Etme

```bash
docker build -t app-php:1.0 .
```

```bash
docker images app-php:1.0
```

### 3. Container'ı Çalıştırma

```bash
docker run -d --name test-php -p 19001:8000 app-php:1.0
```

### 4. Uç Noktaları Test Etme

```bash
curl -s http://localhost:19001/
```

```bash
curl -s http://localhost:19001/health
```

Tarayıcıdan `http://<SUNUCU-IP>:19001` adresini de açabilirsiniz.

### 5. Çalışan Kullanıcıyı Doğrulama

```bash
docker exec test-php id
```

UID değeri `82` olmalıdır; uygulama root ile çalışmıyor.

<details>
<summary><strong>Notlar ve ek deney</strong></summary>

`php -S` PHP'nin yerleşik geliştirme sunucusudur ve labı sade tutmak için kullanılır. Üretimde PHP-FPM ile Nginx birlikte kullanılır.

</details>

## Temizlik

```bash
docker rm -f test-php
```

```bash
docker rmi app-php:1.0
```
