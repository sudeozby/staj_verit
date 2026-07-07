<template>
  <div class="container">
    
    <UstMenu />

    <div class="form-kutusu" style="background: white; padding: 30px; border-radius: 10px; border-left: 8px solid #8e44ad; box-shadow: 0 6px 12px rgba(0,0,0,0.08);">
      <h3>Kayıtlı Panoları İnceleme Ekranı</h3>
      <div class="form-grubu" style="display: flex; flex-direction: column; gap: 15px;">
        <div class="ikili-sutun" style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
          <select v-model="inceleProjeId">
            <option disabled value="">Hangi Projedeki Pano?</option>
            <option v-for="p in projeler" :key="p[0]" :value="p[0]">{{ p[1] }}</option>
          </select>
          
          <select v-model="incelePanoTuru">
            <option disabled value="">Görünüm Seçin</option>
            <option value="TÜM PANOLAR">🔥 Tüm Panoları Getir</option>
            <option value="TÜM MCC LER">⚡ Tüm MCC Panolarını Birleştir</option>
            <option value="TÜM REM LER">🔌 Tüm REM Panolarını Birleştir</option>
            <optgroup label="Tekil Panolar">
              <option v-for="pano in ['ADP 1', 'MCC 1', 'MCC 2', 'MCC 3', 'MCC 4', 'MCC 5', 'REM 100', 'REM 200', 'REM 300', 'REM 400', 'REM 500', 'KONTROL S.', 'SAHA']" :key="pano" :value="pano">{{ pano }}</option>
            </optgroup>
          </select>
        </div>
        <button @click="panoIcerigiGetir" class="btn-kaydet" style="background-color: #8e44ad; color: white; padding: 12px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer;">Kayıtları Filtrele ve Aç</button>
      </div>

      <div v-if="panoIcerigi.length > 0" class="tablo-wrapper" style="margin-top: 25px; overflow-x: auto;">
        <h4 style="margin-top: 0; margin-bottom: 15px; color: #8e44ad;">{{ incelePanoTuru }} İçeriği:</h4>
        
        <div style="display: flex; gap: 10px; margin-bottom: 15px;">
          <button @click="excelIndir" style="background-color: #27ae60; color: white; padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; display: flex; align-items: center; gap: 8px;">
            📊 Excel Olarak İndir
          </button>
          <button v-if="kullaniciRolu !== 'saha_ekibi'" @click="pdfIndir" style="background-color: #e74c3c; color: white; padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; display: flex; align-items: center; gap: 8px;">
            📄 Müşteri Teklifi (PDF) İndir
          </button>
        </div>

        <div v-if="kullaniciRolu === 'yonetici' || kullaniciRolu === 'teklif_ekibi'" style="display: flex; gap: 10px; margin-bottom: 20px; border-bottom: 2px solid #ccc; padding-bottom: 15px;">
          <button @click="seciliTablo = 'satis'" :style="seciliTablo === 'satis' ? 'background-color: #34495e; color: white;' : 'background-color: #ecf0f1; color: #2c3e50;'" style="padding: 10px 20px; border: none; border-radius: 5px; font-weight: bold; cursor: pointer; transition: 0.3s;">
            🛍️ Müşteri Satış Tablosu
          </button>
          <button v-if="kullaniciRolu === 'yonetici'" @click="seciliTablo = 'maliyet'" :style="seciliTablo === 'maliyet' ? 'background-color: #c00000; color: white;' : 'background-color: #ecf0f1; color: #2c3e50;'" style="padding: 10px 20px; border: none; border-radius: 5px; font-weight: bold; cursor: pointer; transition: 0.3s;">
            💼 Yönetim Maliyet Tablosu
          </button>
          <button @click="seciliTablo = 'grafik'" :style="seciliTablo === 'grafik' ? 'background-color: #8e44ad; color: white;' : 'background-color: #ecf0f1; color: #2c3e50;'" style="padding: 10px 20px; border: none; border-radius: 5px; font-weight: bold; cursor: pointer; transition: 0.3s;">
            📊 Döviz & Kâr Dashboard
          </button>
        </div>

        <table v-if="kullaniciRolu === 'teklif_ekibi' || (kullaniciRolu === 'yonetici' && seciliTablo === 'satis')" class="maliyet-tablosu" style="width: 100%; border-collapse: collapse; font-size: 13px; border: 1px solid #000;">
          <thead>
            <tr>
              <th colspan="9" style="background-color: #ffc000; color: #000; text-align: center; border: 1px solid #000; padding: 8px; font-weight: bold; font-size: 14px;">PROJE SATIŞ VE FİYATLANDIRMA LİSTESİ</th>
            </tr>
            <tr style="background-color: #9bc2e6; color: #005a8c;">
              <th style="border: 1px solid #000; padding: 10px;">PANO TÜRÜ</th>
              <th style="border: 1px solid #000; padding: 10px;">MALZEME ADI</th>
              <th style="border: 1px solid #000; padding: 10px;">LİSTE FİYATI</th> 
              <th style="border: 1px solid #000; padding: 10px;">İSKONTO</th>
              <th style="border: 1px solid #000; padding: 10px;">NET FİYAT</th>
              <th style="border: 1px solid #000; padding: 10px;">ADET/SET</th>
              <th style="border: 1px solid #000; padding: 10px;">TOPLAM</th>
              <th style="border: 1px solid #000; padding: 10px;">KUR</th>
              <th style="border: 1px solid #000; padding: 10px;">NOTLAR</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in filtrelenmisPanoIcerigi" :key="index" style="text-align: center; border-bottom: 1px solid #ccc;">
              <td style="border: 1px solid #000; padding: 8px;">{{ item.pano }}</td>
              <td style="border: 1px solid #000; padding: 8px; text-align: left;">{{ item.malzeme }}</td>
              <td style="border: 1px solid #000; padding: 8px; font-weight: bold;">{{ item.liste_fiyati }} {{ item.para_birimi }}</td>
              <td style="border: 1px solid #000; padding: 8px; background-color: #ffe699; font-weight: bold;">% {{ item.iskonto_orani ? (item.iskonto_orani * 100).toFixed(0) : '0' }}</td>
              <td style="border: 1px solid #000; padding: 8px; color: #c00000; font-weight: bold;">{{ item.birim_proje_tl }} ₺</td>
              <td style="border: 1px solid #000; padding: 8px; font-weight: bold; background-color: #e2efda;">{{ item.adet }}</td>
              <td style="border: 1px solid #000; padding: 8px; color: #c00000; font-weight: bold;">{{ item.toplam_proje_tl }} ₺</td>
              <td style="border: 1px solid #000; padding: 8px; background-color: #ffe699;">{{ item.kur_degeri }} ({{ item.para_birimi }})</td>
              <td style="border: 1px solid #000; padding: 8px; background-color: #ffe699;">-</td>
            </tr>
          </tbody>
        </table>

        <div v-if="kullaniciRolu === 'yonetici' && seciliTablo === 'maliyet'">
          <div style="background: #fdf2e9; padding: 15px 25px; border-radius: 8px; border-left: 5px solid #d35400; margin-bottom: 20px; display: flex; gap: 30px; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <div>
              <label style="font-weight: bold; color: #d35400; font-size: 13px;">🎯 Genel Kâr Marjı (%):</label><br>
              <input type="number" v-model="genelKarMarji" style="padding: 10px; border: 1px solid #ccc; border-radius: 4px; width: 140px; margin-top: 5px; font-weight: bold; font-size: 15px;">
            </div>
            <div>
              <label style="font-weight: bold; color: #d35400; font-size: 13px;">👷‍♂️ Toplam İşçilik / Saha Gideri (₺):</label><br>
              <input type="number" v-model="iscilikGideri" style="padding: 10px; border: 1px solid #ccc; border-radius: 4px; width: 200px; margin-top: 5px; font-weight: bold; font-size: 15px;">
            </div>
            <div style="margin-left: auto; text-align: right; background: white; padding: 10px 15px; border-radius: 6px; border: 1px dashed #d35400;">
              <span style="font-size: 13px; color: #d35400; font-weight: bold;">⚡ Simülasyon Aktif</span><br>
              <span style="font-size: 11px; color: #7f8c8d;">Değerleri değiştirdiğiniz an tablo f(x) güncellenir.</span>
            </div>
          </div>

          <div style="overflow-x: auto;">
            <table class="maliyet-tablosu" style="width: 100%; border-collapse: collapse; font-size: 12px; border: 1px solid #000; min-width: 1200px;">
              <thead>
                <tr>
                  <th colspan="13" style="background-color: #ffc000; color: #000; text-align: center; border: 1px solid #000; padding: 8px; font-weight: bold; font-size: 14px;">PROJEYE SATIŞ ŞARTLARI GEÇERLİ</th>
                </tr>
                <tr style="background-color: #9bc2e6; color: #005a8c;">
                  <th style="border: 1px solid #000; padding: 10px;">SIRA</th>
                  <th style="border: 1px solid #000; padding: 10px;">MALİYET KALEMİ</th>
                  <th style="border: 1px solid #000; padding: 10px;">MALİYET GRUBU</th>
                  <th style="border: 1px solid #000; padding: 10px;">MALİYET TRY</th>
                  <th style="border: 1px solid #000; padding: 10px;">MALİYET EUR</th>
                  <th style="border: 1px solid #000; padding: 10px;">MALİYET USD</th>
                  <th style="border: 1px solid #000; padding: 10px;">TEKLİF BEDELİ</th>
                  <th style="border: 1px solid #000; padding: 10px;">± % İSK.</th>
                  <th style="border: 1px solid #000; padding: 10px; color: #c00000;">f(x) NET FİYAT</th>
                  <th style="border: 1px solid #000; padding: 10px;">ADET/SET</th>
                  <th style="border: 1px solid #000; padding: 10px; color: #c00000;">f(x) TOPLAM</th>
                  <th style="border: 1px solid #000; padding: 10px;">KUR</th>
                  <th style="border: 1px solid #000; padding: 10px;">TEKLİF SONUNDA DETAY VERİLECEKLER</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in filtrelenmisPanoIcerigi" :key="index" style="text-align: center; border-bottom: 1px solid #ccc; background-color: #f2f2f2;">
                  <td style="border: 1px solid #000; padding: 8px;">{{ index + 1 }}</td>
                  <td style="border: 1px solid #000; padding: 8px; text-align: left; background-color: white;">{{ item.malzeme }}</td>
                  <td style="border: 1px solid #000; padding: 8px; background-color: white;">{{ item.pano }}</td>
                  <td style="border: 1px solid #000; padding: 8px; font-weight: bold;">{{ item.para_birimi === 'TRY' ? item.birim_proje_tl : (item.birim_proje_tl * item.kur_degeri).toFixed(2) }} ₺</td>
                  <td style="border: 1px solid #000; padding: 8px;">{{ item.para_birimi === 'EUR' ? item.birim_proje_tl + ' €' : '-' }}</td>
                  <td style="border: 1px solid #000; padding: 8px;">{{ item.para_birimi === 'USD' ? item.birim_proje_tl + ' $' : '-' }}</td>
                  <td style="border: 1px solid #000; padding: 8px; font-weight: bold; background-color: #e2efda;">{{ (item.birim_proje_tl * (1 + (genelKarMarji || 0) / 100)).toFixed(2) }} ₺</td>
                  <td style="border: 1px solid #000; padding: 8px;">% {{ item.iskonto_orani ? (item.iskonto_orani * 100).toFixed(0) : '0' }}</td>
                  <td style="border: 1px solid #000; padding: 8px; font-weight: bold; color: #c00000; background-color: #fff2cc;">{{ ((item.birim_proje_tl * (1 + (genelKarMarji || 0) / 100)) * (1 - (item.iskonto_orani || 0))).toFixed(2) }} ₺</td>
                  <td style="border: 1px solid #000; padding: 8px; font-weight: bold;">{{ item.adet }}</td>
                  <td style="border: 1px solid #000; padding: 8px; font-weight: bold; color: #c00000; background-color: #fff2cc;">{{ (((item.birim_proje_tl * (1 + (genelKarMarji || 0) / 100)) * (1 - (item.iskonto_orani || 0))) * item.adet).toFixed(2) }} ₺</td>
                  <td style="border: 1px solid #000; padding: 8px;">{{ item.kur_degeri }} ({{ item.para_birimi }})</td>
                  <td style="border: 1px solid #000; padding: 8px; background-color: white;">-</td>
                </tr>
              </tbody>
              <tfoot v-if="filtrelenmisPanoIcerigi.length > 0">
                <tr style="background-color: #2c3e50; color: white; font-weight: bold;">
                  <td colspan="10" style="text-align: right; padding: 10px; border: 1px solid #000;">ARA TOPLAM (MALZEME):</td>
                  <td style="padding: 10px; border: 1px solid #000;">{{ dinamikAraToplam.toFixed(2) }} ₺</td>
                  <td colspan="2" style="border: 1px solid #000;"></td>
                </tr>
                <tr style="background-color: #34495e; color: white; font-weight: bold;">
                  <td colspan="10" style="text-align: right; padding: 10px; border: 1px solid #000;">İŞÇİLİK / SAHA GİDERİ:</td>
                  <td style="padding: 10px; border: 1px solid #000;">+ {{ iscilikGideri || 0 }} ₺</td>
                  <td colspan="2" style="border: 1px solid #000;"></td>
                </tr>
                <tr style="background-color: #c0392b; color: white; font-weight: bold; font-size: 15px;">
                  <td colspan="10" style="text-align: right; padding: 12px; border: 1px solid #000;">GENEL PROJE SATIŞ BEDELİ:</td>
                  <td style="padding: 12px; border: 1px solid #000; color: #f1c40f;">{{ (dinamikAraToplam + (iscilikGideri || 0)).toFixed(2) }} ₺</td>
                  <td colspan="2" style="border: 1px solid #000;"></td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>

        <table v-if="kullaniciRolu === 'saha_ekibi'" class="maliyet-tablosu" style="width: 100%; border-collapse: collapse; font-size: 13px; border: 1px solid #000;">
          <thead>
            <tr>
              <th colspan="5" style="background-color: #34495e; color: white; text-align: center; border: 1px solid #000; padding: 8px; font-weight: bold; font-size: 14px;">TEKNİK KONFİGÜRASYON VE MALZEME LİSTESİ (SAHA / İMALAT)</th>
            </tr>
            <tr style="background-color: #ecf0f1; color: #2c3e50;">
              <th style="border: 1px solid #000; padding: 10px; width: 10%;">SIRA</th>
              <th style="border: 1px solid #000; padding: 10px; width: 20%;">PANO TÜRÜ</th>
              <th style="border: 1px solid #000; padding: 10px; width: 25%;">SİPARİŞ KODU</th>
              <th style="border: 1px solid #000; padding: 10px; width: 35%;">MALZEME ADI</th>
              <th style="border: 1px solid #000; padding: 10px; width: 10%;">ADET</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in filtrelenmisPanoIcerigi" :key="index" style="text-align: center; border-bottom: 1px solid #ccc;">
              <td style="border: 1px solid #000; padding: 8px;">{{ index + 1 }}</td>
              <td style="border: 1px solid #000; padding: 8px; font-weight: bold;">{{ item.pano }}</td>
              <td style="border: 1px solid #000; padding: 8px; font-family: monospace;">{{ item.siparis_kodu || 'M-CODE-' + index }}</td>
              <td style="border: 1px solid #000; padding: 8px; text-align: left;">{{ item.malzeme }}</td>
              <td style="border: 1px solid #000; padding: 8px; font-weight: bold; background-color: #e2efda;">{{ item.adet }}</td>
            </tr>
          </tbody>
        </table>

        <div v-if="(kullaniciRolu === 'yonetici' || kullaniciRolu === 'teklif_ekibi') && seciliTablo === 'grafik'" style="background: #f8f9fa; padding: 25px; border-radius: 10px; border: 1px solid #ddd;">
          <h3 style="margin-top: 0; color: #2c3e50; border-bottom: 2px solid #8e44ad; padding-bottom: 10px;">Proje Risk ve Kâr Simülasyonu</h3>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-top: 20px;">
            <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); display: flex; flex-direction: column; align-items: center;">
              <h4 style="margin-top: 0; color: #34495e;">Maliyetlerin Döviz Dağılımı (₺ Karşılığı)</h4>
              <div :style="{ background: dovizDagilimi.pastaCss }" style="width: 200px; height: 200px; border-radius: 50%; border: 4px solid #fff; box-shadow: 0 0 10px rgba(0,0,0,0.1); margin: 20px 0;"></div>
              <div style="width: 100%; display: flex; justify-content: space-around; font-weight: bold; font-size: 13px;">
                <div style="color: #2980b9;">🟦 TRY: %{{ dovizDagilimi.tryYuzde.toFixed(1) }}</div>
                <div style="color: #c0392b;">🟥 EUR: %{{ dovizDagilimi.eurYuzde.toFixed(1) }}</div>
                <div style="color: #f39c12;">🟨 USD: %{{ dovizDagilimi.usdYuzde.toFixed(1) }}</div>
              </div>
            </div>
            <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
              <h4 style="margin-top: 0; color: #34495e;">Satış Fiyatı ve Kâr Belirleme</h4>
              <div style="background: #fdf2e9; padding: 15px; border-radius: 6px; border-left: 4px solid #d35400; margin-bottom: 20px;">
                <label style="font-weight: bold; color: #d35400; font-size: 13px;">🎯 Uygulanacak Kâr Marjı (%):</label>
                <input type="number" v-model="genelKarMarji" style="width: 100%; padding: 10px; margin-top: 5px; font-weight: bold; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box;">
                <label style="font-weight: bold; color: #d35400; font-size: 13px; display: block; margin-top: 15px;">👷‍♂️ İşçilik / Saha Gideri (₺):</label>
                <input type="number" v-model="iscilikGideri" style="width: 100%; padding: 10px; margin-top: 5px; font-weight: bold; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box;">
              </div>
              <div style="border: 2px dashed #27ae60; padding: 15px; border-radius: 6px; text-align: right; background: #f9fff9;">
                <p style="margin: 0 0 10px 0; font-size: 13px; color: #555;">Saf Malzeme Maliyeti: <b>{{ dovizDagilimi.genelToplam.toFixed(2) }} ₺</b></p>
                <p style="margin: 0 0 10px 0; font-size: 13px; color: #555;">Kâr + İşçilik Hedefi: <b style="color: #27ae60;">+ {{ ((dinamikAraToplam + iscilikGideri) - dovizDagilimi.genelToplam).toFixed(2) }} ₺</b></p>
                <hr style="border: 0; border-top: 1px solid #ccc; margin: 10px 0;">
                <h3 style="margin: 0; color: #27ae60; font-size: 22px;">TEKLİF BEDELİ: {{ (dinamikAraToplam + iscilikGideri).toFixed(2) }} ₺</h3>
              </div>
            </div>
          </div>
        </div>

      </div>

      <div v-else-if="panoAcildi" style="margin-top: 20px; color: #c0392b; font-weight: bold; text-align: center;">
        Seçilen kriterde henüz kayıtlı malzeme yok.
      </div>
    </div>

    <div style="display: none;">
      <div id="p1-teklif-sablonu" class="pdf-container">
        <div class="pdf-sayfa kapak-sayfasi">
          <div class="kapak-icerik">
            <h1 class="pdf-logo">TEM<span class="kirmizi">K</span>ON</h1>
            <div class="cizgi"></div>
            <h2>RESMİ PROJE TEKLİFİ</h2>
            <p class="alt-baslik">Maliyet ve Teknik Konfigürasyon Belgesi (P1)</p>
            <div class="kapak-alt-bilgi">
              <p><strong>Tarih:</strong> {{ yeniProje.teklif_tarihi }}</p>
              <p><strong>Referans No:</strong> {{ yeniProje.teklif_referans_no }}</p>
            </div>
          </div>
        </div>
        <div class="sayfa-sonu"></div>

        <div class="pdf-sayfa">
          <div class="pdf-baslik-alani">
            <h3>1. GENEL BAKIŞ & PROJE DETAYLARI</h3>
          </div>
          <div class="pdf-metin-kutusu">
            <h4>Hakkımızda</h4>
            <p>TEMKON, endüstriyel otomasyon ve AG/OG pano sistemlerinde esnek, modüler ve yüksek mühendislik standartlarına uygun çözümler üretmektedir.</p>
          </div>
          <div class="pdf-metin-kutusu" style="margin-top: 20px;">
            <h4>Proje Kimlik Kartı</h4>
            <table class="pdf-ozet-tablo">
              <tr><td><strong>Müşteri:</strong></td><td>{{ yeniProje.musteri }}</td></tr>
              <tr><td><strong>Proje Adı:</strong></td><td>{{ yeniProje.proje_adi }}</td></tr>
              <tr><td><strong>Hazırlayan:</strong></td><td>{{ yeniProje.hazirlayan }}</td></tr>
            </table>
          </div>
        </div>
        <div class="sayfa-sonu"></div>

        <div class="pdf-sayfa">
          <div class="pdf-baslik-alani">
            <h3>2. TİCARİ VE TEKNİK ŞARTNAME</h3>
          </div>
          <div class="sartlar-listesi">
            <p><strong>1. Geçerlilik Süresi:</strong> İşbu teklif veriliş tarihinden itibaren 30 takvim günü geçerlidir.</p>
            <p><strong>2. Garanti Şartları:</strong> Tüm pano sistemlerimiz teslim tarihinden itibaren 2 yıl garantilidir.</p>
          </div>
          <div class="imza-alani" style="margin-top: 80px; display: flex; justify-content: space-between;">
            <div class="imza-kutu"><strong>Müşteri Onayı</strong><br><br><br>İmza / Kaşe</div>
            <div class="imza-kutu"><strong>TEMKON Yetkilisi</strong><br><br><br>İmza / Kaşe</div>
          </div>
        </div>
        <div class="sayfa-sonu"></div>

        <div class="pdf-sayfa">
          <div class="pdf-baslik-alani">
            <h3>3. TEKNİK MALZEME SPESİFİKASYONU (FİYATSIZ LİSTE)</h3>
          </div>
          <table class="pdf-malzeme-tablosu">
            <thead>
              <tr>
                <th style="width: 10%">Sıra</th>
                <th style="width: 25%">Pano Türü</th>
                <th style="width: 55%">Malzeme Adı</th>
                <th style="width: 10%">Adet</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in filtrelenmisPanoIcerigi" :key="index">
                <td style="text-align: center;">{{ index + 1 }}</td>
                <td>{{ item.pano }}</td>
                <td>{{ item.malzeme }}</td>
                <td style="text-align: center; font-weight: bold;">{{ item.adet }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import html2pdf from 'html2pdf.js';
import * as XLSX from 'xlsx';
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import UstMenu from '../components/UstMenu.vue';

const router = useRouter();

// ROL KONTROLÜ VE SEKME YÖNETİMİ
const kullaniciRolu = ref(localStorage.getItem('kullaniciRolu') || 'saha_ekibi');
const seciliTablo = ref('satis');

// PANO VE PROJE DEĞİŞKENLERİ
const projeler = ref([]);
const inceleProjeId = ref('');
const incelePanoTuru = ref('');
const panoIcerigi = ref([]);
const panoAcildi = ref(false);

// SİMÜLASYON DEĞİŞKENLERİ
const genelKarMarji = ref(20); 
const iscilikGideri = ref(0);

// PDF İÇİN ŞABLON BİLGİLERİ
const yeniProje = ref({
  musteri: 'TEMKON Müşterisi',
  son_kullanici: 'End User',
  lokasyon: 'Ankara / Türkiye',
  proje_adi: 'Endüstriyel Pano Projesi',
  teklif_konusu: 'CPQ Pano Konfigürasyonu',
  hazirlayan: 'Sude Özbay - İletişim Birim Başkanı', 
  teklif_tarihi: '06.07.2026',
  teklif_referans_no: 'TEMKON-OFFER-2026'
});

// --- HESAPLAMALAR VE FİLTRELER (COMPUTED) ---

const filtrelenmisPanoIcerigi = computed(() => {
  if (!panoIcerigi.value || panoIcerigi.value.length === 0) return [];
  if (incelePanoTuru.value === 'TÜM PANOLAR' || !incelePanoTuru.value) return panoIcerigi.value;
  if (incelePanoTuru.value === 'TÜM MCC LER') return panoIcerigi.value.filter(item => item.pano && item.pano.startsWith('MCC'));
  if (incelePanoTuru.value === 'TÜM REM LER') return panoIcerigi.value.filter(item => item.pano && item.pano.startsWith('REM'));
  return panoIcerigi.value.filter(item => item.pano === incelePanoTuru.value);
});

const dinamikAraToplam = computed(() => {
  if (!filtrelenmisPanoIcerigi.value) return 0;
  return filtrelenmisPanoIcerigi.value.reduce((toplam, item) => {
    const teklifBedeli = item.birim_proje_tl * (1 + (genelKarMarji.value || 0) / 100);
    const netFiyat = teklifBedeli * (1 - (item.iskonto_orani || 0));
    return toplam + (netFiyat * item.adet);
  }, 0);
});

const dovizDagilimi = computed(() => {
  let tryMaliyet = 0;
  let eurMaliyetTL = 0;
  let usdMaliyetTL = 0;

  let eurRaw = 0;
  let usdRaw = 0;

  (filtrelenmisPanoIcerigi.value || []).forEach(item => {
    const safTutar = item.birim_proje_tl * item.adet;
    if (item.para_birimi === 'TRY') {
      tryMaliyet += safTutar;
    } else if (item.para_birimi === 'EUR') {
      eurMaliyetTL += (safTutar * item.kur_degeri);
      eurRaw += safTutar;
    } else if (item.para_birimi === 'USD') {
      usdMaliyetTL += (safTutar * item.kur_degeri);
      usdRaw += safTutar;
    }
  });

  const genelToplam = tryMaliyet + eurMaliyetTL + usdMaliyetTL;
  const tryYuzde = genelToplam ? (tryMaliyet / genelToplam) * 100 : 0;
  const eurYuzde = genelToplam ? (eurMaliyetTL / genelToplam) * 100 : 0;
  const usdYuzde = genelToplam ? (usdMaliyetTL / genelToplam) * 100 : 0;

  const pastaCss = `conic-gradient(#3498db 0% ${tryYuzde}%, #e74c3c ${tryYuzde}% ${tryYuzde + eurYuzde}%, #f1c40f ${tryYuzde + eurYuzde}% 100%)`;

  return {
    tryMaliyet, eurMaliyetTL, usdMaliyetTL, 
    eurRaw, usdRaw, genelToplam,
    tryYuzde, eurYuzde, usdYuzde, pastaCss
  };
});

// --- VERİ ÇEKME VE İNDİRME FONKSİYONLARI ---

const panoIcerigiGetir = async () => {
  if (!inceleProjeId.value || !incelePanoTuru.value) return;
  try {
    const response = await axios.get(`http://127.0.0.1:8000/projeler/${inceleProjeId.value}/maliyet-raporu`);
    panoIcerigi.value = response.data.detaylar || []; 
    panoAcildi.value = true;
  } catch (error) { 
    console.error("Kayıtlar çekilemedi", error);
  }
};

const excelIndir = () => {
  let indirilecekVeri = [];
  let sekmeAdi = "";
  let dosyaAdi = "";

  if (kullaniciRolu.value === 'saha_ekibi') {
    indirilecekVeri = filtrelenmisPanoIcerigi.value.map((item, index) => ({
      "Sıra": index + 1,
      "Pano Türü": item.pano,
      "Sipariş Kodu": item.siparis_kodu || 'M-CODE-' + index,
      "Malzeme Adı": item.malzeme,
      "Adet": item.adet
    }));
    sekmeAdi = "Malzeme Listesi";
    dosyaAdi = "TEMKON_Saha_Malzeme_Listesi.xlsx";
  } else if (kullaniciRolu.value === 'yonetici' && seciliTablo.value === 'maliyet') {
    const karCani = 1 + (genelKarMarji.value || 0) / 100;
    
    indirilecekVeri = filtrelenmisPanoIcerigi.value.map((item, index) => {
      const teklifBedeli = item.birim_proje_tl * karCani;
      const iskontoMultiplier = 1 - (item.iskonto_orani || 0);
      const netFiyat = teklifBedeli * iskontoMultiplier;
      const toplam = netFiyat * item.adet;
      
      return {
        "Sıra": index + 1,
        "Maliyet Kalemi": item.malzeme,
        "Maliyet Grubu": item.pano,
        "Maliyet TRY": item.para_birimi === 'TRY' ? item.birim_proje_tl + " ₺" : (item.birim_proje_tl * item.kur_degeri).toFixed(2) + " ₺",
        "Maliyet EUR": item.para_birimi === 'EUR' ? item.birim_proje_tl + " €" : '-',
        "Maliyet USD": item.para_birimi === 'USD' ? item.birim_proje_tl + " $" : '-',
        "Teklif Bedeli (₺)": teklifBedeli.toFixed(2) + " ₺",
        "İskonto (%)": "% " + (item.iskonto_orani ? (item.iskonto_orani * 100).toFixed(0) : '0'),
        "Net Fiyat (₺)": netFiyat.toFixed(2) + " ₺",
        "Adet/Set": item.adet,
        "Toplam (₺)": toplam.toFixed(2) + " ₺",
        "Kur": `${item.kur_degeri} (${item.para_birimi})`
      };
    });

    indirilecekVeri.push({});
    indirilecekVeri.push({ "Adet/Set": "ARA TOPLAM:", "Toplam (₺)": dinamikAraToplam.value.toFixed(2) + " ₺" });
    indirilecekVeri.push({ "Adet/Set": "İŞÇİLİK/SAHA GİDERİ:", "Toplam (₺)": "+ " + (iscilikGideri.value || 0).toString() + " ₺" });
    indirilecekVeri.push({ "Adet/Set": "GENEL SATIŞ BEDELİ:", "Toplam (₺)": (dinamikAraToplam.value + (iscilikGideri.value || 0)).toFixed(2) + " ₺" });

    sekmeAdi = "Simülasyon Analizi";
    dosyaAdi = "TEMKON_Yonetim_Maliyet_Simulasyonu.xlsx";
  } else {
    indirilecekVeri = filtrelenmisPanoIcerigi.value.map(item => ({
      "Pano Türü": item.pano,
      "Malzeme Adı": item.malzeme,
      "Liste Fiyatı": `${item.liste_fiyati} ${item.para_birimi}`,
      "İskonto (%)": item.iskonto_orani ? (item.iskonto_orani * 100).toFixed(0) : '0',
      "Net Fiyat (₺)": item.birim_proje_tl,
      "Adet": item.adet,
      "Toplam (₺)": item.toplam_proje_tl,
      "Kur": item.kur_degeri
    }));
    sekmeAdi = "Maliyet Analizi";
    dosyaAdi = "TEMKON_Satis_Fiyatlandirma.xlsx";
  }

  const worksheet = XLSX.utils.json_to_sheet(indirilecekVeri);
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, sekmeAdi);
  XLSX.writeFile(workbook, dosyaAdi);
};

const pdfIndir = () => {
  if (kullaniciRolu.value === 'saha_ekibi') return;
  const element = document.getElementById('p1-teklif-sablonu');
  if (!element) return alert("Şablon bulunamadı.");
  const secenekler = {
    margin: 0,
    filename: `${yeniProje.value.proje_adi}_Teklif_Formu.pdf`,
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: { scale: 2, useCORS: true },
    jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
    pagebreak: { mode: ['avoid-all', 'css', 'legacy'] }
  };
  html2pdf().set(secenekler).from(element).save();
};

const verileriYukle = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/projeler/listele');
    projeler.value = response.data;
  } catch (error) { console.error("Projeler yüklenemedi", error); }
};

const cikisYap = () => {
  localStorage.removeItem('girisYapildi');
  localStorage.removeItem('kullaniciRolu');
  router.push('/');
};

onMounted(verileriYukle);
</script>

<style scoped>
.container { max-width: 1000px; margin: 20px auto; padding: 20px; font-family: 'Segoe UI', sans-serif; }
.logo-yazisi { font-weight: 900; letter-spacing: 2px; color: #2c3e50; }
.kirmizi { color: #c0392b; }
input, select { padding: 12px; border: 1px solid #bdc3c7; border-radius: 6px; font-size: 14px; width: 100%; box-sizing: border-box; }
h3 { color: #2c3e50; border-bottom: 2px solid #bdc3c7; padding-bottom: 8px; margin-bottom: 20px; }
/* ================= P1 PDF ŞABLON STİLLERİ ================= */
.pdf-container { background: #ffffff; font-family: 'Helvetica Neue', Arial, sans-serif; color: #2c3e50; width: 210mm; margin: 0 auto; }
.pdf-sayfa { padding: 20mm 15mm; height: 297mm; box-sizing: border-box; position: relative; background: white; }
.sayfa-sonu { page-break-after: always; clear: both; }
.kapak-sayfasi { background: linear-gradient(135deg, #2c3e50 0%, #1a252f 100%); color: white; display: flex; align-items: center; justify-content: center; text-align: center; }
.kapak-icerik { margin-top: 60mm; }
.pdf-logo { font-size: 55px; font-weight: 900; letter-spacing: 4px; margin: 0; }
.kapak-icerik h2 { font-size: 26px; letter-spacing: 2px; margin-top: 20px; }
.alt-baslik { font-size: 14px; opacity: 0.7; }
.cizgi { width: 80mm; height: 4px; background-color: #c0392b; margin: 15px auto; }
.kapak-alt-bilgi { position: absolute; bottom: 25mm; left: 0; right: 0; font-size: 13px; opacity: 0.6; }
.pdf-baslik-alani { border-bottom: 3px solid #2c3e50; padding-bottom: 10px; margin-bottom: 25px; }
.pdf-baslik-alani h3 { margin: 0; font-size: 18px; color: #2c3e50; }
.pdf-metin-kutusu { background: #f8f9fa; padding: 15px; border-radius: 6px; border-left: 5px solid #c0392b; }
.pdf-metin-kutusu h4 { margin: 0 0 10px 0; color: #1a252f; }
.pdf-ozet-tablo { width: 100%; border-collapse: collapse; font-size: 13px; }
.pdf-ozet-tablo td { padding: 8px 5px; border-bottom: 1px solid #edf2f7; }
.sartlar-listesi p { font-size: 13px; line-height: 1.8; margin-bottom: 12px; }
.imza-kutu { border: 1px dashed #bdc3c7; padding: 15px; width: 45%; text-align: center; font-size: 12px; border-radius: 6px; }
.pdf-malzeme-tablosu { width: 100%; border-collapse: collapse; font-size: 11px; }
.pdf-malzeme-tablosu th { background-color: #2c3e50; color: white; padding: 10px; text-align: left; border: 1px solid #34495e; }
.pdf-malzeme-tablosu td { padding: 8px; border: 1px solid #e2e8f0; }
.pdf-malzeme-tablosu tbody tr:nth-child(even) { background-color: #f8fafc; }
</style>