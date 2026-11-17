# LAB-DOC-05 — Polyglot Uygulama Paketleme Atölyesi

| Profil / Araçlar | Açık Portlar |
|---|---|
| `docker build`, Node.js, Python, Go, Java, .NET, PHP ve React taban image'ları | 19001 |

## Amaç

- Farklı dillerde kurulum adımlarının Dockerfile direktiflerine nasıl dönüştüğünü görmek.
- Yorumlanan ve derlenen diller arasındaki paketleme farkını uygulamak.
- Cache dostu sıralama, multi-stage build ve root olmayan kullanıcıyı her dilde tekrar etmek.

Build kavramları (lockfile, lint, test, artifact) için önce [EK-02 — Build Yöneticileri](../ek-02-build-managers-npm-pip/README.md) labına bakın.

## Ön Koşullar

- Host üzerinde **19001** portu boş olmalıdır. Alt lablar aynı portu kullanır; bir alt labı bitirip temizledikten sonra diğerine geçin.
- Host'a Node.js, Python, Go, Java veya .NET kurmayın. Build ortamı image'ın içinde gelir.

## Alt Lablar

İlk üç alt lab zorunludur. Diğerleri isteğe bağlıdır ve büyük SDK image'ları indirdiği için daha uzun sürer.

| Alt lab | Dil | Taban image'lar | Kapsam |
|---|---|---|---|
| [LAB-DOC-05-01](01-nodejs/README.md) | Node.js (Express) | `node:24-alpine` | Zorunlu |
| [LAB-DOC-05-02](02-python/README.md) | Python | `python:3.12-slim` | Zorunlu |
| [LAB-DOC-05-03](03-golang/README.md) | Go | `golang:1.26-alpine` → `scratch` | Zorunlu |
| [LAB-DOC-05-04](04-java-petclinic/README.md) | Java Spring Boot | `maven:3.9-eclipse-temurin-21-alpine` → `eclipse-temurin:21-jre-alpine` | İsteğe bağlı |
| [LAB-DOC-05-05](05-dotnet/README.md) | .NET 8 | `dotnet/sdk:8.0` → `dotnet/aspnet:8.0-alpine` | İsteğe bağlı |
| [LAB-DOC-05-06](06-php/README.md) | PHP 8.3 | `php:8.3-cli-alpine` + `composer:2` | İsteğe bağlı |
| [LAB-DOC-05-07](07-frontend-react/README.md) | React (Vite) | `node:20-alpine` → `nginx-unprivileged:1.27-alpine` | İsteğe bağlı |

## Doğrulama

Tüm alt lablar bittiğinde image boyutlarını karşılaştırın:

```bash
docker images --filter "reference=app-*" --format '{{.Repository}}:{{.Tag}} {{.Size}}'
```

Yaklaşık değerler: Go 8 MB, React 78 MB, PHP 150 MB, .NET 170 MB, Python 200 MB, Node.js 245 MB, Java 375 MB.

## Temizlik

```bash
docker rm -f test-node test-python test-go test-java test-dotnet test-php test-react 2>/dev/null || true
```

```bash
docker rmi app-node:1.0 app-python:1.0 app-go:1.0 app-java:1.0 app-dotnet:1.0 app-php:1.0 app-react:1.0 2>/dev/null || true
```
