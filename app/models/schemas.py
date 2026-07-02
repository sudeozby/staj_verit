from pydantic import BaseModel
from typing import Optional

# 1. PROJE ŞABLONU
class ProjeEkle(BaseModel):
    proje_adi: str
    musteri: str
    son_kullanici: Optional[str] = None
    lokasyon: Optional[str] = None
    teklif_referans_no: Optional[str] = None

# 2. YENİ: İSKONTO GRUBU ŞABLONU (Yeni Mimari İçin)
class IskontoGrubuEkle(BaseModel):
    grup_adi: str
    maliyet_iskonto: float = 0.0
    proje_iskonto: float = 0.0
    satis_iskonto: float = 0.0

# 3. MALZEME ŞABLONU (Güncellendi)
class MalzemeEkle(BaseModel):
    siparis_kodu: str
    urun_adi: str
    marka: Optional[str] = None
    urun_grubu: Optional[str] = None
    tedarikci: Optional[str] = None
    liste_fiyati: float
    para_birimi: str  # Arayüzden "USD" veya "EUR" gelecek
    grup_iskonto_id: Optional[int] = None  # Eski iskonto_orani yerine artık bir GRUBA bağlanıyor

# 4. PROJE PANO LİSTESİ ŞABLONU
class PanoMalzemeEkle(BaseModel):
    proje_id: int
    malzeme_id: int
    pano_turu: str  # Örn: ADP, MCC, REM 100 vb.
    adet: int

# 5. GÜNCELLEME ŞABLONU
class FiyatGuncelle(BaseModel):
    liste_fiyati: float
    grup_iskonto_id: Optional[int] = None