# Docker Sistem, Bakım ve Temizlik Komutları (System & Cleanup Cheatsheet)

Disk alanı analizi, BuildKit cache'ini temizleme ve kullanılmayan kaynakları kaldırma komutları.

---

## 1. Disk Kullanım Analizi (`docker system df`)

Docker'ın diskte ne kadar yer kapladığını kategorik olarak gösterir.

### Genel Disk Kullanım Özeti
```bash
docker system df
```
* **Örnek Çıktı:**
  * `Images`: Toplam image boyutu ve geri kazanılabilir alan (Reclaimable).
  * `Containers`: Container'ların writable layer boyutu.
  * `Local Volumes`: Kalıcı disk alanlarının boyutu.
  * `Build Cache`: Build layer cache boyutu.

### Ayrıntılı Disk Kullanım Dökümü
```bash
docker system df -v
```

---

## 2. Kademeli Temizlik Komutları (`prune`)

> **Uyarı:** `prune` komutları yalnızca sizin değil, sunucudaki bütün kaynaklara uygulanır. Paylaşılan bir lab sunucusunda kullanmayın; kendi kaynaklarınızı adıyla, `docker compose down` ile ya da `--filter label=<label>` ile silin. Aşağıdaki komutlar kişisel makine ve tek sahipli sunucular içindir.

### Durmuş Container'ları ve Boşta Kalan Kaynakları Temizleme (Volume'lere Dokunmaz)
```bash
docker system prune -f
```
* **Neleri Siler:**
  * Tüm durmuş (Exited) container'lar.
  * İsmi olmayan (`<none>`) boşta kalan (dangling) image'lar.
  * Hiçbir container tarafından kullanılmayan ağlar.
  * *Not: Named Volume'lere ve tag'li image'lara DOKUNMAZ.*

### Agresif Image Temizliği (Kullanılmayan Tüm Image'lar Dahil)
```bash
docker system prune -a -f
```
* **Neleri Siler:**
  * Yukarıdakilere ek olarak, şu an çalışan bir container tarafından kullanılmayan **tüm tag'li image'ları da** siler.

### Build Cache'ini (BuildKit) Temizleme
```bash
docker builder prune -f
# Veya tüm derleme geçmişini temizleme:
docker builder prune -a -f
```

### Yalnızca Boşta Kalan Volume'leri Temizleme
```bash
docker volume prune -f
```

---

## 3. Sistem Bilgisi ve Canlı Olay Akışı (Event Stream)

### Docker Engine Bilgilerini İnceleme (`info`)
```bash
docker info
```
* **Önemli Bilgiler:** Cgroup sürümü (`cgroup v2`), Storage Driver (`overlay2`), Docker Root Dir (`/var/lib/docker`), Toplam bellek ve CPU kısıtları.

### Canlı Container Olaylarını Dinleme (`events`)
```bash
docker events
```
* **Açıklama:** Terminali açık bırakarak container'ların başlatılma, durdurulma, OOMKilled ve silinme olaylarını anlık olarak izler.
