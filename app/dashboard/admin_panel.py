import streamlit as st
import sqlite3
import pandas as pd
import requests

# Sayfa Ayarları
st.set_page_config(page_title="Omni-Vision 2.0 Dashboard", page_icon="👁️", layout="wide")

API_MATCH_URL = "http://127.0.0.1:8000/match-product/"
API_CHAT_URL = "http://127.0.0.1:8000/chat/"
DB_PATH = "app/database/omni_vision.db"

def get_table_data(query):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

st.title("👁️ Omni-Vision 2.0: Otonom İşletme Merkezi")
st.markdown("---")

col1, col2 = st.columns([1, 1.2])

# ==========================================
# SOL PANEL: MÜŞTERİ & MULTIMODAL CHAT
# ==========================================
with col1:
    st.subheader("📱 Müşteri WhatsApp Hattı (Otonom)")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "image_context" not in st.session_state:
        st.session_state.image_context = None

    uploaded_file = st.file_uploader("Ürün fotoğrafı gönder (Gemini Vision):", type=["jpg", "jpeg", "png"])
    
    if uploaded_file and st.button("Fotoğrafı Analiz Et"):
        with st.spinner("Gemini ürünü inceliyor..."):
            files = {"file": (uploaded_file.name, uploaded_file, "image/jpeg")}
            response = requests.post(API_MATCH_URL, files=files)
            if response.status_code == 200:
                data = response.json()
                st.session_state.image_context = data["analysis"]
                st.info(f"Yapay Zeka Analizi: {data['analysis']}")

    # Chat Arayüzü
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Mesajınızı yazın..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            payload = {"message": prompt, "image_context": st.session_state.image_context}
            res = requests.post(API_CHAT_URL, json=payload)
            reply = res.json().get("reply", "Hata!")
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

# ==========================================
# SAĞ PANEL: PERSONEL TAKİP EKRANI (LIVE)
# ==========================================
with col2:
    st.subheader("⚙️ Arka Plan Operasyon Takibi")
    
    try:
        products_df = get_table_data("SELECT * FROM products")
        orders_df = get_table_data("SELECT * FROM orders")
        
        # Metrikler
        m1, m2, m3 = st.columns(3)
        m1.metric("Toplam Satış", len(orders_df))
        m2.metric("Aktif Kargo", len(orders_df[orders_df['status'] == 'Kargoya Verildi']))
        # Kritik Stok: Herhangi bir bedeni 2'nin altına düşenler
        low_stock = products_df[(products_df['stock_S'] < 2) | (products_df['stock_M'] < 2) | (products_df['stock_L'] < 2)]
        m3.metric("Kritik Stok Uyarısı", len(low_stock))
        
        st.write("📦 **Beden Bazlı Canlı Stok Durumu**")
        st.dataframe(products_df[['id', 'name', 'stock_S', 'stock_M', 'stock_L', 'price']], use_container_width=True)

        st.write("🚚 **Otonom Oluşan Son Siparişler**")
        st.dataframe(orders_df.tail(10), use_container_width=True)
        
        if st.button("🔄 Verileri Tazele"): st.rerun()

    except Exception as e:
        st.error(f"Veri yüklenemedi: {e}")

# app/dashboard/admin_panel.py içine eklenecek Kargo Yönetimi kısmı

st.markdown("---")
st.subheader("🚚 Sipariş & Kargo Yönetimi (Personel Ekranı)")

# Bekleyen siparişleri çekelim
def update_order_status(order_id, new_status, tracking_no):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE orders 
        SET status = ?, tracking_number = ? 
        WHERE order_id = ?
    """, (new_status, tracking_no, order_id))
    conn.commit()
    conn.close()

# Sadece "Hazırlanıyor" olan siparişleri listele
pending_orders = get_table_data("SELECT * FROM orders WHERE status = 'Hazırlanıyor'")

if not pending_orders.empty:
    selected_order_id = st.selectbox("Güncellenecek Sipariş ID seçin:", pending_orders['order_id'])
    
    col_a, col_b = st.columns(2)
    with col_a:
        new_status = st.selectbox("Yeni Durum:", ["Hazırlanıyor", "Kargoya Verildi", "Teslim Edildi", "İptal Edildi"])
    with col_b:
        tracking_no = st.text_input("Kargo Takip No:", placeholder="Örn: TR123456789")

    if st.button("Siparişi Güncelle ve Kaydet"):
        update_order_status(selected_order_id, new_status, tracking_no)
        st.success(f"{selected_order_id} nolu sipariş güncellendi!")
        st.rerun()
else:
    st.info("Şu an kargoya verilmeyi bekleyen bir sipariş bulunmuyor.")        