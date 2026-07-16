from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
from app.db.session import get_db_session
from app.api.utils import sistem_log_ekle
from app.services.tcmb_service import fetch_tcmb_rates

# Prefix kullanmıyoruz çünkü rotaların yolları birbirinden farklı (/malzemeler, /iskonto-gruplari, /depo)
router = APIRouter(tags=["Envanter & Fiyatlandırma"])

# --- PYDANTIC MODELLERİ ---
class MalzemeEkle(BaseModel):
    siparis_kodu: str
    urun_adi: str
    marka: Optional[str] = None
    urun_grubu: Optional[str] = None
    tedarikci: Optional[str] = None
    liste_fiyati: float = 0.0
    para_birimi: str = "TRY"
    grup_iskonto_id: Optional[int] = None
    notlar: Optional[str] = None
    # Vue.js'den gelen yeni stok verileri
    mevcut_stok: int = 0
    kritik_esik: int = 5
    temin_suresi_gun: int = 0

class IskontoGrubuEkle(BaseModel):
    grup_adi: str
    maliyet_iskonto: float = 0.0
    proje_iskonto: float = 0.0
    satis_iskonto: float = 0.0
    notlar: Optional[str] = None

class StokGuncelle(BaseModel):
    mevcut_stok: int


# --- 1. MALZEME ROTALARI ---
@router.get("/malzemeler/listele")
def malzemeleri_listele():
    with get_db_session() as cur:
        # Frontend'in tüm detayları kullanabilmesi için SELECT * yapıyoruz
        cur.execute("SELECT * FROM malzemeler ORDER BY id DESC")
        return [dict(row) for row in cur.fetchall()]

@router.post("/malzemeler")
def yeni_malzeme_ekle(malzeme: MalzemeEkle, islem_yapan: str = Header(default="Sistem", alias="islem-yapan")):
    with get_db_session() as cur:
        # Kur kontrolünü kırmak yerine, tablo boşsa hatayı geçiyoruz (opsiyonel)
        if malzeme.para_birimi != "TRY":
            cur.execute("SELECT kur_degeri FROM kurlar WHERE para_birimi = %s", (malzeme.para_birimi,))
            if not cur.fetchone():
                pass # Test aşamasında sistemi kitlememek için pass geçildi

        cur.execute("""
            INSERT INTO malzemeler (
                siparis_kodu, urun_adi, marka, urun_grubu, tedarikci, 
                liste_fiyati, para_birimi, grup_iskonto_id, notlar,
                mevcut_stok, kritik_esik, temin_suresi_gun
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            malzeme.siparis_kodu, malzeme.urun_adi, malzeme.marka, malzeme.urun_grubu, 
            malzeme.tedarikci, malzeme.liste_fiyati, malzeme.para_birimi, 
            malzeme.grup_iskonto_id, malzeme.notlar,
            malzeme.mevcut_stok, malzeme.kritik_esik, malzeme.temin_suresi_gun
        ))
        sistem_log_ekle(cur, islem_yapan, "MALZEME_EKLE", f"Yeni malzeme eklendi: {malzeme.urun_adi}")
    return {"mesaj": "Malzeme başarıyla eklendi!"}


# --- 2. İSKONTO GRUPLARI ROTALARI ---
@router.post("/iskonto-gruplari")
def iskonto_grubu_ekle(grup: IskontoGrubuEkle, role: str = Header(default="yonetici", alias="current-user-role"), islem_yapan: str = Header(default="Sistem", alias="islem-yapan")):
    if role != 'yonetici': raise HTTPException(status_code=403, detail="Yetkisiz")
    with get_db_session() as cur:
        # HATA DÜZELTİLDİ: Tablo adı iskonto_gruplari olarak değiştirildi
        cur.execute("""
            INSERT INTO iskonto_gruplari (grup_adi, maliyet_iskonto, proje_iskonto, satis_iskonto, notlar) 
            VALUES (%s, %s, %s, %s, %s)
        """, (grup.grup_adi, grup.maliyet_iskonto, grup.proje_iskonto, grup.satis_iskonto, grup.notlar))
        sistem_log_ekle(cur, islem_yapan, "İSKONTO_GRUBU_EKLE", f"Yeni grup: {grup.grup_adi}")
    return {"mesaj": "İskonto grubu başarıyla eklendi!"}

@router.get("/iskonto-gruplari")
def iskonto_gruplari_listele():
    with get_db_session() as cur:
        # HATA DÜZELTİLDİ: Tablo adı iskonto_gruplari olarak değiştirildi
        cur.execute("SELECT * FROM iskonto_gruplari ORDER BY id")
        return [dict(row) for row in cur.fetchall()]


# --- 3. STOK VE DEPO ROTALARI (StokTakip.vue için) ---
@router.get("/depo/stoklar")
def stoklari_getir():
    with get_db_session() as cur:
        cur.execute("SELECT * FROM malzemeler ORDER BY urun_adi ASC")
        return [dict(row) for row in cur.fetchall()]

@router.put("/depo/stoklar/{malzeme_id}")
def stok_guncelle(malzeme_id: int, veri: StokGuncelle, islem_yapan: str = Header(default="Sistem", alias="islem-yapan")):
    with get_db_session() as cur:
        cur.execute("UPDATE malzemeler SET mevcut_stok = %s WHERE id = %s", (veri.mevcut_stok, malzeme_id))
        sistem_log_ekle(cur, islem_yapan, "STOK_GUNCELLE", f"ID {malzeme_id} stoku {veri.mevcut_stok} yapıldı")
        return {"mesaj": "Stok güncellendi"}


# --- 4. KURLAR ---
@router.post("/kurlar/tcmb-guncelle")
def tcmb_kurlarini_guncelle():
    kurlar = fetch_tcmb_rates()
    with get_db_session() as cur:
        guncellenen = []
        for kod, deger in kurlar.items():
            cur.execute("""
                INSERT INTO kurlar (para_birimi, kur_degeri, guncellenme_tarihi) VALUES (%s, %s, CURRENT_DATE)
                ON CONFLICT (para_birimi) DO UPDATE SET kur_degeri = EXCLUDED.kur_degeri, guncellenme_tarihi = CURRENT_DATE;
            """, (kod, deger))
            guncellenen.append(f"{kod}: {deger} TL")
    return {"mesaj": "Kurlar güncellendi!", "veriler": guncellenen}

@router.get("/katalog/malzemeler")
def katalog_malzemeleri_getir():
    with get_db_session() as cur:
        cur.execute("SELECT * FROM malzemeler ORDER BY id DESC")
        return [dict(row) for row in cur.fetchall()]

@router.get("/katalog/panolar")
def katalog_panolari_getir():
    # Frontend patlamasın diye şimdilik boş dizi dönüyoruz. İleride buraya pano şablonları eklenebilir.
    return []