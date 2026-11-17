# Docker Güvenlik, Kaynak Sınırları ve Çıkış Kodları (Security Cheatsheet)

Linux cgroups kısıtlamaları, non-root çalıştırma, zafiyet taraması ve çıkış kodları referansı.

---

## 1. Kaynak Kısıtlamaları (Linux cgroups)

Container'ların host sunucunun tüm CPU ve RAM'ini tüketerek sistemi kilitlemesini önler.

### Bellek (RAM) ve Swap Sınırı Belirleme
```bash
docker run -d --name limited-app -m 512m --memory-swap 1g my-app:1.0
```
* **Açıklama:** Container en fazla 512 MB fiziksel RAM ve toplam 1 GB (RAM + Swap) kullanabilir. Limiti aşarsa Linux kernel OOM Killer devreye girer.

### CPU Çekirdek Kotası Tanımlama
```bash
docker run -d --name limited-api --cpus 1.5 my-app:1.0
```
* **Açıklama:** Container'ın aynı anda en fazla 1.5 çekirdek güç tüketmesine izin verir.

### Fork Bomb ve Süreç Sayısı Sınırı (`--pids-limit`)
```bash
docker run -d --name secure-app --pids-limit 100 my-app:1.0
```
* **Açıklama:** Container içinde aynı anda en fazla 100 process açılabilir; kontrolsüz thread/process sızıntılarını engeller.

---

## 2. Container Güvenliği (Hardening)

### Non-Root Kullanıcı ile Çalıştırma (`--user`)
```bash
docker run -d --name secure-app --user 10001:10001 my-app:1.0
```
* **Açıklama:** Container içindeki süreçleri root (UID 0) yerine yetkisiz bir kullanıcı kimliğiyle çalıştırır (Container breakout riskini önler).

### Salt Okunur Kök Dosya Sistemi (`--read-only`)
```bash
docker run -d --name hardened-nginx --read-only --tmpfs /tmp --tmpfs /var/cache/nginx -p 8080:80 nginx:alpine
```
* **Açıklama:** Container'ın kök dosya sistemine yazmayı tamamen engeller; yalnızca `/tmp` ve cache dizinlerini RAM üzerinde geçici açar.

### Linux Kernel Yetkilerini Sıfırlama (`--cap-drop`)
```bash
docker run -d --name minimal-caps --cap-drop=ALL --cap-add=NET_BIND_SERVICE my-app:1.0
```
* **Açıklama:** Container'ın gereksiz tüm Linux kernel yetkilerini (`CAP_SYS_ADMIN` vb.) iptal eder; yalnızca düşük port dinleme izni verir.

---

## 3. Güvenlik ve Zafiyet Taraması (Trivy CVE Scan)

### Image'ı Güvenlik Açıklarına Karşı Tarama
```bash
trivy image my-app:1.0
```

### Yalnızca Kritik (CRITICAL) ve Yüksek (HIGH) Zafiyetleri Filtreleme
```bash
trivy image --severity HIGH,CRITICAL my-app:1.0
```

---

## 4. Container Çıkış Kodları (Exit Codes) Referans Tablosu

| Çıkış Kodu | Anlamı | Kök Neden & Teşhis Yöntemi |
| :---: | :--- | :--- |
| **0** | Başarılı (Success) | Container işini tamamlayıp normal şekilde kapandı (Örn: batch job). |
| **1** | Uygulama Hatası (App Error) | Kod içinde exception, syntax hatası veya eksik dosya. `docker logs` ile inceleyin. |
| **125** | Docker Engine Hatası | `docker run` parametre hatası (Örn: geçersiz cgroup ayarı). |
| **126** | Çalıştırılamaz (Not Executable) | `ENTRYPOINT` dosyasında çalıştırma izni yok (`chmod +x` eksik). |
| **127** | Komut Bulunamadı (Command Not Found) | `CMD` veya `ENTRYPOINT` belirtilen binary image içinde yok (PATH hatası). |
| **137** | Zorla Kapatıldı (SIGKILL / OOMKilled) | **Bellek Yetersizliği!** Linux Kernel OOM Killer container'ı öldürdü (`128 + 9 = 137`). `docker inspect -f '{{.State.OOMKilled}}'` ile doğrulayın. |
| **139** | Bellek Erişim Hatası (Segmentation Fault) | C/C++ veya derlenmiş binary bellek taşması (`SIGSEGV`, `128 + 11 = 139`). |
| **143** | Nazik Kapatma (SIGTERM) | `docker stop` veya Kubernetes tarafından kontrollü durduruldu (`128 + 15 = 143`). |
