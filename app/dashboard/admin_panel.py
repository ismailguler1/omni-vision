import streamlit as st
import sqlite3
import pandas as pd
import requests
from datetime import datetime

# ==========================================
# SAYFA AYARLARI VE GELİŞMİŞ CSS
# ==========================================
st.set_page_config(page_title="Omni-Vision Dashboard", page_icon="OV", layout="wide")

st.markdown("""
<style>
/* Ana Arka Plan */
.stApp { background: linear-gradient(135deg, #f7f9fc 0%, #eef4ff 45%, #f8f0ff 100%); }

/* Sidebar Metrik Kutucukları */
.sidebar-metric-container {
    background: white; border: 1px solid #e2e8f0; border-radius: 16px;
    padding: 1rem; margin-bottom: 1rem; box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05); text-align: center;
}
.sidebar-metric-label { color: #64748b; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.2rem; }
.sidebar-metric-value { color: #4f46e5; font-size: 1.6rem; font-weight: 800; }

/* Sidebar Güncelleme Butonu (Büyük ve Mavi) */
[data-testid="stSidebar"] .stButton button {
    background: #4f46e5 !important; color: white !important;
    height: 3.5rem !important; font-size: 1.1rem !important; font-weight: 700 !important;
    border-radius: 12px !important; border: none !important;
    box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3) !important; width: 100%;
}

/* Header Paneli */
.main-header {
    background: linear-gradient(135deg, #4f46e5, #7c3aed, #db2777);
    padding: 2rem; border-radius: 24px; color: white;
    box-shadow: 0 18px 45px rgba(79, 70, 229, 0.25); margin-bottom: 1.5rem;
}
.main-header h1 { margin: 0; font-size: 2.3rem; font-weight: 800; }

/* Panel Kart Tasarımı */
.panel-card {
    background: rgba(255, 255, 255, 0.88); border: 1px solid rgba(148, 163, 184, 0.25);
    border-radius: 22px; padding: 1.4rem; box-shadow: 0 12px 35px rgba(15, 23, 42, 0.08); margin-bottom: 1.2rem;
}
.section-title { font-size: 1.25rem; font-weight: 800; color: #1e293b; margin-bottom: 0.3rem; }

/* Metrik Kartları */
.overview-card { padding: 1.2rem; border-radius: 20px; box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06); margin-bottom: 1rem; }
.orange-card { background: linear-gradient(135deg, #fff7ed, #ffedd5); border: 1px solid #fdba74; }
.red-card { background: linear-gradient(135deg, #fef2f2, #fee2e2); border: 1px solid #fca5a5; }
.blue-card { background: linear-gradient(135deg, #eff6ff, #dbeafe); border: 1px solid #93c5fd; }

/* Log Kutusu */
.log-box {
    background: #1e293b; color: #38bdf8; font-family: 'Courier New', Courier, monospace;
    padding: 10px; border-radius: 12px; font-size: 0.85rem; height: 150px; overflow-y: auto;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# VERİ TABANI VE YARDIMCI FONKSİYONLAR
# ==========================================
DB_PATH = "app/database/omni_vision.db"
API_MATCH_URL = "http://127.0.0.1:8000/match-product/"
API_CHAT_URL = "http://127.0.0.1:8000/chat/"

@st.cache_data(ttl=60) 
def get_table_data(query):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def update_order_status(order_id, new_status, tracking_no):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = ?, tracking_number = ? WHERE order_id = ?", (new_status, tracking_no, order_id))
    conn.commit()
    conn.close()
    st.session_state.logs.append(f"{datetime.now().strftime('%H:%M')} - #{order_id} nolu sipariş '{new_status}' olarak güncellendi.")

def color_stock_cells(val):
    if val < 3: return 'background-color: #fee2e2; color: #991b1b; font-weight: bold'
    elif val < 7: return 'background-color: #fef3c7; color: #92400e'
    return 'background-color: #dcfce7; color: #166534'

# --- SESSION STATE BAŞLATMA ---
if "messages" not in st.session_state: st.session_state.messages = []
if "logs" not in st.session_state: st.session_state.logs = ["Sistem başlatıldı..."]
if "image_context" not in st.session_state: st.session_state.image_context = None

# --- VERİ ÇEKME ---
try:
    products_df = get_table_data("SELECT * FROM products")
    orders_df = get_table_data("""
        SELECT o.order_id, p.name as 'Urun_Adi', o.size, o.status, o.tracking_number, o.customer_phone, p.price
        FROM orders o JOIN products p ON o.product_id = p.id ORDER BY o.order_id DESC
    """)
    total_revenue = orders_df[orders_df["status"] != "İptal Edildi"]["price"].sum()
    pending_count = len(orders_df[orders_df["status"].isin(["Hazırlanıyor", "Kargoya Verildi"])])
    
    # Nokta atışı kritik stok
    critical_rows = []
    for _, row in products_df.iterrows():
        for size in ['S', 'M', 'L']:
            if row[f'stock_{size}'] < 3:
                critical_rows.append({"Ürün": row['name'], "Beden": size, "Kalan": row[f'stock_{size}']})
    critical_df = pd.DataFrame(critical_rows)
except:
    products_df, orders_df, critical_df, total_revenue, pending_count = pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), 0, 0

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("## 👁️ OMNI-VISION v2.0")
    st.markdown("---")
    st.markdown(f'<div class="sidebar-metric-container"><div class="sidebar-metric-label">📦 Toplam Ürün</div><div class="sidebar-metric-value">{len(products_df)}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sidebar-metric-container"><div class="sidebar-metric-label">🚚 Bekleyen İşlem</div><div class="sidebar-metric-value">{pending_count}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sidebar-metric-container"><div class="sidebar-metric-label">⚠️ Kritik Beden</div><div class="sidebar-metric-value">{len(critical_df)}</div></div>', unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🔄 VERİLERİ GÜNCELLE"): st.rerun()

# ==========================================
# ANA PANEL
# ==========================================
st.markdown('<div class="main-header"><h1>Omni-Vision Otonom Mağaza Yönetimi</h1><p>Görsel yapay zeka ve otonom operasyon merkezi.</p></div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1.2], gap="large")

# --- SOL PANEL: MÜŞTERİ (WHATSAPP SİMÜLASYONU) ---
# --- SOL PANEL: MÜŞTERİ EKRANI (DÜZELTİLMİŞ ANALİZ MANTIĞI) ---
with col1:
    st.markdown('<div class="panel-card"><div class="section-title">📱 WhatsApp Hattı</div></div>', unsafe_allow_html=True)
    
    # Session state değişkenlerini garanti altına alalım
    if "messages" not in st.session_state: st.session_state.messages = []
    if "image_context" not in st.session_state: st.session_state.image_context = None
    if "processed_file_id" not in st.session_state: st.session_state.processed_file_id = None

    # Dosya yükleyici
    uploaded_file = st.file_uploader("Bir ürün fotoğrafı yükleyin:", type=["jpg", "jpeg", "png"])
    
    # 1. DOSYA SİLİNDİYSE: Hafızayı temizle
    if uploaded_file is None:
        st.session_state.image_context = None
        st.session_state.processed_file_id = None
    
    # 2. YENİ DOSYA GELDİYSE VE HENÜZ ANALİZ EDİLMEDİYSE: Analiz yap
    # (Dosya adı ve boyutu üzerinden benzersiz bir ID oluşturuyoruz)
    if uploaded_file is not None:
        current_file_id = f"{uploaded_file.name}_{uploaded_file.size}"
        
        if st.session_state.processed_file_id != current_file_id:
            with st.status("Görsel taranıyor...", expanded=False) as status:
                try:
                    files = {"file": (uploaded_file.name, uploaded_file, "image/jpeg")}
                    response = requests.post(API_MATCH_URL, files=files)
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.image_context = data["analysis"]
                        # BU ÇOK KRİTİK: Dosyayı işlendi olarak işaretle
                        st.session_state.processed_file_id = current_file_id
                        status.update(label="Ürün tanımlandı ve hafızaya alındı ✅", state="complete")
                    else:
                        status.update(label="Analiz başarısız.", state="error")
                except Exception as e:
                    status.update(label=f"Bağlantı hatası: {e}", state="error")

    # --- CHAT ARAYÜZÜ ---
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Mesajınızı yazın..."):
        # Mesajı ekrana yaz ve geçmişe ekle
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Asistan yanıtı (Analiz sonucu image_context içinde saklı kalır)
        with st.chat_message("assistant"):
            payload = {
                "message": prompt, 
                "image_context": st.session_state.image_context # Fotoğraf silinene kadar burada durur
            }
            try:
                res = requests.post(API_CHAT_URL, json=payload)
                reply = res.json().get("reply", "Üzgünüm, bir hata oluştu.")
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except:
                st.error("AI servisine ulaşılamadı.")

# --- SAĞ PANEL: PERSONEL (OPERASYON VE ANALİTİK) ---
with col2:
    # 1. Analitik Metrikler
    st.markdown('<div class="panel-card"><div class="section-title">📊 Satış & Stok Analitiği</div></div>', unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    with m1: st.markdown(f'<div class="overview-card blue-card"><div class="overview-label" style="color:#1e40af">Toplam Ciro</div><div class="overview-value" style="color:#1d4ed8">{total_revenue:,.0f} TL</div></div>', unsafe_allow_html=True)
    with m2: st.markdown(f'<div class="overview-card orange-card"><div class="overview-label" style="color:#9a3412">Bekleyen İşlem</div><div class="overview-value" style="color:#ea580c">{pending_count}</div></div>', unsafe_allow_html=True)
    with m3: st.markdown(f'<div class="overview-card red-card"><div class="overview-label" style="color:#991b1b">Kritik Stok</div><div class="overview-value" style="color:#dc2626">{len(critical_df)}</div></div>', unsafe_allow_html=True)

    # 2. Kritik Uyarı Tablosu
    if not critical_df.empty:
        st.markdown('<div class="panel-card" style="border: 2px solid #fca5a5;"><div class="section-title" style="color: #dc2626;">🚨 Kritik Stok Listesi</div>', unsafe_allow_html=True)
        st.dataframe(critical_df.style.applymap(lambda x: 'background-color: #fee2e2; font-weight:bold;', subset=['Kalan']), use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 3. Renkli Stoklar ve Sipariş Listesi (Sekmeli)
    tab1, tab2 = st.tabs(["📦 Canlı Stok", "📝 Tüm Siparişler"])
    with tab1:
        styled_p = products_df[['id', 'name', 'stock_S', 'stock_M', 'stock_L', 'price']].style.applymap(color_stock_cells, subset=['stock_S', 'stock_M', 'stock_L'])
        st.dataframe(styled_p, use_container_width=True, hide_index=True)
    with tab2:
        st.dataframe(orders_df, use_container_width=True, hide_index=True)

    # 4. Kargo Yönetimi
    st.markdown('<div class="panel-card"><div class="section-title">🚚 Kargo Durum & Takip Güncelleme</div></div>', unsafe_allow_html=True)
    active_orders = orders_df[orders_df["status"].isin(["Hazırlanıyor", "Kargoya Verildi"])]
    if not active_orders.empty:
        order_options = active_orders.apply(lambda x: f"ID: {x.iloc[0]} | {x['Urun_Adi']} ({x['status']})", axis=1)
        sel_order = st.selectbox("Sipariş Seçin:", order_options)
        sel_id = int(sel_order.split("|")[0].split(":")[1].strip())
        cur_order = active_orders[active_orders.iloc[:, 0] == sel_id].iloc[0]
        
        ca, cb = st.columns(2)
        with ca: new_s = st.selectbox("Durum:", ["Hazırlanıyor", "Kargoya Verildi", "Teslim Edildi", "İptal Edildi"], index=["Hazırlanıyor", "Kargoya Verildi"].index(cur_order["status"]))
        with cb: t_no = st.text_input("Takip No:", value=cur_order["tracking_number"] if cur_order["tracking_number"] else "")
        if st.button("💾 Bilgileri Kaydet"):
            update_order_status(sel_id, new_s, t_no)
            if new_s == "Kargoya Verildi": st.toast("Müşteriye otonom kargo bildirimi gönderildi! 📱")
            st.rerun()

    # 5. Otonom İşlem Logları (Pasta Cila!)
    st.markdown('<div class="panel-card"><div class="section-title">🖥️ Otonom İşlem Logları</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="log-box">{"<br>".join(st.session_state.logs[::-1])}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)