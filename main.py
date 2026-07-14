from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router
from app.api.routers import inventory, projects, purchase, system, users# 1. ÖNCE 'APP' OLUŞTURULUR
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
# Bizim 5 farklı dosyaya böldüğümüz tüm o 663 satırlık işlemler 
# tek bir satırla sisteme entegre ediliyor!
app.include_router(api_router, prefix="/api")
app.include_router(users.router, prefix="/api/ekip")
app.include_router(purchase.router, prefix="/api/satin-alma")
app.include_router(projects.router, prefix="/api/projeler")
app.include_router(inventory.router, prefix="/api/katalog")
app.include_router(system.router, prefix="/api")