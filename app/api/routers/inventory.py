from fastapi import APIRouter, HTTPException, Header
from app.db.session import get_db_session
from app.models.schemas import MalzemeEkle, IskontoGrubuEkle
from app.api.utils import sistem_log_ekle
from app.services.tcmb_service import fetch_tcmb_rates

router = APIRouter(tags=["Envanter & Fiyatlandırma"])

@router.get("/malzemeler/listele")
def malzemeleri_listele():
    with get_db_session() as cur:
        cur.execute("SELECT id, urun_adi AS malzeme, marka, siparis_kodu FROM malzemeler")
        return cur.fetchall()

@router.post("/malzemeler")
def yeni_malzeme_ekle(malzeme: MalzemeEkle, islem_yapan: str = Header(default="Bilinmeyen")):
    with get_db_session() as cur:
        if malzeme.para_birimi != "TRY":
            cur.execute("SELECT kur_degeri FROM kurlar WHERE para_birimi = %s", (malzeme.para_birimi,))
            if not cur.fetchone():
                raise HTTPException(status_code=400, detail="Kur bulunamadı.")
                
        cur.execute("""
            INSERT INTO malzemeler (siparis_kodu, urun_adi, marka, urun_grubu, tedarikci, liste_fiyati, para_birimi, grup_iskonto_id, notlar)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (malzeme.siparis_kodu, malzeme.urun_adi, malzeme.marka, malzeme.urun_grubu, malzeme.tedarikci, malzeme.liste_fiyati, malzeme.para_birimi, malzeme.grup_iskonto_id, malzeme.notlar))
        sistem_log_ekle(cur, islem_yapan, "MALZEME_EKLE", f"Yeni malzeme eklendi: {malzeme.urun_adi}")
    return {"mesaj": "Malzeme eklendi!"}

@router.post("/iskonto-gruplari")
def iskonto_grubu_ekle(grup: IskontoGrubuEkle, role: str = Header(..., alias="current-user-role"), user: str = Header(default="Bilinmeyen")):
    if role != 'yonetici': raise HTTPException(status_code=403, detail="Yetkisiz")
    with get_db_session() as cur:
        cur.execute("INSERT INTO grup_iskontolar (grup_adi, maliyet_iskonto, proje_iskonto, satis_iskonto) VALUES (%s, %s, %s, %s)",
                    (grup.grup_adi, grup.maliyet_iskonto, grup.proje_iskonto, grup.satis_iskonto))
        sistem_log_ekle(cur, user, "İSKONTO_GRUBU_EKLE", f"Yeni grup: {grup.grup_adi}")
    return {"mesaj": "İskonto eklendi!"}

@router.get("/iskonto-gruplari")
def iskonto_gruplari_listele():
    with get_db_session() as cur:
        cur.execute("SELECT id, grup_adi FROM grup_iskontolar ORDER BY id")
        return cur.fetchall()

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