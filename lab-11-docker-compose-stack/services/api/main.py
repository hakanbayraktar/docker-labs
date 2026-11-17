"""Ürün ve sipariş API'si.

PostgreSQL'e yazar; Redis'i ürün listesi için cache, siparişler için kuyruk olarak kullanır.
"""
import json
import os
from contextlib import asynccontextmanager

import psycopg2
import redis
from fastapi import FastAPI, HTTPException
from psycopg2.extras import RealDictCursor

VERSION = "1.0"

SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    price NUMERIC(10, 2) NOT NULL
);
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    product_id INT NOT NULL REFERENCES products(id),
    qty INT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'beklemede'
);
"""


def sql(query, params=(), fetch="all"):
    """Sorguyu çalıştırır; fetch='all' satır listesi, 'one' tek satır, None hiçbir şey döner."""
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "db"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        dbname=os.environ["POSTGRES_DB"],
    )
    try:
        with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            if fetch == "all":
                return [dict(r) for r in cur.fetchall()]
            if fetch == "one":
                row = cur.fetchone()
                return dict(row) if row else None
            return None
    finally:
        conn.close()


def cache():
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "cache"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        decode_responses=True,
    )


@asynccontextmanager
async def lifespan(_app):
    sql(SCHEMA, fetch=None)
    print("Tablolar hazir.", flush=True)
    yield


app = FastAPI(title="Shop API", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/api/v1/info")
def info():
    return {"service": "shop-api", "version": VERSION}


@app.get("/api/v1/products")
def list_products():
    cached = cache().get("products")
    if cached:
        return {"source": "redis_cache", "data": json.loads(cached)}
    products = sql("SELECT id, title, price::float AS price FROM products ORDER BY id;")
    # Liste 30 saniye cache'te kalır
    cache().setex("products", 30, json.dumps(products))
    return {"source": "postgresql_database", "data": products}


@app.post("/api/v1/products")
def create_product(title: str, price: float):
    product = sql(
        "INSERT INTO products (title, price) VALUES (%s, %s) RETURNING id, title, price::float AS price;",
        (title, price),
        fetch="one",
    )
    cache().delete("products")  # liste değişti, cache'i sil
    return {"message": "Urun eklendi", "product": product}


@app.post("/api/v1/orders")
def create_order(product_id: int, qty: int = 1):
    if not sql("SELECT id FROM products WHERE id = %s;", (product_id,), fetch="one"):
        raise HTTPException(status_code=404, detail="Urun bulunamadi")
    order = sql(
        "INSERT INTO orders (product_id, qty) VALUES (%s, %s) RETURNING id, product_id, qty, status;",
        (product_id, qty),
        fetch="one",
    )
    # Siparişi kuyruğa koy; worker servisi alıp işler
    cache().lpush("orders", order["id"])
    return {"message": "Siparis alindi", "order": order}


@app.get("/api/v1/orders")
def list_orders():
    return sql(
        "SELECT o.id, p.title, o.qty, o.status FROM orders o "
        "JOIN products p ON p.id = o.product_id ORDER BY o.id;"
    )
