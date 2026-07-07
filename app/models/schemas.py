from pydantic import BaseModel
from typing import Optional
from datetime import date

# 1. PROJE ŞABLONU (TEMKON Proje Bilgileri)
class ProjeEkle(BaseModel):
    proje_adi: str
    musteri: Optional[str] = None
    son_kullanici: Optional[str] = None
    lokasyon: Optional[str] = None
    teklif_konusu: Optional[str] = None
    teklif_tarihi: Optional[date] = None
    teklif_referans_no: Optional[str] = None
    teklifi_hazirlayan: Optional[str] = None

# 2. İSKONTO GRUBU ŞABLONU (TEMKON Ön Tanımlı İskonto Oranları)
class IskontoGrubuEkle(BaseModel):
    grup_adi: str
    maliyet_iskonto: float = 0.0
    proje_iskonto: float = 0.0
    satis_iskonto: float = 0.0
    notlar: Optional[str] = None


class Kullanici(BaseModel):
     kullanici_adi: str
     sifre: str
     rol: str

# 3. MALZEME ŞABLONU (TEMKON Aktif Malzeme Listesi)
class MalzemeEkle(BaseModel):
    siparis_kodu: str
    urun_adi: str
    marka: Optional[str] = "Tanımsız"
    urun_grubu: Optional[str] = "Genel"
    tedarikci: Optional[str] = "Tanımsız"
    liste_fiyati: float
    para_birimi: str = "USD"
    grup_iskonto_id: int

# 4. PROJE PANO LİSTESİ ŞABLONU (TEMKON ADP, MCC, REM Panoları)
class ProjePanoEkle(BaseModel):
    proje_id: int
    malzeme_id: int
    pano_turu: str
    adet: int
    ozel_iskonto: Optional[float] = None  # Projeye satış şartları geçerli kısmı için
    notlar: Optional[str] = None

# 5. GÜNCELLEME ŞABLONU (Senin yazdığın mevcut yapıyı koruyoruz)
class FiyatGuncelle(BaseModel):
    liste_fiyati: float
    grup_iskonto_id: Optional[int] = None