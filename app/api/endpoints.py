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
from datetime import datetime

router = APIRouter()

from fastapi import APIRouter, HTTPException, Depends
# ... diğer importların (get_db vb.)

router = APIRouter()

@router.post("/login")
def login(kullanici: KullaniciGiris):
    with get_db_session() as cur:
        # 1. Veritabanından kullanıcıyı sorgula
        cur.execute("SELECT * FROM kullanicilar WHERE kullanici_adi = %s AND sifre = %s", (kullanici.kullanici_adi, kullanici.sifre))
        user = cur.fetchone()
        
        # 2. Güvenlik Kontrolleri
        if not user:
            raise HTTPException(status_code=401, detail="Kullanıcı adı veya şifre hatalı!")
            
        if not user['aktif_mi']:
            raise HTTPException(status_code=403, detail="Bu hesap pasife alınmıştır. Yöneticinizle iletişime geçin.")
            
        # --- 3. SİSTEM LOGU BURADA DEVREYE GİRİYOR ---
        detay_mesaji = f"{user['kullanici_adi']} adlı kullanıcı ({user['rol']}) sisteme başarılı bir şekilde giriş yaptı."
        
        # Log fonksiyonumuzu çağırıyoruz (İşlemi yapan olarak direkt giriş yapan kişinin adını veriyoruz)
        sistem_log_ekle(cur, user['kullanici_adi'], "GİRİŞ_YAPILDI", detay_mesaji)
        
        # 'with' bloğu burada bittiği için, herhangi bir hata yoksa sistem otomatik olarak commit işlemini yapacak ve kapıyı kapatacak!
        
    return {"mesaj": "Giriş başarılı", "rol": user['rol'], "kullanici_adi": user['kullanici_adi']}



# 2. EKİBİ LİSTELEME (Modern Mimari)
@router.get("/ekip")
def ekip_listele():
    with get_db_session() as cur:
        cur.execute("SELECT id, kullanici_adi, rol, aktif_mi FROM kullanicilar ORDER BY id ASC")
        
        # RealDictCursor bizim yerimize her şeyi Vue'nun sevdiği JSON (sözlük) formatına çevirdiği için
        # ekstra bir döngü (dict(row)) yazmadan doğrudan dışarı yolluyoruz!
        return cur.fetchall()
    

from fastapi import Header, HTTPException

# 3. YENİ ÜYE EKLEME (Kullanıcı Adı Kontrollü ve Dinamik Loglamalı)
@router.post("/ekip/ekle")
def uye_ekle(yeni_uye: KullaniciOlustur, islem_yapan: str = Header(default="Bilinmeyen Yönetici")):
    with get_db_session() as cur:
        # 1. MÜKEMMEL KONTROLÜN: Bu kullanıcı adı var mı?
        cur.execute("SELECT id FROM kullanicilar WHERE kullanici_adi = %s", (yeni_uye.kullanici_adi,))
        mevcut_kullanici = cur.fetchone()
        
        if mevcut_kullanici:
            raise HTTPException(status_code=400, detail="Bu kullanıcı adı zaten sistemde kayıtlı. Lütfen farklı bir isim seçin.")
        
        # 2. Yeni üyeyi sisteme ekleme
        cur.execute(
            "INSERT INTO kullanicilar (kullanici_adi, sifre, rol, aktif_mi) VALUES (%s, %s, %s, TRUE)",
            (yeni_uye.kullanici_adi, yeni_uye.sifre, yeni_uye.rol)
        )
        
        # --- 3. SİSTEM LOGU (Artık islem_yapan değişkeniyle dinamik!) ---
        detay_mesaji = f"Sisteme yeni bir personel eklendi: {yeni_uye.kullanici_adi} (Yetki: {yeni_uye.rol})"
        sistem_log_ekle(cur, islem_yapan, "PERSONEL_EKLE", detay_mesaji)

        # 'with' bloğu bittiği an her şey (ekleme + log) otomatik commit edilecek!
        
    return {"mesaj": f"Yeni ekip üyesi {yeni_uye.kullanici_adi} başarıyla eklendi! ✅"}
        
# 4. SİLME (SOFT DELETE - PASİFE ALMA) ve Dinamik Loglama
@router.delete("/ekip/{uye_id}")
def uye_pasife_al(uye_id: int, islem_yapan: str = Header(default="Bilinmeyen Yönetici")):
    with get_db_session() as cur:
        # 1. Önce bu id'ye sahip kişi kimmiş onu bulalım ki loga adını yazabilelim
        cur.execute("SELECT kullanici_adi FROM kullanicilar WHERE id = %s", (uye_id,))
        silinecek_kullanici = cur.fetchone()
        
        if not silinecek_kullanici:
            raise HTTPException(status_code=404, detail="Sistemde böyle bir kullanıcı bulunamadı.")
            
        # RealDictCursor kullandığımız için doğrudan sözlükten çekiyoruz
        kullanici_adi = silinecek_kullanici['kullanici_adi']
        
        # 2. Kullanıcıyı pasife alıyoruz (Soft Delete)
        cur.execute("UPDATE kullanicilar SET aktif_mi = FALSE WHERE id = %s", (uye_id,))
        
        # --- 3. SİSTEM LOGU BURAYA EKLENİYOR (ARTIK DİNAMİK) ---
        detay_mesaji = f"{kullanici_adi} adlı personelin sisteme erişimi kapatıldı."
        
        # Sabit "Yönetici" yazısı yerine Vue'dan gelen 'islem_yapan' değişkenini koyduk!
        sistem_log_ekle(cur, islem_yapan, "ERİŞİM_KAPATILDI", detay_mesaji)
        
        # 'with' bloğu bittiği an her şey (pasife alma + log) otomatik commit edilecek!
        
    return {"mesaj": f"{kullanici_adi} adlı kullanıcı başarıyla pasife alındı."}


# Şifre güncelleme için güvenlik şeması
class SifreGuncelle(BaseModel):
    kullanici_adi: str
    sifre: str = Field(..., min_length=5)

# Şifre güncelleme kapısı (Modern Mimari ve Dinamik Log Destekli)
@router.put("/ekip/sifre-guncelle")
def sifre_guncelle_endpoint(veri: SifreGuncelle, islem_yapan: str = Header(default="Bilinmeyen Yönetici")):
    with get_db_session() as cur:
        # 1. Önce kullanıcı veritabanında var mı kontrol et
        cur.execute("SELECT id FROM kullanicilar WHERE kullanici_adi = %s", (veri.kullanici_adi,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Böyle bir kullanıcı bulunamadı.")

        # 2. Kullanıcı varsa şifresini güncelle
        cur.execute("UPDATE kullanicilar SET sifre = %s WHERE kullanici_adi = %s", (veri.sifre, veri.kullanici_adi))
        
        # --- 3. SİSTEM LOGU BURAYA EKLENİYOR (DİNAMİK) ---
        detay_mesaji = f"{veri.kullanici_adi} adlı personelin sistem giriş şifresi güncellendi."
        sistem_log_ekle(cur, islem_yapan, "ŞİFRE_SIFIRLAMA", detay_mesaji)
        
        # 'with' bloğu bittiğinde veritabanı mühürlemesi (commit) otomatik gerçekleşir.
        
    return {"mesaj": "Şifre başarıyla güncellendi"}

# --- OTOMATİK REFERANS NUMARASI ÜRETİCİ ---
def referans_no_olustur(cur):
    """Günün tarihine göre otomatik TEMKON_OFFER numarası üretir."""
    # Bugünü GGAAYY formatında alıyoruz (Örn: 100726)
    bugun_str = datetime.now().strftime("%d%m%y") 
    baslangic_sablonu = f"TEMKON_OFFER_{bugun_str}_"
    
    cur.execute("""
        SELECT referans_no FROM projeler 
        WHERE referans_no LIKE %s 
        ORDER BY id DESC LIMIT 1
    """, (baslangic_sablonu + '%',))
    
    son_kayit = cur.fetchone()
    
    if son_kayit and son_kayit['referans_no']:
        # Örn: 'TEMKON_OFFER_100726_01' -> ['TEMKON', 'OFFER', '100726', '01']
        parcalar = son_kayit['referans_no'].split('_')
        son_numara = int(parcalar[3]) 
        yeni_numara = son_numara + 1
    else:
        yeni_numara = 1
        
    return f"{baslangic_sablonu}{yeni_numara:02d}"


# --- YENİ PROJE EKLEME (Güncel) ---
@router.post("/projeler")
def yeni_proje_ekle(proje: ProjeEkle, islem_yapan: str = Header(default="Bilinmeyen Kullanıcı")):
    with get_db_session() as cur:
        # 1. Arka planda numarayı otomatik üret
        yeni_referans = referans_no_olustur(cur)
        
        # 2. Üretilen numarayı Vue'dan gelen proje kargosuna tak
        proje.referans_no = yeni_referans
        
        # 3. crud fonksiyonu ile projeyi veritabanına ekle
        crud.insert_proje(cur, proje)

        # --- SİSTEM LOGU ---
        detay_mesaji = f"Sisteme yeni bir proje eklendi: '{proje.proje_adi}' (Ref: {yeni_referans})"
        sistem_log_ekle(cur, islem_yapan, "PROJE_EKLE", detay_mesaji)

    return {
        "mesaj": f"'{proje.proje_adi}' adlı proje başarıyla eklendi! ✅", 
        "referans_no": yeni_referans
    }



# 1. YENİ İSKONTO GRUBU EKLEME (CRUD Mimarisi + Güvenlik + Dinamik Log)
@router.post("/iskonto-gruplari")
def iskonto_grubu_ekle(
    grup: IskontoGrubuEkle, 
    # Frontend'den gelen güvenlik ve kimlik başlıklarını alıyoruz
    current_user_role: str = Header(..., alias="current-user-role"),
    islem_yapan: str = Header(default="Bilinmeyen Yönetici")
):
    # Kapıdaki güvenlik kontrolü
    if current_user_role != 'yonetici':
        raise HTTPException(status_code=403, detail="Bu işlemi yapmaya yetkiniz yok!")
        
    with get_db_session() as cur:
        # Senin kendi temiz mimarin (SQL yazmak yerine crud fonksiyonunu çağırıyoruz)
        crud.insert_iskonto_grubu(cur, grup)
        
        # --- SİSTEM LOGU BURAYA EKLENİYOR (ARTIK DİNAMİK) ---
        detay_mesaji = f"Sisteme yeni bir iskonto grubu tanımlandı: '{grup.grup_adi}'"
        
        # Sabit "Yönetici" yazısı yerine Vue'dan gelen islem_yapan değişkenini koyduk!
        sistem_log_ekle(cur, islem_yapan, "İSKONTO_GRUBU_EKLE", detay_mesaji)
        
    return {"mesaj": f"'{grup.grup_adi}' iskonto grubu başarıyla tanımlandı!"}


@router.get("/iskonto-gruplari")
def iskonto_gruplari_listele():
    """Arayüzdeki açılır menü için iskonto gruplarını isimleriyle getirir."""
    with get_db_session() as cur:
        # Sadece ID ve İsim lazım, RealDictCursor bize sözlük olarak verecek
        cur.execute("SELECT id, grup_adi FROM grup_iskontolar ORDER BY id")
        return cur.fetchall()
    
from fastapi import Header, HTTPException

# --- MALZEMELER ---
@router.post("/malzemeler")
def yeni_malzeme_ekle(malzeme: MalzemeEkle, islem_yapan: str = Header(default="Bilinmeyen Kullanıcı")):
    """Yeni bir malzeme ekler. Para birimini kurlar tablosundan kontrol eder ve işlemi loglar."""
    with get_db_session() as cur:
        # 1. KUR BELİRLEME VE DOĞRULAMA MANTIĞI
        if malzeme.para_birimi == "TRY":
            kur_degeri = 1.0
        else:
            cur.execute("SELECT kur_degeri FROM kurlar WHERE para_birimi = %s", (malzeme.para_birimi,))
            result = cur.fetchone()
            
            if not result:
                raise HTTPException(status_code=400, detail=f"'{malzeme.para_birimi}' kurlar tablosunda bulunamadı.")
            
            # Kur değerini aldık (Eğer ileride fiyata çarpmak vs. istersen burada hazır bekliyor)
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
            malzeme.grup_iskonto_id, 
            malzeme.notlar 
        ))
        
        # --- 3. SİSTEM LOGU BURAYA EKLENİYOR (ARTIK DİNAMİK!) ---
        detay_mesaji = f"Envantere yeni malzeme eklendi: {malzeme.urun_adi} (Marka: {malzeme.marka}, Kod: {malzeme.siparis_kodu})"
        
        # Sabit "Sistem" yerine Header'dan gelen islem_yapan değişkeni kullanılıyor
        sistem_log_ekle(cur, islem_yapan, "MALZEME_EKLE", detay_mesaji)
        
        # 'with' bloğundan çıktığı an hem malzeme hem de log otomatik olarak commit edilecek.

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


def sistem_log_ekle(cur, kullanici, islem, detay):
    try:
        su_an = datetime.now()
        
        # Sütun adlarını DBeaver'daki gibi (kullanici_adi ve islem_turu) yaptık!
        sql = """
            INSERT INTO loglar (kullanici_adi, islem_turu, detay, tarih) 
            VALUES (%s, %s, %s, %s)
        """
        cur.execute(sql, (kullanici, islem, detay, su_an))
        
    except Exception as e:
        print("Log kaydedilemedi:", e)

# --- PROJE PANO LİSTESİ (Dinamik Log Destekli) ---
@router.post("/projeler/pano-malzeme-ekle")
def projeye_pano_malzemesi_ekle(pano_veri: ProjePanoEkle, islem_yapan: str = Header(default="Bilinmeyen Kullanıcı")):
    """Projeye ait panolardan birine malzeme ataması yapar ve işlemi loglar."""
    with get_db_session() as cur:
        # 1. MALZEMEYİ PANOYA EKLE
        cur.execute("""
            INSERT INTO proje_pano_listesi (proje_id, malzeme_id, pano_turu, adet, ozel_iskonto, notlar)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            pano_veri.proje_id, 
            pano_veri.malzeme_id, 
            pano_veri.pano_turu, 
            pano_veri.adet,
            0,     # DÜZELTME 1: Özel iskonto şimdilik 0 olarak sabitlendi
            None   # DÜZELTME 2: Patlamasın diye None (Boş) gönderiyoruz
        ))
        
        # --- 2. SİSTEM LOGU (ARTIK DİNAMİK) ---
        detay_mesaji = f"Projeye malzeme ataması yapıldı (Pano Türü: {pano_veri.pano_turu}, Miktar: {pano_veri.adet} adet)"
        
        # Sabit "Sistem" yerine Header'dan gelen islem_yapan değişkenini ekledik!
        sistem_log_ekle(cur, islem_yapan, "PANO_MALZEME_EKLE", detay_mesaji)
        
        # 'with' bloğundan çıktığı an malzeme ataması ve log kaydı aynı anda commit edilecek.
        
    return {"mesaj": f"Başarıyla atandı: {pano_veri.pano_turu} ✅"}


# --- 3'LÜ FİYAT HESAPLAMA MOTORU (Maliyet / Proje / Satış) ---
@router.get("/projeler/{proje_id}/maliyet-raporu")
def proje_maliyet_raporu_getir(proje_id: int):
    # Kapı açılıyor
    with get_db_session() as cur:
        cur.execute("""
            SELECT 
                pl.degistirildi,    
                pl.id,
                p.proje_adi,
                pl.pano_turu,
                m.urun_adi,
                SUM(pl.adet) as adet,  
                m.liste_fiyati,
                COALESCE(k.kur_degeri, 1.0) as kur_degeri,
                m.para_birimi,
                g.maliyet_iskonto,
                g.proje_iskonto,
                g.satis_iskonto,
                m.marka,
                m.siparis_kodu
            FROM proje_pano_listesi pl
            JOIN projeler p ON pl.proje_id = p.id
            JOIN malzemeler m ON pl.malzeme_id = m.id
            LEFT JOIN kurlar k ON m.para_birimi = k.para_birimi
            LEFT JOIN grup_iskontolar g ON m.grup_iskonto_id = g.id
            WHERE p.id = %s
            GROUP BY 
               
                pl.id,
                pl.degistirildi,
                p.proje_adi,
                pl.pano_turu,
                m.urun_adi,
                m.liste_fiyati,
                k.kur_degeri,
                m.para_birimi,
                g.maliyet_iskonto,
                g.proje_iskonto,
                g.satis_iskonto,
                m.marka,
                m.siparis_kodu
        """, (proje_id,))
        
        satirlar = cur.fetchall()

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

            "id": satir['id'],
            "degistirildi": satir['degistirildi'],
            "pano": satir['pano_turu'],
            "malzeme": satir['urun_adi'],
            "adet": satir['adet'],
            "liste_fiyati": float(satir['liste_fiyati']),
            "kur_degeri": float(satir['kur_degeri']),
            "para_birimi": satir['para_birimi'],
            

            "marka": satir['marka'] if satir['marka'] else "-",          # YENİ EKLENDİ
            "siparis_kodu": satir['siparis_kodu'] if satir['siparis_kodu'] else "-", # YENİ EKLENDİ

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
@router.get("/malzemeler/listele")
def malzemeleri_listele():
    with get_db_session() as cur:
        # 1. Sorguya 'marka' sütununu ekledik ve 'urun_adi' alanını Vue'daki gibi 'malzeme' olarak isimlendirdik
        cur.execute("""
            SELECT id, urun_adi AS malzeme, marka, siparis_kodu 
            FROM malzemeler
        """)
        rows = cur.fetchall()
        
        # 2. Verileri sözlüğe (dict) çeviriyoruz ki Vue kodun item.marka ve item.siparis_kodu diye okuyabilsin:
        if rows and isinstance(rows[0], tuple):
            sutun_isimleri = [desc[0] for desc in cur.description]
            return [dict(zip(sutun_isimleri, row)) for row in rows]
            
        return rows

@router.get("/projeler/listele")
def projeleri_listele():
    with get_db_session() as cur:
        cur.execute("""
            SELECT id, referans_no, proje_adi, musteri, son_kullanici, 
                   lokasyon, teklif_konusu, tarih, hazirlayan, notlar 
            FROM projeler
        """)
        rows = cur.fetchall()
        
        # Eğer veriler sözlük (dict) yerine düz tuple geliyorsa, 
        # dinamik olarak sütun isimleriyle eşleştirip nesne haline getiriyoruz:
        if rows and isinstance(rows[0], tuple):
            sutun_isimleri = [desc[0] for desc in cur.description]
            return [dict(zip(sutun_isimleri, row)) for row in rows]
            
        return rows


@router.put("/pano-malzeme-guncelle/{malzeme_id}")
def pano_malzeme_guncelle(malzeme_id: int, yeni_veri: dict):
    guncellenecekler = {k: v for k, v in yeni_veri.items() if k not in ["id"]}
    if not guncellenecekler:
        return {"mesaj": "Güncellenecek veri bulunamadı."}

    with get_db_session() as cur:
        # 1. Önce satırın "eski" halini çekiyoruz
        sutun_isimleri = ", ".join(guncellenecekler.keys())
        eski_sorgu = f"SELECT {sutun_isimleri} FROM proje_pano_listesi WHERE id = %s"
        cur.execute(eski_sorgu, (malzeme_id,))
        eski_degerler = cur.fetchone()

        # 2. Asıl tabloyu güncelliyoruz ve degistirildi sütununu TRUE yapıyoruz (Kalıcı Sarı Renk)
        sutunlar = []
        degerler = []
        for anahtar, deger in guncellenecekler.items():
            sutunlar.append(f"{anahtar} = %s")
            degerler.append(deger)
            
        sutunlar.append("degistirildi = TRUE") 
        
        sorgu = f"UPDATE proje_pano_listesi SET {', '.join(sutunlar)} WHERE id = %s"
        degerler.append(malzeme_id)
        cur.execute(sorgu, tuple(degerler))

        # 3. SENİN MEVCUT LOG TABLONA YAZIYORUZ
        if eski_degerler:
            for i, (anahtar, yeni_deger) in enumerate(guncellenecekler.items()):
                eski_deger = eski_degerler[anahtar] if isinstance(eski_degerler, dict) else eski_degerler[i]
                
                if str(eski_deger) != str(yeni_deger):  # Değer değişmişse logla
                    detay_metni = f"Malzeme ID {malzeme_id} satırında '{anahtar}' değeri '{eski_deger}' iken '{yeni_deger}' olarak değiştirildi."
                    
                    log_sorgu = """
                        INSERT INTO loglar (kullanici_adi, islem_turu, detay) 
                        VALUES (%s, %s, %s)
                    """
                    # Not: "Yönetici" kısmını eğer frontend'den kullanıcı adını alıyorsan dinamik yapabilirsin
                    cur.execute(log_sorgu, ("Yönetici", "HÜCRE_GÜNCELLEME", detay_metni))

    return {"mesaj": "Başarıyla güncellendi ve loglandı!"}


# SİSTEM LOGLARINI LİSTELEME (Modern ve Temiz Versiyon)
@router.get("/loglar")
def loglari_getir():
    with get_db_session() as cur:
        # Veritabanındaki loglar tablosundan son 100 işlemi en yeniden eskiye sıralayarak çekiyoruz
        cur.execute("SELECT * FROM loglar ORDER BY id DESC LIMIT 100")
        
        # RealDictCursor zaten veriyi Vue için hazır sözlük formatında döndürdüğü için 
        # ekstra bir çevirme işlemi (dict(row)) yapmadan doğrudan Vue'ya yolluyoruz!
        return cur.fetchall()