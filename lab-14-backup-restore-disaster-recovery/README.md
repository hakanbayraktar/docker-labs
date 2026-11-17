# LAB-DOC-14 — Yedekleme ve Felaket Kurtarma: Image, Volume ve Veritabanı

| Profil / Araçlar | Açık Portlar |
|---|---|
| `docker save/load`, `alpine:3.20`, `postgres:16-alpine`, `pg_dump`, `tar`, `sha256sum` | — |

## Amaç

- `docker save` ve `docker load` ile image'ı internetsiz ortama taşımak.
- Named volume'ü yedeklemek ve yeni bir volume'e geri yüklemek.
- PostgreSQL'i `pg_dump` ile yedekleyip geri yüklemek.
- Yedeklerin bütünlüğünü `sha256sum` ile doğrulamak.

## Ön Koşullar

- Lab dizininde en az 200 MB boş alan.

## Adım Adım Uygulama Rehberi

### 1. Image'ı Dosyaya Kaydetme ve Geri Yükleme

```bash
cd ~/docker-labs/lab-14-backup-restore-disaster-recovery
```

```bash
mkdir -p backups
```

```bash
docker pull alpine:3.20
```

```bash
docker tag alpine:3.20 lab14-tool:1.0
```

```bash
docker save lab14-tool:1.0 | gzip > backups/lab14-tool.tar.gz
```

```bash
ls -lh backups/lab14-tool.tar.gz
```

Tag'i silin ve dosyadan geri yükleyin:

```bash
docker rmi lab14-tool:1.0
```

```bash
docker images lab14-tool
```

```bash
docker load -i backups/lab14-tool.tar.gz
```

```bash
docker images lab14-tool
```

### 2. Volume'ü Dosya Seviyesinde Yedekleme

Test verisi olan bir volume oluşturun:

```bash
docker volume create app-data
```

```bash
docker run --rm -v app-data:/data alpine:3.20 sh -c "mkdir -p /data/uploads && echo 'fatura-2026-001' > /data/uploads/fatura.txt && echo 'ayar=1' > /data/config.ini"
```

Volume'ü salt okunur bağlayan bir yardımcı container ile arşivleyin:

```bash
docker run --rm -v app-data:/source:ro -v "$(pwd)/backups:/target" alpine:3.20 tar -czf /target/app-data.tar.gz -C /source .
```

```bash
tar -tzf backups/app-data.tar.gz
```

### 3. Felaket ve Volume Geri Yükleme

```bash
docker volume rm app-data
```

```bash
docker volume create app-data-restored
```

```bash
docker run --rm -v app-data-restored:/target -v "$(pwd)/backups:/source:ro" alpine:3.20 tar -xzf /source/app-data.tar.gz -C /target
```

```bash
docker run --rm -v app-data-restored:/data alpine:3.20 cat /data/uploads/fatura.txt
```

### 4. Veritabanı Hazırlama

```bash
docker volume create shop-db-data
```

```bash
docker run -d --name shop-db -e POSTGRES_PASSWORD='DevOps2026!' -e POSTGRES_DB=shop -v shop-db-data:/var/lib/postgresql/data postgres:16-alpine
```

```bash
until docker exec shop-db pg_isready -h 127.0.0.1 -U postgres -d shop >/dev/null 2>&1; do sleep 1; done
```

```bash
docker exec shop-db psql -U postgres -d shop -c "CREATE TABLE orders (id serial PRIMARY KEY, item text, qty int); INSERT INTO orders (item, qty) VALUES ('klavye', 2), ('monitor', 1), ('kablo', 5);"
```

### 5. pg_dump ile Mantıksal Yedek

Veritabanı çalışırken tutarlı bir yedek alın:

```bash
docker exec shop-db pg_dump -U postgres -d shop --clean --if-exists > backups/shop.sql
```

```bash
grep -E "CREATE TABLE|COPY public.orders" backups/shop.sql
```

### 6. Tutarlı Dosya Yedeği İçin Container'ı Durdurma

Dosya seviyesinde yedek gerekiyorsa veritabanı önce durdurulur:

```bash
docker stop shop-db
```

```bash
docker run --rm -v shop-db-data:/source:ro -v "$(pwd)/backups:/target" alpine:3.20 tar -czf /target/shop-db-files.tar.gz -C /source .
```

```bash
docker start shop-db
```

### 7. Yedeklerin Bütünlüğünü Kaydetme

```bash
cd backups && sha256sum lab14-tool.tar.gz app-data.tar.gz shop.sql shop-db-files.tar.gz > SHA256SUMS && cd ..
```

```bash
cat backups/SHA256SUMS
```

### 8. Veritabanı Felaketi ve Geri Yükleme

Veritabanı container'ını ve volume'ünü tamamen silin:

```bash
docker rm -f shop-db
```

```bash
docker volume rm shop-db-data
```

Geri yüklemeden önce yedeklerin bozulmadığını doğrulayın:

```bash
cd backups && sha256sum -c SHA256SUMS && cd ..
```

Boş bir veritabanı başlatın:

```bash
docker run -d --name shop-db-new -e POSTGRES_PASSWORD='DevOps2026!' -e POSTGRES_DB=shop -v shop-db-new-data:/var/lib/postgresql/data postgres:16-alpine
```

```bash
until docker exec shop-db-new pg_isready -h 127.0.0.1 -U postgres -d shop >/dev/null 2>&1; do sleep 1; done
```

SQL yedeğini geri yükleyin:

```bash
docker exec -i shop-db-new psql -U postgres -d shop -q < backups/shop.sql
```

```bash
docker exec shop-db-new psql -U postgres -d shop -c "SELECT item, qty FROM orders ORDER BY id;"
```

## Temizlik

```bash
docker rm -f shop-db shop-db-new 2>/dev/null || true
```

```bash
docker volume rm app-data app-data-restored shop-db-data shop-db-new-data 2>/dev/null || true
```

```bash
docker rmi lab14-tool:1.0 2>/dev/null || true
```

```bash
rm -rf backups
```
