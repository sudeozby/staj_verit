from fastapi import APIRouter, Header, HTTPException
from app.db.session import get_db_session
from app.db import crud

router = APIRouter()

# --- 1. DASHBOARD (ÖZET) İSTATİSTİKLERİ ---
@router.get("/dashboard/ozet")
def dashboard_ozet_getir(role: str = Header(..., alias="current-user-role")):
    # İstersen buraya yetki kontrolü koyabilirsin:
    # if role != "yonetici":
    #     raise HTTPException(status_code=403, detail="Yetkisiz işlem!")
        
    with get_db_session() as cur:
        # Bekleyen satın alma talepleri
        cur.execute("SELECT COUNT(*) as sayi FROM satin_alma_talepleri WHERE durum = 'BEKLIYOR'")
        bekleyen = cur.fetchone()['sayi']
        
        # Aktif projeler
        cur.execute("SELECT COUNT(*) as sayi FROM projeler")
        projeler = cur.fetchone()['sayi']
        
        # Aktif personel
        cur.execute("SELECT COUNT(*) as sayi FROM kullanicilar WHERE aktif_mi = TRUE")
        personel = cur.fetchone()['sayi']
        
        # Son 5 sistem hareketi (loglar)
        cur.execute("SELECT kullanici_adi, islem_turu, detay, TO_CHAR(tarih, 'DD.MM.YYYY HH24:MI') as saat FROM loglar ORDER BY id DESC LIMIT 5")
        loglar = cur.fetchall()
        
    return {
        "bekleyen_alimlar": bekleyen, 
        "aktif_projeler": projeler, 
        "aktif_personel": personel, 
        "toplam_maliyet_tl": "0.00", 
        "son_hareketler": loglar
    }

# --- 2. TÜM SİSTEM LOGLARINI GETİRME ---
@router.get("/loglar")
def get_logs():
    with get_db_session() as cur:
        return crud.fetch_all_logs(cur)