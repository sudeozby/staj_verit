# app/services/pricing_engine.py

from decimal import Decimal

def hesapla_pano_maliyeti(liste_fiyati: float, iskonto_orani: float, kur_degeri: float, adet: int) -> dict:
    """
    Bir panodaki tek bir malzemenin TL bazlı net fiyatını ve satır toplamını hesaplar.
    Mühendislik notu: Finansal sapmaları önlemek için float değerler Decimal'e çevrilerek hesaplanır.
    """
    
    # 1. Float değerleri 0.0000001 kuruşluk hataları bile önlemek için Decimal'e çeviriyoruz
    d_liste_fiyati = Decimal(str(liste_fiyati))
    d_iskonto = Decimal(str(iskonto_orani))
    d_kur = Decimal(str(kur_degeri))
    
    # 2. İskontolu fiyatı bul (Liste Fiyatı * (1 - İskonto))
    iskontolu_fiyat = d_liste_fiyati * (Decimal('1') - d_iskonto)
    
    # 3. TL karşılığını bul (İskontolu Fiyat * Kur)
    net_fiyat_tl = iskontolu_fiyat * d_kur
    
    # 4. Adet ile çarpıp o satırın toplam maliyetini çıkar
    satir_toplami = net_fiyat_tl * Decimal(adet)
    
    # Çıktıları tekrar arayüzün anlayacağı float tipine (virgülden sonra 2 hane) yuvarlayarak döndür
    return {
        "net_fiyat_tl": float(round(net_fiyat_tl, 2)),
        "satir_toplami": float(round(satir_toplami, 2))
    }