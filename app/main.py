from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import shutil
import google.generativeai as genai
from app.core.agent import get_agent_response
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

app = FastAPI(title="Omni-Vision 2.0 API")

# Gemini API Yapılandırması
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("HATA: GEMINI_API_KEY bulunamadı!")
else:
    genai.configure(api_key=api_key)

vision_model = genai.GenerativeModel('gemini-flash-latest') 

# --- HATA ALAN KISIM BURASI (Eksik Tanım Eklendi) ---
class ChatRequest(BaseModel):
    message: str
    image_context: Optional[str] = None
# --------------------------------------------------

@app.post("/match-product/")
async def match_product(file: UploadFile = File(...)):
    """Görseli analiz eder ve ürün bağlamı çıkarır."""
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Görseli Gemini'a yükle
        img = genai.upload_file(path=temp_path)
        
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

        # /match-product/ içindeki prompt:
        prompt = (
            f"Bu görseldeki ürünü analiz et. Aşağıdaki kataloğa bakarak en uygun ID'yi seç:\n"
            f"{FULL_VISUAL_CATALOG}\n"
            "Yanıtını sadece şu formatta ver: 'Analiz: Ürün ID [ID_NO] ([Ürün İsmi])'"
        )
        response = vision_model.generate_content([img, prompt])
        
        analysis_text = response.text if response else "Ürün tanınamadı."
        
        return {
            "status": "success",
            "analysis": analysis_text
        }
    except Exception as e:
        print(f"Match Product Hatası: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/chat/")
async def chat_with_agent(request: ChatRequest):
    """Ajan ile konuşmayı sağlar."""
    try:
        # agent.py içindeki get_agent_response fonksiyonunu çağırır
        reply = get_agent_response(request.message, request.image_context)
        return {"status": "success", "reply": reply}
    except Exception as e:
        print(f"Chat Hatası: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))