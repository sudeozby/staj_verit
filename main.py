from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models.schemas import Kullanici 
from db_manager import (
    fetch_all_users, add_user, update_user_password, 
    delete_user, save_log, fetch_all_logs
)

app = FastAPI(title="Kurumsal API v1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Loglama fonksiyonu: Artık doğrudan DB'ye kayıt atıyor
def log_islem(kullanici, islem, detay):
    save_log(kullanici, islem, detay)

# --- ROTALAR ---

@app.get("/kullanicilar")
def get_users():
    try:
        return fetch_all_users()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/kullanici-ekle")
def post_user(kullanici: Kullanici):
    try:
        add_user(kullanici.kullanici_adi, kullanici.sifre, kullanici.rol)
        log_islem("Admin", "KULLANICI_EKLEME", f"{kullanici.kullanici_adi} eklendi.")
        return {"mesaj": "Başarıyla eklendi"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/kullanici-sifre-guncelle")
def put_sifre(data: dict):
    try:
        update_user_password(data["kullanici_adi"], data["yeni_sifre"])
        log_islem(data["kullanici_adi"], "ŞİFRE_GÜNCELLEME", "Şifre güncellendi.")
        return {"mesaj": "Şifre başarıyla güncellendi"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@app.delete("/kullanici-sil/{kullanici_adi}")
def delete_user_route(kullanici_adi: str):
    try:
        print(f"Silinmek istenen kullanıcı: {kullanici_adi}") # Bunu terminalde kontrol et
        delete_user(kullanici_adi)
        log_islem("Admin", "KULLANICI_SİLME", f"{kullanici_adi} silindi.")
        return {"mesaj": "Kullanıcı silindi"}
    except Exception as e:
        print(f"HATA: {e}") # Hatayı terminalde gör
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/loglar")
def get_logs():
    try:
        return fetch_all_logs()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))