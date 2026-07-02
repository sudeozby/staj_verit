#business logic layer(veri işleyen yer)

#birden fazla dosya açtık sınıflama oluşturduk ki her table gelip main.py da yığılmasın
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from database import get_db_connection

import urllib.request
import xml.etree.ElementTree as ET

# FastAPI uygulamasını başlat
app = FastAPI(title="Envanter ve Proje Takip API")

@app.get("/")
def ana_sayfa():
    return {"mesaj": "Sistem başarıyla çalışıyor. Arayüz buradan veri çekebilir."}

@app.get("/projeler")
def projeleri_getir():
    """
    Veritabanındaki tüm projeleri çeker ve arayüze liste olarak gönderir.
    """
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Veritabanına bağlanılamadı.")
    
    try:
        cur = conn.cursor()
        # Projeler tablosundaki verileri çek
        cur.execute("SELECT id, proje_adi, musteri, lokasyon FROM projeler;")
        kayitlar = cur.fetchall()
        
        # Arayüzün anlayacağı JSON (sözlük) formatına çevir
        projeler_listesi = []
        for kayit in kayitlar:
            projeler_listesi.append({
                "id": kayit[0],
                "proje_adi": kayit[1],
                "musteri": kayit[2],
                "lokasyon": kayit[3]
            })
            
        cur.close()
        conn.close()
        return {"projeler": projeler_listesi}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    # Arayüzden gelecek verilerin şablonunu belirliyoruz
class ProjeEkle(BaseModel):
    proje_adi: str
    musteri: str
    son_kullanici: str = None
    lokasyon: str = None
    teklif_referans_no: str = None

@app.post("/projeler")
def yeni_proje_ekle(proje: ProjeEkle):
    """
    Arayüzden gelen yeni proje bilgilerini veritabanına kaydeder.
    """
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Veritabanına bağlanılamadı.")
    
    try:
        cur = conn.cursor()
        # %s parametreleri ile verileri güvenli bir şekilde SQL'e yerleştiriyoruz
        cur.execute("""
            INSERT INTO projeler (proje_adi, musteri, son_kullanici, lokasyon, teklif_referans_no) 
            VALUES (%s, %s, %s, %s, %s)
        """, (proje.proje_adi, proje.musteri, proje.son_kullanici, proje.lokasyon, proje.teklif_referans_no))
        
        conn.commit() # Değişiklikleri veritabanına kalıcı olarak yaz
        cur.close()
        conn.close()
        
        return {"mesaj": f"'{proje.proje_adi}' adlı proje başarıyla eklendi!"}
        
    except Exception as e:
        conn.rollback() # Hata olursa işlemi geri al
        raise HTTPException(status_code=500, detail=f"Kayıt eklenirken hata oluştu: {e}")
    
    #kur bilgizi cekmek için merkez bankasından
@app.post("/kurlar/tcmb-guncelle")
def tcmb_kurlarını_guncelle():
    """
    Merkez Bankası (TCMB) web sitesine bağlanarak güncel USD ve EUR satış kurlarını otomatik çeker,
    veritabanındaki kurlar tablosuna kaydeder veya varsa günceller.
    """
    try:
        # 1. TCMB'nin her gün güncellenen resmi XML adresine istek atıyoruz
        url = "https://www.tcmb.gov.tr/kurlar/today.xml"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
        
        # 2. Gelen XML verisini Python'ın anlayacağı bir ağaç yapısına çeviriyoruz
        root = ET.fromstring(xml_data)
        
        guncellenen_kurlar = []
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Veritabanı bağlantısı kurulamadı.")
            
        cur = conn.cursor()
        
        # 3. XML içindeki tüm 'Currency' (Döviz) etiketlerini tek tek dönüyoruz
        for currency in root.findall('Currency'):
            kod = currency.get('CurrencyCode') # USD, EUR, GBP vb.
            
            # Sadece bizim işimize yarayan USD ve EUR kurlarını ayıklıyoruz
            if kod in ['USD', 'EUR']:
                # Döviz Satış (ForexSelling) değerini alıyoruz
                satis_kuru = currency.find('ForexSelling').text
                
                if satis_kuru:
                    kur_float = float(satis_kuru)
                    
                    # 4. Veritabanına akıllıca yazıyoruz (Mühendislik dokunuşu: ON CONFLICT)
                    # Eğer o kur veritabanında hiç yoksa INSERT (ekleme) yapar.
                    # Eğer daha önce eklenmişse (UNIQUE hatası vermez), DO UPDATE diyerek değerini ve tarihini bugüne günceller.
                    cur.execute("""
                        INSERT INTO kurlar (para_birimi, kur_degeri, guncellenme_tarihi)
                        VALUES (%s, %s, CURRENT_DATE)
                        ON CONFLICT (para_birimi) 
                        DO UPDATE SET kur_degeri = EXCLUDED.kur_degeri, guncellenme_tarihi = CURRENT_DATE;
                    """, (kod, kur_float))
                    
                    guncellenen_kurlar.append(f"{kod}: {kur_float} TL")
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            "mesaj": "Merkez Bankası kurları başarıyla çekildi ve veritabanı güncellendi!",
            "guncellenen_veriler": guncellenen_kurlar
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TCMB kurları çekilirken hata oluştu: {e}")
    
    # --- MALZEME İŞLEMLERİ ---

class MalzemeEkle(BaseModel):
    siparis_kodu: str
    urun_adi: str
    marka: str = None
    urun_grubu: str = None
    tedarikci: str = None
    liste_fiyati: float
    para_birimi: str  # Kullanıcı arayüzden "USD" veya "EUR" vb. girecek
    iskonto_orani: float = 0.0

@app.post("/malzemeler")
def yeni_malzeme_ekle(malzeme: MalzemeEkle):
    """Yeni bir malzeme ekler. Para birimini kurlar tablosundan otomatik eşleştirir."""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Veritabanı bağlantısı kurulamadı.")
    
    try:
        cur = conn.cursor()
        
        # 1. Girilen para biriminin (örn: USD) veritabanındaki ID'sini bul (Akıllı Eşleştirme)
        cur.execute("SELECT id FROM kurlar WHERE para_birimi = %s", (malzeme.para_birimi,))
        kur_sonuc = cur.fetchone()
        
        if not kur_sonuc:
            raise HTTPException(status_code=400, detail=f"'{malzeme.para_birimi}' kurlar tablosunda bulunamadı. Lütfen önce TCMB kurlarını çekin.")
            
        para_birimi_id = kur_sonuc[0]
        
        # 2. Malzemeyi veritabanına kaydet
        cur.execute("""
            INSERT INTO malzemeler (siparis_kodu, urun_adi, marka, urun_grubu, tedarikci, liste_fiyati, para_birimi_id, iskonto_orani)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (malzeme.siparis_kodu, malzeme.urun_adi, malzeme.marka, malzeme.urun_grubu, malzeme.tedarikci, malzeme.liste_fiyati, para_birimi_id, malzeme.iskonto_orani))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {"mesaj": f"'{malzeme.urun_adi}' envantere başarıyla eklendi!"}
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Malzeme eklenirken hata: {e}")

@app.get("/malzemeler")
def tum_malzemeleri_getir():
    """Veritabanındaki tüm malzemeleri kurlarıyla birlikte getirir."""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Veritabanı bağlantısı kurulamadı.")
    
    try:
        cur = conn.cursor()
        # SQL JOIN ile iki tabloyu birleştiriyoruz (Malzemeler + Kur İsimleri)
        cur.execute("""
            SELECT m.siparis_kodu, m.urun_adi, m.marka, m.liste_fiyati, k.para_birimi 
            FROM malzemeler m
            JOIN kurlar k ON m.para_birimi_id = k.id
        """)
        malzemeler = cur.fetchall()
        
        sonuclar = []
        for m in malzemeler:
            sonuclar.append({
                "siparis_kodu": m[0],
                "urun_adi": m[1],
                "marka": m[2],
                "liste_fiyati": m[3],
                "para_birimi": m[4]
            })
            
        cur.close()
        conn.close()
        return {"malzemeler": sonuclar}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Veri çekilirken hata: {e}")
    
    # --- PROJE PANO MALZEME LİSTESİ İŞLEMLERİ ---

class PanoMalzemeEkle(BaseModel):
    proje_id: int
    malzeme_id: int
    pano_turu: str  # Örn: ADP, MCC, Kontrol Panosu vb.
    adet: int

@app.post("/proje-pano-listesi")
def projeye_malzeme_ekle(item: PanoMalzemeEkle):
    """Bir projenin panosuna envanterden malzeme ve adet bilgisi bağlar."""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Veritabanı bağlantısı kurulamadı.")
    
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO proje_pano_listesi (proje_id, malzeme_id, pano_turu, adet)
            VALUES (%s, %s, %s, %s)
        """, (item.proje_id, item.malzeme_id, item.pano_turu, item.adet))
        
        conn.commit()
        cur.close()
        conn.close()
        return {"mesaj": "Malzeme başarıyla projeye ve panoya eklendi!"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Bağlantı eklenirken hata: {e}")

@app.get("/proje-pano-listesi/{proje_id}")
def projenin_malzeme_listesini_getir(proje_id: int):
    """Belirli bir projenin içindeki tüm panoları, malzemeleri ve toplam maliyet özetini getirir."""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Veritabanı bağlantısı kurulamadı.")
    
    try:
        cur = conn.cursor()
        # Mühendislik Şovu: 3 Farklı tabloyu (Pano Listesi, Projeler, Malzemeler) JOIN ile tek sorguda birleştiriyoruz
        cur.execute("""
            SELECT p.proje_adi, m.urun_adi, m.siparis_kodu, ppl.pano_turu, ppl.adet, m.liste_fiyati
            FROM proje_pano_listesi ppl
            JOIN projeler p ON ppl.proje_id = p.id
            JOIN malzemeler m ON ppl.malzeme_id = m.id
            WHERE ppl.proje_id = %s
        """, (proje_id,))
        
        veriler = cur.fetchall()
        
        listem = []
        for v in veriler:
            listem.append({
                "proje_adi": v[0],
                "urun_adi": v[1],
                "siparis_kodu": v[2],
                "pano_turu": v[3],
                "adet": v[4],
                "birim_fiyat": v[5],
                "toplam_fiyat": v[4] * v[5] # Kod içinde ufak bir hesaplama yapıp arayüze kolaylık sağlıyoruz
            })
            
        cur.close()
        conn.close()
        return {"proje_id": {proje_id}, "pano_malzemeleri": listem}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Liste çekilirken hata oluştu: {e}")
    
    # --- GÜNCELLEME VE SİLME İŞLEMLERİ (UPDATE & DELETE) ---

class FiyatGuncelle(BaseModel):
    liste_fiyati: float
    iskonto_orani: float = 0.0

@app.put("/malzemeler/{malzeme_id}")
def malzeme_fiyat_guncelle(malzeme_id: int, guncel_veri: FiyatGuncelle):
    """Mevcut bir malzemenin fiyatını ve iskonto oranını günceller."""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Veritabanı bağlantısı kurulamadı.")
    
    try:
        cur = conn.cursor()
        # UPDATE komutu ile sadece belirttiğimiz ID'ye sahip ürünün fiyatlarını değiştiriyoruz
        cur.execute("""
            UPDATE malzemeler 
            SET liste_fiyati = %s, iskonto_orani = %s 
            WHERE id = %s
        """, (guncel_veri.liste_fiyati, guncel_veri.iskonto_orani, malzeme_id))
        
        # Eğer veritabanında öyle bir ID yoksa (cur.rowcount 0 dönerse) arayüze hata fırlat
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Bu ID'ye sahip bir malzeme bulunamadı.")
            
        conn.commit()
        cur.close()
        conn.close()
        
        return {"mesaj": f"ID'si {malzeme_id} olan malzemenin fiyatı başarıyla güncellendi!"}
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Güncelleme işlemi sırasında hata oluştu: {e}")


@app.delete("/malzemeler/{malzeme_id}")
def malzeme_sil(malzeme_id: int):
    """Yanlış eklenen veya envanterden kalkan bir malzemeyi tamamen siler."""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Veritabanı bağlantısı kurulamadı.")
    
    try:
        cur = conn.cursor()
        # DELETE komutu ile belirtilen ID'yi veritabanından kazıyoruz
        cur.execute("DELETE FROM malzemeler WHERE id = %s", (malzeme_id,))
        
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Silinecek malzeme bulunamadı.")
            
        conn.commit()
        cur.close()
        conn.close()
        
        return {"mesaj": f"ID'si {malzeme_id} olan malzeme envanterden kalıcı olarak silindi!"}
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Silme işlemi sırasında hata: {e}")