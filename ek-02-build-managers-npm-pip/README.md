# LAB-DOC-EK-02 — Build Yöneticileri: npm ve pip ile Build

| Profil / Araçlar | Açık Portlar |
|---|---|
| Ubuntu 24.04, Node.js 24 ve npm, Python 3.12, `venv`, pip, ESLint, `node:test`, pytest, flake8, Docker; isteğe bağlı: Java 21 ve Maven | — |

## Amaç

- Build'in dört adımını çalıştırıp her dilde bir artifact üretmek: `.tgz`, `.whl`, `.jar`.
- Build'den çıkan uygulamayı çalıştırıp sonucunu görmek.
- Artifact'ın CI/CD'de nereye gittiğini ve nasıl deploy edildiğini anlamak.
- Aynı build'i multi-stage Dockerfile ile küçük bir image'a dönüştürmek.

## Ön Koşullar

- Ubuntu 24.04 ve `sudo` yetkisi.
- İnternet erişimi: NodeSource, npm, PyPI, Maven Central ve Docker Hub.
- Bölüm 4 için Docker kurulu olmalı (bu reponun ana README'sindeki kurulum bloğu).

## Kavramlar

### Build ve artifact

Build, kaynak kodu çalışmaya hazır tek bir pakete dönüştürür. Bu pakete **artifact** denir. Adımlar her dilde aynıdır:

```text
kaynak kod ─► 1. bağımlılık ─► 2. lint ─► 3. test ─► 4. paket (artifact) ─► çalıştır
```

| Dil | Bağımlılık listesi | Build aracı | Artifact | Artifact nasıl kullanılır? |
|---|---|---|---|---|
| Node.js | `package.json` + `package-lock.json` | npm | `sepet-hesaplama-1.0.0.tgz` | `npm install paket.tgz` |
| Python | `requirements.txt` + `pyproject.toml` | pip | `sepet_hesaplama-1.0.0-py3-none-any.whl` | `pip install paket.whl` |
| Java | `pom.xml` | Maven | `sepet-hesaplama-1.0.0.jar` | `java -jar paket.jar` |

İki şeyi karıştırmayın:

- **Bağımlılık kurmak** (`npm ci`, `pip install -r`) **başkalarının** paketlerini indirir; kodumuzu test edip çalıştırabilmek için gerekir. Build'in başıdır.
- **Artifact üretmek** (`npm pack`, `pip wheel`, `mvn package`) **bizim** kodumuzu tek bir dosyaya koyar. Build'in sonudur; başka bir sunucuya taşınan ve kurulan şey budur.

Bir benzetme: bağımlılık listesi alışveriş listesi, bağımlılık kurmak markete gidip malzemeleri almak. Artifact ise pişirip kutuya koyduğumuz, teslim ettiğimiz yemek.

<details>
<summary><strong>Lint ve test build'de ne işe yarar?</strong></summary>

Bu labdaki lint ve testler, kodun her satırını test etmek için değildir. Görevleri build'in **kalite kapısı** olmaktır: geliştiricinin yazdığı birkaç kontrol her build'de otomatik çalışır, biri bile başarısız olursa build durur ve artifact üretilmez.

- **Lint:** Kodu çalıştırmadan okur; yazım hatası, kullanılmayan değişken, tanımsız isim gibi sorunları saniyeler içinde bulur.
- **Test:** Kodun temel davranışını doğrular. Burada dört test var: KDV doğru mu, `0.10 + 0.20` tam `0.30` mu, boş sepet sıfır mı, geçersiz adet hata veriyor mu?

Kazancı: hata canlıda kullanıcı tarafından değil, dakikalar içinde CI'da bulunur. Bozuk kod pakete giremez. Her commit aynı kontrollerden geçtiği için "benim makinemde çalışıyordu" durumu ortadan kalkar.

</details>

<details>
<summary><strong>Artifact nereye gider? (artifact repository ve deploy)</strong></summary>

Bu labda artifact'ları sunucuda üretip bırakıyoruz. Gerçek bir CI/CD akışında artifact bir **artifact repository**'ye gönderilir; deploy da oradan yapılır:

```text
git push ─► CI: build ─► artifact repository ─► deploy: test ortamı ─► onay ─► deploy: production
            lint, test,   sürüm numarasıyla      aynı artifact                  aynı artifact
            paket         saklanır
```

| Artifact | Saklandığı yer |
|---|---|
| `.tgz` (npm) | npm registry; şirket içinde Nexus, Artifactory, GitLab ya da GitHub Packages |
| `.whl` (Python) | PyPI; şirket içinde Nexus, Artifactory ya da GitLab Package Registry |
| `.jar` (Java) | Maven repository; şirket içinde Nexus ya da Artifactory |
| Docker image | Container registry: Docker Hub, Harbor, GitLab Container Registry |

Kurallar:

- Artifact **bir kez** üretilir. Test ortamına ve production'a aynı dosya kurulur; production için yeniden build edilmez.
- Her artifact sürüm numarasıyla saklanır ve üzerine yazılmaz. Bir sorun çıkarsa önceki sürüm repository'den alınıp yeniden deploy edilir.
- Deploy, istendiğinde repository'den çekilerek yapılır: otomatik ya da bir onaydan sonra.

Artifact'ı repository'ye gönderme ve oradan deploy etme adımları Jenkins, GitLab CI ve Harbor lablarında yapılır.

</details>

## Adım Adım Uygulama Rehberi

### Bölüm 1: Node.js ve npm

| Komut | Ne yapar? | Build adımı |
|---|---|---|
| `npm ci` | `package-lock.json`'da yazan paketleri `node_modules` klasörüne kurar | 1. bağımlılık |
| `npm run lint` | `package.json`'daki `lint` betiğini, yani `eslint .` komutunu çalıştırır | 2. lint |
| `npm test` | `test` betiğini, yani `node --test` komutunu çalıştırır; `test/` klasöründeki testleri koşar | 3. test |
| `npm pack` | Uygulamayı tek bir `.tgz` paketine dönüştürür | 4. paket |
| `npm start` | `start` betiğini, yani `node src/index.js` komutunu çalıştırır | çalıştırma |

`npm run <ad>`, `package.json` içindeki `scripts` bölümünde o adla yazılmış komutu çalıştırır. `npm test` ve `npm start` bunun kısa yazılışıdır.

#### 1. Node.js kurulumu

Ubuntu 24.04 deposundaki Node.js 18'dir ve artık güncelleme almaz. Node.js 24'ü NodeSource deposundan kurun. Önce NodeSource'un kurulum betiğini indirin:

```bash
curl -fsSL https://deb.nodesource.com/setup_24.x -o /tmp/nodesource_setup.sh
```

Betiği çalıştırın. Betik Node.js'i kurmaz; NodeSource deposunu ve imza anahtarını `apt`'ye ekler:

```bash
sudo bash /tmp/nodesource_setup.sh
```

Node.js'i kurun. npm, Node.js ile birlikte gelir:

```bash
sudo apt-get install -y nodejs
```

```bash
node --version
```

```bash
npm --version
```

`node --version` çıktısı `v24` ile başlamalıdır.

#### 2. Manifest ve lockfile

```bash
cd ~/docker-labs/ek-02-build-managers-npm-pip/app-node
```

Projenin tanım dosyasını görüntüleyin: adı, sürümü, betikleri ve bağımlılıkları burada yazılıdır.

```bash
cat package.json
```

`dependencies` uygulamanın çalışırken ihtiyaç duyduğu paketlerdir; `devDependencies` yalnızca build sırasında gereken araçlardır (ESLint). `^10.4.3` bir sürüm aralığıdır: 10.x serisinde 10.4.3 ve üstü. Kurulacak kesin sürüm `package-lock.json` dosyasında yazılıdır. `grep -A3`, bulduğu satırı ve altındaki 3 satırı gösterir:

```bash
grep -A3 '"node_modules/decimal.js"' package-lock.json
```

`version` kesin sürümdür, `integrity` paketin parmak izidir: npm indirdiği dosyayı bununla doğrular.

#### 3. Bağımlılıkları kurma: `npm ci`

`npm ci`, lockfile'daki sürümleri birebir kurar. Bugün de, bir ay sonra da, CI sunucusunda da aynı sürümler gelir. `--no-audit --no-fund` yalnızca güvenlik özeti ve bağış mesajlarını kapatır:

```bash
npm ci --no-audit --no-fund
```

Kurulan doğrudan bağımlılıkları listeleyin. `--depth=0` alt bağımlılıkları göstermez:

```bash
npm ls --depth=0
```

`package.json`'da 4 paket yazılıdır; `npm ci` ise yaklaşık 80 paket kurar. Fark, bu dört paketin kendi bağımlılıklarıdır. `npm notice` ile başlayan satırlar npm'in yeni sürüm duyurusudur; hata değildir, npm'i güncellemeyin.

#### 4. Lint

ESLint kodu çalıştırmadan tarar. Hata yoksa bir şey yazmaz; sonucu çıkış kodundan okuyun. `$?` son komutun çıkış kodudur: `0` başarı, başka bir sayı hata demektir. CI araçları adımın geçip geçmediğine bu koda bakar:

```bash
npm run lint; echo "lint cikis kodu: $?"
```

`lint cikis kodu: 0` görünür.

#### 5. Test

```bash
npm test
```

Çıktının sonunda `pass 4` ve `fail 0` görünür.

#### 6. Paket (artifact)

```bash
npm pack
```

Paketin içindeki dosyaları, paketi açmadan listeleyin:

```bash
tar -tzf sepet-hesaplama-1.0.0.tgz
```

Pakette yalnızca `package.json` ve `src/` klasörü vardır; bunu `package.json` içindeki `"files": ["src"]` satırı belirler. Testler, lint ayarları ve `node_modules` pakete girmez. Paketi kuran sunucu, çalışma bağımlılığını (`decimal.js`) kurulum sırasında kendisi indirir.

#### 7. Çalıştırma

Uygulama örnek bir sepetin toplamını hesaplar ve sonucu JSON olarak ekrana yazar (`npm start` ile aynı işi yapar):

```bash
node src/index.js
```

```text
{"araToplam":"200.30","kdv":"40.06","genelToplam":"240.36"}
```

#### 8. Kırmızı build: bozuk test

Bir testteki beklenen değeri bilerek bozun. `sed -i` dosyadaki metni yerinde değiştirir; burada KDV'nin beklenen değerini `40.00`'dan `36.00`'a çeviriyoruz:

```bash
sed -i "s/assert.equal(sonuc.kdv, '40.00');/assert.equal(sonuc.kdv, '36.00');/" test/cart.test.js
```

```bash
npm test; echo "test cikis kodu: $?"
```

Çıktıda `fail 1` ve `test cikis kodu: 1` görünür. CI bu adımda durur ve paket adımına geçmez. Aynı komutla değeri `40.00`'a geri yazın:

```bash
sed -i "s/assert.equal(sonuc.kdv, '36.00');/assert.equal(sonuc.kdv, '40.00');/" test/cart.test.js
```

### Bölüm 2: Python ve pip

| Komut | Ne yapar? | Build adımı |
|---|---|---|
| `pip install -r requirements-dev.txt` | Dosyada yazan paketleri sanal ortama kurar | 1. bağımlılık |
| `flake8 .` | Kodu çalıştırmadan tarar | 2. lint |
| `pytest` | `tests/` klasöründeki testleri koşar | 3. test |
| `pip wheel .` | Uygulamayı tek bir `.whl` paketine dönüştürür | 4. paket |
| `python cart.py` | Uygulamayı çalıştırır | çalıştırma |

#### 9. Sanal ortam (venv)

Ubuntu, `pip` ile sistem geneline paket kurulmasına izin vermez. Paketler projenin içindeki bir sanal ortama kurulur. Sanal ortam desteğini kurun:

```bash
sudo apt-get install -y python3-venv
```

```bash
cd ~/docker-labs/ek-02-build-managers-npm-pip/app-python
```

Proje klasöründe `.venv` adında boş bir sanal ortam oluşturun:

```bash
python3 -m venv .venv
```

Sanal ortamı bu terminalde etkinleştirin. Komut satırının başında `(.venv)` görünür:

```bash
source .venv/bin/activate
```

Sanal ortam etkin olduğu sürece `pip` ve `python` komutları `.venv` içindekilerdir. `which` bir komutun hangi dosyadan çalıştığını gösterir; yol `.venv/bin/pip` ile bitmelidir:

```bash
which pip
```

#### 10. Bağımlılıkları kurma

`requirements.txt` çalışma bağımlılığını (`babel`), `requirements-dev.txt` ek olarak build araçlarını (`pytest`, `flake8`) kesin sürümle (`==`) verir. Python'da kesin sürümü lockfile değil, bu dosyalardaki `==` belirler:

```bash
cat requirements.txt requirements-dev.txt
```

`-r` dosyada yazan bütün paketleri kurar. `requirements-dev.txt` içindeki `-r requirements.txt` satırı diğer dosyayı da çağırdığı için ikisi birlikte kurulur:

```bash
pip install --disable-pip-version-check -r requirements-dev.txt
```

#### 11. Lint

flake8, Python için ESLint'in karşılığıdır:

```bash
flake8 .; echo "flake8 cikis kodu: $?"
```

`flake8 cikis kodu: 0` görünür.

#### 12. Test

`-q` çıktıyı kısaltır:

```bash
pytest -q
```

Çıktının sonunda `4 passed` görünür.

#### 13. Paket (artifact)

`pyproject.toml`, paketin adını, sürümünü ve çalışma bağımlılığını tanımlar; `pip wheel` bu dosyaya bakarak `.whl` paketini üretir:

```bash
cat pyproject.toml
```

`--no-deps` yalnızca bizim paketimizi üretir, bağımlılıklarınkini değil; `-w dist` paketi `dist` klasörüne yazar:

```bash
pip wheel . --no-deps --disable-pip-version-check -w dist
```

```bash
ls dist
```

`.whl` bizim kodumuzun teslim edilen paketidir. Başka bir sunucuda `pip install sepet_hesaplama-1.0.0-py3-none-any.whl` komutu uygulamayı ve çalışma bağımlılığını (`babel`) kurar; pytest ve flake8 gelmez.

#### 14. Çalıştırma

```bash
python cart.py
```

Node.js ile aynı sonuç ekrana yazılır.

`deactivate` sanal ortamı kapatır. Sanal ortamdan çıkın ve lab dizinine dönün:

```bash
deactivate
```

```bash
cd ..
```

### Bölüm 3 (isteğe bağlı): Java ve Maven

<details>
<summary><strong>Java bölümünü açmak için tıklayın</strong></summary>

| Komut | Ne yapar? | Build adımı |
|---|---|---|
| `mvn compile` | `pom.xml`'deki bağımlılıkları indirir ve kodu derler; derleyici uyarıları hata sayılır | 1. bağımlılık ve 2. lint |
| `mvn test` | `src/test` altındaki JUnit testlerini koşar | 3. test |
| `mvn package` | Uygulamayı tek bir `.jar` paketine dönüştürür | 4. paket |
| `java -jar` | Jar paketini çalıştırır | çalıştırma |

Maven'da her komut kendinden önceki adımları da çalıştırır: `mvn package` önce derler, sonra test eder, en son paketler. `-B` çıktıyı sade ve etkileşimsiz yapar; `-ntp` indirme satırlarını gizler.

#### J1. Java ve Maven kurulumu

```bash
sudo apt-get install -y openjdk-21-jdk-headless maven
```

```bash
java -version
```

```bash
mvn -version
```

`java -version` çıktısında `21` görünür.

#### J2. pom.xml

```bash
cd ~/docker-labs/ek-02-build-managers-npm-pip/app-java
```

`pom.xml`, `package.json`'ın Java'daki karşılığıdır. Maven'da lockfile yoktur; bağımlılık ve eklenti sürümleri bu dosyada kesin sayıyla yazılır. JUnit'in `test` kapsamında olduğuna dikkat edin: yalnızca build sırasında kullanılır, jar paketine girmez.

```bash
cat pom.xml
```

#### J3. Derleme ve lint

İlk çalıştırmada Maven, JUnit'i ve kendi eklentilerini indirip `~/.m2` klasörüne koyar; bir dakika kadar sürebilir. `pom.xml`'deki `-Xlint:all -Werror` ayarı, derleyicinin bulduğu her uyarıyı hataya çevirir; Java'da lint işini bu yapar:

```bash
mvn -B -ntp compile
```

Son satırlarda `BUILD SUCCESS` görünür.

#### J4. Test

```bash
mvn -B -ntp test
```

Çıktıda `Tests run: 4, Failures: 0, Errors: 0, Skipped: 0` ve `BUILD SUCCESS` görünür.

#### J5. Paket ve çalıştırma

```bash
mvn -B -ntp package
```

Jar, derlenmiş kodu ve hangi sınıfla başlayacağını söyleyen bilgiyi tek dosyada taşır:

```bash
ls target/*.jar
```

```bash
java -jar target/sepet-hesaplama-1.0.0.jar
```

Diğer iki dille aynı sonuç ekrana yazılır.

#### J6. Kırmızı build: paket hiç oluşmaz

```bash
sed -i 's/new BigDecimal("40.00"), sonuc.kdv()/new BigDecimal("36.00"), sonuc.kdv()/' src/test/java/com/example/sepet/SepetTest.java
```

`clean` önceki build'in `target` klasörünü siler; ardından paket yeniden üretilmeye çalışılır:

```bash
mvn -B -ntp clean package; echo "mvn cikis kodu: $?"
```

Çıktıda `Tests run: 4, Failures: 1`, `BUILD FAILURE` ve `mvn cikis kodu: 1` görünür. Build test adımında durdu ve paket adımına geçmedi; jar dosyası yoktur:

```bash
ls target/*.jar
```

`No such file or directory` görünür. Değeri `40.00`'a geri yazıp lab dizinine dönün:

```bash
sed -i 's/new BigDecimal("36.00"), sonuc.kdv()/new BigDecimal("40.00"), sonuc.kdv()/' src/test/java/com/example/sepet/SepetTest.java
```

```bash
cd ..
```

</details>

### Bölüm 4: Aynı build Docker ile

Docker ile sunucuya hiçbir şey kurmak gerekmez; Node.js ve Python sürümünü image tag'i belirler (`node:24-alpine`, `python:3.12-slim`). Dockerfile'lar **multi-stage**'dir: **build** aşamasında Bölüm 1–3'teki build çalışır; **çalışma** aşaması temiz bir image'a yalnızca artifact'ı alıp kurar. Build için gerekip çalışırken gereksiz olanlar son image'a girmez:

| Dil | Son image'a girmeyenler |
|---|---|
| Node.js | ESLint ve diğer `devDependencies`, testler, kaynak klasör, npm cache |
| Python | pytest, flake8, testler, build klasörleri, pip cache |
| Java | Derleyici (JDK), Maven, `~/.m2` altındaki kütüphaneler, kaynak kod |

Küçük image daha hızlı indirilir, daha az güvenlik açığı taşır ve içinde saldırganın kullanabileceği derleyici ya da paket yöneticisi bulunmaz.

#### 15. Node.js image'ı

```bash
cd app-node
```

```bash
cat Dockerfile
```

`docker build`, bulunduğunuz klasördeki Dockerfile'ı adım adım çalıştırıp bir image üretir; `-t` image'a ad ve sürüm verir:

```bash
docker build -t sepet-node:1.0.0 .
```

Karşılaştırma için yalnızca ilk aşamayı da ayrı bir image olarak üretin. `--target build` Dockerfile'ı `build` aşamasının sonunda durdurur:

```bash
docker build --target build -t sepet-node:build-stage .
```

İki image'ın boyutunu karşılaştırın:

```bash
docker image ls sepet-node
```

`build-stage` image'ı, içindeki ESLint, testler ve cache yüzünden `1.0.0`'dan büyüktür. Deploy edilen image `1.0.0`'dır.

#### 16. Kırmızı build Docker'da da durur

8. adımdaki gibi testi bilerek bozun:

```bash
sed -i "s/assert.equal(sonuc.kdv, '40.00');/assert.equal(sonuc.kdv, '36.00');/" test/cart.test.js
```

```bash
docker build -t sepet-node:bozuk .; echo "docker build cikis kodu: $?"
```

`RUN npm test` adımı hata verir, build durur ve `sepet-node:bozuk` image'ı oluşmaz. Değeri `40.00`'a geri yazın:

```bash
sed -i "s/assert.equal(sonuc.kdv, '36.00');/assert.equal(sonuc.kdv, '40.00');/" test/cart.test.js
```

#### 17. Python image'ı

```bash
cd ../app-python
```

```bash
cat Dockerfile
```

```bash
docker build -t sepet-python:1.0.0 .
```

```bash
cd ..
```

<details>
<summary><strong>İsteğe bağlı: Java image'ı</strong></summary>

Java ve Maven'ı sunucuya kurmadıysanız bile bu adım çalışır; ikisi de build aşamasındaki `maven:3.9.9-eclipse-temurin-21` image'ında gelir. Çalışma aşaması ise derleyicisi olmayan, yalnızca Java çalışma ortamını içeren `eclipse-temurin:21-jre-alpine` image'ıdır.

```bash
cd app-java
```

```bash
cat Dockerfile
```

```bash
docker build -t sepet-java:1.0.0 .
```

```bash
docker run --rm sepet-java:1.0.0
```

```bash
cd ..
```

</details>

#### 18. Image'ları çalıştırma

Her image'dan bir container çalıştırın. Uygulama sonucu yazıp kapanır; `--rm` kapanan container'ı siler:

```bash
docker run --rm sepet-node:1.0.0
```

```bash
docker run --rm sepet-python:1.0.0
```

İkisi de aynı sonucu yazar. Bu kez uygulamalar sunucuya kurduğumuz Node.js ve Python ile değil, image'ların içindekilerle çalışıyor.

## Temizlik

Lab bittiğinde sunucuda bu labdan hiçbir şey kalmaz: image'lar, build çıktıları ve sunucuya kurulan araçlar silinir.

```bash
cd ~/docker-labs/ek-02-build-managers-npm-pip
```

Image'ları silin:

```bash
docker image rm sepet-node:1.0.0 sepet-node:build-stage sepet-python:1.0.0
```

Build çıktılarını silin; kaynak koda dokunulmaz:

```bash
rm -rf app-node/node_modules app-node/reports app-node/*.tgz app-python/.venv app-python/reports app-python/dist app-python/build app-python/*.egg-info app-python/.pytest_cache app-python/__pycache__ app-python/tests/__pycache__ app-java/target
```

npm ve pip'in indirdiği paket cache'lerini silin:

```bash
rm -rf ~/.npm ~/.cache/pip
```

Node.js'i ve NodeSource deposunu kaldırın:

```bash
sudo apt-get purge -y nodejs
```

```bash
sudo rm -f /etc/apt/sources.list.d/nodesource.list /etc/apt/sources.list.d/nodesource.sources /etc/apt/keyrings/nodesource.gpg /usr/share/keyrings/nodesource.gpg /etc/apt/preferences.d/nodejs /etc/apt/preferences.d/nsolid
```

Python sanal ortam desteğini kaldırın:

```bash
sudo apt-get purge -y python3-venv python3.12-venv python3-pip-whl python3-setuptools-whl
```

```bash
sudo apt-get update
```

<details>
<summary><strong>Java bölümünü yaptıysanız</strong></summary>

```bash
docker image rm sepet-java:1.0.0
```

Java ve Maven'ı kaldırın. `autoremove`, onlarla birlikte gelen ve artık kullanılmayan paketleri de kaldırır:

```bash
sudo apt-get purge -y openjdk-21-jdk-headless maven
```

```bash
sudo apt-get autoremove --purge -y
```

Maven'ın indirdiği kütüphaneleri silin:

```bash
rm -rf ~/.m2
```

</details>

Temizliği doğrulayın. Lab klasöründe git'in tanımadığı ya da yok saydığı dosya kalmadıysa çıktı boştur:

```bash
git -C ~/docker-labs status --short --ignored ek-02-build-managers-npm-pip
```

```bash
docker ps -a --filter name=sepet- --format '{{.Names}}'; docker image ls --format '{{.Repository}}:{{.Tag}}' | grep sepet- || echo "sepet image'i yok"
```

```bash
command -v node mvn || echo "node ve mvn kaldirildi"
```
