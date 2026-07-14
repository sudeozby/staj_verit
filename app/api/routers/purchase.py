from fastapi import APIRouter, HTTPException, Header
from app.db.session import get_db_session
from app.api.utils import sistem_log_ekle

router = APIRouter(prefix="/satin-alma", tags=["Satın Alma"])

@router.get("/talepler")
def satin_alma_taleplerini_getir(role: str = Header(..., alias="current-user-role")):
    if role != 'yonetici': raise HTTPException(status_code=403, detail="Yetkisiz!")
    with get_db_session() as cur:
        cur.execute("""
            SELECT sat.id, TO_CHAR(sat.tarih, 'DD.MM.YYYY HH24:MI') as tarih, sat.malzeme_kodu, m.urun_adi, sat.talep_edilen_adet as adet, sat.durum 
            FROM satin_alma_talepleri sat LEFT JOIN malzemeler m ON sat.malzeme_kodu = m.siparis_kodu
            ORDER BY CASE WHEN sat.durum = 'BEKLIYOR' THEN 1 ELSE 2 END, sat.id DESC
        """)
        return cur.fetchall()

@router.get("/talepler")
def satin_alma_taleplerini_getir(role: str = Header(..., alias="current-user-role")):
    if role != 'yonetici': raise HTTPException(status_code=403, detail="Yetkisiz!")
    with get_db_session() as cur:
        # Veritabanı ekran görüntündeki 'talep_tarihi' sütun ismine göre güncellendi
        cur.execute("""
            SELECT sat.id, TO_CHAR(sat.talep_tarihi, 'DD.MM.YYYY HH24:MI') as tarih, 
                   sat.malzeme_kodu, m.urun_adi, sat.talep_edilen_adet as adet, sat.durum 
            FROM satin_alma_talepleri sat 
            LEFT JOIN malzemeler m ON sat.malzeme_kodu = m.siparis_kodu
            ORDER BY CASE WHEN sat.durum = 'BEKLIYOR' THEN 1 ELSE 2 END, sat.id DESC
        """)
        return cur.fetchall()