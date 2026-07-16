from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router
from app.api.routers import (
    inventory, 
    projects, 
    purchase, 
    system, 
    users, 
    musteriler, 
    revisions, 
    imalat
)

# 1. ÖNCE 'APP' OLUŞTURULUR
app = FastAPI(title="Kurumsal ERP API v1.0")

# 2. GÜVENLİK/CORS AYARLARI EKLENİR 
# Frontend (Vue.js) ile iletişimi açıyoruz
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173"
    ], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. EN SON ROUTER (YOLLAR) EKLENİR
app.include_router(api_router, prefix="/api")
app.include_router(system.router, prefix="/api")

# Ana Modüller
app.include_router(users.router, prefix="/api/ekip", tags=["Ekip"])
app.include_router(purchase.router, prefix="/api/satin-alma", tags=["Satın Alma"])
app.include_router(musteriler.router, prefix="/api/musteriler", tags=["Müşteriler/CRM"])
app.include_router(revisions.router, prefix="/api/revizyonlar", tags=["Revizyonlar"])
app.include_router(imalat.router, prefix="/api/imalat", tags=["İmalat"])

# Projeler Modülü (pano-malzeme-guncelle kök /api'den geldiği için iki kez bağlanıyor)
app.include_router(projects.router, prefix="/api/projeler", tags=["Projeler"])
app.include_router(projects.router, prefix="/api", tags=["Projeler Dinamik Düzenleme"])

# Envanter Modülü 
# (Depo, Malzeme ve İskonto işlemlerini inventory.py içinde topladığımız için prefix="/api" yapıyoruz)
app.include_router(inventory.router, prefix="/api", tags=["Envanter, Katalog ve İskonto"])