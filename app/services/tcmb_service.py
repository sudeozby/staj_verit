# app/services/tcmb_service.py

import urllib.request
import xml.etree.ElementTree as ET

def fetch_tcmb_rates() -> dict:
    """
    Merkez Bankası (TCMB) web sitesine bağlanarak güncel USD ve EUR satış kurlarını çeker.
    Veritabanına bağlanmaz, sadece ayıklanmış veriyi sözlük (dict) olarak döndürür.
    """
    url = "https://www.tcmb.gov.tr/kurlar/today.xml"
    
    # TCMB'nin bot olduğumuzu düşünüp bizi engellememesi için tarayıcı kimliği (User-Agent) ekliyoruz
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    try:
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
            
        # XML verisini Python'ın anlayacağı ağaç yapısına çeviriyoruz
        root = ET.fromstring(xml_data)
        
        rates = {}
        
        # Sadece bizim işimize yarayan USD ve EUR kurlarını ayıklıyoruz
        for currency in root.findall('Currency'):
            kod = currency.get('CurrencyCode')
            if kod in ['USD', 'EUR']:
                satis_kuru = currency.find('ForexSelling').text
                if satis_kuru:
                    rates[kod] = float(satis_kuru)
                    
        # Örnek çıktı: {"USD": 33.15, "EUR": 35.80}
        return rates
        
    except Exception as e:
        raise Exception(f"TCMB kur verileri çekilirken ağ hatası oluştu: {e}")