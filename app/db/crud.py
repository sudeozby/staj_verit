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


def insert_iskonto_grubu(cur, grup):
    """Yeni iskonto grubunu (CPQ Mimarisi) veritabanına ekler."""
    cur.execute("""
        INSERT INTO grup_iskontolar (grup_adi, maliyet_iskonto, proje_iskonto, satis_iskonto)
        VALUES (%s, %s, %s, %s)
    """, (grup.grup_adi, grup.maliyet_iskonto, grup.proje_iskonto, grup.satis_iskonto))

# crud.py içindeki get_kur_id fonksiyonunu bu şekilde düzelt:
def get_kur_id(cur, para_birimi):
    """Girilen para biriminin (Örn: USD) kurlar tablosundaki ID'sini bulur."""
    cur.execute("SELECT id FROM kurlar WHERE para_birimi = %s", (para_birimi,))
    sonuc = cur.fetchone()
    # RealDictCursor kullandığımız için artık sonuc[0] değil, anahtar ismiyle çağırıyoruz:
    return sonuc['id'] if sonuc else None
#Sonradan eklenen sutun adlarıyla eslesmıs duzgun olan proje ekeme fonk
def insert_proje(cur, proje):
    """Gelen Pydantic proje verisini yeni veritabanı mimarisine eksiksiz ekler."""
    cur.execute("""
        INSERT INTO projeler 
        (referans_no, proje_adi, musteri, son_kullanici, lokasyon, teklif_konusu, tarih, hazirlayan, notlar) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        proje.referans_no,         # Arka planda bizim otomatik ürettiğimiz o kusursuz numara
        proje.proje_adi, 
        proje.musteri, 
        proje.son_kullanici, 
        proje.lokasyon, 
        proje.teklif_konusu, 
        proje.teklif_tarihi,       # Vue'dan gelen tarih
        proje.hazirlayan,          # Vue'dan gelen hazırlayan kişi
        proje.notlar               # DBeaver'da yeni açtığımız notlar alanı
    ))

def get_pano_detay_by_id(cur, proje_id, pano_turu):
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
    # RealDictCursor kullanıyorsan direkt döner, normal cursor ise dönüşümü burada yapmalısın
    return cur.fetchall()

def update_pano_malzeme_adet(cur, id, yeni_adet):
    """Yöneticinin düzenlediği adet bilgisini veritabanına kaydeder."""
    cur.execute("UPDATE proje_pano_listesi SET adet = %s WHERE id = %s;", (yeni_adet, id))
    

# app/db/crud.py içerisinde olması gereken HALE:

def get_user_by_username(cur, username):
    """Sorguyu çalıştırır ve RealDictCursor sayesinde doğrudan sözlük (dict) döndürür."""
    cur.execute("SELECT kullanici_adi, sifre, rol FROM kullanicilar WHERE kullanici_adi = %s;", (username,))
    
    # Ekstra bir dönüşüme gerek yok, veriyi direkt dışarı aktarıyoruz.
    return cur.fetchone()

def save_log(cur, username, islem, detay):
    """Veritabanına log kaydı atar. Bağlantı dışarıdan yönetilir."""
    cur.execute(
        "INSERT INTO loglar (kullanici_adi, islem_turu, detay) VALUES (%s, %s, %s);",
        (username, islem, detay)
    )
    # conn.commit() burada değil, main.py tarafında yapılacak!
    
# app/db/crud.py

def fetch_all_logs(cur):
    """Veritabanından tüm logları çeker. Bağlantı dışarıdan yönetilir."""
    cur.execute("SELECT * FROM loglar ORDER BY tarih DESC;")
    return cur.fetchall()

# app/db/crud.py

def fetch_all_users(cur):
    """Sadece kullanıcıları çeker."""
    cur.execute("SELECT id, kullanici_adi, rol FROM kullanicilar;")
    return cur.fetchall()

def add_user(cur, username, password, role):
    """Sadece kullanıcı ekleme sorgusunu çalıştırır."""
    cur.execute(
        "INSERT INTO kullanicilar (kullanici_adi, sifre, rol) VALUES (%s, %s, %s);",
        (username, password, role)
    )

def update_user_password(cur, username, new_password):
    """Sadece şifre güncelleme sorgusunu çalıştırır."""
    cur.execute(
        "UPDATE kullanicilar SET sifre = %s WHERE kullanici_adi = %s;",
        (new_password, username)
    )

# app/db/crud.py

def delete_user(cur, username):
    """Sadece silme sorgusunu çalıştırır."""
    cur.execute("DELETE FROM kullanicilar WHERE kullanici_adi = %s;", (username,))

def fetch_all_projects(cur):
    """Sadece proje listesini çeker."""
    cur.execute("SELECT * FROM projeler;")
    return cur.fetchall()

def fetch_all_malzemeler(cur):
    """Sadece malzeme listesini çeker."""
    cur.execute("SELECT * FROM malzemeler;")
    return cur.fetchall()

# app/db/crud.py



def add_malzeme(cur, malzeme):
    """Pydantic objesinden gelen yeni malzemeyi veritabanına eksiksiz ekler."""
    cur.execute("""
        INSERT INTO malzemeler (siparis_kodu, urun_adi, marka, urun_grubu, tedarikci, liste_fiyati, para_birimi, notlar) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    """, (
        malzeme.siparis_kodu, 
        malzeme.urun_adi, 
        malzeme.marka, 
        malzeme.urun_grubu, 
        malzeme.tedarikci, 
        malzeme.liste_fiyati, 
        malzeme.para_birimi,
        malzeme.notlar # Şemadan gelen notlar alanını SQL'e bağladık
    ))