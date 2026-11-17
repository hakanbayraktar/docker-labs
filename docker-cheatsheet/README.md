# Docker Komut Rehberi ve Hızlı Başvuru (Docker Cheatsheet)

En sık kullanılan Docker komutları, konulara göre ayrılmış kısa başvuru dosyaları.

---

## Konu Başlıklarına Göre Modüler Rehberler

İncelemek istediğiniz konunun detaylı dokümanına aşağıdaki tablodan doğrudan erişebilirsiniz:

| No | Modül / Konu | Açıklama | Dosya Bağlantısı |
|:---:|:---|:---|:---:|
| **01** | **Container Yönetimi** | Container başlatma, yaşam döngüsü (`stop`/`rm`), canlı shell (`exec`), loglar, dosya kopyalama (`cp`), canlı kaynak izleme (`stats`) ve `inspect`. | [**01-containers.md**](01-containers.md) |
| **02** | **Image Yönetimi** | Image build (`build`), multi-stage target'lar, image tag'leme (`tag`), Docker Hub / Harbor'a gönderme (`push`/`pull`), `save`/`load`. | [**02-images.md**](02-images.md) |
| **03** | **Depolama (Storage)** | Named Volume, Bind Mount (canlı kod bağlama, `:ro`), tmpfs (RAM mount) ve Helper Container ile veritabanı yedekleme/kurtarma. | [**03-storage.md**](03-storage.md) |
| **04** | **Ağ Yönetimi (Networking)** | Bridge, host ve none network driver'ları, dahili DNS (`127.0.0.11`) ile servis keşfi, canlı ağa bağlama (`connect`) ve izolasyon. | [**04-networking.md**](04-networking.md) |
| **05** | **Docker Compose** | Çok container'lı mimarileri tek komutla yönetme (`up -d`, `down -v`), canlı log takibi, servis ölçekleme (`--scale`) ve YAML doğrulama. | [**05-compose.md**](05-compose.md) |
| **06** | **Sistem, Bakım ve Temizlik** | Disk alanı analizi (`system df`), güvenli ve agresif temizlik (`system prune`), BuildKit cache temizliği ve olay akışı (`events`). | [**06-system-and-cleanup.md**](06-system-and-cleanup.md) |
| **07** | **Güvenlik ve Hata Ayıklama** | Linux cgroups (RAM/CPU) kotaları, non-root çalıştırma, Trivy CVE zafiyet taraması ve container Çıkış Kodları (Exit Codes) tablosu. | [**07-security-and-troubleshooting.md**](07-security-and-troubleshooting.md) |

---

## Günlük Operasyonlarda En Sık Kullanılan 20 Komut

Aşağıdaki tablo, bir DevOps mühendisinin terminalde en çok çalıştırdığı kritik komutların hızlı özetidir:

| No | Amaç | Komut |
|:---:|:---|:---|
| **1** | Port yönlendirmeli web container'ı başlatma | `docker run -d --name web -p 8080:80 nginx:alpine` |
| **2** | Geçici test container'ında interaktif shell açma | `docker run -it --rm ubuntu:24.04 bash` |
| **3** | Çalışan container'ları listeleme | `docker ps` |
| **4** | Durmuş container'lar dahil tümünü listeleme | `docker ps -a` |
| **5** | Container'ın canlı log akışını izleme | `docker logs -f --tail 50 <container>` |
| **6** | Çalışan container'ın içine interaktif shell açma | `docker exec -it <container> sh` |
| **7** | Container'ı nazikçe durdurma (SIGTERM) | `docker stop <container>` |
| **8** | Durmuş container'ı silme | `docker rm <container>` |
| **9** | Dockerfile ile yeni bir image build etme | `docker build -t my-app:1.0 .` |
| **10** | Sistemdeki yerel image'ları listeleme | `docker images` |
| **11** | Image'ı uzak registry için tag'leme | `docker tag my-app:1.0 user/repo:tag` |
| **12** | Image'ı Registry'ye yükleme | `docker push user/repo:tag` |
| **13** | Image'ı silme | `docker rmi <image>` |
| **14** | Kalıcı depolama alanı (Volume) oluşturma | `docker volume create my_data` |
| **15** | Özel bridge ağı oluşturma | `docker network create my_net` |
| **16** | Çok servisli stack'i arka planda ayağa kaldırma | `docker compose up -d` |
| **17** | Compose servislerini ve ağlarını temizleme | `docker compose down` |
| **18** | Anlık CPU ve RAM tüketimini izleme | `docker stats --no-stream` |
| **19** | Docker disk kullanımını analiz etme | `docker system df` |
| **20** | Kullanılmayan kaynakları toplu temizleme (yalnızca kendi makinenizde; paylaşılan sunucuda kullanmayın) | `docker system prune -f` |

---

## İpuçları ve En İyi Pratikler (Best Practices)

1. **İsimlendirme:** Her zaman `--name` bayrağını kullanın. Rastgele üretilen container isimleri yerine işlevini belirten isimler operasyonu kolaylaştırır.
2. **Kalıcılık:** Üretim ortamında veritabanı gibi durum bilgisi tutan (stateful) servislerde mutlaka **Named Volume** kullanın.
3. **İzolasyon:** Farklı projeleri ve mikroservis gruplarını mutlaka kendi özel bridge ağlarında (`--network`) çalıştırın.
4. **Güvenlik:** Container'ları varsayılan root kullanıcısıyla çalıştırmaktan kaçının; Dockerfile içinde `USER 10001` tanımlayın veya `docker run --user` parametresini kullanın.
5. **Temizlik:** Yalnızca kendi kaynaklarınızı silin: adıyla (`docker rm -f <ad>`, `docker image rm <image>`), Compose ile (`docker compose down -v`) ya da label ile (`docker container prune --filter label=<label>`). `docker system prune` bütün sunucuya uygulanır; paylaşılan bir sunucuda başkalarının container ve image'larını da siler.
