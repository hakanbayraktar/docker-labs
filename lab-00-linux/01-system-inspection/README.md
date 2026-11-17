# LAB-DOC-00-01 — Linux Sistem Teftişi: Donanım, Kullanıcı, Servis, Ağ, Paket ve İzinler

| Profil / Araçlar | Açık Portlar |
|---|---|
| Ubuntu 22.04/24.04, `bash`, `sudo`, `systemctl`, `journalctl`, `ss`, `apt` | — |

## Amaç

- Sunucunun çekirdek, CPU ve bellek bilgilerini okumak.
- Kullanıcı, servis (`systemctl`, `journalctl`) ve paket (`apt`) yönetimi yapmak.
- Ağ arayüzlerini, portları ve DNS ayarlarını incelemek.
- Dosya izinlerini `chmod` ve `namei` ile uygulamak.

## Ön Koşullar

- `sudo` yetkisi olan bir kullanıcı ile Ubuntu sunucuya SSH bağlantısı.
- Lab dosyaları `~/docker-labs` altında olmalıdır.

## Adım Adım Uygulama Rehberi

### Hazırlık

#### 1. Çalışma Dizinine Geçiş
```bash
cd ~/docker-labs/lab-00-linux
```

```bash
mkdir -p sandbox && cd sandbox
```

### Sistem ve Donanım Bilgisi

#### 2. Çekirdek ve İşletim Sistemi Bilgilerini Görüntüleme
```bash
uname -srm
```

```bash
cat /etc/os-release | grep -E "PRETTY_NAME|VERSION_ID"
```

#### 3. CPU Donanım Bilgilerini İnceleme
```bash
lscpu | grep -E "Model name|CPU\(s\):"
```

```bash
nproc
```

`nproc` çekirdek sayısını verir. Load average bu sayının üzerine sürekli çıkıyorsa CPU kuyruğu birikiyor demektir.

#### 4. Bellek (RAM) ve Swap Kullanımını Kontrol Etme
```bash
free -h
```

Asıl bakılacak sütun `available` değeridir; `free` sütunu düşük olsa bile Linux boş belleği önbellek (buff/cache) için kullanır.

#### 5. Sistem Çalışma Süresi ve Yük Ortalaması (Load Average)
```bash
uptime
```

Üç değer sırasıyla son 1, 5 ve 15 dakikanın ortalama yüküdür.

### Kullanıcı Yönetimi

#### 6. Mevcut Kullanıcı ve Oturum Bilgilerini Görme
```bash
whoami
```

```bash
id
```

```bash
w
```

#### 7. Yeni Bir Test Kullanıcısı Oluşturma
```bash
sudo useradd -m -s /bin/bash devopsdemo
```

#### 8. Kullanıcıya Parola Atama
```bash
echo "devopsdemo:DevOpsPass123!" | sudo chpasswd
```

#### 9. Kullanıcıyı Sudo Grubuna Ekleme
```bash
sudo usermod -aG sudo devopsdemo
```

#### 10. Kullanıcıyı Doğrulama
```bash
id devopsdemo
```

```bash
grep "devopsdemo" /etc/passwd
```

#### 11. Test Kullanıcısını Ev Diziniyle Birlikte Silme
```bash
sudo userdel -r devopsdemo
```

### Servisler ve Journal Logları

#### 12. Çalışan Tüm Servisleri Listeleme
```bash
systemctl list-units --type=service --state=running --no-pager
```

#### 13. Docker ve Nginx Servis Durumunu Sorgulama
```bash
systemctl is-active docker
```

```bash
systemctl is-active nginx
```

#### 14. Servislerin Açılışta Otomatik Başlama Ayarını Denetleme
```bash
systemctl is-enabled docker
```

```bash
systemctl is-enabled nginx
```

#### 15. Docker Servisinin Son Günlüklerini (Log) Okuma
```bash
journalctl -u docker -n 30 --no-pager
```

#### 16. Açılıştan İtibaren Sistem Hata (Error) Loglarını Filtreleme
```bash
journalctl -p err -b -n 20 --no-pager
```

#### 17. Son 30 Dakikaya Ait Günlükleri İnceleme
```bash
journalctl --since "30 min ago" -n 20 --no-pager
```

#### 18. Journal Günlük Dosyalarının Boyutunu Görme
```bash
journalctl --disk-usage
```

### Ağ

#### 19. Ağ Arayüzleri ve IP Adreslerini Listeleme
```bash
ip -brief addr show
```

#### 20. Varsayılan Ağ Geçidini (Routing Table) Görüntüleme
```bash
ip route show
```

#### 21. Sunucuda Dinlenen (LISTEN) Portları İnceleme
```bash
sudo ss -tulpn
```

#### 22. DNS Çözümleme Yapılandırmasını İnceleme
```bash
cat /etc/resolv.conf
```

```bash
cat /etc/hosts
```

#### 23. Alan Adı Çözümleme (DNS Lookup) Testi
```bash
nslookup google.com
```

#### 24. HTTP Uç Noktası Sağlık Kontrolü
```bash
curl -I -s http://127.0.0.1:80 | head -n 5
```

### Paket Yönetimi

#### 25. Paket İndeksini Güncelleme
```bash
sudo apt-get update -y
```

#### 26. Paket Depo Bilgisini Sorgulama
```bash
apt-cache policy ncdu
```

#### 27. Örnek CLI Aracı Kurma (ncdu)
```bash
sudo apt-get install -y ncdu
```

#### 28. Kurulan Paketi Doğrulama
```bash
ncdu -v
```

```bash
dpkg -s ncdu | grep -E "Package:|Version:|Status:"
```

#### 29. Test Paketini Sistemden Kaldırma
```bash
sudo apt-get remove -y ncdu
```

### Dosya İzinleri

#### 30. Dosya İzinleri Pratiği (chmod 755)
```bash
cat <<'EOF' > deploy.sh
#!/bin/bash
echo "Deploy scripti calisti!"
EOF
```

```bash
chmod 755 deploy.sh
```

```bash
./deploy.sh
```

#### 31. Gizli Dosya İzin Standardı (chmod 600)
```bash
touch api-token.env
```

```bash
chmod 600 api-token.env
```

```bash
ls -l api-token.env
```

#### 32. Dosya İzin Zincirini İnceleme (namei)
```bash
namei -l deploy.sh
```

## Temizlik

```bash
cd ~/docker-labs/lab-00-linux
```

```bash
rm -rf sandbox
```
