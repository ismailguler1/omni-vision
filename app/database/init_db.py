import sqlite3
import os
import json

# Veritabanı dosyasının oluşturulacağı yol
DB_PATH = "app/database/omni_vision.db"
JSON_PATH = "app/database/products.json"

def create_tables(cursor):
    """Gerekli tabloları (products ve orders) oluşturur."""
    
    # Ürünler Tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY, -- FAISS indeksindeki ID ile aynı olacak
        name TEXT NOT NULL,
        category TEXT,
        price REAL,
        stock INTEGER,
        image_filename TEXT
    )
    """)

    # Siparişler Tablosu (Otomasyon testleri için)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_phone TEXT,
        product_id INTEGER,
        status TEXT,
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
    """)
    print("Tablolar başarıyla oluşturuldu.")

def insert_mock_data(cursor):
    """Veritabanını test için sahte ürünler ve siparişlerle doldurur."""
    
    # 1. Sahte Ürünler (20-200 ürün arası bir yelpazeyi simüle etmek için örnekler)
    # id değerleri 0'dan başlıyor çünkü FAISS vektör veritabanı indekslemeye 0'dan başlar.
# 1. JSON dosyasından gerçek ürünleri oku
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        products_data = json.load(f)

    sample_products = [
        (p["id"], p["name"], p["category"], p["price"], p["stock"], p["image_filename"])
        for p in products_data
    ]

    # Tabloyu temizle (Kodu birden fazla kez çalıştırırsak veri çoğalmasın diye)
    cursor.execute("DELETE FROM products")
    cursor.execute("DELETE FROM orders")

    # Ürünleri ekle
    cursor.executemany("""
    INSERT INTO products (id, name, category, price, stock, image_filename)
    VALUES (?, ?, ?, ?, ?, ?)
    """, sample_products)
    print(f"{len(sample_products)} adet gerçek ürün JSON'dan eklendi.")

    # 2. Sahte Siparişler ("Siparişim nerede?" soruları için)
    sample_orders = [
        ("5551234567", 0, "Kargoya Verildi"),
        ("5559876543", 1, "Beklemede")
    ]

    cursor.executemany("""
    INSERT INTO orders (customer_phone, product_id, status)
    VALUES (?, ?, ?)
    """, sample_orders)
    print(f"{len(sample_orders)} adet mock sipariş eklendi.")

def main():
    # Veritabanına bağlan (dosya yoksa oluşturur)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        create_tables(cursor)
        insert_mock_data(cursor)
        conn.commit() # Değişiklikleri kaydet
        print(f"Veritabanı kurulumu tamamlandı. Dosya konumu: {DB_PATH}")
    except sqlite3.Error as e:
        print(f"Veritabanı hatası: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()