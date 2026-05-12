# 👁️ Omni-Vision: "Görselden Sepete" KOBİ Otomasyon Sistemi

Omni-Vision, fiziksel mağaza ve online satışı birleştiren (hybrid) e-ticaret işletmeleri ve KOBİ'ler için geliştirilmiş, **Yapay Zeka Destekli Otonom Müşteri ve Operasyon Asistanıdır.**

Müşterilerin gönderdiği ürün fotoğraflarını saniyeler içinde analiz eder, stok durumunu kontrol eder ve doğal dil işleme (LLM) yetenekleriyle müşteri iletişimini, sipariş takibini ve ödeme süreçlerini tamamen otonom hale getirir.

## 🚀 Proje Mimarisi ve Teknoloji Yığını

Sistem 3 ana katmandan oluşmaktadır:
1. **Görsel Zeka (Computer Vision & FAISS):** Gelen müşteri fotoğrafları `MobileNetV3` modeli ile matematiksel vektörlere çevrilir ve yüksek hızlı benzerlik araması için `FAISS` indeksinde sorgulanarak katalogdaki en doğru ürünle eşleştirilir.
2. **Otonom Ajan (LLM & RAG):** `Google Gemini 2.5 Flash` modeli üzerine kurulu ajanımız, müşteri mesajlarını anlar ve veritabanı üzerinde aksiyon almak için "Function Calling" (Sipariş sorgulama, ödeme linki oluşturma) yeteneklerini kullanır.
3. **Merkezi Backend & Panel:** Tüm API akışı `FastAPI` ile yönetilirken, işletme sahibinin canlı stok ve sipariş takibi yapabildiği simülasyon arayüzü `Streamlit` ile geliştirilmiştir.

---

## 🛠️ Kurulum Adımları (Geliştiriciler İçin)

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

Projenin veri tabanını ve görsel hafızasını oluşturmak için kurulumdan sonra şu iki komutu sırasıyla çalıştırın:

1. Katalog görsellerini vektörleştirir ve FAISS indeksini oluşturur:
`python app/models/vision_model.py`

2. JSON verilerini SQLite veri tabanına yazar:
`python app/database/init_db.py`

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
1. Sol panelden (Sanal WhatsApp) test amaçlı bir ürün görseli yükleyin.
2. Sistem ürünü tanıyıp eşleştirdikten sonra, alt taraftaki mesaj kutusuna *"Bu üründen almak istiyorum, stokta var mı?"* yazın.
3. Ajanın veritabanını kontrol edip size ödeme linki oluşturmasını izleyin.
4. Müşteri sipariş durumu sormak için *"5551234567 numaralı telefonla verdiğim siparişimin durumu nedir?"* yazarak RAG entegrasyonunu test edin.
5. Sağ panelden canlı stokların ve siparişlerin durumunu patron gözüyle inceleyin.

## ⚠️ Bilinen Kısıtlamalar (Gelecek Vizyonu)
MVP aşamasında, sistem arka planı karmaşık olan müşteri fotoğraflarında (Domain Shift) yanılabilmektedir. Gelecek sürümlerde görsel eşleştirme doğruluğunu artırmak için `YOLO` tabanlı otomatik obje kırpma (Object Detection) mimarisi eklenecektir.