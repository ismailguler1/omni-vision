import google.generativeai as genai
import os
import sqlite3
from dotenv import load_dotenv

# .env dosyasındaki API anahtarını yükle
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("UYARI: .env dosyasında GEMINI_API_KEY bulunamadı!")
else:
    genai.configure(api_key=api_key)

DB_PATH = "app/database/omni_vision.db"

# --- 1. AJANIN KULLANACAĞI ARAÇLAR (FUNCTIONS) ---

def check_order_status(customer_phone: str) -> str:
    """Müşterinin telefon numarasına göre aktif sipariş durumunu veritabanından çeker."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT orders.status, products.name 
        FROM orders 
        JOIN products ON orders.product_id = products.id 
        WHERE orders.customer_phone = ?
    """, (customer_phone,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return f"Sipariş durumu: {result[0]}, Ürün: {result[1]}"
    return "Bu telefon numarasına ait aktif bir sipariş bulunamadı."

def create_payment_link(product_id: int) -> str:
    """Satın alınmak istenen ürün için sahte bir ödeme linki oluşturur."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, price, stock FROM products WHERE id = ?", (product_id,))
    result = cursor.fetchone()
    conn.close()

    if result and result[2] > 0:
        return f"Harika! {result[0]} ({result[1]} TL) için güvenli ödeme linkiniz: https://omnipara.com/pay/{product_id}abc"
    return "Maalesef bu ürün şu an stoklarımızda yok."

# --- 2. GEMINI AJANININ KURULUMU ---

# Gemini'a yukarıdaki fonksiyonları "araç" (tools) olarak veriyoruz.
# gemini-1.5-flash, hızlı işlemler ve agent mimarisi için en ideal modeldir.
try:
    agent_model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        tools=[check_order_status, create_payment_link],
        system_instruction="Sen 'Omni-Vision' adında, KOBİ'ler için çalışan nazik ve zeki bir müşteri asistanısın. Görevin müşteri sorularını yanıtlamak ve gerekirse araçlarını (tools) kullanarak veritabanından bilgi çekmektir."
    )
    # Chat oturumu başlat (Geçmişi hafızada tutması için)
    chat_session = agent_model.start_chat(enable_automatic_function_calling=True)
except Exception as e:
    print(f"Gemini Başlatma Hatası: {e}")
    chat_session = None

def get_agent_response(user_message: str, context: str = None) -> str:
    """
    Kullanıcı mesajını Gemini'a iletir ve yanıtı döner.
    Eğer görüntü işlemeden gelen bir bağlam (context) varsa, onu da mesaja ekler.
    """
    if not chat_session:
        return "Yapay zeka asistanı şu an devre dışı (API Key eksik olabilir)."

    # Eğer görsel eşleşmesi sonucu bir ürün bulunduysa, bunu LLM'e bilgi olarak sunuyoruz
    full_prompt = user_message
    if context:
        full_prompt = f"Sistem Notu: (Kullanıcı az önce bir fotoğraf gönderdi ve sistem bunu şu ürünle eşleştirdi: {context}). \n\nMüşteri Mesajı: {user_message}"

    response = chat_session.send_message(full_prompt)
    return response.text