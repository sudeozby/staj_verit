# app/api/utils.py
from datetime import datetime

def sistem_log_ekle(cur, kullanici, islem, detay):
    """Tüm sistemin ortak loglama motoru"""
    try:
        su_an = datetime.now()
        sql = "INSERT INTO loglar (kullanici_adi, islem_turu, detay, tarih) VALUES (%s, %s, %s, %s)"
        cur.execute(sql, (kullanici, islem, detay, su_an))
    except Exception as e:
        print("Log kaydedilemedi:", e)

def referans_no_olustur(cur):
    """Otomatik TEMKON_OFFER numarası üretici"""
    bugun_str = datetime.now().strftime("%d%m%y") 
    baslangic_sablonu = f"TEMKON_OFFER_{bugun_str}_"
    
    cur.execute("""
        SELECT referans_no FROM projeler 
        WHERE referans_no LIKE %s ORDER BY id DESC LIMIT 1
    """, (baslangic_sablonu + '%',))
    son_kayit = cur.fetchone()
    
    if son_kayit and son_kayit['referans_no']:
        parcalar = son_kayit['referans_no'].split('_')
        yeni_numara = int(parcalar[3]) + 1
    else:
        yeni_numara = 1
        
    return f"{baslangic_sablonu}{yeni_numara:02d}"