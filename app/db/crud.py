# app/db/crud.py

def get_all_projeler(cur):
    """Veritabanındaki tüm projeleri çeker. (RealDictCursor sayesinde dönüşüm otomatik)"""
    cur.execute("SELECT id, referans_no, proje_adi, musteri, lokasyon, tarih FROM projeler ORDER BY id DESC;")
    return cur.fetchall() # Döngüye gerek kalmadı, sözlük listesi hazır!

def insert_iskonto_grubu(cur, grup):
    """Yeni iskonto grubunu (CPQ Mimarisi) veritabanına ekler."""
    cur.execute("""
        INSERT INTO grup_iskontolar (grup_adi, maliyet_iskonto, proje_iskonto, satis_iskonto, notlar)
        VALUES (%s, %s, %s, %s, %s)
    """, (grup.grup_adi, grup.maliyet_iskonto, grup.proje_iskonto, grup.satis_iskonto, grup.notlar))

def get_kur_id(cur, para_birimi):
    """Girilen para biriminin (Örn: USD) kurlar tablosundaki ID'sini bulur."""
    cur.execute("SELECT id FROM kurlar WHERE para_birimi = %s", (para_birimi,))
    sonuc = cur.fetchone()
    return sonuc['id'] if sonuc else None

def insert_proje(cur, proje):
    """Gelen Pydantic proje verisini yeni veritabanı mimarisine eksiksiz ekler."""
    cur.execute("""
        INSERT INTO projeler 
        (referans_no, proje_adi, musteri, son_kullanici, lokasyon, teklif_konusu, tarih, hazirlayan, notlar) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        proje.referans_no,         
        proje.proje_adi, 
        proje.musteri, 
        proje.son_kullanici, 
        proje.lokasyon, 
        proje.teklif_konusu, 
        proje.teklif_tarihi,       
        proje.hazirlayan,          
        proje.notlar               
    ))

def get_pano_detay_by_id(cur, proje_id, pano_turu=None):
    """Proje ve pano türüne göre malzeme listesini çeker."""
    query = """
        SELECT p.id, m.urun_adi, m.siparis_kodu, p.adet, m.liste_fiyati
        FROM proje_pano_listesi p
        JOIN malzemeler m ON p.malzeme_id = m.id
        WHERE p.proje_id = %s
    """
    params = [proje_id]
    
    if pano_turu and pano_turu != "Tüm Panoları Getir":
        query += " AND p.pano_turu = %s"
        params.append(pano_turu)
        
    cur.execute(query, tuple(params))
    return cur.fetchall()

def update_pano_malzeme_adet(cur, id, yeni_adet):
    """Yöneticinin düzenlediği adet bilgisini veritabanına kaydeder."""
    cur.execute("UPDATE proje_pano_listesi SET adet = %s, degistirildi = TRUE WHERE id = %s;", (yeni_adet, id))

# --- KULLANICI İŞLEMLERİ ---

def get_user_by_username(cur, username):
    """Kullanıcıyı çeker."""
    cur.execute("SELECT id, kullanici_adi, sifre, rol, aktif_mi FROM kullanicilar WHERE kullanici_adi = %s;", (username,))
    return cur.fetchone()

def fetch_all_users(cur):
    """Sadece kullanıcıları çeker."""
    cur.execute("SELECT id, kullanici_adi, rol, aktif_mi FROM kullanicilar ORDER BY id ASC;")
    return cur.fetchall()

def add_user(cur, username, password, role):
    """Kullanıcı ekleme sorgusunu çalıştırır."""
    cur.execute(
        "INSERT INTO kullanicilar (kullanici_adi, sifre, rol, aktif_mi) VALUES (%s, %s, %s, TRUE);",
        (username, password, role)
    )

def update_user_password(cur, username, new_password):
    """Şifre güncelleme sorgusunu çalıştırır."""
    cur.execute(
        "UPDATE kullanicilar SET sifre = %s WHERE kullanici_adi = %s;",
        (new_password, username)
    )

def delete_user(cur, uye_id):
    """Kullanıcıyı SİLMEZ, ilişkilerin bozulmaması için PASİFE ALIR (Soft Delete)."""
    cur.execute("UPDATE kullanicilar SET aktif_mi = FALSE WHERE id = %s;", (uye_id,))

# --- MALZEME VE LOG İŞLEMLERİ ---

def fetch_all_malzemeler(cur):
    """Sadece malzeme listesini çeker."""
    cur.execute("SELECT id, siparis_kodu, urun_adi, marka, liste_fiyati, para_birimi FROM malzemeler ORDER BY id DESC;")
    return cur.fetchall()

def add_malzeme(cur, malzeme):
    """Pydantic objesinden gelen yeni malzemeyi, iskonto grubu dahil veritabanına eksiksiz ekler."""
    cur.execute("""
        INSERT INTO malzemeler (siparis_kodu, urun_adi, marka, urun_grubu, tedarikci, liste_fiyati, para_birimi, grup_iskonto_id, notlar) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
    """, (
        malzeme.siparis_kodu, 
        malzeme.urun_adi, 
        malzeme.marka, 
        malzeme.urun_grubu, 
        malzeme.tedarikci, 
        malzeme.liste_fiyati, 
        malzeme.para_birimi,
        malzeme.grup_iskonto_id, # BU EKSİKTİ, EKLENDİ!
        malzeme.notlar 
    ))

def fetch_all_logs(cur):
    """Veritabanından tüm logları çeker."""
    cur.execute("SELECT * FROM loglar ORDER BY id DESC LIMIT 200;")
    return cur.fetchall()

# Not: save_log fonksiyonunu sildik çünkü onu "app/api/utils.py" içine 'sistem_log_ekle' olarak merkezi bir yapıya taşıdık!