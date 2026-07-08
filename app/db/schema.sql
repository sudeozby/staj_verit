-- 1. KURLAR TABLOSU
CREATE TABLE kurlar (
    id SERIAL PRIMARY KEY,
    para_birimi VARCHAR(10) NOT NULL UNIQUE, 
    kur_degeri DECIMAL(10, 4) NOT NULL,
    guncellenme_tarihi DATE DEFAULT CURRENT_DATE
);

-- 2. İSKONTO GRUPLARI (CPQ Motorunun Kalbi)
CREATE TABLE grup_iskontolar (
    id SERIAL PRIMARY KEY,
    grup_adi VARCHAR(100) UNIQUE NOT NULL,
    maliyet_iskonto DECIMAL(5, 4) DEFAULT 0.0,
    proje_iskonto DECIMAL(5, 4) DEFAULT 0.0,
    satis_iskonto DECIMAL(5, 4) DEFAULT 0.0,
    notlar TEXT
);

-- 3. PROJELER TABLOSU (Güncellenmiş alanlar)
CREATE TABLE projeler (
    id SERIAL PRIMARY KEY,
    proje_adi VARCHAR(255) NOT NULL,
    musteri VARCHAR(255),
    son_kullanici VARCHAR(255),
    lokasyon VARCHAR(255),
    teklif_konusu TEXT,
    teklif_tarihi DATE,
    teklif_referans_no VARCHAR(100) UNIQUE,
    teklifi_hazirlayan VARCHAR(255)
);

-- 4. MALZEMELER TABLOSU
CREATE TABLE malzemeler (
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

-- 5. PROJE PANO LİSTESİ (İskonto ve Notlar ile)
CREATE TABLE proje_pano_listesi (
    id SERIAL PRIMARY KEY,
    proje_id INT REFERENCES projeler(id) ON DELETE CASCADE,
    malzeme_id INT REFERENCES malzemeler(id) ON DELETE RESTRICT,
    pano_turu VARCHAR(50) NOT NULL,
    adet INT NOT NULL,
    ozel_iskonto DECIMAL(5, 4) DEFAULT 0.0,
    notlar TEXT,
    eklenme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. KULLANICILAR TABLOSU (Giriş Sistemi için)
CREATE TABLE kullanicilar (
    id SERIAL PRIMARY KEY,
    kullanici_adi VARCHAR(100) UNIQUE NOT NULL,
    sifre VARCHAR(100) NOT NULL,
    rol VARCHAR(50) NOT NULL
);

-- 7. LOG TABLOSU
CREATE TABLE loglar (
    id SERIAL PRIMARY KEY,
    kullanici_adi VARCHAR(100),
    islem_turu VARCHAR(50),
    detay TEXT,
    tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);