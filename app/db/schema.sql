-- datalayer (veri saklayan yer) - GÜNCELLENMİŞ CPQ MİMARİSİ
-- iskonto eklendi
-- 1. KURLAR TABLOSU
CREATE TABLE kurlar (
    id SERIAL PRIMARY KEY,
    para_birimi VARCHAR(10) NOT NULL UNIQUE, 
    kur_degeri DECIMAL(10, 4) NOT NULL,      
    guncellenme_tarihi DATE DEFAULT CURRENT_DATE
);

-- 2. PROJELER TABLOSU
CREATE TABLE projeler (
    id SERIAL PRIMARY KEY,
    proje_adi VARCHAR(255) NOT NULL,
    musteri VARCHAR(255) NOT NULL,
    son_kullanici VARCHAR(255),
    lokasyon VARCHAR(255),
    teklif_referans_no VARCHAR(100) UNIQUE,
    olusturulma_tarihi DATE DEFAULT CURRENT_DATE
);

-- 3. YENİ: İSKONTO GRUPLARI TABLOSU (Hesaplama Motorunun Kalbi)
CREATE TABLE grup_iskontolar (
    id SERIAL PRIMARY KEY,
    grup_adi VARCHAR(100) UNIQUE NOT NULL,
    maliyet_iskonto DECIMAL(5, 4) DEFAULT 0.0000,
    proje_iskonto DECIMAL(5, 4) DEFAULT 0.0000, 
    satis_iskonto DECIMAL(5, 4) DEFAULT 0.0000
);

-- 4. MALZEMELER TABLOSU (Güncellendi)
CREATE TABLE malzemeler (
    id SERIAL PRIMARY KEY,
    siparis_kodu VARCHAR(100) UNIQUE NOT NULL,
    urun_adi VARCHAR(255) NOT NULL,
    marka VARCHAR(100),
    urun_grubu VARCHAR(100),
    tedarikci VARCHAR(255),
    liste_fiyati DECIMAL(15, 2) NOT NULL,
    para_birimi_id INT REFERENCES kurlar(id), 
    -- Artık tek bir iskonto yok, malzeme bir İskonto Grubuna bağlanıyor
    grup_iskonto_id INT REFERENCES grup_iskontolar(id) ON DELETE SET NULL  
);

-- 5. MAKROLAR TABLOSU (Şablonlar)
CREATE TABLE makrolar (
    id SERIAL PRIMARY KEY,
    makro_adi VARCHAR(255) NOT NULL UNIQUE
);

-- 6. MAKRO İÇERİKLERİ
CREATE TABLE makro_icerikleri (
    id SERIAL PRIMARY KEY,
    makro_id INT REFERENCES makrolar(id) ON DELETE CASCADE,
    malzeme_id INT REFERENCES malzemeler(id) ON DELETE RESTRICT,
    adet INT DEFAULT 1
);

-- 7. PROJE PANO MALZEME LİSTESİ (ADP, MCC vb.)
CREATE TABLE proje_pano_listesi (
    id SERIAL PRIMARY KEY,
    proje_id INT REFERENCES projeler(id) ON DELETE CASCADE,
    malzeme_id INT REFERENCES malzemeler(id) ON DELETE RESTRICT,
    pano_turu VARCHAR(50) NOT NULL, 
    adet INT NOT NULL,
    eklenme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);