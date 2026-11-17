# LAB-DOC-05-04 — Java Spring Boot: Layered JAR ve JVM Bellek Ayarı

| Profil / Araçlar | Açık Portlar |
|---|---|
| `maven:3.9-eclipse-temurin-21-alpine`, `eclipse-temurin:21-jre-alpine`, `curl` | 19001 |

## Amaç

- Maven ile derlenen Spring Boot uygulamasını JDK yerine yalnızca JRE içeren image'a taşımak.
- Spring Boot layered JAR ile bağımlılıkları ve uygulama kodunu ayrı layer'lara bölmek.
- JVM'in container bellek limitini `MaxRAMPercentage` ile nasıl kullandığını ölçmek.

## Ön Koşullar

- Host üzerinde **19001** portu boş olmalıdır. Aynı portu kullanan başka bir alt lab çalışıyorsa önce onu silin.
- Host'a programlama dili veya SDK kurmayın; build ortamı image'ın içindedir.

## Adım Adım Uygulama Rehberi

### 1. Dosyaları İnceleme

```bash
cd ~/docker-labs/lab-05-polyglot-application-packaging/04-java-petclinic
```

```bash
ls -la
```

```bash
cat Dockerfile
```

### 2. Image'ı Build Etme

```bash
docker build -t app-java:1.0 .
```

```bash
docker images app-java:1.0
```

### 3. Container'ı Çalıştırma

```bash
docker run -d --name test-java -p 19001:8080 app-java:1.0
```

```bash
sleep 15
```

### 4. Uç Noktaları Test Etme

```bash
curl -s http://localhost:19001/
```

```bash
curl -s http://localhost:19001/api/pets
```

Tarayıcıdan `http://<SUNUCU-IP>:19001` adresini de açabilirsiniz.

### 5. Çalışan Kullanıcıyı Doğrulama

```bash
docker exec test-java id
```

UID değeri `100` olmalıdır; uygulama root ile çalışmıyor.

<details>
<summary><strong>Notlar ve ek deney</strong></summary>

İlk build Maven bağımlılıklarını indirdiği için birkaç dakika sürer.

`ENTRYPOINT` içindeki `exec`, shell'in yerini JVM'e bırakmasını sağlar. Böylece JVM PID 1 olur ve `docker stop` ile gönderilen SIGTERM sinyalini doğrudan alır.

#### JVM Bellek Limitini Ölçme

Container'ı 512 MB bellek limitiyle yeniden başlatın. JVM, limitin %75'ini (yaklaşık 384 MB) en fazla heap olarak kullanır:

```bash
docker rm -f test-java
```

```bash
docker run -d --name test-java -p 19001:8080 --memory=512m app-java:1.0
```

```bash
sleep 15
```

```bash
curl -s http://localhost:19001/
```

Yanıttaki `max_memory_mb` değeri 380 civarındadır. Limit olmadan bu değer host belleğinin %75'idir.

</details>

## Temizlik

```bash
docker rm -f test-java
```

```bash
docker rmi app-java:1.0
```
