# LAB-DOC-05-02 — Python API Paketleme

| Profil / Araçlar | Açık Portlar |
|---|---|
| `python:3.12-slim`, `pip`, `curl` | 19001 |

## Amaç

- Bir Python HTTP API'sini `requirements.txt` bağımlılıklarıyla image'a paketlemek.
- `PYTHONUNBUFFERED` ve `PYTHONDONTWRITEBYTECODE` ayarlarının nedenini öğrenmek.
- Uygulamayı `useradd` ile oluşturulan UID 10001 kullanıcısıyla çalıştırmak.

## Ön Koşullar

- Host üzerinde **19001** portu boş olmalıdır. Aynı portu kullanan başka bir alt lab çalışıyorsa önce onu silin.
- Host'a programlama dili veya SDK kurmayın; build ortamı image'ın içindedir.

## Adım Adım Uygulama Rehberi

### 1. Dosyaları İnceleme

```bash
cd ~/docker-labs/lab-05-polyglot-application-packaging/02-python
```

```bash
ls -la
```

```bash
cat Dockerfile
```

### 2. Image'ı Build Etme

```bash
docker build -t app-python:1.0 .
```

```bash
docker images app-python:1.0
```

### 3. Container'ı Çalıştırma

```bash
docker run -d --name test-python -p 19001:8000 app-python:1.0
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
docker exec test-python id
```

UID değeri `10001` olmalıdır; uygulama root ile çalışmıyor.

<details>
<summary><strong>Notlar ve ek deney</strong></summary>

`PYTHONUNBUFFERED=1` olmadan Python çıktıyı tamponlar ve `docker logs` satırları gecikmeli görünür.

</details>

## Temizlik

```bash
docker rm -f test-python
```

```bash
docker rmi app-python:1.0
```
