# app/api/endpoints.py
from fastapi import APIRouter

# Yeni oluşturduğumuz modülleri içeri aktarıyoruz
from app.api.routers import users, inventory, projects, purchase, system

# Ana yönlendiriciyi oluştur
router = APIRouter()

# Tüm modülleri ana sisteme bağla
router.include_router(users.router)
router.include_router(inventory.router)
router.include_router(projects.router)
router.include_router(purchase.router)
router.include_router(system.router)