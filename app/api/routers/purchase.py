from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
from app.db.session import get_db_session
from app.api.utils import sistem_log_ekle

# Prefix burada tanımlandığı için rotalara tekrar /satin-alma yazmıyoruz
router = APIRouter(prefix="/satin-alma", tags=["Satın Alma"])

# --- PYDANTIC MODELLERİ (Vue.js'den gelecek verileri karşılamak için) ---
class TalepDurum(BaseModel):
    durum: str

class YeniTalep(BaseModel):
    malzeme_id: int
    malzeme_adi: str
    adet: int
    talep_eden: str
    durum: str = 'BEKLIYOR'

# 1. SATIN ALMA TALEPLERİNİ LİSTELE (SatinAlma.vue için)
@router.get("/talepler")
def satin_alma_taleplerini_getir(role: str = Header(default="standart", alias="current-user-role")):
    # role kontrolünü esnek tuttuk ki frontend'den gelen veri boş olsa bile 500 hatası çakmasın
    with get_db_session() as cur:
        # sat.talep_tarihi yazan yeri sat.tarih olarak değiştirdik
        cur.execute("""
            SELECT sat.id, TO_CHAR(sat.tarih, 'DD.MM.YYYY HH24:MI') as tarih, 
                   sat.malzeme_id, sat.malzeme_adi, sat.adet, sat.talep_eden, sat.durum 
            FROM satin_alma_talepleri sat 
            ORDER BY CASE WHEN sat.durum = 'BEKLIYOR' THEN 1 ELSE 2 END, sat.id DESC
        """)
        # cur.fetchall() zaten RealDictCursor sayesinde dictionary listesi döner
        return [dict(row) for row in cur.fetchall()]

# 2. YENİ TALEP OLUŞTUR (StokTakip.vue sayfasındaki "🛒 Talep Aç" butonu için)
@router.post("/talepler")
def yeni_talep_olustur(veri: YeniTalep, islem_yapan: str = Header(default="Sistem")):
    with get_db_session() as cur:
        cur.execute("""
            INSERT INTO satin_alma_talepleri (malzeme_id, malzeme_adi, adet, talep_eden, durum)
            VALUES (%s, %s, %s, %s, %s)
        """, (veri.malzeme_id, veri.malzeme_adi, veri.adet, veri.talep_eden, veri.durum))
        return {"mesaj": "Talep başarıyla oluşturuldu"}

# 3. TALEP DURUMUNU GÜNCELLE (SatinAlma.vue sayfasındaki Onayla/Reddet butonları için)
@router.put("/talepler/{talep_id}/durum")
def talep_durum_guncelle(talep_id: int, veri: TalepDurum, islem_yapan: str = Header(default="Sistem")):
    with get_db_session() as cur:
        cur.execute("UPDATE satin_alma_talepleri SET durum = %s WHERE id = %s", (veri.durum, talep_id))
        return {"mesaj": f"Talep durumu {veri.durum} olarak güncellendi"}