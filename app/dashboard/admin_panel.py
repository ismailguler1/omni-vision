import streamlit as st
import sqlite3
import pandas as pd
import requests

# Sayfa Ayarları
st.set_page_config(page_title="Omni-Vision Dashboard", page_icon="👁️", layout="wide")

# API URL'leri (FastAPI sunucumuzun adresleri)
API_MATCH_URL = "http://127.0.0.1:8000/match-product/"
API_CHAT_URL = "http://127.0.0.1:8000/chat/"
DB_PATH = "app/database/omni_vision.db"

# Veritabanından veri çekme fonksiyonu
def get_table_data(query):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Ana Başlık
st.title("👁️ Omni-Vision: Otonom Mağaza Asistanı")
st.markdown("---")

# Ekranı ikiye bölüyoruz: Sol (Müşteri Chat) - Sağ (Yönetici Paneli)
col1, col2 = st.columns([1, 1.2])

# ==========================================
# SOL PANEL: MÜŞTERİ SİMÜLASYONU (CHAT)
# ==========================================
with col1:
    st.subheader("📱 Müşteri Ekranı (WhatsApp Simülasyonu)")
    
    # Sohbet geçmişini tutmak için
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "matched_product_context" not in st.session_state:
        st.session_state.matched_product_context = None

    # Görsel Yükleme Alanı
    uploaded_file = st.file_uploader("Ürün fotoğrafı gönder (Görselden Arama):", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        if st.button("Fotoğrafı Gönder ve Ara"):
            with st.spinner("Omni-Vision AI fotoğrafı analiz ediyor..."):
                files = {"file": (uploaded_file.name, uploaded_file, "image/jpeg")}
                response = requests.post(API_MATCH_URL, files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    if data["status"] == "success":
                        st.success(f"Eşleşme Bulundu: {data['product_name']}")
                        st.write(f"**Kategori:** {data['category']} | **Fiyat:** {data['price']} TL | **Stok:** {data['stock_quantity']} adet")
                        # LLM için bağlamı kaydet
                        st.session_state.matched_product_context = f"{data['product_name']} (ID: {data['matched_id']}, Stok: {data['stock_quantity']})"
                    else:
                        st.warning(data.get("message", "Eşleşme bulunamadı veya görsel karmaşık."))
                else:
                    st.error("Görsel arama servisinde bir hata oluştu.")

    # Sohbet Arayüzü
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Kullanıcıdan Metin Girişi
    if prompt := st.chat_input("Mesajınızı yazın (Örn: Siparişim nerede? Veya bu üründen alacağım)"):
        # Kullanıcı mesajını ekrana bas
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Gemini Ajanına gönder
        with st.chat_message("assistant"):
            with st.spinner("Asistan yazıyor..."):
                payload = {
                    "message": prompt,
                    "image_context": st.session_state.matched_product_context
                }
                res = requests.post(API_CHAT_URL, json=payload)
                if res.status_code == 200:
                    reply = res.json().get("reply", "Bir hata oluştu.")
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                else:
                    st.error(f"API Hatası: {res.status_code}")

# ==========================================
# SAĞ PANEL: YÖNETİCİ KONTROL PANELİ
# ==========================================
with col2:
    st.subheader("⚙️ Yönetici Paneli (Canlı Veri)")
    
    # Metrik Kartları
    try:
        products_df = get_table_data("SELECT * FROM products")
        orders_df = get_table_data("SELECT * FROM orders")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Toplam Ürün Çeşidi", len(products_df))
        m2.metric("Bekleyen Siparişler", len(orders_df[orders_df['status'] != 'Teslim Edildi']))
        m3.metric("Kritik Stok Uyarısı", len(products_df[products_df['stock'] < 5]))
        
        st.markdown("---")
        st.write("📦 **Canlı Stok Durumu**")
        # Stokta azalanları kırmızı ile göstermek için basit bir renklendirme stili
        st.dataframe(products_df[['id', 'name', 'category', 'price', 'stock']].style.highlight_min(subset=['stock'], color='#ffcccc'), use_container_width=True)

        st.markdown("---")
        st.write("🚚 **Son Siparişler**")
        st.dataframe(orders_df, use_container_width=True)
        
        # Ekranı manuel yenileme butonu
        if st.button("🔄 Verileri Yenile"):
            st.rerun()

    except Exception as e:
        st.error(f"Veritabanı okunamadı. Lütfen önce veritabanını oluşturun. Hata: {e}")