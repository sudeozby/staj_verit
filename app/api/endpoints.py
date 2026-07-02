from fastapi import APIRouter, HTTPException
from app.db.session import get_db_session
from app.models.schemas import ProjeEkle, IskontoGrubuEkle, MalzemeEkle
from app.db import crud  # Depocuyu (CRUD) çağırıyoruz!

router = APIRouter()

# --- PROJELER ---

@router.get("/projeler")
def projeleri_getir():
    """Veritabanındaki tüm projeleri çeker ve arayüze liste olarak gönderir."""
    with get_db_session() as cur:
        # SQL yazmak yok! Sadece crud'daki fonksiyonu çağırıyoruz.
        projeler_listesi = crud.get_all_projeler(cur)
        return {"projeler": projeler_listesi}

@router.post("/projeler")
def yeni_proje_ekle(proje: ProjeEkle):
    """Arayüzden gelen yeni proje bilgilerini veritabanına kaydeder."""
    with get_db_session() as cur:
        crud.insert_proje(cur, proje)
    return {"mesaj": f"'{proje.proje_adi}' adlı proje başarıyla eklendi!"}


# --- İSKONTO GRUPLARI (Yeni CPQ Mimarisi) ---

@router.post("/iskonto-gruplari")
def iskonto_grubu_ekle(grup: IskontoGrubuEkle):
    """Sisteme yeni bir iskonto şablonu (Örn: Kablolar, Panolar) ekler."""
    with get_db_session() as cur:
        crud.insert_iskonto_grubu(cur, grup)
    return {"mesaj": f"'{grup.grup_adi}' iskonto grubu başarıyla tanımlandı!"}


# --- MALZEMELER ---

@router.post("/malzemeler")
def yeni_malzeme_ekle(malzeme: MalzemeEkle):
    """Yeni bir malzeme ekler. Para birimini kurlar tablosundan otomatik eşleştirir."""
    with get_db_session() as cur:
        # 1. Kuru bul
        para_birimi_id = crud.get_kur_id(cur, malzeme.para_birimi)
        
        if not para_birimi_id:
            raise HTTPException(status_code=400, detail=f"'{malzeme.para_birimi}' kurlar tablosunda bulunamadı. Lütfen önce TCMB kurlarını çekin.")
            
        # 2. Malzemeyi kaydet
        crud.insert_malzeme(cur, malzeme, para_birimi_id)
        
    return {"mesaj": f"'{malzeme.urun_adi}' envantere başarıyla eklendi!"}