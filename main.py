from fastapi import FastAPI
from app.api.endpoints import router

# 1. Uygulamayı (Sistemi) Başlat
app = FastAPI(
    title="Kurumsal CPQ ve Proje Takip API",
    description="Şirketin fiyatlandırma, iskonto hesaplama ve envanter yönetim sistemi.",
    version="1.0.0"
)

# 2. Rotaları (Garsonu) Ana Sisteme Bağla
app.include_router(router)

# 3. Kök Dizin (Sistemin Ayakta Olduğunu Gösteren Karşılama Ekranı)
@app.get("/")
def ana_sayfa():
    return {
        "mesaj": "Sistem mimarisi başarıyla parçalandı ve tıkır tıkır çalışıyor!",
        "dokumantasyon_adresi": "/docs"
    }