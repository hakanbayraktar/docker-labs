# Derleme her zaman derleyicinin kendi mimarisinde (BUILDPLATFORM) çalışır; emülasyon gerekmez
FROM --platform=$BUILDPLATFORM golang:1.26-alpine AS builder
# BuildKit, hedef platform için bu değişkenleri otomatik doldurur
ARG TARGETOS
ARG TARGETARCH
WORKDIR /src
COPY go.mod main.go ./
# Go, hedef işletim sistemi ve mimari için çapraz derleme yapar
RUN CGO_ENABLED=0 GOOS=$TARGETOS GOARCH=$TARGETARCH go build -ldflags="-s -w" -o /out/hello .

FROM scratch
COPY --from=builder /out/hello /hello
ENTRYPOINT ["/hello"]
