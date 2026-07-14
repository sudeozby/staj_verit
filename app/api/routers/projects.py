from fastapi import APIRouter, Header
from app.db.session import get_db_session
from app.models.schemas import ProjeEkle, ProjePanoEkle
from app.api.utils import sistem_log_ekle, referans_no_olustur
from app.services.pricing_engine import hesapla_pano_maliyeti
from app.db import crud

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
        cur.execute("INSERT INTO proje_pano_listesi (proje_id, malzeme_id, pano_turu, adet, ozel_iskonto, notlar) VALUES (%s, %s, %s, %s, %s, %s)",
                    (pano_veri.proje_id, pano_veri.malzeme_id, pano_veri.pano_turu, pano_veri.adet, 0, None))
        
        # ERP STOK ZEKASI
        cur.execute("SELECT siparis_kodu, urun_adi FROM malzemeler WHERE id = %s", (pano_veri.malzeme_id,))
        m = cur.fetchone()
        if m and m['siparis_kodu']:
            cur.execute("INSERT INTO malzeme_stok (malzeme_kodu, malzeme_adi, mevcut_stok, kritik_esik) VALUES (%s, %s, 0, 10) ON CONFLICT DO NOTHING", (m['siparis_kodu'], m['urun_adi']))
            cur.execute("UPDATE malzeme_stok SET mevcut_stok = mevcut_stok - %s WHERE malzeme_kodu = %s RETURNING mevcut_stok, kritik_esik", (pano_veri.adet, m['siparis_kodu']))
            stok = cur.fetchone()
            if stok and (stok['mevcut_stok'] < stok['kritik_esik']):
                cur.execute("INSERT INTO satin_alma_talepleri (proje_id, malzeme_kodu, talep_edilen_adet, durum) VALUES (%s, %s, %s, 'BEKLIYOR')", (pano_veri.proje_id, m['siparis_kodu'], pano_veri.adet))
                sistem_log_ekle(cur, "ERP_SİSTEMİ", "OTOMATİK_SİPARİŞ", f"{m['urun_adi']} stoku kritik. Sipariş açıldı.")

        sistem_log_ekle(cur, islem_yapan, "PANO_MALZEME_EKLE", f"Pano: {pano_veri.pano_turu}, Miktar: {pano_veri.adet}")
    return {"mesaj": "Atandı ve stok güncellendi ✅"}

@router.put("/pano-malzeme-guncelle/{malzeme_id}")
def pano_malzeme_guncelle(malzeme_id: int, yeni_veri: dict):
    guncellenecekler = {k: v for k, v in yeni_veri.items() if k not in ["id"]}
    if not guncellenecekler: return {"mesaj": "Veri yok."}
    with get_db_session() as cur:
        sutun_isimleri = ", ".join(guncellenecekler.keys())
        cur.execute(f"SELECT {sutun_isimleri} FROM proje_pano_listesi WHERE id = %s", (malzeme_id,))
        eski_degerler = cur.fetchone()

        sutunlar, degerler = [], []
        for a, d in guncellenecekler.items():
            sutunlar.append(f"{a} = %s")
            degerler.append(d)
        
        sutunlar.append("degistirildi = TRUE")
        degerler.append(malzeme_id)
        cur.execute(f"UPDATE proje_pano_listesi SET {', '.join(sutunlar)} WHERE id = %s", tuple(degerler))

        if eski_degerler:
            for i, (a, y_d) in enumerate(guncellenecekler.items()):
                e_d = eski_degerler[a] if isinstance(eski_degerler, dict) else eski_degerler[i]
                if str(e_d) != str(y_d):
                    cur.execute("INSERT INTO loglar (kullanici_adi, islem_turu, detay) VALUES (%s, %s, %s)", ("Yönetici", "HÜCRE_GÜNCELLEME", f"ID {malzeme_id}: '{a}' {e_d} -> {y_d}"))
    return {"mesaj": "Güncellendi."}

@router.get("/{proje_id}/maliyet-raporu")
def proje_maliyet_raporu_getir(proje_id: int):
    with get_db_session() as cur:
        cur.execute("""
            SELECT pl.degistirildi, pl.id, p.proje_adi, pl.pano_turu, m.urun_adi, SUM(pl.adet) as adet, m.liste_fiyati, COALESCE(k.kur_degeri, 1.0) as kur_degeri, m.para_birimi, g.maliyet_iskonto, g.proje_iskonto, g.satis_iskonto, m.marka, m.siparis_kodu
            FROM proje_pano_listesi pl
            JOIN projeler p ON pl.proje_id = p.id
            JOIN malzemeler m ON pl.malzeme_id = m.id
            LEFT JOIN kurlar k ON m.para_birimi = k.para_birimi
            LEFT JOIN grup_iskontolar g ON m.grup_iskonto_id = g.id
            WHERE p.id = %s
            GROUP BY pl.id, pl.degistirildi, p.proje_adi, pl.pano_turu, m.urun_adi, m.liste_fiyati, k.kur_degeri, m.para_birimi, g.maliyet_iskonto, g.proje_iskonto, g.satis_iskonto, m.marka, m.siparis_kodu
        """, (proje_id,))
        satirlar = cur.fetchall()

    if not satirlar: return {"proje_adi": "Yeni Proje", "genel_toplamlar": {"maliyet_tl": 0, "proje_tl": 0, "satis_tl": 0}, "detaylar": []}

    rapor, toplamlar = [], {"maliyet": 0.0, "proje": 0.0, "satis": 0.0}
    for satir in satirlar:
        mal = hesapla_pano_maliyeti(satir['liste_fiyati'], satir['maliyet_iskonto'], satir['kur_degeri'], satir['adet'])
        pro = hesapla_pano_maliyeti(satir['liste_fiyati'], satir['proje_iskonto'], satir['kur_degeri'], satir['adet'])
        sat = hesapla_pano_maliyeti(satir['liste_fiyati'], satir['satis_iskonto'], satir['kur_degeri'], satir['adet'])
        toplamlar["maliyet"] += mal['satir_toplami']
        toplamlar["proje"] += pro['satir_toplami']
        toplamlar["satis"] += sat['satir_toplami']
        rapor.append({
            "id": satir['id'], "degistirildi": satir['degistirildi'], "pano": satir['pano_turu'], "malzeme": satir['urun_adi'], "adet": satir['adet'], "liste_fiyati": float(satir['liste_fiyati']), "kur_degeri": float(satir['kur_degeri']), "para_birimi": satir['para_birimi'], "marka": satir['marka'] or "-", "siparis_kodu": satir['siparis_kodu'] or "-",
            "birim_maliyet_tl": mal['net_fiyat_tl'], "toplam_maliyet_tl": mal['satir_toplami'],
            "birim_proje_tl": pro['net_fiyat_tl'], "toplam_proje_tl": pro['satir_toplami'],
            "birim_satis_tl": sat['net_fiyat_tl'], "toplam_satis_tl": sat['satir_toplami']
        })
    return {"proje_adi": satirlar[0]['proje_adi'], "genel_toplamlar": {k: round(v, 2) for k, v in toplamlar.items()}, "detaylar": rapor}