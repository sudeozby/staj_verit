from fastapi import APIRouter, HTTPException, Header
from app.db.session import get_db_session
from app.models.schemas import KullaniciOlustur, KullaniciGiris, SifreGuncelle
from app.api.utils import sistem_log_ekle

router = APIRouter(prefix="/ekip", tags=["Kullanıcı & Ekip"])

@router.post("/login")
def login(kullanici: KullaniciGiris):
    with get_db_session() as cur:
        cur.execute("SELECT * FROM kullanicilar WHERE kullanici_adi = %s AND sifre = %s", (kullanici.kullanici_adi, kullanici.sifre))
        user = cur.fetchone()
        if not user:
            raise HTTPException(status_code=401, detail="Kullanıcı adı veya şifre hatalı!")
        if not user['aktif_mi']:
            raise HTTPException(status_code=403, detail="Bu hesap pasife alınmıştır.")
            
        sistem_log_ekle(cur, user['kullanici_adi'], "GİRİŞ_YAPILDI", f"{user['kullanici_adi']} giriş yaptı.")
    return {"mesaj": "Giriş başarılı", "rol": user['rol'], "kullanici_adi": user['kullanici_adi']}

@router.get("/")
def ekip_listele():
    with get_db_session() as cur:
        cur.execute("SELECT id, kullanici_adi, rol, aktif_mi FROM kullanicilar ORDER BY id ASC")
        return cur.fetchall()

@router.post("/ekle")
def uye_ekle(yeni_uye: KullaniciOlustur, islem_yapan: str = Header(default="Bilinmeyen")):
    with get_db_session() as cur:
        cur.execute("SELECT id FROM kullanicilar WHERE kullanici_adi = %s", (yeni_uye.kullanici_adi,))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="Bu kullanıcı adı zaten kayıtlı.")
        
        cur.execute("INSERT INTO kullanicilar (kullanici_adi, sifre, rol, aktif_mi) VALUES (%s, %s, %s, TRUE)",
                    (yeni_uye.kullanici_adi, yeni_uye.sifre, yeni_uye.rol))
        sistem_log_ekle(cur, islem_yapan, "PERSONEL_EKLE", f"Yeni personel: {yeni_uye.kullanici_adi}")
    return {"mesaj": f"Yeni ekip üyesi {yeni_uye.kullanici_adi} eklendi!"}

@router.delete("/{uye_id}")
def uye_pasife_al(uye_id: int, islem_yapan: str = Header(default="Bilinmeyen")):
    with get_db_session() as cur:
        cur.execute("SELECT kullanici_adi FROM kullanicilar WHERE id = %s", (uye_id,))
        kullanici = cur.fetchone()
        if not kullanici:
            raise HTTPException(status_code=404, detail="Bulunamadı.")
            
        cur.execute("UPDATE kullanicilar SET aktif_mi = FALSE WHERE id = %s", (uye_id,))
        sistem_log_ekle(cur, islem_yapan, "ERİŞİM_KAPATILDI", f"{kullanici['kullanici_adi']} pasife alındı.")
    return {"mesaj": f"{kullanici['kullanici_adi']} pasife alındı."}

@router.put("/sifre-guncelle")
def sifre_guncelle_endpoint(veri: SifreGuncelle, islem_yapan: str = Header(default="Bilinmeyen")):
    with get_db_session() as cur:
        cur.execute("UPDATE kullanicilar SET sifre = %s WHERE kullanici_adi = %s RETURNING id", (veri.sifre, veri.kullanici_adi))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")
        sistem_log_ekle(cur, islem_yapan, "ŞİFRE_SIFIRLAMA", f"{veri.kullanici_adi} şifresi güncellendi.")
    return {"mesaj": "Şifre başarıyla güncellendi"}