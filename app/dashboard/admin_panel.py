import streamlit as st
import sqlite3
import pandas as pd
import requests

st.set_page_config(
    page_title="Omni-Vision Dashboard",
    page_icon="OV",
    layout="wide"
)

API_MATCH_URL = "http://127.0.0.1:8000/match-product/"
API_CHAT_URL = "http://127.0.0.1:8000/chat/"
DB_PATH = "app/database/omni_vision.db"


def get_table_data(query):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f7f9fc 0%, #eef4ff 45%, #f8f0ff 100%);
}

.block-container {
    padding-top: 2rem;
}

.main-header {
    background: linear-gradient(135deg, #4f46e5, #7c3aed, #db2777);
    padding: 2rem;
    border-radius: 24px;
    color: white;
    box-shadow: 0 18px 45px rgba(79, 70, 229, 0.25);
    margin-bottom: 1.5rem;
}

.main-header h1 {
    margin: 0;
    font-size: 2.3rem;
    font-weight: 800;
}

.main-header p {
    margin-top: 0.6rem;
    font-size: 1.05rem;
    opacity: 0.92;
}

.panel-card {
    background: rgba(255, 255, 255, 0.88);
    border: 1px solid rgba(148, 163, 184, 0.25);
    border-radius: 22px;
    padding: 1.4rem;
    box-shadow: 0 12px 35px rgba(15, 23, 42, 0.08);
    margin-bottom: 1.2rem;
}

.section-title {
    font-size: 1.25rem;
    font-weight: 800;
    color: #1e293b;
    margin-bottom: 0.3rem;
}

.section-desc {
    color: #64748b;
    font-size: 0.95rem;
    margin-bottom: 1rem;
}

.overview-card {
    padding: 1.2rem;
    border-radius: 20px;
    margin-bottom: 1rem;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
}

.overview-label {
    font-size: 0.9rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.overview-value {
    font-size: 2rem;
    font-weight: 800;
}

.orange-card {
    background: linear-gradient(135deg, #fff7ed, #ffedd5);
    border: 1px solid #fdba74;
}

.orange-label {
    color: #9a3412;
}

.orange-value {
    color: #ea580c;
}

.red-card {
    background: linear-gradient(135deg, #fef2f2, #fee2e2);
    border: 1px solid #fca5a5;
}

.red-label {
    color: #991b1b;
}

.red-value {
    color: #dc2626;
}

div[data-testid="stMetric"] {
    background: white;
    border-radius: 18px;
    padding: 1rem;
    border: 1px solid #e2e8f0;
    box-shadow: 0 8px 22px rgba(15, 23, 42, 0.06);
}

div[data-testid="stMetric"] label {
    color: #64748b !important;
    font-weight: 600;
}

div[data-testid="stMetricValue"] {
    color: #4f46e5;
    font-weight: 800;
}

.stButton > button {
    width: 100%;
    border-radius: 14px;
    border: none;
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    color: white;
    font-weight: 700;
    padding: 0.7rem 1rem;
    box-shadow: 0 8px 20px rgba(79, 70, 229, 0.22);
}

.stButton > button:hover {
    background: linear-gradient(135deg, #4338ca, #6d28d9);
    color: white;
}

div[data-testid="stFileUploader"] {
    background: #f8fafc;
    border: 1px dashed #94a3b8;
    border-radius: 18px;
    padding: 1rem;
}

[data-testid="stChatMessage"] {
    border-radius: 18px;
    padding: 0.6rem;
    background: rgba(255, 255, 255, 0.72);
}

.stDataFrame {
    border-radius: 18px;
    overflow: hidden;
}

.info-box {
    background: linear-gradient(135deg, #eff6ff, #f5f3ff);
    border-left: 5px solid #6366f1;
    padding: 1rem;
    border-radius: 16px;
    color: #334155;
    margin-bottom: 1rem;
}

.success-box {
    background: #ecfdf5;
    border: 1px solid #bbf7d0;
    color: #166534;
    padding: 1rem;
    border-radius: 16px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="main-header">
    <h1>Omni-Vision Otonom Mağaza Asistanı</h1>
    <p>Görsel ürün eşleştirme, müşteri sohbeti, stok takibi ve sipariş yönetimi için tek panel.</p>
</div>
""", unsafe_allow_html=True)


try:
    products_df = get_table_data("SELECT * FROM products")
    orders_df = get_table_data("SELECT * FROM orders")

    pending_orders = len(orders_df[orders_df["status"] != "Teslim Edildi"])
    critical_products = products_df[products_df["stock"] < 5]

    with st.sidebar:
        st.markdown("## Omni-Vision")
        st.caption("Operasyon paneli")

        st.metric("Toplam Ürün", len(products_df))
        st.metric("Bekleyen Sipariş", pending_orders)
        st.metric("Kritik Stok", len(critical_products))

        st.success("Sistem Aktif")

        st.markdown("---")

        if st.button("Verileri Yenile"):
            st.rerun()

except Exception:
    products_df = pd.DataFrame()
    orders_df = pd.DataFrame()
    pending_orders = 0
    critical_products = pd.DataFrame()

    with st.sidebar:
        st.markdown("## Omni-Vision")
        st.error("Veritabanı okunamadı")


col1, col2 = st.columns([1, 1.2], gap="large")


with col1:
    st.markdown("""
    <div class="panel-card">
        <div class="section-title">Müşteri Ekranı</div>
        <div class="section-desc">WhatsApp benzeri müşteri deneyimini test edin.</div>
    </div>
    """, unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "matched_product_context" not in st.session_state:
        st.session_state.matched_product_context = None

    uploaded_file = st.file_uploader(
        "Ürün fotoğrafı gönder",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file is not None:
        if st.button("Fotoğrafı analiz et ve ürünü ara"):
            with st.spinner("Omni-Vision AI fotoğrafı analiz ediyor..."):
                files = {"file": (uploaded_file.name, uploaded_file, "image/jpeg")}
                response = requests.post(API_MATCH_URL, files=files)

                if response.status_code == 200:
                    data = response.json()

                    if data["status"] == "success":
                        st.markdown(
                            f"""
                            <div class="success-box">
                                Eşleşme bulundu: {data['product_name']}<br>
                                Kategori: {data['category']} |
                                Fiyat: {data['price']} TL |
                                Stok: {data['stock_quantity']} adet
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        st.session_state.matched_product_context = (
                            f"{data['product_name']} "
                            f"(ID: {data['matched_id']}, "
                            f"Stok: {data['stock_quantity']})"
                        )
                    else:
                        st.warning(
                            data.get(
                                "message",
                                "Eşleşme bulunamadı veya görsel karmaşık."
                            )
                        )
                else:
                    st.error("Görsel arama servisinde bir hata oluştu.")

    st.markdown("""
    <div class="info-box">
        Müşteri mesajlarını buradan test edebilirsiniz. Görsel eşleşme varsa,
        ürün bilgisi otomatik olarak asistana bağlam olarak gönderilir.
    </div>
    """, unsafe_allow_html=True)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input(
        "Mesajınızı yazın. Örn: Siparişim nerede? Bu ürünü almak istiyorum."
    ):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Asistan yanıt hazırlıyor..."):
                payload = {
                    "message": prompt,
                    "image_context": st.session_state.matched_product_context
                }

                res = requests.post(API_CHAT_URL, json=payload)

                if res.status_code == 200:
                    reply = res.json().get("reply", "Bir hata oluştu.")
                    st.markdown(reply)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": reply}
                    )
                else:
                    st.error(f"API Hatası: {res.status_code}")


with col2:
    st.markdown("""
    <div class="panel-card">
        <div class="section-title">Genel Bakış</div>
        <div class="section-desc">
            Operasyon ve stok süreçlerini gerçek zamanlı takip edin.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if products_df.empty:
        st.error(
            "Veritabanı okunamadı. Lütfen önce veritabanını oluşturun."
        )
    else:
        g1, g2 = st.columns(2)

        with g1:
            st.markdown(f"""
            <div class="overview-card orange-card">
                <div class="overview-label orange-label">Bekleyen Sipariş</div>
                <div class="overview-value orange-value">{pending_orders}</div>
            </div>
            """, unsafe_allow_html=True)

        with g2:
            st.markdown(f"""
            <div class="overview-card red-card">
                <div class="overview-label red-label">Kritik Stok Ürünü</div>
                <div class="overview-value red-value">{len(critical_products)}</div>
            </div>
            """, unsafe_allow_html=True)

        if len(critical_products) > 0:
            st.markdown("""
            <div class="panel-card">
                <div class="section-title">Kritik Stok Uyarıları</div>
                <div class="section-desc">
                    Stoğu azalan ürünler hızlı aksiyon gerektiriyor.
                </div>
            </div>
            """, unsafe_allow_html=True)

            warning_df = critical_products[
                ["name", "category", "stock", "price"]
            ].copy()

            warning_df.columns = [
                "Ürün",
                "Kategori",
                "Stok",
                "Fiyat"
            ]

            st.dataframe(
                warning_df.style.apply(
                    lambda x: [
                        "background-color:#fee2e2;color:#991b1b;font-weight:600"
                    ] * len(x),
                    axis=1
                ),
                use_container_width=True,
                hide_index=True
            )

        st.markdown("""
        <div class="panel-card">
            <div class="section-title">Canlı Stok Durumu</div>
            <div class="section-desc">
                Ürünlerin kategori, fiyat ve stok bilgileri.
            </div>
        </div>
        """, unsafe_allow_html=True)

        def highlight_stock(row):
            if row["stock"] < 5:
                return ["background-color: #fee2e2"] * len(row)
            if row["stock"] <= 10:
                return ["background-color: #fef3c7"] * len(row)
            return ["background-color: #dcfce7"] * len(row)

        st.dataframe(
            products_df[
                ["id", "name", "category", "price", "stock"]
            ].style.apply(highlight_stock, axis=1),
            use_container_width=True,
            hide_index=True
        )

        st.markdown("""
        <div class="panel-card">
            <div class="section-title">Son Siparişler</div>
            <div class="section-desc">
                Veritabanındaki mevcut sipariş kayıtları.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if orders_df.empty:
            st.info("Henüz sipariş kaydı bulunmuyor.")
        else:
            st.dataframe(
                orders_df,
                use_container_width=True,
                hide_index=True
            )