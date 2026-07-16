from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.db.session import get_db_session

router = APIRouter()

class StokGuncelle(BaseModel):
    mevcut_stok: int

class MalzemeEkle(BaseModel):
    siparis_kodu: str
    urun_adi: str
    marka: Optional[str] = None
    urun_grubu: Optional[str] = None
    tedarikci: Optional[str] = None
    mevcut_stok: int = 0
    kritik_esik: int = 5
    temin_suresi_gun: int = 0
    liste_fiyati: float = 0.0
    para_birimi: str = "TRY"
    grup_iskonto_id: Optional[int] = None
    notlar: Optional[str] = None

class RezerveMalzeme(BaseModel):
    malzeme_id: int
    adet: int

class RezervasyonIstegi(BaseModel):
    proje_id: int
    malzemeler: List[RezerveMalzeme]

# --- DEPO / STOK ROTALARI ---
@router.get("/stoklar")
def stoklari_getir():
    with get_db_session() as cur:
        cur.execute("SELECT * FROM malzemeler ORDER BY urun_adi ASC")
        return [dict(r) for r in cur.fetchall()]

@router.put("/stoklar/{malzeme_id}")
def stok_guncelle(malzeme_id: int, veri: StokGuncelle, islem_yapan: str = Header(default="Sistem")):
    with get_db_session() as cur:
        cur.execute("UPDATE malzemeler SET mevcut_stok = %s WHERE id = %s", (veri.mevcut_stok, malzeme_id))
        return {"mesaj": "Stok güncellendi"}

@router.post("/rezerve-et")
def stok_rezerve_et(istek: RezervasyonIstegi, islem_yapan: str = Header(default="Sistem")):
    with get_db_session() as cur:
        for m in istek.malzemeler:
            cur.execute("SELECT mevcut_stok FROM malzemeler WHERE id = %s", (m.malzeme_id,))
            stok = cur.fetchone()['mevcut_stok']
            if stok < m.adet:
                raise HTTPException(status_code=409, detail="Yetersiz Stok")
            # Stoğu eksilt
            cur.execute("UPDATE malzemeler SET mevcut_stok = mevcut_stok - %s WHERE id = %s", (m.adet, m.malzeme_id))
        return {"status": "success", "mesaj": "Stoklar rezerve edildi"}

# --- MALZEME ROTALARI (Frontend'deki /api/malzemeler istekleri için) ---
@router.get("/listele")
def malzemeleri_listele():
    with get_db_session() as cur:
        cur.execute("SELECT * FROM malzemeler ORDER BY id DESC")
        return [dict(r) for r in cur.fetchall()]

@router.post("")
def malzeme_ekle(veri: MalzemeEkle, islem_yapan: str = Header(default="Sistem")):
    with get_db_session() as cur:
        cur.execute("""
            INSERT INTO malzemeler (siparis_kodu, urun_adi, marka, urun_grubu, tedarikci, mevcut_stok, kritik_esik, temin_suresi_gun, liste_fiyati, para_birimi, grup_iskonto_id, notlar)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (veri.siparis_kodu, veri.urun_adi, veri.marka, veri.urun_grubu, veri.tedarikci, veri.mevcut_stok, veri.kritik_esik, veri.temin_suresi_gun, veri.liste_fiyati, veri.para_birimi, veri.grup_iskonto_id, veri.notlar))
        return {"mesaj": "Malzeme başarıyla depoya eklendi"}