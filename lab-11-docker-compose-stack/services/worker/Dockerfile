FROM python:3.12-slim-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY worker.py .

# Root olmayan kullanıcı
RUN useradd -u 10001 -M appuser
USER 10001

# -u: çıktı tamponlanmaz, docker compose logs satırları hemen görür
CMD ["python", "-u", "worker.py"]
