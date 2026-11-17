# Docker Image Yönetimi Komutları (Image Cheatsheet)

Image build, tag'leme, layer analizi, registry'ye gönderme ve image arşivleme komutları.

---

## 1. Image Build (`docker build`)

Dockerfile talimatlarını okuyarak layer'lardan oluşan bir Docker image'ı üretir.

### Temel Image Build
```bash
docker build -t my-app:1.0 .
```
* **Açıklama:** Bulunduğunuz dizindeki (`.`) Dockerfile'ı kullanarak `my-app:1.0` adında image build eder.

### Farklı Bir Dockerfile Konumu Belirtme (`-f`)
```bash
docker build -f docker/Dockerfile.prod -t my-app:prod .
```

### Cache'i Devre Dışı Bırakarak Sıfırdan Build (`--no-cache`)
```bash
docker build --no-cache -t my-app:fresh .
```
* **Açıklama:** Tüm layer'ları (`RUN apt-get update` vb.) cache'ten okumadan yeniden çalıştırır.

### Multi-Stage Build İçinden Belirli Bir Aşamayı Build Etme (`--target`)
```bash
docker build --target builder -t my-app:builder .
```
* **Açıklama:** Yalnızca `AS builder` aşamasına kadar build yapar (test veya build artifact'larını incelemek için).

### Build Sırasında Değişken Geçme (`--build-arg`)
```bash
docker build --build-arg APP_VERSION=2.4.0 -t my-app:2.4.0 .
```

---

## 2. Image'ları Listeleme ve İnceleme

### Yerel Sistemdeki Image'ları Listeleme
```bash
docker images
```

### Yalnızca İsim ve Boyut Bilgisi Görme
```bash
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
```

### Boşta Kalan (Dangling - `<none>`) Image'ları Filtreleme
```bash
docker images -f "dangling=true"
```

### Image'ın Layer'larını ve Boyut Dağılımını İnceleme (`history`)
```bash
docker history my-app:1.0
```
* **Açıklama:** Image'ın her bir layer'ının hangi komutla (`COPY`, `RUN` vb.) üretildiğini ve boyutunu gösterir.

### Image Metadata Bilgilerini Okuma (`inspect`)
```bash
# İmajın çalışma kullanıcısını (User) görme:
docker inspect -f '{{.Config.User}}' my-app:1.0

# İmajın varsayılan CMD ve ENTRYPOINT bilgisini görme:
docker inspect -f 'Entrypoint: {{.Config.Entrypoint}}, Cmd: {{.Config.Cmd}}' my-app:1.0
```

---

## 3. Image Tag'leme ve Registry (Push / Pull)

### Image'ı Docker Hub İçin Tag'leme
```bash
docker tag my-app:1.0 <KULLANICI_ADI>/devops-app-pub:nginx-1.0
```
* **Format:** `<KULLANICI_ADI>/<REPO_ADI>:<ETİKET>`

### Image'ı Özel Registry (Örn: Harbor) İçin Tag'leme
```bash
docker tag my-app:1.0 127.0.0.1:18444/devops-public/my-app:1.0
```
* **Format:** `<REGISTRY_HOST>:<PORT>/<PROJE_ADI>/<IMAJ_ADI>:<ETİKET>`

### Image'ı Registry'ye Yükleme (`push`)
```bash
# Docker Hub'a gönderme:
docker push <KULLANICI_ADI>/devops-app-pub:nginx-1.0

# Harbor'a gönderme:
docker push 127.0.0.1:18444/devops-public/my-app:1.0
```

### Image'ı Registry'den İndirme (`pull`)
```bash
docker pull alpine:3.20
docker pull 127.0.0.1:18444/devops-public/my-app:1.0
```

---

## 4. Image Silme ve Temizlik

### Belirli Bir Image'ı Silme
```bash
docker rmi my-app:1.0
```

### Image'ı Zorla Silme (Container Tarafından Kullanılıyorsa)
```bash
docker rmi -f my-app:1.0
```

### Kullanılmayan (Dangling) Image'ları Temizleme
```bash
docker image prune -f
```

### Container'lar Tarafından Kullanılmayan Tüm Image'ları Temizleme
```bash
docker image prune -a -f
```

---

## 5. Image Arşivleme ve Çevrimdışı Taşıma (Air-Gapped)

İnternet erişimi olmayan kapalı devre sunuculara image aktarmak için kullanılır.

### Image'ı `.tar` Arşivi Olarak Kaydetme (`docker save`)
```bash
docker save -o my-app.tar my-app:1.0
```

### `.tar.gz` Olarak Sıkıştırarak Kaydetme
```bash
docker save my-app:1.0 | gzip > my-app.tar.gz
```

### `.tar` Arşivinden Image'ı Geri Yükleme (`docker load`)
```bash
docker load -i my-app.tar
# Veya sıkıştırılmış dosyadan:
docker load < my-app.tar.gz
```
