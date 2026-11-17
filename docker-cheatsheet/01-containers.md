# Docker Container Yönetimi Komutları (Container Cheatsheet)

Container'ların yaşam döngüsünü başlatma, durdurma, canlı hata ayıklama ve kaynak izleme komutları.

---

## 1. Container Başlatma ve Çalıştırma (`docker run`)

Yeni bir image'dan izole bir container oluşturur ve başlatır.

### En Sık Kullanılan Temel Başlatma
```bash
docker run -d --name web-server -p 8080:80 nginx:alpine
```
* **Açıklama:** `nginx:alpine` image'ını arka planda (`-d`), `web-server` adıyla ve sunucunun 8080 portunu container'ın 80 portuna bağlayarak çalıştırır.

### Etkileşimli Terminal ile Çalıştırma
```bash
docker run -it --rm ubuntu:24.04 bash
```
* **Açıklama:** Terminali doğrudan container'ın içine bağlar (`-it`). Container'dan çıkıldığında (`exit`) container'ı otomatik siler (`--rm`).

### Ortam Değişkeni (Environment Variable) Tanımlama
```bash
docker run -d --name my-db -e POSTGRES_PASSWORD=secret123 postgres:16-alpine
```
* **Açıklama:** `-e` parametresiyle container içine ortam değişkeni enjekte eder.

### Otomatik Yeniden Başlatma (Restart Policy)
```bash
docker run -d --name critical-api --restart always -p 3000:3000 my-api:1.0
```
* **Açıklama:** Container çökerse veya Docker daemon yeniden başlarsa container'ı otomatik olarak yeniden ayağa kaldırır (`always` / `unless-stopped`).

---

## 2. Container Listeleme ve Durum Kontrolü (`docker ps`)

### Çalışan Container'ları Listeleme
```bash
docker ps
```

### Durmuş (Exited) Dahil Tüm Container'ları Listeleme
```bash
docker ps -a
```

### Özel Formatla Listeleme (Yalnızca İsim, Durum ve Port)
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### Yalnızca Container ID'lerini Listeleme (Toplu İşlemler İçin)
```bash
docker ps -q
```

---

## 3. Yaşam Döngüsü: Durdurma, Başlatma ve Silme

### Container'ı Nazikçe Durdurma (SIGTERM ➔ SIGKILL)
```bash
docker stop web-server
```
* **Açıklama:** Container'daki ana sürece `SIGTERM` gönderir, 10 saniye içinde kapanmazsa `SIGKILL` ile zorlar.

### Container'ı Anında Zorla Durdurma (SIGKILL)
```bash
docker kill web-server
```

### Durmuş Container'ı Yeniden Başlatma
```bash
docker start web-server
```

### Container'ı Yeniden Başlatma (Restart)
```bash
docker restart web-server
```

### Container'ı Geçici Olarak Dondurma ve Çözme (cgroups Freezer)
```bash
docker pause web-server
docker unpause web-server
```
* **Açıklama:** Süreci RAM'de dondurur, CPU tüketimini sıfırlar; durdurmadan bekletir.

### Durmuş Container'ı Silme
```bash
docker rm web-server
```

### Çalışan Container'ı Zorla Silme
```bash
docker rm -f web-server
```

### Tüm Durmuş Container'ları Tek Komutla Temizleme
```bash
docker container prune -f
```

---

## 4. Canlı Teftiş ve Hata Ayıklama (Troubleshooting)

### Çalışan Container'ın İçine Canlı Shell Açma
```bash
docker exec -it web-server sh
```
* **Açıklama:** Container içine girip komut çalıştırmayı sağlar (Alpine image'larında `sh`, Debian/Ubuntu image'larında `bash`).

### Container İçinde Tek Bir Komut Çalıştırıp Çıktısını Alma
```bash
docker exec web-server nginx -t
```
* **Açıklama:** Container'ın içine girmeden Nginx konfigürasyon sözdizimini test eder.

### Container Loglarını İnceleme
```bash
docker logs web-server
```

### Canlı Log Takibi (Tail -f Gibi)
```bash
docker logs -f --tail 50 web-server
```

### Dosya Kopyalama (Host ➔ Container veya Container ➔ Host)
```bash
# Host'tan konteynere dosya kopyalama:
docker cp index.html web-server:/usr/share/nginx/html/index.html

# Konteynerden host'a dosya kopyalama:
docker cp web-server:/etc/nginx/nginx.conf ./nginx.conf
```

### Container Dosya Sistemindeki Değişiklikleri İnceleme (`diff`)
```bash
docker diff web-server
```
* **Açıklama:** Image'ın orijinal haline göre eklenen (`A`), silinen (`D`) veya değiştirilen (`C`) dosyaları gösterir.

### Container İçindeki Süreçleri (Process) Görme
```bash
docker top web-server
```

### Anlık CPU ve Bellek Tüketimi (Canlı İstatistik)
```bash
docker stats --no-stream
```

### Container'ın Tüm JSON Metadata Bilgilerini İnceleme (`inspect`)
```bash
# Tüm yapılandırmayı okuma:
docker inspect web-server

# Yalnızca IP adresini filtreleme:
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' web-server

# Konteynerin OOMKilled durumunu okuma:
docker inspect -f '{{.State.OOMKilled}}' web-server
```
