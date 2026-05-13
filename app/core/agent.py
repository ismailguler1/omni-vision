import google.generativeai as genai
import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

DB_PATH = "app/database/omni_vision.db"

# --- AJAN ARAÇLARI (TOOLS) ---

def check_stock_and_size(product_id: int, size: str) -> str:
    """Belirli bir ürünün seçilen bedendeki (S, M, L) stok durumunu kontrol eder."""
    size_col = f"stock_{size.upper()}"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT name, {size_col}, price FROM products WHERE id = ?", (product_id,))
        res = cursor.fetchone()
        if res:
            return f"{res[0]} ürünü {size.upper()} beden için stokta {res[1]} adet var. Fiyat: {res[2]} TL."
        return "Ürün bulunamadı."
    finally:
        conn.close()

def create_autonomous_order(customer_phone: str, product_id: int, size: str) -> str:
    """Müşteri için otonom sipariş oluşturur ve stoğu günceller."""
    size_col = f"stock_{size.upper()}"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT {size_col}, name FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()
        if not product or product[0] <= 0:
            return "Maalesef seçtiğiniz beden tükenmiş."

        # Sipariş oluştur
        cursor.execute("""
            INSERT INTO orders (customer_phone, product_id, size, status, tracking_number)
            VALUES (?, ?, ?, ?, ?)
        """, (customer_phone, product_id, size.upper(), "Hazırlanıyor", "Henüz Oluşmadı"))
        
        # Stoğu düş
        cursor.execute(f"UPDATE products SET {size_col} = {size_col} - 1 WHERE id = ?", (product_id,))
        conn.commit()
        return f"Siparişiniz başarıyla alındı! {product[1]} ({size.upper()}) hazırlanıyor."
    finally:
        conn.close()

def track_cargo(customer_phone: str):
    """Müşterinin telefon numarasına ait TÜM siparişlerin durumunu sorgular."""
    import sqlite3
    conn = sqlite3.connect("app/database/omni_vision.db")
    cursor = conn.cursor()
    
    # Tüm siparişleri ID sırasına göre çekiyoruz
    cursor.execute("""
        SELECT order_id, product_id, status, tracking_number 
        FROM orders 
        WHERE customer_phone = ?
        ORDER BY order_id DESC
    """, (customer_phone,))
    
    results = cursor.fetchall()
    conn.close()

    if not results:
        return "Bu telefon numarasına ait bir sipariş bulunamadı."

    # Birden fazla siparişi düzenli bir metin haline getiriyoruz
    report = f"Bu numaraya ait toplam {len(results)} sipariş bulundu:\n"
    for order in results:
        report += (f"- Sipariş #{order[0]}: Ürün ID: {order[1]}, "
                   f"Durum: {order[2]}, Takip No: {order[3]}\n")
    
    return report

# --- GEMINI AJAN KURULUMU ---

FULL_VISUAL_CATALOG = """
        Görsel Eşleştirme ve ID Rehberi:

        TİŞÖRTLER:
        - 1001: Beyaz tişört, üzerinde büyük kırmızı kirazlar ve "CHERRIES" yazısı var.
        - 1002: Beyaz tişört, üzerinde siyah beyaz klasik araba ve "VINTAGE" yazısı var.
        - 1003: Beyaz tişört, üzerinde mavi kelebekler, yıldızlar ve "Believe in your abilities" yazısı var.
        - 1004: Açık mavi tişört, sol göğüs kısmında küçük papatya çiçekleri işlemesi var.
        - 1005: Beyaz tişört, tam ortasında altın/sarı renkli büyük Güneş ve Ay sembolü var.

        PANTOLONLAR:
        - 2001: Düz, desensiz siyah kumaş pantolon.
        - 2002: Düz, beyaz renkli keten/kumaş pantolon.
        - 2003: Gri/Siyah tonlarında kareli (ekose) desenli pantolon.
        - 2004: Düz, kahverengi renkli klasik kesim pantolon.
        - 2005: Gri renkli, bol kesim (Baggy) kot/denim pantolon.

        ELBİSELER:
        - 3001: Siyah renkli, belinde veya askısında gümüş/gold toka detayı olan elbise.
        - 3002: Bordo renkli, ince askılı, düz ve sade gece/günlük elbise.
        - 3003: Her yeri leopar desenli (siyah/kahve benekli) elbise.
        - 3004: Düz mavi renkli, zarif kesim elbise.
        - 3005: Düz lacivert (koyu mavi) renkli elbise.

        GÖMLEKLER:
        - 4001: Beyaz üzerine siyah veya lacivert ince çizgili (pinstripe) gömlek.
        - 4002: Düz bordo renkli, düğmeli klasik gömlek.
        - 4003: Yaka veya kol kısımlarında fırfır (volan) detayları olan beyaz/açık renkli gömlek.
        - 4004: Düz açık mavi renkli klasik gömlek.
        - 4005: Düz saf beyaz renkli klasik gömlek.

        ETEKLER:
        - 5001: Düz bordo renkli etek.
        - 5002: Düz beyaz renkli etek.
        - 5003: Siyah renkli, kat kat fırfırlı mini etek.
        - 5004: Düz pembe (şeker pembesi) renkli etek.
        - 5005: Her yeri leopar desenli etek.
        """


try:
    agent_model = genai.GenerativeModel(
    model_name='gemini-flash-latest', # Listenizdeki onaylı isim
    tools=[check_stock_and_size, create_autonomous_order, track_cargo],
        system_instruction=(
            f"Sen Omni-Vision otonom asistanısın. Ürün Kataloğumuz:\n{FULL_VISUAL_CATALOG}\n"
            "Kurallar:\n"
            "1. Görsel analizden gelen ID ile yukarıdaki katalog listesini karşılaştır.\n"
            "2. Eğer kullanıcı 'leopar elbise' diyorsa ID'nin 3003 olduğundan emin ol.\n"
            "3. Doğru ID'yi bulduğunda önce 'check_stock_and_size' ile stok bak.\n"
            "4. Beden (S, M, L) ve stok teyidi almadan 'create_autonomous_order' kullanma."
            )
    )
    chat_session = agent_model.start_chat(enable_automatic_function_calling=True)
except Exception as e:
    print(f"Ajan Başlatma Hatası: {e}")
    chat_session = None

def get_agent_response(user_message: str, context: str = None) -> str:
    if not chat_session: return "Asistan şu an uykuda."
    full_prompt = f"Bağlam: {context}\nKullanıcı: {user_message}" if context else user_message
    return chat_session.send_message(full_prompt).text