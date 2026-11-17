#!/usr/bin/env bash
# ==============================================================================
# Harbor ve Trivy kurulum betiği (HTTP, port 18444)
#
# Kullanım:
#   sudo HARBOR_HOSTNAME=harbor.lab.local HARBOR_ADMIN_PASSWORD='...' bash ./install_harbor.sh
#
# Notlar:
# - Docker CLI erişimi 127.0.0.1:18444 üzerinden yapılır. Docker, 127.0.0.0/8
#   adreslerindeki registry'leri TLS olmadan kabul ettiği için
#   /etc/docker/daemon.json dosyasında değişiklik gerekmez ve dosyaya dokunulmaz.
# - TLS, Harbor'ın önündeki reverse proxy'de sonlandırılır.
# ==============================================================================
set -euo pipefail

HARBOR_VERSION="${HARBOR_VERSION:-v2.12.2}"
HARBOR_PORT="${HARBOR_PORT:-18444}"
HARBOR_HOSTNAME="${HARBOR_HOSTNAME:-harbor.lab.local}"
HARBOR_ADMIN_PASSWORD="${HARBOR_ADMIN_PASSWORD:-Harbor12345}"
INSTALL_DIR="${INSTALL_DIR:-/opt/harbor}"

command -v docker >/dev/null || { echo "HATA: Docker bulunamadi."; exit 1; }
docker compose version >/dev/null || { echo "HATA: Docker Compose v2 bulunamadi."; exit 1; }

if curl -fsS "http://127.0.0.1:${HARBOR_PORT}/api/v2.0/systeminfo" >/dev/null 2>&1; then
    echo "Harbor zaten ${HARBOR_PORT} portunda calisiyor; kurulum atlandi."
    exit 0
fi

mkdir -p "${INSTALL_DIR}"
WORK_DIR="$(mktemp -d)"
trap 'rm -rf "${WORK_DIR}"' EXIT

echo "===> Harbor ${HARBOR_VERSION} indiriliyor..."
curl -fsSL "https://github.com/goharbor/harbor/releases/download/${HARBOR_VERSION}/harbor-online-installer-${HARBOR_VERSION}.tgz" \
    -o "${WORK_DIR}/harbor.tgz"
tar -xzf "${WORK_DIR}/harbor.tgz" -C "${INSTALL_DIR}" --strip-components=1

echo "===> harbor.yml hazirlaniyor..."
cd "${INSTALL_DIR}"
cp -f harbor.yml.tmpl harbor.yml
# Harbor, hostname olarak IP veya localhost kabul etmez; FQDN gerekir.
sed -i "s|^hostname: .*|hostname: ${HARBOR_HOSTNAME}|" harbor.yml
sed -i "s|^  port: 80$|  port: ${HARBOR_PORT}|" harbor.yml
sed -i "s|^harbor_admin_password: .*|harbor_admin_password: ${HARBOR_ADMIN_PASSWORD}|" harbor.yml
sed -i "s|^data_volume: .*|data_volume: ${INSTALL_DIR}/data|" harbor.yml
# HTTPS bloğu kapatılır; TLS reverse proxy'de sonlandırılır.
sed -i '/^https:/,/private_key:/ s/^/#/' harbor.yml

grep -q "${HARBOR_HOSTNAME}" /etc/hosts || echo "127.0.0.1 ${HARBOR_HOSTNAME}" >> /etc/hosts

echo "===> Harbor ve Trivy baslatiliyor..."
./prepare --with-trivy
./install.sh --with-trivy

echo "Harbor hazir: http://127.0.0.1:${HARBOR_PORT} (kullanici: admin)"
