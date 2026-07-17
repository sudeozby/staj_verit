from fastapi import APIRouter, Header
from typing import Dict, Any
from app.db.session import get_db_session
from app.models.schemas import ProjeEkle, ProjePanoEkle
from app.api.utils import sistem_log_ekle, referans_no_olustur
from app.db import crud
from app.services.pricing_engine import hesapla_pano_maliyeti

router = APIRouter(prefix="/projeler", tags=["Projeler"])

@router.get("/listele")
def projeleri_listele():
    with get_db_session() as cur:
        cur.execute("SELECT id, referans_no, proje_adi, musteri, son_kullanici, lokasyon, teklif_konusu, tarih, hazirlayan, notlar FROM projeler")
        return cur.fetchall()

@router.post("/")
def yeni_proje_ekle(proje: ProjeEkle, islem_yapan: str = Header(default="Bilinmeyen")):
    with get_db_session() as cur:
        proje.referans_no = referans_no_olustur(cur)
        crud.insert_proje(cur, proje)
        sistem_log_ekle(cur, islem_yapan, "PROJE_EKLE", f"Proje eklendi: {proje.proje_adi} ({proje.referans_no})")
    return {"mesaj": "Proje eklendi!", "referans_no": proje.referans_no}

@router.post("/pano-malzeme-ekle")
def projeye_pano_malzemesi_ekle(pano_veri: ProjePanoEkle, islem_yapan: str = Header(default="Bilinmeyen")):
    with get_db_session() as cur:
        # 1. Malzemeyi Projenin Panosuna Ekle
        cur.execute("INSERT INTO proje_pano_listesi (proje_id, malzeme_id, pano_turu, adet, ozel_iskonto, notlar) VALUES (%s, %s, %s, %s, %s, %s)",
                    (pano_veri.proje_id, pano_veri.malzeme_id, pano_veri.pano_turu, pano_veri.adet, 0, None))
        
        # 2. ERP STOK ZEKASI (Doğrudan Malzemeler tablosundan düşüyoruz)
        cur.execute("""
            UPDATE malzemeler 
            SET mevcut_stok = mevcut_stok - %s 
            WHERE id = %s 
            RETURNING siparis_kodu, urun_adi, mevcut_stok, kritik_esik
        """, (pano_veri.adet, pano_veri.malzeme_id))
        
        yeni_stok = cur.fetchone()
        
        if yeni_stok and (yeni_stok['mevcut_stok'] < yeni_stok['kritik_esik']):
            # Stok eşiğin altına düştü! Satın almaya uyarı gönderiyoruz.
            # talep_edilen_adet kısmını 0 yapıyoruz ki satın almacı kendi karar verip kutucuğa yazsın.
            cur.execute("""
                INSERT INTO satin_alma_talepleri (proje_id, malzeme_kodu, talep_edilen_adet, durum) 
                VALUES (%s, %s, 0, 'STOK_UYARISI')
            """, (pano_veri.proje_id, yeni_stok['siparis_kodu']))
            
            sistem_log_ekle(cur, "ERP_SİSTEMİ", "STOK_ALARM", f"{yeni_stok['urun_adi']} kritik stok! (Kalan: {yeni_stok['mevcut_stok']})")

        sistem_log_ekle(cur, islem_yapan, "PANO_MALZEME_EKLE", f"Pano: {pano_veri.pano_turu}, Miktar: {pano_veri.adet}")
        
    return {"mesaj": "Malzeme atandı ve stok güncellendi."}

@router.put("/pano-malzeme-guncelle/{kayit_id}")
def pano_malzeme_guncelle(kayit_id: int, yeni_veri: Dict[str, Any], islem_yapan: str = Header(default="Sistem", alias="islem-yapan")):
    if not yeni_veri: 
        return {"mesaj": "Veri yok."}
    
    # Güvenlik ve İsim Eşleştirme (SQL Injection Koruması)
    izin_verilenler = {
        "adet": "adet", 
        "pano": "pano_turu", 
        "iskonto_orani": "ozel_iskonto", 
        "notlar": "notlar", 
        "liste_fiyati": "liste_fiyati"
    }
    
    guncellenecekler = {}
    for k, v in yeni_veri.items():
        if k in izin_verilenler:
            guncellenecekler[izin_verilenler[k]] = v
            
    if not guncellenecekler:
        return {"mesaj": "Geçerli veri yok."}

    with get_db_session() as cur:
        # Eski değerleri oku (Loglama için)
        sutun_isimleri = ", ".join(guncellenecekler.keys())
        cur.execute(f"SELECT {sutun_isimleri} FROM proje_pano_listesi WHERE id = %s", (kayit_id,))
        eski_degerler = cur.fetchone()

        # Güncelleme sorgusunu hazırla
        sutunlar, degerler = [], []
        for a, d in guncellenecekler.items():
            sutunlar.append(f"{a} = %s")
            degerler.append(d)
        
        sutunlar.append("degistirildi = TRUE")
        degerler.append(kayit_id)
        
        cur.execute(f"UPDATE proje_pano_listesi SET {', '.join(sutunlar)} WHERE id = %s", tuple(degerler))

        # Senin vizyonun olan hücre değişiklik loglarını sisteme kaydet
        if eski_degerler:
            for i, (a, y_d) in enumerate(guncellenecekler.items()):
                e_d = eski_degerler[a] if isinstance(eski_degerler, dict) else eski_degerler[i]
                if str(e_d) != str(y_d):
                    cur.execute("INSERT INTO loglar (kullanici_adi, islem_turu, detay) VALUES (%s, %s, %s)", 
                                (islem_yapan, "HÜCRE_GÜNCELLEME", f"ID {kayit_id}: '{a}' {e_d} -> {y_d}"))
                    
    return {"mesaj": "Güncellendi."}

@router.get("/{proje_id}/maliyet-raporu")
def proje_maliyet_raporu_getir(proje_id: int):
    with get_db_session() as cur:
        cur.execute("""
            SELECT 
                pl.degistirildi, pl.id, p.proje_adi, pl.pano_turu, m.urun_adi, pl.adet, 
                m.liste_fiyati, COALESCE(k.kur_degeri, 1.0) as kur_degeri, m.para_birimi, 
                g.maliyet_iskonto, g.proje_iskonto, g.satis_iskonto, m.marka, m.siparis_kodu,
                pl.ozel_iskonto, pl.notlar
            FROM proje_pano_listesi pl
            JOIN projeler p ON pl.proje_id = p.id
            JOIN malzemeler m ON pl.malzeme_id = m.id
            LEFT JOIN kurlar k ON m.para_birimi = k.para_birimi
            LEFT JOIN grup_iskontolar g ON m.grup_iskonto_id = g.id
            WHERE p.id = %s
            ORDER BY pl.pano_turu, m.urun_adi
        """, (proje_id,))
        satirlar = cur.fetchall()

    if not satirlar: 
        return {"proje_adi": "Yeni Proje", "genel_toplamlar": {"maliyet_tl": 0, "proje_tl": 0, "satis_tl": 0}, "detaylar": []}

    rapor, toplamlar = [], {"maliyet": 0.0, "proje": 0.0, "satis": 0.0}
    for satir in satirlar:
        aktif_iskonto = satir['ozel_iskonto'] if satir['ozel_iskonto'] is not None else (satir['proje_iskonto'] or 0.0)

        mal = hesapla_pano_maliyeti(satir['liste_fiyati'], satir['maliyet_iskonto'], satir['kur_degeri'], satir['adet'])
        pro = hesapla_pano_maliyeti(satir['liste_fiyati'], aktif_iskonto, satir['kur_degeri'], satir['adet'])
        sat = hesapla_pano_maliyeti(satir['liste_fiyati'], satir['satis_iskonto'], satir['kur_degeri'], satir['adet'])
        
        toplamlar["maliyet"] += mal['satir_toplami']
        toplamlar["proje"] += pro['satir_toplami']
        toplamlar["satis"] += sat['satir_toplami']
        
        rapor.append({
            "id": satir['id'], 
            "degistirildi": satir['degistirildi'], 
            "pano": satir['pano_turu'], 
            "malzeme": satir['urun_adi'], 
            "adet": satir['adet'], 
            "liste_fiyati": float(satir['liste_fiyati']), 
            "kur_degeri": float(satir['kur_degeri']), 
            "para_birimi": satir['para_birimi'], 
            "marka": satir['marka'] or "-", 
            "siparis_kodu": satir['siparis_kodu'] or "-",
            "iskonto_orani": float(aktif_iskonto),
            "notlar": satir['notlar'],
            
            "birim_maliyet_tl": mal['net_fiyat_tl'], 
            "toplam_maliyet_tl": mal['satir_toplami'],
            "birim_proje_tl": pro['net_fiyat_tl'], 
            "toplam_proje_tl": pro['satir_toplami'],
            "birim_satis_tl": sat['net_fiyat_tl'], 
            "toplam_satis_tl": sat['satir_toplami']
        })
        
    return {"proje_adi": satirlar[0]['proje_adi'], "genel_toplamlar": {k: round(v, 2) for k, v in toplamlar.items()}, "detaylar": rapor}

@router.get("/{proje_id}/malzemeler")
def proje_malzemelerini_getir(proje_id: int):
    with get_db_session() as cur:
        cur.execute("""
            SELECT 
                ppl.id, 
                ppl.pano_turu as pano, 
                ppl.adet, 
                ppl.malzeme_id, 
                m.urun_adi as malzeme, 
                m.siparis_kodu,
                m.marka
            FROM proje_pano_listesi ppl
            JOIN malzemeler m ON ppl.malzeme_id = m.id
            WHERE ppl.proje_id = %s
            ORDER BY ppl.pano_turu, m.urun_adi
        """, (proje_id,))
        return [dict(row) for row in cur.fetchall()]