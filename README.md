# Docker ve Container Teknolojileri Labları

Docker labları. Her lab bağımsızdır; sunumda hangi konudaysanız o labı doğrudan açabilirsiniz.

---

## Ubuntu için Docker ve Docker Compose kurulumu

Aşağıdaki blok tekrar tekrar çalıştırılabilir:

- Docker kuruluysa yalnızca sürümleri gösterir; kurulu değilse Docker CE ve Compose'u kurar.

Kurulumdan sonra SSH oturumunu kapatıp yeniden açın.

```bash
#!/usr/bin/env bash
set -euo pipefail

if command -v docker >/dev/null 2>&1 && docker --version >/dev/null 2>&1; then
    echo "=========================================================="
    echo "✅ Docker zaten sistemde kurulu:"
    docker --version
    docker compose version 2>/dev/null || true
    echo "=========================================================="
else
    echo "=========================================================="
    echo "🚀 Docker Engine ve Compose Kurulumu Başlatılıyor..."
    echo "=========================================================="
    
    # 1. Eski paket kalıntılarını güvenle kaldır
    for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do
        sudo apt-get remove -y "$pkg" 2>/dev/null || true
    done

    # 2. Ön koşul paketleri ve GPG anahtarı
    sudo apt-get update
    sudo apt-get install -y ca-certificates curl gnupg
    sudo install -m 0755 -d /etc/apt/keyrings
    sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc

    # 3. Resmi Docker APT deposu
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    # 4. Paketleri kur
    sudo apt-get update
    sudo apt-get install -y \
        docker-ce \
        docker-ce-cli \
        containerd.io \
        docker-buildx-plugin \
        docker-compose-plugin

    # 5. Non-root yetkisi ve servis aktivasyonu
    sudo usermod -aG docker "$USER"
    sudo systemctl enable --now docker

    echo "=========================================================="
    echo "✅ Docker kurulumu tamamlandı!"
    docker --version
    docker compose version
    echo "=========================================================="
fi
```

> **Not:** Scripti dosya üzerinden çalıştırmak isterseniz:
> ```bash
> bash ~/docker-labs/lab-01-container-lifecycle-and-cli/scripts/install-docker.sh
> ```

---

## Lab Kataloğu

**`*` işaretli lablar sunumda anlatılan konuların labıdır; derste bunlar yapılır.** İşaretsiz lablar ek çalışmadır; zaman kalırsa veya kendi başınıza yapılabilir. Lablar birbirine bağımlı değildir.

| | No | Lab | Konu | Port |
|:---:|:---:|---|---|:---:|
|  | **00** | [Linux Temelleri](lab-00-linux/README.md) | Sistem teftişi; performans, disk ve log sorun giderme | — |
| **\*** | **01** | [Container Yaşam Döngüsü ve Temel CLI](lab-01-container-lifecycle-and-cli/README.md) | Image ve container, `run`/`stop`/`pause`/`kill`/`rm`, port eşleme | `8080` |
| **\*** | **02** | [Canlı Container Teftişi](lab-02-live-debugging-and-logging/README.md) | `exec`, `cp`, `diff`, `logs`, `top`, `stats`, `inspect` | `8081` |
| **\*** | **03** | [Sıfırdan Dockerfile](lab-03-dockerfile-from-scratch/README.md) | Python (pip) ve Node.js (npm) uygulamasını build edip çalıştırma | `3000, 3001` |
| **\*** | **04** | [Layer Cache ve Multi-Stage](lab-04-layer-caching-and-multistage/README.md) | Cache sırası, `.dockerignore`, multi-stage | `8080` |
|  | **05** | [Polyglot Uygulama Paketleme](lab-05-polyglot-application-packaging/README.md) | Node.js, Python, Go (zorunlu); Java, .NET, PHP, React (isteğe bağlı) | `19001` |
|  | **06** | [BuildKit ve Çoklu Mimari](lab-06-buildkit-and-multiarch/README.md) | Cache/secret mount, amd64+arm64, SBOM | `5000`† |
| **\*** | **07** | [Docker Hub: Public ve Private Repository](lab-07-image-tagging-and-registry/README.md) | `tag`, `push`, `pull`, `login`/`logout` | `19001` |
| **\*** | **08** | [Ağlar ve Dahili DNS](lab-08-networking-and-dns/README.md) | Bridge, DNS, izolasyon, port yayınlama, host/none/internal | `8084, 8088` |
| **\*** | **09** | [Depolama](lab-09-storage-bind-mount-vs-volume/README.md) | Bind mount, volume, tmpfs, PostgreSQL kalıcılığı | `8082` |
| **\*** | **10** | [Compose Hızlı Başlangıç](lab-10-docker-compose-quickstart/README.md) | WordPress + MariaDB, `.env`, `service_healthy` | `19001` |
| **\*** | **11** | [Compose Pratiği: Çok Servisli Uygulama](lab-11-docker-compose-stack/README.md) | Kendi Dockerfile'ı olan web, api, worker + Redis + PostgreSQL; compose build, tek servis logs/stop/start/rebuild, scale | `19001` |
|  | **12** | [Kaynak Limitleri ve OOMKilled](lab-12-cgroups-resource-limits-and-oom/README.md) | `--cpus`, `--memory`, cgroup v2, çıkış kodu 137 | — |
| **\*** | **13** | [Container Güvenliği](lab-13-container-security-and-hardening/README.md) | Non-root, distroless, Trivy (bölüm 01 ve 03); runtime sıkılaştırma | `8080` |
|  | **14** | [Yedekleme ve Felaket Kurtarma](lab-14-backup-restore-disaster-recovery/README.md) | `save`/`load`, volume yedeği, `pg_dump` | — |
| **\*** | **15** | [Kurumsal Registry: Harbor](lab-15-enterprise-harbor-registry/README.md) | Projeler, robot hesap, immutability, Trivy, REST API | `18444` |
|  | **16** | [Sorun Giderme Senaryoları](lab-16-container-troubleshooting-scenarios/README.md) | Çıkış kodları ve yedi bozuk senaryo | `8095, 8096` |
| **\*** | **EK-02** | [Build Yöneticileri: npm ve pip ile Build](ek-02-build-managers-npm-pip/README.md) | Build'in dört adımı ve artifact (`.tgz`, `.whl`, `.jar`), artifact deposu ve deploy akışı, lint ve testin kalite kapısı rolü, uygulamayı çalıştırma, kırmızı build, multi-stage Dockerfile ile küçük image; isteğe bağlı Java ve Maven | — |

† Yalnızca `127.0.0.1` üzerinde yayınlanır; güvenlik duvarında açılmaz.

---

## Host Üzerinde Açılması Gereken Portlar

Eğitim sunucusunda 80 ve 443 portlarını kullanan Nginx, alan adı ile gelen istekleri yerel portlara yönlendirir. Örneğin sunucu adı `student101` ise:

| Alan adı | Yönlendirildiği port |
|---|---|
| `https://student101-app1.devopsatolyesi.com` | `127.0.0.1:19001` |
| `https://student101-harbor.devopsatolyesi.com` | `127.0.0.1:18444` |

Kendi adresinizi `echo "https://$(hostname)-app1.devopsatolyesi.com"` ile görebilirsiniz.

### 1. Port Dağılım Matrisi

| Servis / Kategori | Port | Erişim | Kullanan lablar |
|---|:---:|---|---|
| SSH | `22` | `ssh <kullanıcı>@<SUNUCU-IP>` | Tümü |
| Nginx (HTTP/HTTPS, alan adı yönlendirme) | `80, 443` | `https://<sunucu-adı>-app1.devopsatolyesi.com` | 05, 07, 10, 11, 15 |
| Harbor | `18444` | Web: alan adı; CLI: `127.0.0.1:18444` | 15 |
| App1 slotu | `19001` | `http://<SUNUCU-IP>:19001` | 05, 07, 10, 11 |
| Arcade ve araçlar | `19002 - 19008` | `http://<SUNUCU-IP>:<PORT>` | `devops-arcade-and-tools` |
| Tekil lab container'ları | `8080 - 8090` | `http://<SUNUCU-IP>:<PORT>` | 01, 02, 04, 08, 09, 13 |
| Sorun giderme senaryoları | `8095, 8096` | `http://<SUNUCU-IP>:<PORT>` | 16 |
| Python ve Node.js örnekleri | `3000, 3001` | `http://<SUNUCU-IP>:<PORT>` | 03 |
| Compose temelleri API | `8000` | `http://<SUNUCU-IP>:8000` | 11 |

### 2. Ubuntu UFW Güvenlik Duvarı Açma Komutları

```bash
# Yönetim ve web trafiği
sudo ufw allow 22/tcp comment 'SSH'
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'

# Kurumsal servisler ve uygulama slotları
sudo ufw allow 18444/tcp comment 'Harbor'
sudo ufw allow 19001:19008/tcp comment 'Uygulama slotlari'

# Lab konteynerleri
sudo ufw allow 3000:3001/tcp comment 'Docker lab Python ve Node.js'
sudo ufw allow 8000/tcp comment 'Docker lab Compose API'
sudo ufw allow 8080:8090/tcp comment 'Docker lab tekil konteynerler'
sudo ufw allow 8095:8096/tcp comment 'Docker lab sorun giderme'

sudo ufw reload
```

Docker'ın yayınladığı portlar UFW kurallarından önce işlenen iptables kuralları ile açılır. Bu yüzden yalnızca sunucunun kendisinden erişilmesi gereken servisler `-p 127.0.0.1:<port>:<port>` biçiminde yayınlanmalıdır (LAB-DOC-08).

---

## Hızlı Başvuru Rehberi (Cheatsheet Bağlantıları)

Operasyonel komut referanslarına doğrudan erişebilirsiniz:

* [**01. Container Yönetimi (Containers)**](docker-cheatsheet/01-containers.md) — `run`, `ps`, `exec`, `logs`, `cp`, `diff`, `stats`, `inspect`
* [**02. Image Yönetimi (Images)**](docker-cheatsheet/02-images.md) — `build`, `history`, `tag`, `push`, `pull`, `rmi`, `save`, `load`
* [**03. Depolama (Storage)**](docker-cheatsheet/03-storage.md) — Named Volume, Bind Mount, tmpfs, Backup/Restore Helper
* [**04. Ağ Yönetimi (Networking)**](docker-cheatsheet/04-networking.md) — Bridge, host, none, dahili DNS (`127.0.0.11`), connect/disconnect
* [**05. Docker Compose**](docker-cheatsheet/05-compose.md) — `up`, `down`, `ps`, `logs`, `exec`, `scale`, `config`
* [**06. Sistem ve Temizlik (System & Cleanup)**](docker-cheatsheet/06-system-and-cleanup.md) — `system df`, `system prune`, `builder prune`, `events`
* [**07. Güvenlik ve Hata Ayıklama (Security & Troubleshooting)**](docker-cheatsheet/07-security-and-troubleshooting.md) — cgroups limitleri, non-root, Trivy, Exit Codes

Detaylı genel bakış ve en sık kullanılan 20 komut tablosu için [**📖 Docker Cheatsheet Ana Sayfası**](docker-cheatsheet/README.md) belgesini inceleyebilirsiniz.
