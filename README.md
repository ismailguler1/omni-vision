# 👁️ Omni-Vision: "Görselden Sepete" KOBİ Otomasyon Sistemi

Omni-Vision, fiziksel mağaza ve online satışı birleştiren (hybrid) e-ticaret işletmeleri ve KOBİ'ler için geliştirilmiş, **Yapay Zeka Destekli Otonom Müşteri ve Operasyon Asistanıdır.**

Müşterilerin gönderdiği ürün fotoğraflarını saniyeler içinde analiz eder, stok durumunu kontrol eder ve doğal dil işleme (LLM) yetenekleriyle müşteri iletişimini, sipariş takibini ve ödeme süreçlerini tamamen otonom hale getirir.

## ✨ 2.0 "The Multimodal Era" Yenilikleri

* **🔍 Gemini Vision Match:** Eski nesil FAISS veya yerel vektör modelleri yerine, Google Gemini 2.0 Flash'ın multimodal yeteneği ile görsel anlama tabanlı, yüksek doğrulukta ürün eşleştirme.
* **💰 Finansal Analitik Dashboard:** Toplam ciro, aktif sipariş sayısı ve kritik stok durumlarının admin paneli üzerinden anlık takibi.
* **🖥️ Otonom İşlem Logları:** Arka planda çalışan yapay zeka ajanının (Function Calling) yaptığı her işlemin (stok düşüşü, sipariş onayı, kargo bildirimi) şeffaf terminal dökümü.
* **📍 Nokta Atışı Stok Yönetimi:** S-M-L beden bazlı canlı stok takibi ve stoğu biten spesifik ürün-beden çiftleri için otomatik kritik uyarılar.
* **⚡ Yüksek Performans:** `@st.cache_data` (Veri önbellekleme) ve `Session State Locking` (Analiz kilidi) ile optimize edilmiş, gecikmesiz kullanıcı deneyimi.

---

## 🚀 Teknoloji Yığını

* **Multimodal AI Engine:** `Google Gemini 2.0 Flash` (Vision + Text + Function Calling)
* **Backend:** `FastAPI` (Asenkron API katmanı)
* **Frontend:** `Streamlit` (Modern, SaaS odaklı Admin & Müşteri arayüzü)
* **Veri Yönetimi:** `SQLite` & `Pandas`
* **Güvenlik:** `Python-Dotenv` (API Anahtarı izolasyonu)

---

## 🛠️ Kurulum ve Hazırlık

Projenin yerel ortamda sorunsuz çalışması için aşağıdaki adımları sırasıyla uygulayın:

**1. Repoyu Klonlayın:**
`git clone https://github.com/ismailguler1/omni-vision.git`
`cd omni-vision`

**2. Sanal Ortamı (Virtual Environment) Kurun ve Aktifleştirin:**
*Windows (PowerShell) için:*
`python -m venv venv`
`.\venv\Scripts\activate`

**3. Gerekli Kütüphaneleri Yükleyin:**
`pip install -r requirements.txt`

*(Not: Windows'ta `rembg` motor hatası almamak için kurulum komutunu `pip install "rembg[cpu]"` şeklinde çalıştırmanız gerekebilir.)*

**4. Çevresel Değişkenleri Ayarlayın:**
Proje kök dizininde bir `.env` dosyası oluşturun ve Gemini API anahtarınızı ekleyin. 
*(API Key almak için: https://aistudio.google.com/api-keys)*
`GEMINI_API_KEY=sizin_api_anahtariniz_buraya_gelecek`

---

## ⚙️ Sistemi İlk Kez Başlatma (Sadece Bir Kere Yapılır)

Sistemin kullanacağı tabloları ve örnek verileri oluşturmak için veritabanını başlatın:

python app/database/init_db.py

---

## 💻 Sistemi Çalıştırma (Çift Terminal Yaklaşımı)

Sistemin uçtan uca çalışması için **Backend (FastAPI)** ve **Frontend (Streamlit)** sunucularının aynı anda açık olması gerekir.

**Terminal 1 (Backend - FastAPI):**
Ana terminalde sanal ortamınız aktifken yapay zeka ve veritabanı sunucusunu başlatın:
`uvicorn app.main:app --reload`

**Terminal 2 (Frontend - Yönetici ve Müşteri Paneli):**
VS Code üzerinden yeni bir terminal açın, sanal ortamı tekrar aktif edin ve arayüzü başlatın:
`.\venv\Scripts\activate`
`streamlit run app/dashboard/admin_panel.py`
*Bu komut çalıştıktan sonra tarayıcınızda `http://localhost:8501` adresinde Omni-Vision paneli açılacaktır.*

---

## 🎯 Demo Kullanım Senaryosu
Görsel Analiz: Müşteri, sol paneldeki "WhatsApp Hattı" simülasyonu üzerinden bir kıyafet fotoğrafı yükler. Gemini Vision, görseli katalogdaki ürün tanımlarıyla semantik olarak eşleştirir.

Otonom Satış: Müşteri "Bunu almak istiyorum" dediğinde Ajan, istenen bedeni stokta bulur, veritabanına anlık sipariş kaydını işler ve "İşlem Logları"na not düşer.

Operasyonel Takip: İşletme sahibi, sağ paneldeki mavi metrik kartlarından güncel ciroyu takip eder ve renklendirilmiş stok tablosundan azalan ürünleri (Örn: Mavi Gömlek - L Beden) anında tespit eder.

Kargo Yönetimi: Personel, sistem üzerinden kargo numarasını girdiğinde, sistem otonom olarak durumu günceller ve "Müşteriye bildirim iletildi" mesajı ile operasyonu tamamlar.

## Performans ve Güvenlik Notları
Analysis Lock: Aynı fotoğrafın sohbetteki her mesaj gönderiminde tekrar analiz edilmesini engelleyen processed_file_id kontrolü ile API maliyetleri ve gecikme süreleri sıfıra indirilmiştir.

Smart Caching: Veritabanı yükünü minimize eden 60 saniyelik otomatik önbellekleme sistemi kullanılmıştır.

Environment Safety: API anahtarları .env dosyasında izole edilmiştir ve .gitignore kuralları gereği uzak sunucuya (repo) gönderilmez.

---

Omni-Vision - İşletmenizi Geleceğin Otonom Dünyasına Taşır.