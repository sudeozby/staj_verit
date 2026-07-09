import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


from fastapi import APIRouter, Depends, HTTPException, Header
from app.db.session import get_db_session
from app.models.schemas import ProjeEkle, IskontoGrubuEkle, MalzemeEkle, ProjePanoEkle
from app.db import crud  # Senin harika depocu mimarin
from app.services.tcmb_service import fetch_tcmb_rates
from app.services.pricing_engine import hesapla_pano_maliyeti
# Eğer endpoints.py içinden çağırıyorsan:
from app.models.schemas import IskontoGrubuEkle
from pydantic import BaseModel, Field
from app.models.schemas import KullaniciOlustur, KullaniciGiris
from db_manager import get_db_connection
import psycopg2
import psycopg2.extras

router = APIRouter()

from fastapi import APIRouter, HTTPException, Depends
# ... diğer importların (get_db vb.)

router = APIRouter()

# 1. GİRİŞ YAPMA (LOGIN)
@router.post("/login")
def login(kullanici: KullaniciGiris):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM kullanicilar WHERE kullanici_adi = %s AND sifre = %s", (kullanici.kullanici_adi, kullanici.sifre))
    user = cur.fetchone()
    
    if not user:
        raise HTTPException(status_code=401, detail="Kullanıcı adı veya şifre hatalı!")
        
    if not user['aktif_mi']:
        raise HTTPException(status_code=403, detail="Bu hesap pasife alınmıştır. Yöneticinizle iletişime geçin.")
        
    return {"mesaj": "Giriş başarılı", "rol": user['rol'], "kullanici_adi": user['kullanici_adi']}

# 2. EKİBİ LİSTELEME (GÜNCELLENDİ)
@router.get("/ekip")
def ekip_listele():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute("SELECT id, kullanici_adi, rol, aktif_mi FROM kullanicilar ORDER BY id ASC")
        kullanicilar = cur.fetchall()
        
        # FastAPI'nin Vue'ya düzgün JSON (isim:değer) gönderebilmesi için dict() kullanıyoruz:
        return [dict(row) for row in kullanicilar]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Veriler çekilirken hata oluştu: " + str(e))
    finally:
        cur.close()
        conn.close()

# 3. YENİ ÜYE EKLEME (Kullanıcı Adı Kontrollü)
@router.post("/ekip/ekle")
def uye_ekle(yeni_uye: KullaniciOlustur):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute("SELECT id FROM kullanicilar WHERE kullanici_adi = %s", (yeni_uye.kullanici_adi,))
        mevcut_kullanici = cur.fetchone()
        
        if mevcut_kullanici:
            raise HTTPException(status_code=400, detail="Bu kullanıcı adı zaten sistemde kayıtlı. Lütfen farklı bir isim seçin.")
        
        cur.execute(
            "INSERT INTO kullanicilar (kullanici_adi, sifre, rol, aktif_mi) VALUES (%s, %s, %s, TRUE)",
            (yeni_uye.kullanici_adi, yeni_uye.sifre, yeni_uye.rol)
        )
        conn.commit()
        return {"mesaj": "Yeni ekip üyesi başarıyla eklendi!"}
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Sistem hatası: " + str(e))

# 4. SİLME (SOFT DELETE - PASİFE ALMA)
@router.delete("/ekip/{uye_id}")
def uye_pasife_al(uye_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE kullanicilar SET aktif_mi = FALSE WHERE id = %s", (uye_id,))
    conn.commit()
    return {"mesaj": "Kullanıcı başarıyla pasife alındı."}
    

# Şifre güncelleme için güvenlik şeması
class SifreGuncelle(BaseModel):
    kullanici_adi: str
    sifre: str = Field(..., min_length=5)

# Şifre güncelleme kapısı
@router.put("/ekip/sifre-guncelle")
def sifre_guncelle_endpoint(veri: SifreGuncelle):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Önce kullanıcı veritabanında var mı kontrol et
        cur.execute("SELECT id FROM kullanicilar WHERE kullanici_adi = %s", (veri.kullanici_adi,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Böyle bir kullanıcı bulunamadı.")

        # Kullanıcı varsa şifresini güncelle
        cur.execute("UPDATE kullanicilar SET sifre = %s WHERE kullanici_adi = %s", (veri.sifre, veri.kullanici_adi))
        conn.commit()
        return {"mesaj": "Şifre başarıyla güncellendi"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Veritabanı hatası: " + str(e))
    finally:
        cur.close()
        conn.close()
        
    
# --- PROJELER ---
@router.get("/projeler")
def projeleri_getir():
    with get_db_session() as cur:
        projeler_listesi = crud.get_all_projeler(cur)
        return {"projeler": projeler_listesi}

@router.post("/projeler")
def yeni_proje_ekle(proje: ProjeEkle):
    with get_db_session() as cur:
        crud.insert_proje(cur, proje)
    return {"mesaj": f"'{proje.proje_adi}' adlı proje başarıyla eklendi!"}

# --- İSKONTO GRUPLARI (TEMKON Mimarisi) ---
@router.post("/iskonto-gruplari")
def iskonto_grubu_ekle(grup: IskontoGrubuEkle):
    with get_db_session() as cur:
        # CRUD dosyanı da bu yeni 3'lü iskonto sistemine göre güncellediğini varsayıyoruz
        crud.insert_iskonto_grubu(cur, grup)
    return {"mesaj": f"'{grup.grup_adi}' iskonto grubu başarıyla tanımlandı!"}


@router.post("/iskonto-gruplari/ekle")
def iskonto_grubu_ekle(
    grup: IskontoGrubuEkle, 
    # Frontend'den gelen 'current-user-role' başlığını yakalaması için alias ekledik
    current_user_role: str = Header(..., alias="current-user-role")
):
    # Yetki kontrolü
    if current_user_role != 'yonetici':
        raise HTTPException(status_code=403, detail="Bu işlemi yapmaya yetkiniz yok!")
        
    with get_db_session() as cur:
        cur.execute("""
            INSERT INTO grup_iskontolar (grup_adi, maliyet_iskonto, proje_iskonto, satis_iskonto, notlar)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            grup.grup_adi, 
            grup.maliyet_iskonto, 
            grup.proje_iskonto, 
            grup.satis_iskonto,
            grup.notlar # Buradaki 'no' kısmını 'notlar' olarak düzelttik
        ))
    return {"mesaj": "Yeni iskonto grubu başarıyla tanımlandı!"}



@router.get("/iskonto-gruplari")
def iskonto_gruplari_listele():
    """Arayüzdeki açılır menü için iskonto gruplarını isimleriyle getirir."""
    with get_db_session() as cur:
        # Sadece ID ve İsim lazım, RealDictCursor bize sözlük olarak verecek
        cur.execute("SELECT id, grup_adi FROM grup_iskontolar ORDER BY id")
        return cur.fetchall()
    
# --- MALZEMELER ---
@router.post("/malzemeler")
def yeni_malzeme_ekle(malzeme: MalzemeEkle):
    """Yeni bir malzeme ekler. Para birimini kurlar tablosundan kontrol eder."""
    with get_db_session() as cur:
        # 1. KUR BELİRLEME MANTIĞI
        if malzeme.para_birimi == "TRY":
            kur_degeri = 1.0
        else:
            cur.execute("SELECT kur_degeri FROM kurlar WHERE para_birimi = %s", (malzeme.para_birimi,))
            result = cur.fetchone()
            
            if not result:
                raise HTTPException(status_code=400, detail=f"'{malzeme.para_birimi}' kurlar tablosunda bulunamadı.")
            
            # DÜZELTME 1: RealDictCursor sözlük yapısı kullanıldığı için [0] yerine anahtar isimle çağırdık
            kur_degeri = result['kur_degeri'] 
        
        # 2. MALZEME EKLEME
        cur.execute("""
            INSERT INTO malzemeler (siparis_kodu, urun_adi, marka, urun_grubu, tedarikci, liste_fiyati, para_birimi, grup_iskonto_id, notlar)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            malzeme.siparis_kodu, 
            malzeme.urun_adi, 
            malzeme.marka, 
            malzeme.urun_grubu, 
            malzeme.tedarikci, 
            malzeme.liste_fiyati, 
            malzeme.para_birimi, 
            malzeme.grup_iskonto_id, # DÜZELTME: Artık None değil, şablondan gelen ID'yi yazıyoruz
            malzeme.notlar 
        ))
        
    return {"mesaj": f"'{malzeme.urun_adi}' envantere başarıyla eklendi! ✅"}
@router.post("/kurlar/tcmb-guncelle")
def tcmb_kurlarini_guncelle():
    kurlar_verisi = fetch_tcmb_rates()
    with get_db_session() as cur:
        guncellenen_kurlar = []
        for kod, kur_degeri in kurlar_verisi.items():
            cur.execute("""
                INSERT INTO kurlar (para_birimi, kur_degeri, guncellenme_tarihi)
                VALUES (%s, %s, CURRENT_DATE)
                ON CONFLICT (para_birimi) 
                DO UPDATE SET kur_degeri = EXCLUDED.kur_degeri, guncellenme_tarihi = CURRENT_DATE;
            """,(kod, kur_degeri))
            guncellenen_kurlar.append(f"{kod}: {kur_degeri} TL")
            
    return {
        "mesaj": "TCMB kurları başarıyla çekildi ve güncellendi!",
        "guncellenen_veriler": guncellenen_kurlar
    }

# --- PROJE PANO LİSTESİ (TEMKON Güncellemesi) ---
@router.post("/projeler/pano-malzeme-ekle")
def projeye_pano_malzemesi_ekle(pano_veri: ProjePanoEkle):
    """Projeye ait panolardan birine malzeme ataması yapar."""
    with get_db_session() as cur:
        # İŞTE GÜNCELLEYECEĞİN SQL BÖLÜMÜ:
        cur.execute("""
            INSERT INTO proje_pano_listesi (proje_id, malzeme_id, pano_turu, adet, ozel_iskonto, notlar)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            pano_veri.proje_id, 
            pano_veri.malzeme_id, 
            pano_veri.pano_turu, 
            pano_veri.adet,
            0,     # DÜZELTME 1: pano_veri.ozel_iskonto yerine 0 yazıyoruz
            None   # DÜZELTME 2: Eğer pano_veri.notlar varsa patlamasın diye None yazıyoruz
        ))
        
    return {"mesaj": f"Başarıyla atandı: {pano_veri.pano_turu} ✅"}
# --- 3'LÜ FİYAT HESAPLAMA MOTORU (Maliyet / Proje / Satış) ---
# --- 3'LÜ FİYAT HESAPLAMA MOTORU (Maliyet / Proje / Satış) ---
@router.get("/projeler/{proje_id}/maliyet-raporu")
def proje_maliyet_raporu_getir(proje_id: int):
    # Kapı açılıyor
    with get_db_session() as cur:
        cur.execute("""
            SELECT 
                p.proje_adi,
                pl.pano_turu,
                m.urun_adi,
                pl.adet,
                m.liste_fiyati,
                COALESCE(k.kur_degeri, 1.0) as kur_degeri,
                m.para_birimi,
                g.maliyet_iskonto,
                g.proje_iskonto,
                g.satis_iskonto
            FROM proje_pano_listesi pl
            JOIN projeler p ON pl.proje_id = p.id
            JOIN malzemeler m ON pl.malzeme_id = m.id
            LEFT JOIN kurlar k ON m.para_birimi = k.para_birimi
            LEFT JOIN grup_iskontolar g ON m.grup_iskonto_id = g.id
            WHERE p.id = %s
        """, (proje_id,))
        
        # Kapı kapanmadan veriyi alıyoruz
        satirlar = cur.fetchall()

    # GÜVENLİK ÖNLEMİ 1: Proje boşsa çökmesin
    if not satirlar:
        return {
           "proje_adi": "Yeni Proje (Boş)",
           "genel_toplamlar": {"maliyet_tl": 0, "proje_tl": 0, "satis_tl": 0},
           "detaylar": []
        } 
 
    rapor = []
    toplam_maliyet_tl = 0.0
    toplam_proje_tl = 0.0
    toplam_satis_tl = 0.0

    # Çekilen her bir malzeme satırı için 3'LÜ HESAPLAMA
    for satir in satirlar:
    # 1. HESAPLAMA MOTORUNU ÇAĞIR
        maliyet_sonuc = hesapla_pano_maliyeti(satir['liste_fiyati'], satir['maliyet_iskonto'], satir['kur_degeri'], satir['adet'])
        proje_sonuc = hesapla_pano_maliyeti(satir['liste_fiyati'], satir['proje_iskonto'], satir['kur_degeri'], satir['adet'])
        satis_sonuc = hesapla_pano_maliyeti(satir['liste_fiyati'], satir['satis_iskonto'], satir['kur_degeri'], satir['adet'])
    
    # 2. TOPLAMLARA EKLE
        toplam_maliyet_tl += maliyet_sonuc['satir_toplami']
        toplam_proje_tl += proje_sonuc['satir_toplami']
        toplam_satis_tl += satis_sonuc['satir_toplami']
        
        rapor.append({
            "pano": satir['pano_turu'],
            "malzeme": satir['urun_adi'],
            "adet": satir['adet'],
            "liste_fiyati": float(satir['liste_fiyati']),
            "kur_degeri": float(satir['kur_degeri']),
            "para_birimi": satir['para_birimi'],
        
            "birim_maliyet_tl": maliyet_sonuc['net_fiyat_tl'],
            "toplam_maliyet_tl": maliyet_sonuc['satir_toplami'],
        
            "birim_proje_tl": proje_sonuc['net_fiyat_tl'],
            "toplam_proje_tl": proje_sonuc['satir_toplami'],
        
            "birim_satis_tl": satis_sonuc['net_fiyat_tl'],
            "toplam_satis_tl": satis_sonuc['satir_toplami']
    })

    return {
    "proje_adi": satirlar[0]['proje_adi'], # İlk satırdan proje adını alıyoruz
    "genel_toplamlar": {
        "maliyet_tl": round(toplam_maliyet_tl, 2),
        "proje_tl": round(toplam_proje_tl, 2),
        "satis_tl": round(toplam_satis_tl, 2)
    },
    "detaylar": rapor
}
# --- MALZEME VE PROJE LİSTELEME (Dinamik seçim için) ---
@router.get("/malzemeler/listele")
def malzemeleri_listele():
    with get_db_session() as cur:
        cur.execute("SELECT id, urun_adi, siparis_kodu FROM malzemeler")
        return cur.fetchall()

@router.get("/projeler/listele")
def projeleri_listele():
    with get_db_session() as cur:
        cur.execute("SELECT id, proje_adi FROM projeler")
        return cur.fetchall()