import sqlite3
import json
import os

DB_PATH = "app/database/omni_vision.db"
JSON_PATH = "app/database/products.json"

def create_tables(cursor):
    # ÇOK KRİTİK: Eski tabloları tamamen kaldırıyoruz ki yeni kolonlar eklenebilsin
    cursor.execute("DROP TABLE IF EXISTS products")
    cursor.execute("DROP TABLE IF EXISTS orders")

    # Ürünler Tablosu (Yeni 8 kolonlu yapı)
    cursor.execute("""
    CREATE TABLE products (
        id INTEGER PRIMARY KEY,
        name TEXT, 
        category TEXT, 
        price REAL,
        stock_S INTEGER, 
        stock_M INTEGER, 
        stock_L INTEGER,
        image_filename TEXT
    )
    """)

    # Siparişler Tablosu
    cursor.execute("""
    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_phone TEXT, 
        product_id INTEGER,
        size TEXT, 
        status TEXT, 
        tracking_number TEXT
    )
    """)

def setup():
    if not os.path.exists("app/database"):
        os.makedirs("app/database")
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabloları tertemiz oluştur
    create_tables(cursor)
    
    # JSON'dan 25 ürünü oku ve aktar
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    for p in data:
        cursor.execute("""
            INSERT INTO products VALUES (?,?,?,?,?,?,?,?)
        """, (p["id"], p["name"], p["category"], p["price"], 
              p["stock_S"], p["stock_M"], p["stock_L"], p["image_filename"]))
    
    conn.commit()
    conn.close()
    print("🚀 Başarılı: Eski veritabanı silindi ve 25 ürünle 8 kolonlu yeni yapı kuruldu!")

if __name__ == "__main__":
    setup()