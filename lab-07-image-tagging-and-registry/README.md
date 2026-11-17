# LAB-DOC-07 — Docker Hub: Public ve Private Repository'ye Push ve Pull

| Profil / Araçlar | Açık Portlar |
|---|---|
| `docker tag`, `docker push`, `docker pull`, Docker Hub hesabı | 19001 |

## Amaç

- Bir image'ı Docker Hub'daki public ve private repository'ye göndermek.
- Oturum kapalıyken public image'ın çekildiğini, private image'ın reddedildiğini görmek.
- Giriş yapıp private image'ı çekip çalıştırmak.

## Ön Koşullar

- Ücretsiz bir [Docker Hub](https://hub.docker.com) hesabı.
- Host üzerinde **19001** portu boş olmalıdır. Doluysa: `docker ps --filter publish=19001`

## Adım Adım Uygulama Rehberi

### 1. Image'ı Build Etme

```bash
cd ~/docker-labs/lab-07-image-tagging-and-registry
```

```bash
docker build -t devops-app:1.0.0 starter/
```

```bash
docker run --rm devops-app:1.0.0 cat /usr/share/nginx/html/index.html | grep Surum
```

Beklenen çıktı: `<p>Surum: 1.0.0</p>`

### 2. Docker Hub'da İki Repository Açma

1. [hub.docker.com](https://hub.docker.com) adresinde oturum açın.
2. **Repositories → Create repository** ile `devops-app-public` adında **Public** bir repository oluşturun.
3. Aynı yolla `devops-app-private` adında **Private** bir repository oluşturun.
4. **Account settings → Personal access tokens** bölümünden `Read & Write` yetkili bir token oluşturup kopyalayın.

### 3. Giriş Yapma

Kendi kullanıcı adınızı yazın:

```bash
DOCKERHUB_USERNAME="<DOCKERHUB_KULLANICI_ADINIZ>"
```

Şifre sorulduğunda token'ı yapıştırın:

```bash
docker login -u "${DOCKERHUB_USERNAME}"
```

Beklenen çıktı: `Login Succeeded`

### 4. Tag'leme ve Push

Docker Hub'a gönderilecek image'ın adı `<kullanıcı>/<repository>:<etiket>` biçiminde olmalıdır:

```bash
docker tag devops-app:1.0.0 "${DOCKERHUB_USERNAME}/devops-app-public:1.0.0"
```

```bash
docker tag devops-app:1.0.0 "${DOCKERHUB_USERNAME}/devops-app-private:1.0.0"
```

```bash
docker push "${DOCKERHUB_USERNAME}/devops-app-public:1.0.0"
```

```bash
docker push "${DOCKERHUB_USERNAME}/devops-app-private:1.0.0"
```

### 5. Oturum Kapalıyken Pull

```bash
docker logout
```

```bash
docker rmi "${DOCKERHUB_USERNAME}/devops-app-public:1.0.0" "${DOCKERHUB_USERNAME}/devops-app-private:1.0.0"
```

Public image giriş yapmadan çekilir:

```bash
docker pull "${DOCKERHUB_USERNAME}/devops-app-public:1.0.0"
```

Private image reddedilir:

```bash
docker pull "${DOCKERHUB_USERNAME}/devops-app-private:1.0.0"
```

Çıktıda `pull access denied` hatası görünür: Docker Hub, giriş yapmamış birine private repository'nin varlığını bile göstermez.

### 6. Giriş Yapıp Private Image'ı Çalıştırma

```bash
docker login -u "${DOCKERHUB_USERNAME}"
```

```bash
docker pull "${DOCKERHUB_USERNAME}/devops-app-private:1.0.0"
```

```bash
docker run -d --name test-private -p 19001:80 "${DOCKERHUB_USERNAME}/devops-app-private:1.0.0"
```

Tarayıcıdan açılacak adres:

```bash
echo "https://$(hostname)-app1.devopsatolyesi.com"
```

## Temizlik

```bash
docker rm -f test-private 2>/dev/null || true
```

```bash
docker rmi devops-app:1.0.0 "${DOCKERHUB_USERNAME}/devops-app-public:1.0.0" "${DOCKERHUB_USERNAME}/devops-app-private:1.0.0" 2>/dev/null || true
```

```bash
docker logout
```

Docker Hub'daki iki repository'yi **Settings → Delete repository** ile silebilirsiniz.
