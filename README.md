# Omni-Vision: "Görselden Sepete" Otomasyon Sistemi

Omni-Vision, fiziksel mağaza ve online satışı birleştiren (hybrid) KOBİ'ler için geliştirilmiş yapay zeka destekli bir operasyonel verimlilik asistanıdır.

## 🛠️ Kurulum Adımları (Geliştiriciler İçin)

Projenin yerel ortamda sorunsuz çalışması için aşağıdaki adımları sırasıyla uygulayın:

1. **Repoyu Klonlayın:**
   `git clone https://github.com/KULLANICI_ADINIZ/omni-vision.git`
   `cd omni-vision`

2. **Sanal Ortamı (Virtual Environment) Kurun ve Aktifleştirin:**
   *Windows (PowerShell) için:*
   `python -m venv venv`
   `.\venv\Scripts\activate`

3. **Gerekli Kütüphaneleri Yükleyin:**
   `pip install -r requirements.txt`

4. **Çevresel Değişkenleri Ayarlayın:**
   Kök dizinde bir `.env` dosyası oluşturun ve Gemini API anahtarınızı ekleyin:
   `GEMINI_API_KEY=sizin_api_anahtariniz`

## 🚀 Sistemi İlk Kez Başlatma (Sadece Bir Kere Yapılır)

Projenin veri tabanını ve görsel hafızasını oluşturmak için kurulumdan sonra şu iki komutu sırasıyla çalıştırın:
1. `python app/models/vision_model.py` (Katalog görsellerini vektörleştirir ve FAISS indeksini oluşturur)
2. `python app/database/init_db.py` (JSON verilerini SQLite veri tabanına yazar)

## 💻 Günlük Çalıştırma

Sistem verileri oluşturulduktan sonra projeyi başlatmak için her seferinde sadece şu komutu kullanmanız yeterlidir:
`uvicorn app.main:app --reload`