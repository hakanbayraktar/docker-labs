# LAB-DOC-05-03 — Go Mikroservisini Scratch Image'la Paketleme

| Profil / Araçlar | Açık Portlar |
|---|---|
| `golang:1.26-alpine`, `scratch`, `curl` | 19001 |

## Amaç

- Go uygulamasını multi-stage build ile statik binary olarak derlemek.
- Hiçbir işletim sistemi dosyası içermeyen `scratch` image'ı ile 10 MB altı image üretmek.
- Shell'i olmayan bir image'da `docker exec` ile komut çalıştırılamadığını görmek.

## Ön Koşullar

- Host üzerinde **19001** portu boş olmalıdır. Aynı portu kullanan başka bir alt lab çalışıyorsa önce onu silin.
- Host'a programlama dili veya SDK kurmayın; build ortamı image'ın içindedir.

## Adım Adım Uygulama Rehberi

### 1. Dosyaları İnceleme

```bash
cd ~/docker-labs/lab-05-polyglot-application-packaging/03-golang
```

```bash
ls -la
```

```bash
cat Dockerfile
```

### 2. Image'ı Build Etme

```bash
docker build -t app-go:1.0 .
```

```bash
docker images app-go:1.0
```

### 3. Container'ı Çalıştırma

```bash
docker run -d --name test-go -p 19001:8080 app-go:1.0
```

### 4. Uç Noktaları Test Etme

```bash
curl -s http://localhost:19001/
```

```bash
curl -s http://localhost:19001/health
```

Tarayıcıdan `http://<SUNUCU-IP>:19001` adresini de açabilirsiniz.

### 5. Shell Olmadığını Doğrulama

```bash
docker exec test-go sh || echo "scratch imajinda sh yok"
```

`scratch` image'ında shell, paket yöneticisi veya başka bir araç yoktur; içinde yalnızca uygulama binary'si bulunur.

<details>
<summary><strong>Notlar ve ek deney</strong></summary>

`CGO_ENABLED=0` binary'nin C kütüphanelerine bağımlı olmamasını sağlar; bu yüzden içinde libc bile olmayan `scratch` image'ında çalışabilir.

</details>

## Temizlik

```bash
docker rm -f test-go
```

```bash
docker rmi app-go:1.0
```
