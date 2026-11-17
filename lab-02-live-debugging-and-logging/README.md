# LAB-DOC-02 — Canlı Container Teftişi: exec, cp, diff, logs, top, stats ve inspect

| Profil / Araçlar | Açık Portlar |
|---|---|
| `docker`, `nginx:alpine`, `curl` | 8081 |

## Amaç

- Çalışan container'da komut çalıştırmak ve shell açmak (`exec`).
- Dosya kopyalamak ve değişiklikleri görmek (`cp`, `diff`); canlı düzeltmenin neden kaybolduğunu görmek.
- Logları izlemek (`logs --tail`, `--since`, `-f`).
- Süreçleri, kaynak kullanımını ve metadata'yı sorgulamak (`top`, `stats`, `inspect`).

## Ön Koşullar

- Host üzerinde **8081** portu boş olmalıdır.

## Adım Adım Uygulama Rehberi

### 1. Test Container'ını Başlatma

```bash
cd ~/docker-labs/lab-02-live-debugging-and-logging
```

```bash
docker run -d --name debug-web -p 8081:80 nginx:alpine
```

### 2. Container İçinde Komut Çalıştırma (exec)

Tek komut:

```bash
docker exec debug-web cat /etc/os-release
```

Etkileşimli shell açın, içeride inceleme yapıp `exit` ile çıkın:

```bash
docker exec -it debug-web sh
```

```bash
hostname
```

```bash
ls -la /usr/share/nginx/html
```

```bash
exit
```

### 3. Canlı Dosya Kopyalama (cp)

Hazır `ornek-hotfix.html` dosyasını container'daki ana sayfanın üzerine kopyalayın:

```bash
docker cp ornek-hotfix.html debug-web:/usr/share/nginx/html/index.html
```

```bash
curl -s http://localhost:8081 | grep "Hotfix"
```

Container'daki Nginx yapılandırmasını host'a çekin:

```bash
docker cp debug-web:/etc/nginx/nginx.conf ./extracted-nginx.conf
```

```bash
head -n 5 extracted-nginx.conf
```

### 4. Dosya Sistemi Farklarını İnceleme (diff)

`A` eklenen, `C` değişen, `D` silinen dosyaları gösterir:

```bash
docker diff debug-web
```

`/usr/share/nginx/html/index.html` satırı `C` olarak görünür.

### 5. Canlı Düzeltmenin Kalıcı Olmadığını Görme

Container'ı silip aynı image'dan yeniden oluşturun:

```bash
docker rm -f debug-web
```

```bash
docker run -d --name debug-web -p 8081:80 nginx:alpine
```

```bash
curl -s http://localhost:8081 | grep -c "Hotfix" || echo "Hotfix kayboldu: degisiklik yalnizca silinen konteynerin yazilabilir katmanindaydi"
```

`docker cp` ile yapılan değişiklik kalıcı değildir; yalnızca teşhis ve acil durum içindir.

### 6. Log İnceleme

Log üretmek için birkaç istek gönderin:

```bash
curl -s http://localhost:8081 > /dev/null
```

```bash
curl -s http://localhost:8081/olmayan-sayfa > /dev/null
```

Son satırları zaman damgasıyla görün:

```bash
docker logs --tail 5 -t debug-web
```

Yalnızca son 2 dakikanın loglarını görün:

```bash
docker logs --since 2m debug-web
```

Yalnızca hata (404) satırlarını filtreleyin:

```bash
docker logs debug-web 2>&1 | grep " 404 "
```

Logları canlı izleyin. Başka bir terminalden `curl http://localhost:8081` çalıştırıp yeni satırın geldiğini görün, ardından `Ctrl+C` ile çıkın:

```bash
docker logs -f debug-web
```

<details>
<summary><strong>İsteğe bağlı: Log dosyası nerede durur, nasıl sınırlanır?</strong></summary>

Docker, container'ın standart çıktısını varsayılan olarak (`json-file` driver) host'ta bir dosyaya yazar. Bu dosyanın yerini görün:

```bash
docker inspect --format '{{.LogPath}}' debug-web
```

Bu dosyanın varsayılan bir boyut sınırı yoktur; uzun süre çok log yazan bir container diski doldurabilir. Sınırı container başlatılırken verin: en fazla 1 MB'lık 3 dosya tutulur, eskisi silinir:

```bash
docker run -d --name debug-web-log --log-opt max-size=1m --log-opt max-file=3 nginx:alpine
```

```bash
docker inspect --format '{{json .HostConfig.LogConfig}}' debug-web-log
```

Çıktıda `"max-file":"3"` ve `"max-size":"1m"` görünür. Aynı sınır sunucudaki bütün container'lar için `/etc/docker/daemon.json` içindeki `log-opts` ayarıyla da verilebilir. Deneme container'ını silin:

```bash
docker rm -f debug-web-log
```

</details>

### 7. Süreç ve Kaynak Analizi (top, stats)

```bash
docker top debug-web
```

```bash
docker stats --no-stream debug-web
```

`docker top` host üzerindeki gerçek PID'leri gösterir; container içindeki `ps` ise container'ın kendi PID namespace'ini gösterir.

### 8. Düşük Seviye Metadata Sorgulama (inspect)

```bash
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' debug-web
```

```bash
docker inspect -f '{{.State.Status}} (OOMKilled: {{.State.OOMKilled}}, ExitCode: {{.State.ExitCode}})' debug-web
```

```bash
docker inspect -f '{{.Config.Image}} {{json .HostConfig.PortBindings}}' debug-web
```

## Temizlik

```bash
docker rm -f debug-web
```

```bash
rm -f ./extracted-nginx.conf
```
