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

# YENİ EKLENEN: Sipariş Verme Modeli
class SiparisVeri(BaseModel):
    alim_adedi: int
    termin_suresi: str

# YENİ EKLENEN: Mal Kabul / Stoğa Ekleme Modeli
class MalKabulVeri(BaseModel):
    gelen_adet: int
    malzeme_kodu: str

# 1. SATIN ALMA TALEPLERİNİ LİSTELE (SatinAlma.vue ve ozet.vue için)
# 1. SATIN ALMA TALEPLERİNİ LİSTELE (SatinAlma.vue ve ozet.vue için)
@router.get("/talepler")
def satin_alma_taleplerini_getir(role: str = Header(default="standart", alias="current-user-role")):
    with get_db_session() as cur:
        cur.execute("""
            SELECT sat.id, TO_CHAR(sat.tarih, 'DD.MM.YYYY HH24:MI') as tarih, 
                   sat.malzeme_id, sat.malzeme_adi, sat.malzeme_kodu, 
                   sat.adet, sat.talep_edilen_adet, sat.talep_eden, sat.durum,
                   COALESCE(m.mevcut_stok, 0) as mevcut_stok
            FROM satin_alma_talepleri sat 
            LEFT JOIN malzemeler m ON sat.malzeme_kodu = m.siparis_kodu
            ORDER BY CASE 
                WHEN sat.durum = 'STOK_UYARISI' THEN 1 
                WHEN sat.durum = 'BEKLIYOR' THEN 2 
                ELSE 3 
            END, sat.id DESC
        """)
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

# 3. TALEP DURUMUNU GÜNCELLE (Klasik Onayla/Reddet butonları için)
@router.put("/talepler/{talep_id}/durum")
def talep_durum_guncelle(talep_id: int, veri: TalepDurum, islem_yapan: str = Header(default="Sistem")):
    with get_db_session() as cur:
        cur.execute("UPDATE satin_alma_talepleri SET durum = %s WHERE id = %s", (veri.durum, talep_id))
        return {"mesaj": f"Talep durumu {veri.durum} olarak güncellendi"}

# 4. YENİ EKLENEN: SİPARİŞİ OLUŞTUR (Termin ve Adet Belirleme)
@router.put("/talepler/{talep_id}/siparis-ver")
def siparis_olustur(talep_id: int, veri: SiparisVeri, islem_yapan: str = Header(default="Sistem")):
    with get_db_session() as cur:
        # Durumu güncelliyoruz ve satın almacının girdiği miktarı kaydediyoruz. 
        yeni_durum = f"SİPARİŞ VERİLDİ ({veri.termin_suresi})"
        cur.execute("UPDATE satin_alma_talepleri SET durum = %s, talep_edilen_adet = %s WHERE id = %s", 
                    (yeni_durum, veri.alim_adedi, talep_id))
        
        sistem_log_ekle(cur, islem_yapan, "SİPARİŞ_AÇILDI", f"Talep #{talep_id} için {veri.alim_adedi} adet sipariş verildi.")
        return {"mesaj": "Sipariş başarıyla oluşturuldu."}

# 5. YENİ EKLENEN: STOĞA EKLE / MAL KABUL (Sipariş geldiğinde ana stoğu artırır)
@router.put("/talepler/{talep_id}/mal-kabul")
def mal_kabul_yap(talep_id: int, veri: MalKabulVeri, islem_yapan: str = Header(default="Sistem")):
    with get_db_session() as cur:
        # A) Ana stok tablosuna (malzemeler) gelen adedi ekle
        cur.execute("UPDATE malzemeler SET mevcut_stok = mevcut_stok + %s WHERE siparis_kodu = %s", 
                    (veri.gelen_adet, veri.malzeme_kodu))
        
        # B) Satın alma talebini arşive kaldır (Tamamlandı)
        cur.execute("UPDATE satin_alma_talepleri SET durum = 'TAMAMLANDI' WHERE id = %s", (talep_id,))
        
        sistem_log_ekle(cur, islem_yapan, "MAL_KABUL", f"{veri.malzeme_kodu} kodlu üründen {veri.gelen_adet} adet stoğa eklendi.")
        return {"mesaj": f"{veri.gelen_adet} adet ürün ana stoğa başarıyla eklendi!"}