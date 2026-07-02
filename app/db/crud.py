# app/db/crud.py

def get_all_projeler(cur):
    """Veritabanındaki tüm projeleri çeker ve sözlük (dict) listesi olarak döndürür."""
    cur.execute("SELECT id, proje_adi, musteri, lokasyon FROM projeler;")
    kayitlar = cur.fetchall()
    
    projeler_listesi = []
    for kayit in kayitlar:
        projeler_listesi.append({
            "id": kayit[0],
            "proje_adi": kayit[1],
            "musteri": kayit[2],
            "lokasyon": kayit[3]
        })
    return projeler_listesi

def insert_proje(cur, proje):
    """Gelen proje verisini veritabanına ekler."""
    cur.execute("""
        INSERT INTO projeler (proje_adi, musteri, son_kullanici, lokasyon, teklif_referans_no) 
        VALUES (%s, %s, %s, %s, %s)
    """, (proje.proje_adi, proje.musteri, proje.son_kullanici, proje.lokasyon, proje.teklif_referans_no))

def insert_iskonto_grubu(cur, grup):
    """Yeni iskonto grubunu (CPQ Mimarisi) veritabanına ekler."""
    cur.execute("""
        INSERT INTO grup_iskontolar (grup_adi, maliyet_iskonto, proje_iskonto, satis_iskonto)
        VALUES (%s, %s, %s, %s)
    """, (grup.grup_adi, grup.maliyet_iskonto, grup.proje_iskonto, grup.satis_iskonto))

def get_kur_id(cur, para_birimi):
    """Girilen para biriminin (Örn: USD) kurlar tablosundaki ID'sini bulur."""
    cur.execute("SELECT id FROM kurlar WHERE para_birimi = %s", (para_birimi,))
    sonuc = cur.fetchone()
    return sonuc[0] if sonuc else None

def insert_malzeme(cur, malzeme, para_birimi_id):
    """Yeni malzemeyi, bağlı olduğu kur ID'si ve iskonto grubuyla birlikte ekler."""
    cur.execute("""
        INSERT INTO malzemeler (siparis_kodu, urun_adi, marka, urun_grubu, tedarikci, liste_fiyati, para_birimi_id, grup_iskonto_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (malzeme.siparis_kodu, malzeme.urun_adi, malzeme.marka, malzeme.urun_grubu, 
          malzeme.tedarikci, malzeme.liste_fiyati, para_birimi_id, malzeme.grup_iskonto_id))