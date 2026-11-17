# LAB-DOC-05-05 — .NET 8 Minimal API Paketleme

| Profil / Araçlar | Açık Portlar |
|---|---|
| `mcr.microsoft.com/dotnet/sdk:8.0`, `mcr.microsoft.com/dotnet/aspnet:8.0-alpine`, `curl` | 19001 |

## Amaç

- `dotnet publish` çıktısını SDK içermeyen ASP.NET runtime image'ına taşımak.
- `.csproj` dosyasını önce kopyalayarak `dotnet restore` layer'ını cache'te tutmak.
- .NET 8 image'larındaki hazır root olmayan kullanıcıyı (`$APP_UID`) kullanmak.

## Ön Koşullar

- Host üzerinde **19001** portu boş olmalıdır. Aynı portu kullanan başka bir alt lab çalışıyorsa önce onu silin.
- Host'a programlama dili veya SDK kurmayın; build ortamı image'ın içindedir.

## Adım Adım Uygulama Rehberi

### 1. Dosyaları İnceleme

```bash
cd ~/docker-labs/lab-05-polyglot-application-packaging/05-dotnet
```

```bash
ls -la
```

```bash
cat Dockerfile
```

### 2. Image'ı Build Etme

```bash
docker build -t app-dotnet:1.0 .
```

```bash
docker images app-dotnet:1.0
```

### 3. Container'ı Çalıştırma

```bash
docker run -d --name test-dotnet -p 19001:8080 app-dotnet:1.0
```

### 4. Uç Noktaları Test Etme

```bash
curl -s http://localhost:19001/
```

```bash
curl -s http://localhost:19001/health
```

Tarayıcıdan `http://<SUNUCU-IP>:19001` adresini de açabilirsiniz.

### 5. Çalışan Kullanıcıyı Doğrulama

```bash
docker exec test-dotnet id
```

UID değeri `1654` olmalıdır; uygulama root ile çalışmıyor.

<details>
<summary><strong>Notlar ve ek deney</strong></summary>

İlk build SDK image'ını indirdiği için birkaç dakika sürer.

</details>

## Temizlik

```bash
docker rm -f test-dotnet
```

```bash
docker rmi app-dotnet:1.0
```
