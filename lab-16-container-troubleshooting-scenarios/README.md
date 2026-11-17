# LAB-DOC-16 — Container Sorun Giderme Senaryoları

| Profil / Araçlar | Açık Portlar |
|---|---|
| `docker ps -a`, `docker logs`, `docker inspect`, `docker events`, `docker exec`, `ss`, `docker compose` | 8095, 8096 |

## Amaç

- Container çıkış kodlarını (0, 1, 125, 126, 127, 137, 143) okuyup hatanın türünü belirlemek.
- Bilerek bozulmuş yedi senaryoda belirtiyi görmek, teşhis komutlarıyla nedeni bulmak ve düzeltmek.
- Her sorunda aynı teşhis sırasını uygulamak: durum → loglar → yapılandırma → ağ/depolama.

## Ön Koşullar

- Host üzerinde **8095** ve **8096** portları boş olmalıdır.

## Adım Adım Uygulama Rehberi

### Hazırlık

```bash
cd ~/docker-labs/lab-16-container-troubleshooting-scenarios
```

```bash
mkdir -p work
```

### Senaryo 1: Komut Bulunamadı (127)

```bash
docker run -d --name ts-127 python:3.12-alpine sh -c 'pyhton3 -m http.server 8000'
```

Belirti ve teşhis:

```bash
docker ps -a --filter name=ts-127 --format '{{.Names}} {{.Status}}'
```

```bash
docker logs ts-127
```

```bash
docker inspect -f '{{json .Config.Cmd}}' ts-127
```

Neden: komut adı yanlış yazılmış (`pyhton3`). Düzeltme:

```bash
docker rm ts-127
```

```bash
docker run -d --name ts-127 python:3.12-alpine sh -c 'python3 -m http.server 8000'
```

```bash
docker ps --filter name=ts-127 --format '{{.Names}} {{.Status}}'
```

### Senaryo 2: Çalıştırma İzni Yok (126)

```bash
mkdir -p work/s2
```

```bash
printf '#!/bin/sh\necho "Uygulama basladi"\nsleep 3600\n' > work/s2/start.sh
```

```bash
chmod 644 work/s2/start.sh
```

```bash
printf 'FROM alpine:3.20\nWORKDIR /app\nCOPY start.sh .\nCMD ["sh", "-c", "./start.sh"]\n' > work/s2/Dockerfile
```

```bash
docker build -q -t ts-126:bad work/s2
```

```bash
docker run -d --name ts-126 ts-126:bad
```

```bash
docker ps -a --filter name=ts-126 --format '{{.Names}} {{.Status}}'
```

```bash
docker logs ts-126
```

```bash
docker run --rm --entrypoint ls ts-126:bad -l /app/start.sh
```

Neden: betik çalıştırma izni (`x`) olmadan image'a kopyalandı. Düzeltme: `COPY --chmod=755` ile izni image'da ver:

```bash
printf 'FROM alpine:3.20\nWORKDIR /app\nCOPY --chmod=755 start.sh .\nCMD ["sh", "-c", "./start.sh"]\n' > work/s2/Dockerfile
```

```bash
docker build -q -t ts-126:fixed work/s2
```

```bash
docker rm ts-126
```

```bash
docker run -d --name ts-126 ts-126:fixed
```

```bash
docker logs ts-126
```

### Senaryo 3: Eksik Ortam Değişkeni ve Yeniden Başlama Döngüsü (1)

```bash
docker run -d --name ts-crash --restart on-failure:5 python:3.12-alpine python3 -c 'import os; print("Veritabani:", os.environ["DATABASE_URL"])'
```

```bash
sleep 10
```

```bash
docker ps -a --filter name=ts-crash --format '{{.Names}} {{.Status}}'
```

```bash
docker inspect -f 'restarts={{.RestartCount}} exit={{.State.ExitCode}}' ts-crash
```

```bash
docker logs --tail 4 ts-crash
```

Neden: uygulama `DATABASE_URL` değişkenini bekliyor (`KeyError`). Restart politikası sorunu çözmez, yalnızca tekrarlar. Düzeltme:

```bash
docker rm -f ts-crash
```

```bash
docker run -d --name ts-crash --restart on-failure:5 -e DATABASE_URL=postgres://db:5432/app python:3.12-alpine python3 -c 'import os; print("Veritabani:", os.environ["DATABASE_URL"])'
```

```bash
docker inspect -f 'restarts={{.RestartCount}} exit={{.State.ExitCode}}' ts-crash
```

```bash
docker logs ts-crash
```

### Senaryo 4: Port Zaten Kullanımda (125)

```bash
docker run -d --name ts-port-a -p 8095:80 nginx:alpine
```

```bash
docker run -d --name ts-port-b -p 8095:80 nginx:alpine; echo "docker run cikis kodu: $?"
```

İkinci komut `port is already allocated` hatası verir ve container `Created` durumunda kalır:

```bash
docker ps -a --filter name=ts-port --format '{{.Names}} {{.Status}}'
```

Portu kimin kullandığını bulun:

```bash
docker ps --filter publish=8095 --format '{{.Names}} {{.Ports}}'
```

```bash
sudo ss -tlnp | grep ':8095 '
```

Düzeltme: boş bir port kullanın:

```bash
docker rm ts-port-b
```

```bash
docker run -d --name ts-port-b -p 8096:80 nginx:alpine
```

Senaryoyu kapatın; 8095 portu sonraki senaryoda kullanılacak:

```bash
docker rm -f ts-port-a ts-port-b
```

### Senaryo 5: Uygulama Yalnızca Container'ın İçinden Erişilebilir

```bash
docker run -d --name ts-bind -p 8095:8000 python:3.12-alpine python3 -m http.server 8000 --bind 127.0.0.1
```

```bash
curl -s -m 3 http://localhost:8095 || echo "ERISILEMIYOR: konteyner calisiyor ama yanit yok"
```

```bash
docker ps --filter name=ts-bind --format '{{.Names}} {{.Status}} {{.Ports}}'
```

Container içinde hangi adresin dinlendiğine bakın:

```bash
docker exec ts-bind netstat -tln
```

Neden: uygulama container'ın kendi `127.0.0.1` adresinde dinliyor. Docker'ın yönlendirdiği trafik container'ın ağ arayüzüne (`eth0`) gelir. Düzeltme: `0.0.0.0` üzerinde dinle:

```bash
docker rm -f ts-bind
```

```bash
docker run -d --name ts-bind -p 8095:8000 python:3.12-alpine python3 -m http.server 8000 --bind 0.0.0.0
```

```bash
curl -s -o /dev/null -w "HTTP %{http_code}\n" http://localhost:8095
```

### Senaryo 6: Servis Adı Çözülemiyor

```bash
docker run -d --name ts-cache redis:7.4-alpine
```

```bash
docker run --rm redis:7.4-alpine redis-cli -h ts-cache ping
```

```bash
docker inspect -f '{{range $ag, $_ := .NetworkSettings.Networks}}{{$ag}}{{end}}' ts-cache
```

Neden: iki container de varsayılan `bridge` ağında; bu ağda isimle çözümleme yoktur. Düzeltme: kullanıcı tanımlı ağ:

```bash
docker network create ts-net
```

```bash
docker network connect ts-net ts-cache
```

```bash
docker run --rm --network ts-net redis:7.4-alpine redis-cli -h ts-cache ping
```

### Senaryo 7: Volume'e Yazma İzni Yok

```bash
docker volume create ts-data
```

```bash
docker run --rm --user 10001 -v ts-data:/data alpine:3.20 sh -c 'echo kayit > /data/kayit.txt'
```

```bash
docker run --rm -v ts-data:/data alpine:3.20 ls -ld /data
```

Neden: yeni volume'ün kök dizini root'a ait; UID 10001 yazamaz. Düzeltme: dizini image'da doğru sahiplikle oluşturun. Boş bir volume ilk bağlandığında image'daki dizinin içeriğini ve sahipliğini kopyalar:

```bash
mkdir -p work/s7
```

```bash
printf 'FROM alpine:3.20\nRUN mkdir /data && chown 10001:10001 /data\nUSER 10001\nCMD ["sh", "-c", "echo kayit > /data/kayit.txt && ls -l /data"]\n' > work/s7/Dockerfile
```

```bash
docker build -q -t ts-volume:fixed work/s7
```

```bash
docker volume rm ts-data
```

```bash
docker run --rm -v ts-data:/data ts-volume:fixed
```

## Doğrulama

```bash
docker ps --filter name=ts- --format '{{.Names}} {{.Status}}' | sort
```

```bash
docker inspect -f '{{.Name}} exit={{.State.ExitCode}} restarts={{.RestartCount}}' ts-crash
```

```bash
curl -s -o /dev/null -w "HTTP %{http_code}\n" http://localhost:8095
```

```bash
docker run --rm --network ts-net redis:7.4-alpine redis-cli -h ts-cache ping
```

## Temizlik

```bash
docker rm -f -v ts-127 ts-126 ts-crash ts-port-a ts-port-b ts-bind ts-cache 2>/dev/null || true
```

```bash
docker network rm ts-net 2>/dev/null || true
```

```bash
docker volume rm ts-data 2>/dev/null || true
```

```bash
docker rmi ts-126:bad ts-126:fixed ts-volume:fixed 2>/dev/null || true
```

```bash
rm -rf work
```
