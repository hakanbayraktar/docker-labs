# LAB-DOC-13-02 — Çalışma Zamanı Sıkılaştırma: Read-Only, Capabilities ve no-new-privileges

| Profil / Araçlar | Açık Portlar |
|---|---|
| `docker run --read-only --tmpfs --cap-drop --security-opt --pids-limit`, `alpine:3.20`, `sec-demo:hardened` | 8080 |

## Amaç

- Kök dosya sistemini salt okunur yapmak.
- Capability'leri `--cap-drop ALL` ile kaldırmak.
- `no-new-privileges` ve `--pids-limit` uygulamak.
- Bu ayarları birlikte kullanarak sıkılaştırılmış bir container çalıştırmak.

## Ön Koşullar

- Host üzerinde **8080** portu boş olmalıdır.

## Adım Adım Uygulama Rehberi

### 1. Varsayılan Ayarlarla Çalıştırma

```bash
cd ~/docker-labs/lab-13-container-security-and-hardening/app
```

```bash
docker build -f Dockerfile.hardened -t sec-demo:hardened .
```

```bash
docker run -d --name harden-default -p 8080:8080 sec-demo:hardened
```

```bash
curl -s http://localhost:8080
```

`"app_dir_writable": true`: uygulama kendi dizinine yazabiliyor.

```bash
docker rm -f harden-default
```

### 2. Salt Okunur Dosya Sistemi

```bash
docker run -d --name harden-ro -p 8080:8080 --read-only --tmpfs /tmp:rw,noexec,nosuid,size=16m sec-demo:hardened
```

```bash
curl -s http://localhost:8080
```

`"app_dir_writable": false` ve `"tmp_writable": true`: yalnızca `/tmp` yazılabilir.

```bash
docker exec harden-ro sh -c 'echo x > /app/data/deneme' || echo "SALT OKUNUR: dosya sistemine yazilamaz"
```

```bash
docker rm -f harden-ro
```

### 3. Capability'ler

Varsayılan container birçok capability ile başlar. Root kullanıcı bir dosyanın sahibini değiştirebilir (`CAP_CHOWN`):

```bash
docker run --rm alpine:3.20 sh -c 'grep CapEff /proc/self/status && touch /tmp/f && chown nobody /tmp/f && echo "chown basarili"'
```

Tüm capability'ler kaldırıldığında root bile bu işlemi yapamaz:

```bash
docker run --rm --cap-drop ALL alpine:3.20 sh -c 'grep CapEff /proc/self/status; touch /tmp/f && chown nobody /tmp/f || echo "ENGELLENDI: CAP_CHOWN yok"'
```

`CapEff: 0000000000000000`: hiçbir capability yok. Gerçekten gerekenler `--cap-add` ile tek tek geri eklenir.

### 4. no-new-privileges

```bash
docker run --rm alpine:3.20 grep NoNewPrivs /proc/self/status
```

```bash
docker run --rm --security-opt no-new-privileges alpine:3.20 grep NoNewPrivs /proc/self/status
```

`NoNewPrivs: 1` olduğunda süreç ve alt süreçleri, `sudo` veya `su` gibi setuid programlarla bile yeni yetki kazanamaz.

### 5. Süreç Sayısı Limiti

```bash
docker run --rm --pids-limit 64 alpine:3.20 cat /sys/fs/cgroup/pids.max
```

### 6. Tüm Ayarlarla Sıkılaştırılmış Container

```bash
docker run -d --name harden-full -p 8080:8080 \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=16m \
  --cap-drop ALL \
  --security-opt no-new-privileges \
  --pids-limit 64 \
  --memory 128m \
  sec-demo:hardened
```

```bash
curl -s http://localhost:8080
```

```bash
docker inspect -f 'ReadOnly={{.HostConfig.ReadonlyRootfs}} CapDrop={{.HostConfig.CapDrop}} SecurityOpt={{.HostConfig.SecurityOpt}} Pids={{.HostConfig.PidsLimit}}' harden-full
```

## Doğrulama

```bash
curl -s http://localhost:8080
```

```bash
docker exec harden-full grep -E "CapEff|NoNewPrivs" /proc/1/status
```

Beklenen sonuç:

```text
{"service": "hardened-demo", "running_uid": 10001, "is_root": false, "app_dir_writable": false, "tmp_writable": true}
CapEff:	0000000000000000
NoNewPrivs:	1
```

## Temizlik

```bash
docker rm -f harden-default harden-ro harden-full 2>/dev/null || true
```

```bash
docker rmi sec-demo:hardened 2>/dev/null || true
```
