# LAB-DOC-05-07 — React (Vite) SPA'yı Nginx ile Paketleme

| Profil / Araçlar | Açık Portlar |
|---|---|
| `node:20-alpine`, `nginxinc/nginx-unprivileged:1.27-alpine`, `curl` | 19001 |

## Amaç

- React uygulamasını Node.js aşamasında statik dosyalara build etmek ve yalnızca bu dosyaları Nginx image'ına taşımak.
- SPA yönlendirmesi için Nginx `try_files` ayarını uygulamak.
- Nginx'i root olmayan kullanıcıyla 8080 portunda çalıştırmak.

## Ön Koşullar

- Host üzerinde **19001** portu boş olmalıdır. Aynı portu kullanan başka bir alt lab çalışıyorsa önce onu silin.
- Host'a programlama dili veya SDK kurmayın; build ortamı image'ın içindedir.

## Adım Adım Uygulama Rehberi

### 1. Dosyaları İnceleme

```bash
cd ~/docker-labs/lab-05-polyglot-application-packaging/07-frontend-react
```

```bash
ls -la
```

```bash
cat Dockerfile
```

### 2. Image'ı Build Etme

```bash
docker build -t app-react:1.0 .
```

```bash
docker images app-react:1.0
```

### 3. Container'ı Çalıştırma

```bash
docker run -d --name test-react -p 19001:8080 app-react:1.0
```

### 4. Uç Noktaları Test Etme

```bash
curl -s http://localhost:19001/
```

Tarayıcıdan `http://<SUNUCU-IP>:19001` adresini de açabilirsiniz.

### 5. Çalışan Kullanıcıyı Doğrulama

```bash
docker exec test-react id
```

UID değeri `101` olmalıdır; uygulama root ile çalışmıyor.

<details>
<summary><strong>Notlar ve ek deney</strong></summary>

SPA'larda tarayıcı `/dashboard` gibi bir adresi doğrudan istediğinde Nginx dosya bulamaz. `try_files $uri $uri/ /index.html;` satırı bu istekleri `index.html`'e yönlendirir:

```bash
curl -s -o /dev/null -w "HTTP %{http_code}\n" http://localhost:19001/dashboard
```

Yanıt `HTTP 200` olur.

</details>

## Temizlik

```bash
docker rm -f test-react
```

```bash
docker rmi app-react:1.0
```
