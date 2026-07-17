from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db.session import get_db_session

# Eğer ana dosyada prefix="/imalat" tanımlıysa router böyle kalır
router = APIRouter()

# Frontend'den gelecek durum bilgisini karşılayacak model
class DurumGuncelleme(BaseModel):
    durum: str
    pano_turu: str
@router.get("/is-emirleri")
def is_emirleri_getir():
    with get_db_session() as cur:
        # Harika Dokunuş: Projedeki malzemeleri gruplayarak eşsiz panoları liste olarak sahaya döküyoruz!
        cur.execute("""
            SELECT 
                p.id as proje_id, 
                p.proje_adi, 
                p.musteri, 
                pl.pano_turu, 
                MAX(pl.durum) as durum 
            FROM projeler p
            JOIN proje_pano_listesi pl ON p.id = pl.proje_id
            GROUP BY p.id, p.proje_adi, p.musteri, pl.pano_turu
            ORDER BY p.id DESC, pl.pano_turu
        """)
        return [dict(r) for r in cur.fetchall()]

@router.get("/is-emirleri/aktif")
def aktif_is_emirleri():
    with get_db_session() as cur:
        # Sadece tamamlanmamış panoları çekiyoruz
        cur.execute("""
            SELECT p.id as proje_id, p.proje_adi, pl.pano_turu 
            FROM projeler p
            JOIN proje_pano_listesi pl ON p.id = pl.proje_id
            WHERE pl.durum != 'TAMAMLANDI'
            GROUP BY p.id, p.proje_adi, pl.pano_turu
        """)
        return [dict(r) for r in cur.fetchall()]

# İŞTE YENİ EKLEDİĞİMİZ KAPI BURASI! 
# Arayüzden seçilen "Montajda", "Tamamlandı" gibi durumları burası kaydedecek.
@router.put("/is-emirleri/{proje_id}/durum")
def is_emri_durum_guncelle(proje_id: int, veri: DurumGuncelleme):
    try:
        with get_db_session() as cur:
            # Sadece tıklanan spesifik panonun (Örn: Sadece MCC 1'in) durumunu güncelliyoruz
            cur.execute(
                "UPDATE proje_pano_listesi SET durum = %s WHERE proje_id = %s AND pano_turu = %s",
                (veri.durum, proje_id, veri.pano_turu)
            )
            
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Güncellenecek pano bulunamadı.")
                
        return {"mesaj": f"{veri.pano_turu} durumu güncellendi", "yeni_durum": veri.durum}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))