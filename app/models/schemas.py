from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

# 1. PROJE ŞABLONU
class ProjeEkle(BaseModel):
    proje_adi: str
    musteri: Optional[str] = None
    son_kullanici: Optional[str] = None
    lokasyon: Optional[str] = None
    teklif_konusu: Optional[str] = None
    teklif_tarihi: Optional[date] = None
    teklif_referans_no: Optional[str] = None
    hazirlayan: Optional[str] = None

# 2. MALZEME ŞABLONU
class MalzemeEkle(BaseModel):
    siparis_kodu: str
    urun_adi: str
    marka: Optional[str] = "-"       # Gözden kaçmasın diye çizgi koyduk
    urun_grubu: Optional[str] = "-"  # Gözden kaçmasın diye çizgi koyduk
    tedarikci: Optional[str] = "-"   # Gözden kaçmasın diye çizgi koyduk
    liste_fiyati: float
    para_birimi: str = "TRY"         # Varsayılan para birimi TRY oldu
    grup_iskonto_id: Optional[int] = None  # Yeni eklediğimiz iskonto katmanı
    notlar: Optional[str] = "-"      # Boş kalırsa çizgi atacak

# 3. PANO MALZEME ATAMA
class ProjePanoEkle(BaseModel):
    proje_id: int
    malzeme_id: int
    pano_turu: str
    adet: int
    notlar: Optional[str] = None # NOTLAR EKLENDİ

# 4. FİYAT GÜNCELLEME (İstediğin yeni şema)
class FiyatGuncelle(BaseModel):
    liste_fiyati: float
    grup_iskonto_id: Optional[int] = None
    notlar: Optional[str] = None # Fiyat güncelleme sebebi için notlar alanı

# 5. KULLANICI ŞABLONU
class KullaniciOlustur(BaseModel):
    kullanici_adi: str
    sifre: str = Field(..., min_length=5, description="Şifre en az 5 karakter olmalıdır.")
    rol: str


class KullaniciGiris(BaseModel):
    kullanici_adi: str
    sifre: str

# 6. İSKONTO GRUBU ŞABLONU
class IskontoGrubuEkle(BaseModel):
    grup_adi: str
    maliyet_iskonto: float = 0.0
    proje_iskonto: float = 0.0
    satis_iskonto: float = 0.0
    notlar: Optional[str] = None