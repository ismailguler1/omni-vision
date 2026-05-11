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