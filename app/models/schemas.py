from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from enum import Enum

# 1. ENUMLAR (Daha güvenli girişler için)
class ParaBirimi(str, Enum):
    TRY = "TRY"
    USD = "USD"
    EUR = "EUR"

# 2. PROJE ŞABLONU
class ProjeEkle(BaseModel):
    proje_adi: str
    musteri: Optional[str] = None
    son_kullanici: Optional[str] = None
    lokasyon: Optional[str] = None
    teklif_konusu: Optional[str] = None
    teklif_tarihi: Optional[date] = None
    hazirlayan: Optional[str] = None
    notlar: Optional[str] = None # Boş bırakılabilir
    referans_no: Optional[str] = None # Arka planda otomatik üretilecek

# 3. MALZEME ŞABLONU
class MalzemeEkle(BaseModel):
    siparis_kodu: str
    urun_adi: str
    marka: Optional[str] = "-"     
    urun_grubu: Optional[str] = "-"  # Gözden kaçmasın diye çizgi 
    tedarikci: Optional[str] = "-"   
    liste_fiyati: float = Field(..., ge=0) # Fiyat negatif olamaz!
    para_birimi: ParaBirimi = ParaBirimi.TRY # Enum kullanarak zorunlu kıldık   
    grup_iskonto_id: Optional[int] = None  # İskonto katmanı
    notlar: Optional[str] = "-"      # Boş kalırsa çizgi atacak

# 4. PANO MALZEME ATAMA
class ProjePanoEkle(BaseModel):
    proje_id: int
    malzeme_id: int
    pano_turu: str
    adet: int = Field(..., gt=0) # Adet 0'dan büyük olmalı!
    notlar: Optional[str] = None # NOTLAR EKLENDİ

# 5. FİYAT GÜNCELLEME
class FiyatGuncelle(BaseModel):
    liste_fiyati: float
    grup_iskonto_id: Optional[int] = None
    notlar: Optional[str] = None # Fiyat güncelleme sebebi için notlar alanı

# 6. KULLANICI ŞABLONLARI
class KullaniciOlustur(BaseModel):
    kullanici_adi: str
    sifre: str = Field(..., min_length=5, description="Şifre en az 5 karakter olmalıdır.")
    rol: str

class KullaniciGiris(BaseModel):
    kullanici_adi: str
    sifre: str

class SifreGuncelle(BaseModel):
    kullanici_adi: str
    sifre: str = Field(..., min_length=5, description="Yeni şifre en az 5 karakter olmalıdır.")
    
# 7. İSKONTO GRUBU ŞABLONU
class IskontoGrubuEkle(BaseModel):
    grup_adi: str
    maliyet_iskonto: float = 0.0
    proje_iskonto: float = 0.0
    satis_iskonto: float = 0.0
    notlar: Optional[str] = None