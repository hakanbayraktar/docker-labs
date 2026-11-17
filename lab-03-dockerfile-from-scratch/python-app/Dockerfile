# Taban image: Python kurulu hafif Debian
FROM python:3.12-slim

# Container içindeki çalışma dizini
WORKDIR /app

# Önce bağımlılık listesini kopyala ve paketleri kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sonra uygulama kodunu kopyala
COPY app.py .

# Uygulamanın dinlediği port
EXPOSE 5000

# Container başlayınca çalışacak komut
CMD ["python", "app.py"]
