# LAB-DOC-00-02 — Linux Performans, Disk ve Log Sorun Giderme

| Profil / Araçlar | Açık Portlar |
|---|---|
| Ubuntu 22.04/24.04, `ps`, `top`, `htop`, `vmstat`, `df`, `du`, `lsof`, `grep`, `awk`, `tail` | — |

## Amaç

- `ps`, `top`, `htop` ve `vmstat` ile CPU ve bellek tüketen süreçleri bulmak ve güvenle sonlandırmak.
- `df -h`, `du` ve `find` ile diski dolduran dosyaları bulmak; silinmiş ama açık tutulan dosya sorununu çözmek.
- `tail`, `head`, `less`, `grep`, `awk` ve `zgrep` ile uygulama ve sistem loglarını analiz etmek.
- Gerçekçi bir "sunucu yavaşladı" olayında CPU, disk ve log teşhisini birlikte uygulamak.

## Ön Koşullar

- `sudo` yetkisi olan bir kullanıcı ile Ubuntu sunucuya SSH bağlantısı.
- Sandbox dizininde en az 1 GB boş disk alanı (senaryolar geçici büyük dosyalar oluşturur).

## Adım Adım Uygulama Rehberi

### Hazırlık

#### 1. Çalışma Dizinine Geçiş
```bash
cd ~/docker-labs/lab-00-linux
```

```bash
mkdir -p sandbox && cd sandbox
```

### Süreç ve Performans İzleme

#### 2. En Çok Bellek Tüketen Süreçleri Sıralama
```bash
ps -eo pid,user,%cpu,%mem,comm --sort=-%mem | head -n 10
```

#### 3. En Çok CPU Tüketen Süreçleri ve Süreç Durumlarını İnceleme
```bash
ps -eo pid,ppid,user,%cpu,%mem,etime,stat,comm --sort=-%cpu | head -n 10
```

```bash
ps -eo stat= | cut -c1 | sort | uniq -c
```

`STAT` sütunu: `R` çalışıyor, `S` uyuyor, `D` disk/IO bekliyor (kesilemez), `Z` zombie. Çok sayıda `D` durumundaki süreç genellikle disk veya NFS darboğazına işaret eder.

#### 4. Belirli Bir Süreci Bulma ve Süreç Ağacını Görme
```bash
pgrep -a dockerd
```

```bash
ps aux | grep "[d]ockerd"
```

```bash
ps -f --forest -u "$USER"
```

#### 5. top ile Anlık Sistem Görüntüsü Alma
```bash
top -b -n 1 | head -n 15
```

```bash
top -b -n 1 -o %MEM | head -n 15
```

Üst bölümde okunacak alanlar:

| Alan | Anlamı |
|---|---|
| `load average` | 1/5/15 dakikalık yük ortalaması |
| `us` / `sy` | Kullanıcı ve çekirdek alanında harcanan CPU yüzdesi |
| `id` | Boşta (idle) CPU yüzdesi |
| `wa` | Disk/IO beklerken boşa geçen CPU yüzdesi; yüksekse sorun disktedir |
| `MiB Mem` / `MiB Swap` | Toplam, boş, kullanılan bellek ve swap |

<details>
<summary><strong>İsteğe bağlı — 6. top Etkileşimli Kullanımı</strong></summary>

```bash
top
```

| Tuş | İşlev |
|---|---|
| `P` | CPU kullanımına göre sırala |
| `M` | Bellek kullanımına göre sırala |
| `1` | Her CPU çekirdeğini ayrı göster |
| `c` | Tam komut satırını göster |
| `k` | PID girerek süreç sonlandır |
| `q` | Çık |

</details>

<details>
<summary><strong>İsteğe bağlı — 7. htop ile Görsel Süreç İzleme</strong></summary>

```bash
sudo apt-get install -y htop
```

```bash
htop
```

| Tuş | İşlev |
|---|---|
| `F6` | Sıralama sütununu seç (CPU%, MEM% vb.) |
| `F5` | Ağaç (tree) görünümü |
| `F4` | İsme göre filtrele |
| `F3` | Ara |
| `F9` | Seçili sürece sinyal gönder |
| `F10` veya `q` | Çık |

</details>

<details>
<summary><strong>İsteğe bağlı — 8. vmstat ile CPU, Bellek ve IO Eğilimini İzleme</strong></summary>

```bash
vmstat 1 5
```

| Sütun | Anlamı |
|---|---|
| `r` | CPU sırası bekleyen süreç sayısı; sürekli `nproc` değerinden büyükse CPU yetmiyor |
| `b` | IO bekleyen (D durumundaki) süreç sayısı |
| `si` / `so` | Swap'tan okunan / swap'a yazılan bellek; sıfırdan büyükse RAM yetmiyor |
| `us` / `sy` / `id` / `wa` | CPU dağılımı; yüksek `wa` disk darboğazıdır |

</details>

#### 9. Senaryo: CPU Tüketen Süreci Bulma ve Sonlandırma
Bir çekirdeği %100 kullanan süreç başlatın. `timeout`, süreç unutulsa bile 5 dakika sonra durdurur.
```bash
timeout 300 yes > /dev/null &
```

```bash
CPU_PID=$!
```

```bash
top -b -n 1 -o %CPU | head -n 12
```

```bash
ps -eo pid,ppid,%cpu,etime,comm --sort=-%cpu | head -n 5
```

```bash
vmstat 1 3
```

`yes` sürecinin `%CPU` değeri 100'e yakın olmalıdır. `vmstat` tüm çekirdeklerin ortalamasını gösterdiği için `us` artışı çekirdek sayısına bölünür (4 çekirdekte yaklaşık %25). Süreci SIGTERM (15) ile kibarca sonlandırın:
```bash
kill -15 "${CPU_PID}"
```

```bash
pgrep -a -x yes || echo "CPU tuketen surec sonlandirildi."
```

#### 10. Süreç Başlatma ve Güvenli Sonlandırma (kill -15)
```bash
sleep 120 &
```

```bash
DUMMY_PID=$!
```

```bash
kill -15 "${DUMMY_PID}"
```

```bash
ps -p "${DUMMY_PID}" || echo "Surec sonlandirildi."
```

`kill -9` (SIGKILL) yalnızca süreç SIGTERM'e yanıt vermediğinde kullanılır; uygulamaya temizlik yapma fırsatı vermez.

### Disk Kullanımı ve Kapasite Sorunları

#### 11. Disk Blok Aygıtlarını ve Bölümlerini Listeleme
```bash
lsblk
```

#### 12. Dosya Sistemi Kapasite Doluluğunu Denetleme
```bash
df -h
```

```bash
df -h -x tmpfs -x devtmpfs -x squashfs -x overlay
```

```bash
df -hT /
```

#### 13. Inode (Dosya Sayısı Sınırı) Doluluğunu Kontrol Etme
```bash
df -i /
```

`df -h` boş alan gösterdiği hâlde "No space left on device" hatası alınıyorsa inode'lar tükenmiş olabilir.

#### 14. En Çok Alan Tüketen Dizinleri Sıralama
```bash
sudo du -xhd1 /var 2>/dev/null | sort -h | tail -n 8
```

```bash
sudo du -xhd1 /var/lib/docker 2>/dev/null | sort -h | tail -n 5
```

#### 15. Senaryo: Diski Dolduran Dosyaları Bulma
Sandbox içinde büyük dosyalar oluşturun:
```bash
mkdir -p disk-lab/logs disk-lab/backups
```

```bash
fallocate -l 300M disk-lab/backups/db-dump-old.sql
```

```bash
fallocate -l 120M disk-lab/logs/app-debug.log
```

```bash
fallocate -l 5M disk-lab/logs/app.log
```

```bash
df -h .
```

Alanı tüketen dizini ve dosyayı daraltın:
```bash
du -sh disk-lab/*
```

```bash
du -ah disk-lab | sort -rh | head -n 5
```

```bash
find disk-lab -type f -size +100M -exec ls -lh {} \;
```

Aynı aramayı kök dosya sisteminde 500 MB üzeri dosyalar için yapın:
```bash
sudo find / -xdev -type f -size +500M -exec ls -lh {} \; 2>/dev/null
```

Gereksiz eski yedeği silin ve alanın geri geldiğini doğrulayın:
```bash
rm disk-lab/backups/db-dump-old.sql
```

```bash
df -h .
```

#### 16. Senaryo: Silinmiş Ama Hâlâ Açık Tutulan Dosya
Bir uygulamanın açık tuttuğu log dosyası silindiğinde alan, süreç dosyayı kapatana kadar geri gelmez.
```bash
fallocate -l 200M disk-lab/logs/rotated.log
```

```bash
sleep 600 < disk-lab/logs/rotated.log &
```

```bash
HOLD_PID=$!
```

```bash
df -h .
```

```bash
rm disk-lab/logs/rotated.log
```

```bash
df -h .
```

`df` hâlâ aynı kullanımı gösterir, `du` ise dosyayı göremez:
```bash
du -sh disk-lab
```

Silinmiş ama açık dosyaları bulun:
```bash
sudo lsof +L1 2>/dev/null | grep rotated.log
```

```bash
ls -l /proc/"${HOLD_PID}"/fd | grep deleted
```

Dosyayı tutan süreci sonlandırın ve alanın geri geldiğini doğrulayın:
```bash
kill -15 "${HOLD_PID}"
```

```bash
df -h .
```

#### 17. Aktif Log Dosyasını Güvenle Boşaltma (truncate)
Çalışan bir uygulamanın log dosyasını `rm` yerine boşaltmak, 16. adımdaki sorunu önler.
```bash
ls -lh disk-lab/logs/app-debug.log
```

```bash
truncate -s 0 disk-lab/logs/app-debug.log
```

```bash
ls -lh disk-lab/logs/app-debug.log
```

<details>
<summary><strong>İsteğe bağlı — 18. Kalıcı Disk Bağlantı Tablosunu (/etc/fstab) İnceleme</strong></summary>

```bash
cat /etc/fstab | grep -v "^#"
```

</details>

### Log Analizi

#### 19. Sistem Log Dosyalarını İnceleme (/var/log)
```bash
ls -lhS /var/log | head -n 10
```

```bash
sudo tail -n 20 /var/log/syslog
```

```bash
sudo grep -i "error" /var/log/syslog | tail -n 10
```

```bash
sudo grep -E "Failed password|Accepted (password|publickey)" /var/log/auth.log | tail -n 10
```

<details>
<summary><strong>İsteğe bağlı — 20. Çekirdek (Kernel) Mesajlarını İnceleme (dmesg)</strong></summary>

```bash
sudo dmesg -T | tail -n 20
```

```bash
sudo dmesg -T | grep -i -E "oom|killed process|i/o error" || echo "Kritik kernel mesaji bulunamadi."
```

OOM (Out Of Memory) satırları, çekirdeğin bellek yetmediği için bir süreci zorla sonlandırdığını gösterir.

</details>

#### 21. Örnek Uygulama Log Dosyalarını Oluşturma
```bash
cat <<'EOF' > server.log
2026-09-22 10:00:01 INFO [auth] User admin login successful
2026-09-22 10:00:15 WARN [api] Latency high on /api/v1/products (1450 ms)
2026-09-22 10:00:22 ERROR [db] Connection timeout to postgres:5432
2026-09-22 10:00:45 INFO [auth] User student login successful
2026-09-22 10:01:02 ERROR [gateway] 502 Bad Gateway upstream=api:8080
2026-09-22 10:01:10 ERROR [db] Connection timeout to postgres:5432
2026-09-22 10:01:30 INFO [api] GET /api/v1/orders completed in 85 ms
2026-09-22 10:01:48 WARN [auth] Failed login attempt for user root from 203.0.113.50
2026-09-22 10:01:49 WARN [auth] Failed login attempt for user root from 203.0.113.50
2026-09-22 10:02:10 ERROR [payment] Unhandled exception in charge()
    at PaymentService.charge (payment.js:88)
    at Router.handle (router.js:41)
2026-09-22 10:02:30 INFO [api] Health check OK
2026-09-22 10:03:05 ERROR [db] Too many connections (max_connections=100)
2026-09-22 10:03:40 WARN [disk] /var usage at 91%
2026-09-22 10:04:12 INFO [worker] Report job finished
2026-09-22 10:05:00 ERROR [gateway] 504 Gateway Timeout upstream=api:8080
2026-09-22 10:05:30 INFO [auth] User admin logout
EOF
```

```bash
cat <<'EOF' > access.log
192.168.1.10 - - [22/Sep/2026:10:00:01 +0300] "GET /api/v1/products HTTP/1.1" 200 5120 0.042
192.168.1.11 - - [22/Sep/2026:10:00:03 +0300] "GET /api/v1/orders HTTP/1.1" 200 2048 0.085
203.0.113.50 - - [22/Sep/2026:10:00:05 +0300] "POST /login HTTP/1.1" 401 128 0.011
203.0.113.50 - - [22/Sep/2026:10:00:06 +0300] "POST /login HTTP/1.1" 401 128 0.010
203.0.113.50 - - [22/Sep/2026:10:00:07 +0300] "POST /login HTTP/1.1" 401 128 0.012
192.168.1.10 - - [22/Sep/2026:10:00:15 +0300] "GET /api/v1/products HTTP/1.1" 200 5120 1.450
192.168.1.12 - - [22/Sep/2026:10:01:02 +0300] "GET /api/v1/cart HTTP/1.1" 502 157 0.003
192.168.1.14 - - [22/Sep/2026:10:01:20 +0300] "GET /static/app.js HTTP/1.1" 304 0 0.001
192.168.1.13 - - [22/Sep/2026:10:02:10 +0300] "POST /api/v1/payment HTTP/1.1" 500 230 0.310
192.168.1.11 - - [22/Sep/2026:10:02:30 +0300] "GET /health HTTP/1.1" 200 2 0.001
192.168.1.12 - - [22/Sep/2026:10:03:05 +0300] "GET /api/v1/orders HTTP/1.1" 200 2048 2.870
203.0.113.50 - - [22/Sep/2026:10:03:10 +0300] "GET /wp-admin HTTP/1.1" 404 153 0.002
192.168.1.10 - - [22/Sep/2026:10:05:00 +0300] "GET /api/v1/products HTTP/1.1" 504 160 30.001
EOF
```

#### 22. Logun Başını, Sonunu ve Boyutunu Görme (head, tail, wc, less)
```bash
wc -l server.log access.log
```

```bash
head -n 3 server.log
```

```bash
tail -n 3 server.log
```

```bash
less server.log
```

`less` içinde `/ERROR` ile arayın, `n` ile sonraki eşleşmeye, `G` ile dosya sonuna gidin, `q` ile çıkın.

#### 23. grep ile Temel Filtreleme
```bash
grep "ERROR" server.log
```

```bash
grep -c "ERROR" server.log
```

```bash
grep -n "ERROR" server.log
```

```bash
grep -i "timeout" server.log
```

```bash
grep -v "INFO" server.log
```

```bash
grep -E "ERROR|WARN" server.log
```

```bash
grep "\[db\]" server.log
```

#### 24. grep ile Bağlam Görme ve Dizinde Arama
Hata satırından sonraki 2 satırı (stack trace) gösterin:
```bash
grep -A 2 "Unhandled exception" server.log
```

Eşleşmenin öncesini ve sonrasını birlikte gösterin:
```bash
grep -B 1 -A 1 "502 Bad Gateway" server.log
```

Dizindeki tüm dosyalarda arayın ve yalnızca dosya adlarını listeleyin:
```bash
grep -rn "203.0.113.50" .
```

```bash
grep -rl "ERROR" .
```

#### 25. Hataları Bileşene Göre Gruplama (grep & awk)
```bash
grep "ERROR" server.log | awk '{print $4}' | sort | uniq -c | sort -rn
```

Log seviyelerinin dağılımı:
```bash
grep -E "^[0-9-]+ " server.log | awk '{print $3}' | sort | uniq -c
```

#### 26. Web Erişim Logu (Access Log) Analizi
HTTP durum kodlarının dağılımı:
```bash
awk '{print $9}' access.log | sort | uniq -c | sort -rn
```

En çok istek gönderen IP adresleri:
```bash
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -n 3
```

Sunucu hataları (5xx):
```bash
awk '$9 >= 500' access.log
```

1 saniyeden uzun süren yavaş istekler (son sütun yanıt süresi):
```bash
awk '$11 > 1.0 {print $11, $6, $7}' access.log | sort -rn
```

Başarısız giriş denemesi yapan IP adresleri:
```bash
awk '$7 == "/login" && $9 == 401 {print $1}' access.log | sort | uniq -c
```

<details>
<summary><strong>İsteğe bağlı — 27. Zaman Aralığına Göre Log Filtreleme</strong></summary>

```bash
awk '$2 >= "10:02:00" && $2 <= "10:04:00"' server.log
```

```bash
sed -n '/10:01:02/,/10:03:05/p' server.log
```

`sed` aralığı, logda gerçekten bulunan başlangıç ve bitiş zamanlarını ister; `awk` karşılaştırması ise logda olmayan sınır değerlerle de çalışır.

</details>

<details>
<summary><strong>İsteğe bağlı — 28. Sıkıştırılmış (Rotate Edilmiş) Loglarda Arama</strong></summary>

`logrotate` eski logları `.gz` olarak saklar. Örnek bir rotate dosyası oluşturun:
```bash
gzip -k server.log
```

```bash
ls -lh server.log*
```

```bash
zgrep -c "ERROR" server.log.gz
```

```bash
zcat server.log.gz | tail -n 3
```

```bash
ls -lh /var/log/*.gz 2>/dev/null | head -n 5
```

</details>

#### 29. Canlı Log İzleme (tail -f)
Arka planda 40 saniye boyunca log üreten bir süreç başlatın:
```bash
( for i in $(seq 1 40); do
    echo "$(date '+%F %T') INFO [worker] job-$i processed"
    if [ $((i % 4)) -eq 0 ]; then echo "$(date '+%F %T') ERROR [worker] job-$i failed: timeout"; fi
    sleep 1
  done ) >> live.log &
```

Logu canlı izleyin, birkaç satır geldikten sonra `Ctrl+C` ile çıkın:
```bash
tail -f live.log
```

Yalnızca hataları canlı izleyin, ardından `Ctrl+C` ile çıkın:
```bash
tail -f live.log | grep --line-buffered "ERROR"
```

Systemd servislerinin loglarını da aynı şekilde canlı izleyebilirsiniz (`Ctrl+C` ile çıkın):
```bash
journalctl -u docker -f
```

Log rotate edilen dosyalarda `tail -F` kullanılır; dosya yeniden oluşturulduğunda izlemeye devam eder.

### Olay Senaryosu: "Sunucu Yavaşladı"

#### 30. Olayı Başlatma
Aşağıdaki betik aynı anda CPU tüketen bir süreç, büyük bir dump dosyası ve saniyede bir hata yazan bir log üretir. Tüm süreçler en geç 10 dakika sonra kendiliğinden durur.
```bash
cat <<'EOF' > incident.sh
#!/bin/bash
mkdir -p incident-logs
timeout 600 bash -c 'while :; do :; done' incident-cpu-hog &
timeout 600 bash -c 'while :; do echo "$(date "+%F %T") ERROR [payment] Database connection refused"; sleep 1; done >> incident-logs/payment.log' incident-log-writer &
fallocate -l 300M incident-logs/heap-dump.hprof
echo "Olay baslatildi. Sunucuyu inceleyin."
EOF
```

```bash
bash incident.sh
```

#### 31. CPU Teşhisi
```bash
uptime
```

```bash
top -b -n 1 -o %CPU | head -n 12
```

`top` yalnızca `bash` gösterir. Hangi komutun çalıştığını tam komut satırıyla görün:
```bash
ps -eo pid,ppid,%cpu,etime,args --sort=-%cpu | head -n 5
```

#### 32. Disk Teşhisi
```bash
df -h .
```

```bash
du -ah incident-logs | sort -rh | head -n 5
```

```bash
find . -type f -size +100M -exec ls -lh {} \;
```

#### 33. Log Teşhisi
```bash
ls -lh incident-logs/payment.log
```

```bash
tail -n 5 incident-logs/payment.log
```

```bash
grep -c "connection refused" incident-logs/payment.log
```

Hatanın sürekli aktığını canlı görün, ardından `Ctrl+C` ile çıkın:
```bash
tail -f incident-logs/payment.log
```

Logu yazan süreci bulun:
```bash
pgrep -af incident-log-writer
```

#### 34. Müdahale ve Doğrulama
```bash
pkill -15 -f incident-cpu-hog
```

```bash
pkill -15 -f incident-log-writer
```

```bash
rm incident-logs/heap-dump.hprof
```

```bash
pgrep -af "incident-cpu-hog|incident-log-writer" || echo "Olay surecleri temizlendi."
```

```bash
top -b -n 1 -o %CPU | head -n 10
```

```bash
df -h .
```

## Temizlik

```bash
pkill -15 -f "incident-cpu-hog|incident-log-writer" || true
```

```bash
cd ~/docker-labs/lab-00-linux
```

```bash
rm -rf sandbox
```
