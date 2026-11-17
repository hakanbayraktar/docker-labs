"""Sipariş worker'ı: Redis'teki 'orders' kuyruğundan sipariş alır, hazırlar
ve durumunu PostgreSQL'de 'hazirlandi' yapar."""
import os
import signal
import sys
import time

import psycopg2
import redis

# docker compose stop gönderdiğinde beklemeden kapan
signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "cache"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    decode_responses=True,
)

print("worker basladi, 'orders' kuyrugu dinleniyor", flush=True)

while True:
    # Kuyrukta iş yoksa 5 saniye bekler, sonra tekrar dener
    item = r.brpop("orders", timeout=5)
    if item is None:
        continue
    order_id = int(item[1])
    time.sleep(1)  # siparişi hazırlama süresi
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "db"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        dbname=os.environ["POSTGRES_DB"],
    )
    with conn, conn.cursor() as cur:
        cur.execute("UPDATE orders SET status = 'hazirlandi' WHERE id = %s;", (order_id,))
    conn.close()
    print(f"siparis {order_id} hazirlandi", flush=True)
