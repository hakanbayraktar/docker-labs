# LAB-DOC-00 — Linux Temelleri: Sistem Teftişi ve Sorun Giderme

| Profil / Araçlar | Açık Portlar |
|---|---|
| Ubuntu 22.04/24.04, `bash`, `sudo` | — |

## Amaç

- Docker labları öncesinde, container'ların üzerinde çalıştığı Linux sunucuyu teftiş etmeyi öğrenmek.
- Performans, disk ve log sorunlarını gerçek komutlarla teşhis edip çözmek.

## Bölümler

Bölümleri sırayla uygulayın:

| Bölüm | Konu |
|---|---|
| [LAB-DOC-00-01 — Linux Sistem Teftişi](01-system-inspection/README.md) | Donanım, kullanıcılar, servisler ve journal, ağ, paketler, dosya izinleri |
| [LAB-DOC-00-02 — Performans, Disk ve Log Sorun Giderme](02-troubleshooting/README.md) | `ps`/`top`/`htop`/`vmstat`, disk doluluğu ve silinmiş-açık dosya, `tail`/`grep`/`awk` log analizi, "sunucu yavaşladı" olay senaryosu |

Her iki bölüm de `~/docker-labs/lab-00-linux/sandbox` dizininde çalışır ve sistemde kalıcı değişiklik bırakmaz.

