from pydantic import BaseModel
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
    marka: Optional[str] = "Tanımsız"
    urun_grubu: Optional[str] = "Genel"
    tedarikci: Optional[str] = "Tanımsız"
    liste_fiyati: float
    para_birimi: str = "USD"
    notlar: Optional[str] = None # NOTLAR EKLENDİ

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
class Kullanici(BaseModel):
    kullanici_adi: str
    sifre: str
    rol: str

# 6. İSKONTO GRUBU ŞABLONU
class IskontoGrubuEkle(BaseModel):
    grup_adi: str
    maliyet_iskonto: float = 0.0
    proje_iskonto: float = 0.0
    satis_iskonto: float = 0.0
    notlar: Optional[str] = None