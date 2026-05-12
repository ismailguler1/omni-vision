from fastapi import FastAPI, UploadFile, File, HTTPException
import sqlite3
import faiss
import numpy as np
import shutil
import os
from app.models.vision_model import OmniVisionModel
from app.core.agent import get_agent_response
from pydantic import BaseModel
from rembg import remove
from typing import Optional

app = FastAPI(
    title="Omni-Vision API", 
    description="KOBİ'ler için Görselden Sepete Otomasyon Sistemi API'si"
)

# Sistem bellek değişkenleri
vision_model = None
vector_index = None
DB_PATH = "app/database/omni_vision.db"

@app.on_event("startup")
async def load_systems():
    """Uygulama başlarken yapay zeka modelini ve vektör veritabanını RAM'e yükler."""
    global vision_model, vector_index
    print("Sistemler başlatılıyor, yapay zeka modelleri yükleniyor...")
    
    # Görüntü işleme modelini başlat
    vision_model = OmniVisionModel()
    
    # FAISS indeksini yükle
    if os.path.exists("vector_index.faiss"):
        vector_index = faiss.read_index("vector_index.faiss")
        print("FAISS indeksi başarıyla yüklendi.")
    else:
        print("UYARI: vector_index.faiss bulunamadı. Önce vision_model.py çalıştırılmalı!")

def get_db_connection():
    """SQLite veritabanı bağlantısı sağlar."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # Verileri JSON gibi sözlük formatında almak için
    return conn

@app.post("/match-product/")
async def match_product(file: UploadFile = File(...)):
    """
    Kullanıcının gönderdiği fotoğrafı alır, vektöre çevirir, 
    FAISS'te arar ve SQLite'tan stok durumunu döner.
    """
    if not vector_index:
        raise HTTPException(status_code=500, detail="Sistem henüz tam yüklenmedi veya FAISS indeksi eksik.")

    # 1. Gelen fotoğrafı geçici olarak kaydet (İşlem bitince silinecek)
    temp_path = f"temp_{file.filename}"

    #input_image_data = await file.read() # Fotoğrafı oku
    ## rembg ile arka planı yok et
    #clean_image_data = remove(input_image_data)

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        #buffer.write(clean_image_data)

    try:
        # 2. Görselden vektör çıkar (Kişi 1'in modülü)
        embedding = vision_model.get_embedding(temp_path)
        embedding_np = np.array([embedding]).astype('float32')

        # 3. FAISS ile kosinüs benzerliği araması yap ve en yakın 1 ürünü bul
        distances, indices = vector_index.search(embedding_np, 1)
        matched_id = int(indices[0][0])
        distance_score = float(distances[0][0]) # Eşleşme mesafesini alıyoruz

        print(f"Eşleşen ID: {matched_id}, Mesafe Skoru: {distance_score}")

        # GÜVEN SKORU KONTROLÜ (Threshold)
        # Not: MobileNetV3 vektörleri için 150-200 arası bir sınır genelde idealdir. 
        # Bunu testlerle (örneğin kedi fotoğrafı yükleyerek) optimize edebilirsiniz.
        THRESHOLD = 7000.0 

        if distance_score > THRESHOLD:
            return {
                "status": "warning",
                "message": "Görsel çok karmaşık veya sistemdeki hiçbir ürüne yeterince benzemiyor. Lütfen ürünü daha yakından çekin.",
                "distance": distance_score
            }


        # 4. Bulunan ID'yi SQLite veritabanından sorgula (Kişi 2'nin modülü)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = ?", (matched_id,))
        product = cursor.fetchone()
        conn.close()

        if product:
            return {
                "status": "success",
                "matched_id": product["id"],
                "product_name": product["name"],
                "category": product["category"],
                "stock_quantity": product["stock"],
                "price": product["price"],
                "distance": distance_score
            }
        else:
            return {"status": "error", "message": "Eşleşen ürün veritabanında bulunamadı."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # 5. Sistemi temiz tutmak için geçici dosyayı sil
        if os.path.exists(temp_path):
            os.remove(temp_path)
    

    # Kullanıcıdan gelecek chat mesajının yapısı
class ChatRequest(BaseModel):
    message: str
    image_context: Optional[str] = None  # Artık açıkça "null" gelmesini de kabul ediyor

@app.post("/chat/")
async def chat_with_agent(request: ChatRequest):
    """
    Kullanıcının metin mesajlarını Gemini ajanı ile işler.
    Eğer fonksiyon çağırması gerekirse (sipariş durumu vb.) otomatik yapar.
    """
    try:
        reply = get_agent_response(request.message, request.image_context)
        return {"status": "success", "reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))