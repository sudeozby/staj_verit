-- 1. KURLAR TABLOSU
CREATE TABLE IF NOT EXISTS kurlar (
    id SERIAL PRIMARY KEY,
    para_birimi VARCHAR(10) NOT NULL UNIQUE, 
    kur_degeri DECIMAL(10, 4) NOT NULL,
    guncellenme_tarihi DATE DEFAULT CURRENT_DATE
);

-- 2. İSKONTO GRUPLARI (CPQ Motorunun Kalbi)
CREATE TABLE IF NOT EXISTS grup_iskontolar (
    id SERIAL PRIMARY KEY,
    grup_adi VARCHAR(100) UNIQUE NOT NULL,
    maliyet_iskonto DECIMAL(5, 4) DEFAULT 0.0,
    proje_iskonto DECIMAL(5, 4) DEFAULT 0.0,
    satis_iskonto DECIMAL(5, 4) DEFAULT 0.0,
    notlar TEXT
);

-- 3. PROJELER TABLOSU (Python crud.py ile tam uyumlu hale getirildi)
CREATE TABLE IF NOT EXISTS projeler (
    id SERIAL PRIMARY KEY,
    proje_adi VARCHAR(255) NOT NULL,
    musteri VARCHAR(255),
    son_kullanici VARCHAR(255),
    lokasyon VARCHAR(255),
    teklif_konusu TEXT,
    tarih DATE,                     -- 'teklif_tarihi' -> 'tarih' olarak güncellendi
    referans_no VARCHAR(100) UNIQUE,-- 'teklif_referans_no' -> 'referans_no' olarak güncellendi
    hazirlayan VARCHAR(255),        -- 'teklifi_hazirlayan' -> 'hazirlayan' olarak güncellendi
    notlar TEXT                     -- Endpoint'teki notlar() alanını karşılamak için eklendi
);

-- 4. MALZEMELER TABLOSU
CREATE TABLE IF NOT EXISTS malzemeler (
    id SERIAL PRIMARY KEY,
    siparis_kodu VARCHAR(100) UNIQUE NOT NULL,
    urun_adi VARCHAR(255) NOT NULL,
    marka VARCHAR(100),
    urun_grubu VARCHAR(100),
    tedarikci VARCHAR(255),
    liste_fiyati DECIMAL(15, 2) NOT NULL,
    para_birimi VARCHAR(10),
    grup_iskonto_id INT REFERENCES grup_iskontolar(id) ON DELETE SET NULL,
    notlar TEXT
);

-- 5. PROJE PANO LİSTESİ (İskonto, Notlar ve Revizyon Takibi ile)
CREATE TABLE IF NOT EXISTS proje_pano_listesi (
    id SERIAL PRIMARY KEY,
    proje_id INT REFERENCES projeler(id) ON DELETE CASCADE,
    malzeme_id INT REFERENCES malzemeler(id) ON DELETE RESTRICT,
    pano_turu VARCHAR(50) NOT NULL,
    adet INT NOT NULL,
    ozel_iskonto DECIMAL(5, 4) DEFAULT 0.0,
    notlar TEXT,
    eklenme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    degistirildi BOOLEAN DEFAULT FALSE -- Fiyat/Adet değiştiğinde arayüzde sarı yapmak için EKLENDİ
);

-- 6. KULLANICILAR TABLOSU (Giriş Sistemi ve Soft Delete için)
CREATE TABLE IF NOT EXISTS kullanicilar (
    id SERIAL PRIMARY KEY,
    kullanici_adi VARCHAR(100) UNIQUE NOT NULL,
    sifre VARCHAR(100) NOT NULL,
    rol VARCHAR(50) NOT NULL,
    aktif_mi BOOLEAN DEFAULT TRUE -- Ekip üyesini pasife alabilmek için EKLENDİ
);

-- 7. LOG TABLOSU
CREATE TABLE IF NOT EXISTS loglar (
    id SERIAL PRIMARY KEY,
    kullanici_adi VARCHAR(100),
    islem_turu VARCHAR(50),
    detay TEXT,
    tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. MALZEME STOK (ERP Otomasyonu İçin YENİ EKLENDİ)
CREATE TABLE IF NOT EXISTS malzeme_stok (
    id SERIAL PRIMARY KEY,
    malzeme_kodu VARCHAR(100) UNIQUE NOT NULL,
    malzeme_adi VARCHAR(255),
    mevcut_stok INTEGER DEFAULT 0,
    kritik_esik INTEGER DEFAULT 10
);

-- 9. SATIN ALMA TALEPLERİ (ERP Otomasyonu İçin YENİ EKLENDİ)
CREATE TABLE IF NOT EXISTS satin_alma_talepleri (
    id SERIAL PRIMARY KEY,
    proje_id INTEGER REFERENCES projeler(id) ON DELETE CASCADE,
    malzeme_kodu VARCHAR(100) NOT NULL,
    talep_edilen_adet INTEGER NOT NULL,
    durum VARCHAR(50) DEFAULT 'BEKLIYOR',
    olusturulma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);