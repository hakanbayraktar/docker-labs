# LAB-DOC-13 — Container Güvenliği ve Sıkılaştırma

| Profil / Araçlar | Açık Portlar |
|---|---|
| `docker`, `python:3.12-alpine`, `gcr.io/distroless/static-debian12`, `tini`, `aquasec/trivy:0.65.0` | 8080 |

## Amaç

- Container'ları root olmayan kullanıcıyla ve shell içermeyen minimal image'larla çalıştırmak.
- Çalışma zamanında salt okunur dosya sistemi, capability kısıtlaması ve `no-new-privileges` uygulamak.
- Image'lardaki bilinen açıkları (CVE) ve Dockerfile hatalarını Trivy ile bulup CI/CD kapısı kurmak.

## Bölümler

Her bölüm bağımsızdır. `*` ile işaretli bölümler sunumda anlatılan konulardır.

| | Bölüm | Konu |
|:---:|---|---|
| **\*** | [LAB-DOC-13-01 — Non-Root Kullanıcı ve Distroless Image](01-nonroot-and-distroless/README.md) | `USER`, root container'ın host dosyalarına etkisi, shell'siz image |
| | [LAB-DOC-13-02 — Çalışma Zamanı Sıkılaştırma](02-runtime-hardening/README.md) | `--read-only`, `--tmpfs`, `--cap-drop ALL`, `no-new-privileges`, `--pids-limit` |
| **\*** | [LAB-DOC-13-03 — Trivy ile Zafiyet Taraması ve Güvenlik Kapısı](03-vulnerability-scanning-trivy/README.md) | Image ve Dockerfile taraması, `--exit-code` |

## Ön Koşullar

- Host üzerinde **8080** portu boş olmalıdır.
