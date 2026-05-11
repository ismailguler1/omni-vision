import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import faiss
import numpy as np
import os

class OmniVisionModel:
    def __init__(self):
        # MobileNetV3-Small: Hafif, hızlı ve hackathon için ideal
        self.model = models.mobilenet_v3_small(weights='IMAGENET1K_V1')
        self.model.eval() # Eğitim modunu kapat
        
        # Görsel ön işleme (MobileNet standartları)
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

    def get_embedding(self, image_path):
        """Görseli okur ve 576 boyutlu bir özellik vektörü döner."""
        img = Image.open(image_path).convert('RGB')
        img_t = self.transform(img).unsqueeze(0)
        
        with torch.no_grad():
            # Son sınıflandırma katmanından önceki özellikleri alıyoruz
            features = self.model.forward(img_t)
            # Vektörü düzleştir ve numpy array'e çevir
            return features.flatten().numpy()

# Kişi 1'in FAISS indeksi oluşturma betiği
if __name__ == "__main__":
    extractor = OmniVisionModel()
    image_dir = "data/product_images/"
    embeddings = []
    metadata = [] # ID'leri eşleştirmek için

    
    #deneme
    for idx, filename in enumerate(os.listdir(image_dir)):
        if filename.endswith((".jpg", ".png", ".jpeg")):
            path = os.path.join(image_dir, filename)
            vec = extractor.get_embedding(path)
            embeddings.append(vec)
            metadata.append(idx) # Şimdilik basit ID

    # FAISS İndeksi oluşturma
    embeddings_np = np.array(embeddings).astype('float32')
    dimension = embeddings_np.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_np)

    # İndeksi kaydet
    faiss.write_index(index, "vector_index.faiss")
    print(f"Başarıyla {len(embeddings)} ürün vektörleştirildi ve kaydedildi.")