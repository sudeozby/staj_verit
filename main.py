from fastapi import FastAPI
from app.api.endpoints import router
#web based uyg ıcın

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from app.api.endpoints import router
# 1. Uygulamayı (Sistemi) Başlat
app = FastAPI(
    title="Kurumsal CPQ ve Proje Takip API",
    description="Şirketin fiyatlandırma, iskonto hesaplama ve envanter yönetim sistemi.",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Şimdilik her yerden gelen isteklere açık
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT, DELETE hepsine izin ver
    allow_headers=["*"],
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