<template>
  <div class="container">
    
    <UstMenu />

    <div class="form-kutusu" style="background: white; padding: 30px; border-radius: 10px; border-left: 8px solid #8e44ad; box-shadow: 0 6px 12px rgba(0,0,0,0.08);">
      <h3>Kayıtlı Panoları İnceleme Ekranı</h3>
      <div class="form-grubu" style="display: flex; flex-direction: column; gap: 15px;">
        <div class="ikili-sutun" style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
          <select v-model="inceleProjeId">
            <option disabled value="">Hangi Projedeki Pano?</option>
            <option v-for="p in projeler" :key="p.id" :value="p.id">{{ p.proje_adi }}</option>
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

  <div id="p1-teklif-sablonu" class="pdf-container">
   <table class="pdf-detay-tablosu">
     <thead>
       <tr>
         <th>NU.</th>
         <th>MALZEME ADI</th>
         <th>MARKA</th>          <th>SİPARİŞ NO</th>     <th>ADET</th>
       </tr>
     </thead>
     <tbody>
       <tr v-for="(item, index) in filtrelenmisPanoIcerigi" :key="index">
         <td>{{ index + 1 }}</td>
         <td>{{ item.malzeme }}</td>
         <td>{{ item.marka || '-' }}</td> <td>{{ item.siparis_no || '-' }}</td>
         <td>{{ item.adet }}</td>
       </tr>
     </tbody>
   </table>
</div>

    <div class="pdf-sayfa">
      <div class="kapak-logo-alani">
        <h1 class="temkon-logo">TEM<span style="color:red">K</span>ON</h1>
        <div class="kirmizi-cizgi"></div>
        <p class="kapak-alt-baslik">proje teklif dosyası</p>
      </div>

      <div class="kapak-bilgiler">
       <table class="kapak-tablo">
  <tr>
    <td class="baslik">FİRMA / COMPANY</td>
    <td class="iki-nokta">:</td>
    <td class="deger">{{ aktifProje.musteri || 'Belirtilmedi' }}</td>
  </tr>
  <tr>
    <td class="baslik">TEKLİF TARİHİ / OFFER DATE</td>
    <td class="iki-nokta">:</td>
    <td class="deger">{{ aktifProje.tarih || new Date().toLocaleDateString('tr-TR') }}</td>
  </tr>
  <tr>
    <td class="baslik">İLGİLİ PROJE / RELATED PROJECT</td>
    <td class="iki-nokta">:</td>
    <td class="deger">{{ aktifProje.proje_adi || 'Belirtilmedi' }}</td>
  </tr>
  <tr>
    <td class="baslik">REFERANS / REFERENCE ID</td>
    <td class="iki-nokta">:</td>
    <td class="deger">{{ aktifProje.referans_no || 'Atanmadı' }}</td>
  </tr>
  <tr>
    <td class="baslik">HAZIRLAYAN / PREPARED BY</td>
    <td class="iki-nokta">:</td>
    <td class="deger">{{ aktifProje.hazirlayan || 'Belirtilmedi' }}</td>
  </tr>
</table>
      </div>
    </div>

    <div class="pdf-sayfa">
      <div class="sayfa-ust-bilgi">
        <span class="sol-soluk">temkon hakkında</span>
        <h2 class="temkon-logo-kucuk">TEM<span style="color:red">K</span>ON</h2>
      </div>
      <div class="kirmizi-cizgi"></div>

      <div class="hakkinda-icerik">
        <h3 class="hakkinda-baslik">türk endüstriyel elektrik ve makine<br>kontrol ekipmanları teknolojisi</h3>
        <p class="hakkinda-metin">
          TEMKON 'Türk Endüstriyel Elektrik ve Makine Kontrol Ekipmanları Teknolojisi' çağın gerektirdiği teknolojik gelişme hızını endüstriyel tesislere uygulamak, üretim süreçlerinde insan faktörünü azaltmak, ürün kalitesindeki homojenliği sağlamak ve bu yüksek teknolojiyi türk sanayisine katma değer kazandıracak biçimde projelendirerek uygulamak üzere bilgi birikimini ve tecrübesini türk ekonomisinin hizmetine sunmaktan gurur duymaktadır.
        </p>
        <p class="hakkinda-metin mt-4">
          TEMKON, müşteri memnuniyetini mühendisliğin temel ilkeleri ile harmanlayıp çevreye ve doğaya saygılı, enerji verimliliği yüksek, teknolojik sürekliliği olan ve endüstrinin can damarındaki projelere, sürekli kendini yenileyen dinamik kadrosu ve her gün yenilenen teknolojisiyle cevap vermeye devam edecektir.
        </p>
        
        <div class="hakkinda-vizyon">
          <p><strong>yenilikçi</strong> - sürekli düşün, sürekli geliştir</p>
          <p><strong>teknik</strong> - mühendislik, know how, işgücü</p>
          <p><strong>projeksiyon</strong> - yüksel, parla, birlikte çalış</p>
        </div>
      </div>
    </div>

    <div class="pdf-sayfa">
      <div class="sayfa-ust-bilgi">
        <span class="sol-soluk">proje teklifi</span>
        <h2 class="temkon-logo-kucuk">TEM<span style="color:red">K</span>ON</h2>
      </div>
      <div class="kirmizi-cizgi"></div>

      <div class="teklif-giris">
        Fiyat teklifimiz aşağıdaki tablo ve ticari maddelerden ibarettir. Teklifimizin olumlu karşılanacağını umuyoruz. TEMKON olarak <strong>{{ yeniProje.musteri }}</strong> ile çalışmaktan kıvanç duyacağız.
      </div>

      <h3 class="kirmizi-baslik-ortali">PROJE TEKLİFİ</h3>

      <table class="teklif-tablosu">
        <thead>
          <tr>
            <th>NU.</th>
            <th>TANIM</th>
            <th>ADET</th>
            <th>ADET FİYATI</th>
            <th>TOPLAM FİYAT</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>1</td>
            <td>{{ yeniProje.proje_adi }} - Kontrol Sistemi Panolarının Projelendirilmesi ve İmalatı İçin Gerekli Malzeme Temini</td>
            <td>1</td>
            <td>{{ (dinamikAraToplam || 0).toLocaleString('tr-TR', {minimumFractionDigits: 2}) }} ₺</td>
            <td>{{ (dinamikAraToplam || 0).toLocaleString('tr-TR', {minimumFractionDigits: 2}) }} ₺</td>
          </tr>
          <tr>
            <td>2</td>
            <td>Saha Montajı İçin Gerekli Kablo, Kablo Kanalı, Saha Montaj Malzemesi Temini ve İşçilik</td>
            <td>1</td>
            <td>{{ (iscilikGideri || 0).toLocaleString('tr-TR', {minimumFractionDigits: 2}) }} ₺</td>
            <td>{{ (iscilikGideri || 0).toLocaleString('tr-TR', {minimumFractionDigits: 2}) }} ₺</td>
          </tr>
        </tbody>
        <tfoot>
          <tr>
            <td colspan="4" class="sag-hizala"><strong>PROJE TOPLAMI (KDV HARİÇ):</strong></td>
            <td><strong>{{ ((dinamikAraToplam || 0) + (iscilikGideri || 0)).toLocaleString('tr-TR', {minimumFractionDigits: 2}) }} ₺</strong></td>
          </tr>
        </tfoot>
      </table>
    </div>

    <div class="pdf-sayfa">
      <div class="sayfa-ust-bilgi">
        <span class="sol-soluk">ticari şartlar</span>
        <h2 class="temkon-logo-kucuk">TEM<span style="color:red">K</span>ON</h2>
      </div>
      <div class="kirmizi-cizgi"></div>

      <h3 class="siyah-baslik-ortali">TİCARİ ve TEKNİK ŞARTLAR</h3>

      <ol class="sartlar-listesi">
        <li>Teklif edilen fiyatlara KDV dahil değildir.</li>
        <li>Döviz verilen tekliflerde fatura kesim tarihindeki TCMB efektif satış kuru esas alınacaktır.</li>
        <li>Teklifimiz sahadaki panolara malzeme temini ve montajından ibarettir.</li>
        <li>Teklifin geçerlilik süresi 15 gündür.</li>
        <li>Ödeme şekli: %40 Sipariş ile birlikte avans, kalan tutar pano tesliminde nakit/havale şeklindedir.</li>
      </ol>

      <div class="imza-alani">
        <p class="imza-sirket-adi"><strong>TEMKON Endüstriyel Elektrik Yazılım Bilgisayar ve Elektronik Sistemler İnş. San. Tic. Ltd. Şti.</strong></p>
        <div class="kase-kutusu">
          <p class="soluk-yazi">Kaşe ve İmza</p>
        </div>
      </div>
    </div>

    <div class="pdf-sayfa" v-if="filtrelenmisPanoIcerigi && filtrelenmisPanoIcerigi.length > 0">
      <div class="sayfa-ust-bilgi">
        <span class="sol-soluk">detay bilgiler</span>
        <h2 class="temkon-logo-kucuk">TEM<span style="color:red">K</span>ON</h2>
      </div>
      <div class="kirmizi-cizgi"></div>

      <h3 class="siyah-baslik-ortali">PROJE DETAYLARI</h3>

      <div class="detay-tablo-kapsayici">
        <div class="mavi-baslik">PANOLAR DETAYLI MALZEME LİSTESİ</div>
        <table class="detay-tablosu">
          <thead>
            <tr>
              <th style="width: 10%">NU.</th>
              <th style="width: 45%">MALZEME ADI</th>
              <th style="width: 15%">MARKA</th>
              <th style="width: 20%">SİPARİŞ NUMARASI</th>
              <th style="width: 10%">ADET</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in filtrelenmisPanoIcerigi" :key="index">
              <td style="text-align: center;">{{ index + 1 }}</td>
              <td>{{ item.malzeme }}</td>
              <td>{{ item.marka || '-' }}</td>
              <td>{{ item.siparis_kodu || '-' }}</td>
              <td style="text-align: center; font-weight: bold;">{{ item.adet }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      
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
import { API_BASE } from '../config' // Klasör yapına göre yol farklıysa düzelt
const router = useRouter();
onMounted(() => {
  if (!localStorage.getItem('girisYapildi')) {
    router.push('/');
    return;
  }
  verileriYukle();
});

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
  musteri: '',
  son_kullanici: '',
  lokasyon: '',
  proje_adi: '',
  teklif_konusu: '',
  hazirlayan: '', 
  teklif_tarihi: '',
  teklif_referans_no: ''
})


const aktifProje = computed(() => {
  if (!projeler.value || !inceleProjeId.value) return {};
  
  // Vue'nun Proxy kutusunu kırıp saf listeyi alıyoruz
  const safListe = JSON.parse(JSON.stringify(projeler.value));
  const arananId = String(inceleProjeId.value).trim(); // Boşlukları bile siler
  
  // Hem id hem proje_id alanlarını tarar
  const bulunan = safListe.find(x => String(x.id).trim() === arananId || String(x.proje_id).trim() === arananId);
  
  return bulunan || {};
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
   const response = await axios.get(`${API_BASE}/projeler/${inceleProjeId.value}/maliyet-raporu`);
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

  const p = aktifProje.value; 

  // --- YENİ NESİL HATA AVCISI ---
  if (!p || Object.keys(p).length === 0) {
    const safListe = JSON.parse(JSON.stringify(projeler.value));
    alert("DİKKAT: Proje yine bulunamadı! F12 Konsoluna bak.");
    console.error("ARANAN ID:", inceleProjeId.value);
    console.error("ELİMİZDEKİ VERİLER (AÇIK HALİ):\n" + JSON.stringify(safListe, null, 2));
    return; // Hata varsa PDF basmasın
  }

  // Dosya adını güvenli oluşturma
  const musteriAdi = p.musteri ? String(p.musteri).replace(/\s+/g, '_') : 'Musteri';
  const refNo = p.referans_no ? String(p.referans_no) : 'Teklif_Dosyasi';
  const dinamikDosyaAdi = `${musteriAdi}_${refNo}.pdf`;

  const secenekler = {
    margin: 0,
    filename: dinamikDosyaAdi,
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: { scale: 2, useCORS: true },
    jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
    pagebreak: { mode: ['avoid-all', 'css', 'legacy'] }
  };
  
  html2pdf().set(secenekler).from(element).save();
};

const verileriYukle = async () => {
  try {
    const response = await axios.get(`${API_BASE}/projeler/listele`);
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




/* PDF GENEL AYARLARI */
.pdf-container {
  width: 210mm; /* A4 Genişliği */
  background: white;
  color: black;
  font-family: Arial, sans-serif;
  font-size: 13px;
}

/* SAYFA BÖLME MANTIĞI */
.pdf-sayfa {
  padding: 15mm;
  page-break-after: always;
  min-height: 260mm; 
  position: relative;
}
.pdf-sayfa:last-child {
  page-break-after: auto;
}



/* LOGO VE ÜST ÇİZGİLER */
.temkon-logo { font-size: 28px; font-weight: 900; margin: 0; text-align: right; }
.temkon-logo-kucuk { font-size: 20px; font-weight: 900; margin: 0; text-align: right; }
.kirmizi-cizgi { border-bottom: 3px solid #e30613; margin-top: 5px; margin-bottom: 20px; }
.sayfa-ust-bilgi { display: flex; justify-content: space-between; align-items: flex-end; }
.sol-soluk { color: #95a5a6; font-style: italic; font-size: 11px; }

/* 1. SAYFA - KAPAK TASARIMI */
.kapak-logo-alani { margin-top: 150px; }
.kapak-alt-baslik { color: #7f8c8d; font-size: 14px; text-align: right; margin-top: -15px; }
.kapak-bilgiler { margin-top: 100px; }
.kapak-tablo { width: 100%; border-collapse: collapse; }
.kapak-tablo td { padding: 8px; border: 1px solid #bdc3c7; }
.kapak-tablo .baslik { width: 40%; color: #7f8c8d; font-size: 12px; }
.kapak-tablo .iki-nokta { width: 2%; text-align: center; border-left: none; border-right: none; }
.kapak-tablo .deger { font-weight: bold; }

/* 2. SAYFA - HAKKINDA */
.hakkinda-icerik { padding: 40px; text-align: center; }
.hakkinda-baslik { font-size: 18px; color: #555; margin-bottom: 30px; }
.hakkinda-metin { color: #7f8c8d; line-height: 1.6; text-align: justify; }
.mt-4 { margin-top: 20px; }
.hakkinda-vizyon { margin-top: 50px; font-size: 12px; color: #333; text-align: center; }

/* 3. SAYFA - TEKLİF TABLOSU */
.teklif-giris { border: 1px solid #ccc; padding: 15px; text-align: center; margin-bottom: 30px; font-weight: bold; }
.kirmizi-baslik-ortali { color: #e30613; text-align: center; margin-bottom: 10px; }
.teklif-tablosu { width: 100%; border-collapse: collapse; border: 2px solid black; }
.teklif-tablosu th { background-color: white; border: 2px solid black; border-bottom: 3px solid black; padding: 10px; font-size: 11px; }
.teklif-tablosu td { border: 1px solid black; padding: 10px; vertical-align: top; }
.sag-hizala { text-align: right; }

/* 4. SAYFA - ŞARTLAR VE İMZA */
.siyah-baslik-ortali { text-align: center; border-top: 2px solid black; border-bottom: 2px solid black; padding: 5px 0; margin-bottom: 20px; }
.sartlar-listesi { line-height: 1.8; margin-bottom: 50px; }
.imza-alani { margin-top: 80px; text-align: center; }
.imza-sirket-adi { font-size: 14px; margin-bottom: 20px; }
.kase-kutusu { border: 1px dashed #ccc; width: 300px; height: 150px; margin: 0 auto; display: flex; align-items: center; justify-content: center; }
.soluk-yazi { color: #bdc3c7; font-style: italic; }

/* 5. SAYFA - DETAY TABLOSU */
.mavi-baslik { background-color: #a9cce3; padding: 8px; text-align: center; font-weight: bold; border: 2px solid #2c3e50; border-bottom: none; }
.detay-tablosu { width: 100%; border-collapse: collapse; border: 2px solid #2c3e50; }
.detay-tablosu th { background-color: #2c3e50; color: white; padding: 8px; font-size: 10px; border: 1px solid #2c3e50; }
.detay-tablosu td { border: 1px solid #2c3e50; padding: 6px; font-size: 11px; }
</style>