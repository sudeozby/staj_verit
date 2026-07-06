from fastapi import APIRouter, HTTPException
from app.db.session import get_db_session
from app.models.schemas import ProjeEkle, IskontoGrubuEkle, MalzemeEkle, ProjePanoEkle
from app.db import crud  # Senin harika depocu mimarin
from app.services.tcmb_service import fetch_tcmb_rates

router = APIRouter()

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
            
            kur_degeri = result[0] # Veritabanından gelen değeri alıyoruz
        
        # 2. MALZEME EKLEME
        cur.execute("""
            INSERT INTO malzemeler (siparis_kodu, urun_adi, marka, urun_grubu, tedarikci, liste_fiyati, para_birimi, grup_iskonto_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            malzeme.siparis_kodu, malzeme.urun_adi, malzeme.marka, 
            malzeme.urun_grubu, malzeme.tedarikci, malzeme.liste_fiyati, 
            malzeme.para_birimi, malzeme.grup_iskonto_id
        ))
        
    return {"mesaj": f"'{malzeme.urun_adi}' envantere başarıyla eklendi!"}
# --- TCMB CANLI KURLARI (Mükemmel olan kodun hiç değişmedi) ---
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
def projeye_pano_malzemesi_ekle(veri: ProjePanoEkle):
    with get_db_session() as cur:
        # Yeni sütunlar eklendi: ozel_iskonto ve notlar
        cur.execute("""
            INSERT INTO proje_pano_listesi (proje_id, malzeme_id, pano_turu, adet, ozel_iskonto, notlar)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (veri.proje_id, veri.malzeme_id, veri.pano_turu, veri.adet, veri.ozel_iskonto, veri.notlar))
        
    return {"mesaj": f"{veri.proje_id} ID'li projeye, {veri.adet} adet malzeme başarıyla eklendi!"}

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
            "genel_toplamlar": {
                "maliyet_tl": 0,
                "proje_tl": 0,
                "satis_tl": 0
            },
            "detaylar": []
        }

    rapor = []
    toplam_maliyet_tl = 0.0
    toplam_proje_tl = 0.0
    toplam_satis_tl = 0.0

    # Çekilen her bir malzeme satırı için 3'LÜ HESAPLAMA
    for satir in satirlar:
        proje_adi, pano_turu, urun_adi, adet, liste_fiyati, kur_degeri, para_birimi, m_isk, p_isk, s_isk = satir
        
        # GÜVENLİK ÖNLEMİ 2: Matematik Çökmesini Engelleme (Boş gelen veriyi 0 kabul ediyoruz)
        guvenli_liste_fiyati = float(liste_fiyati or 0.0)
        guvenli_kur_degeri = float(kur_degeri or 1.0)
        guvenli_adet = float(adet or 0.0)
        
        mal_isk_oran = float(m_isk or 0.0)
        proj_isk_oran = float(p_isk or 0.0)
        sat_isk_oran = float(s_isk or 0.0)
        
        # 1. Ham Fiyatı TL'ye Çevir
        tl_liste_fiyati = guvenli_liste_fiyati * guvenli_kur_degeri
        
        # 2. ÜÇ FARKLI BİRİM FİYAT (İskontoları düşerek)
        birim_maliyet = tl_liste_fiyati * (1 - mal_isk_oran)
        birim_proje = tl_liste_fiyati * (1 - proj_isk_oran)
        birim_satis = tl_liste_fiyati * (1 - sat_isk_oran)
        
        # 3. ÜÇ FARKLI TOPLAM TUTAR (Adet ile çarparak)
        tutar_maliyet = birim_maliyet * guvenli_adet
        tutar_proje = birim_proje * guvenli_adet
        tutar_satis = birim_satis * guvenli_adet
        
        # 4. Proje Genel Toplamlarına Ekle
        toplam_maliyet_tl += tutar_maliyet
        toplam_proje_tl += tutar_proje
        toplam_satis_tl += tutar_satis
        
        rapor.append({
            "pano": pano_turu,
            "malzeme": urun_adi,
            "adet": guvenli_adet,
            
            # GÖRSELDEKİ YENİ ALANLAR İÇİN EKLENENLER:
            "liste_fiyati": guvenli_liste_fiyati,
            
            "iskonto_orani": proj_isk_oran,  # Proje iskontosunu çekiyoruz
            "kur_degeri": guvenli_kur_degeri,
            "para_birimi": para_birimi,
            
            "birim_maliyet_tl": round(birim_maliyet, 2),
            "toplam_maliyet_tl": round(tutar_maliyet, 2),
            "birim_proje_tl": round(birim_proje, 2),
            "toplam_proje_tl": round(tutar_proje, 2),
            "birim_satis_tl": round(birim_satis, 2),
            "toplam_satis_tl": round(tutar_satis, 2)
        })

    return {
        "proje_adi": satirlar[0][0],
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