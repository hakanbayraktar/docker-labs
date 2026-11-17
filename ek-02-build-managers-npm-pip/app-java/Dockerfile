# ---------- 1. aşama: build -------------------------------------------------
# Bölüm 3'teki adımların aynısı: derleme ve lint, test, paket.
# Bu aşamada JDK, Maven ve indirilen kütüphaneler (~/.m2) vardır; son image'a girmezler.
FROM maven:3.9.9-eclipse-temurin-21 AS build
WORKDIR /app

# Önce yalnızca pom.xml: bağımlılıklar indirilir ve bu layer cache'te kalır
COPY pom.xml ./
RUN mvn -B -ntp -q dependency:go-offline

COPY src ./src
RUN mvn -B -ntp package

# ---------- 2. aşama: çalışma -----------------------------------------------
# Yalnızca artifact (.jar) alınır; derleyici değil, yalnızca Java çalışma ortamı (JRE) gerekir.
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=build /app/target/sepet-hesaplama-1.0.0.jar app.jar

USER nobody
CMD ["java", "-jar", "app.jar"]
