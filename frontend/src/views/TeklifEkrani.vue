<template>
  <div class="sistem-container">

    <UstMenu />

    <div class="header-alani">
      <h2>📊 Proje ve Pano Analiz Merkezi</h2>
      <p>Kayıtlı projelerin maliyet simülasyonlarını, satış tablolarını ve detaylı analizlerini buradan yönetin.</p>
    </div>

    <!-- FİLTRELEME VE ARAMA KARTI -->
    <div class="filtre-karti">
      <div class="filtre-grid">
        <div class="input-grubu">
          <label>📁 Proje Seçimi</label>
          <select v-model="inceleProjeId" class="modern-select">
            <option disabled value="">İncelenecek Projeyi Seçin...</option>
            <option v-for="p in projeler" :key="p.id" :value="p.id">{{ p.proje_adi }}</option>
          </select>
        </div>
        
        <div class="input-grubu">
          <label>⚙️ Görünüm / Pano Tipi</label>
          <select v-model="incelePanoTuru" class="modern-select">
            <option disabled value="">Filtre Seçin...</option>
            <option value="TÜM PANOLAR">🔥 Tüm Panoları Getir</option>
            <option value="TÜM MCC LER">⚡ Tüm MCC Panolarını Birleştir</option>
            <option value="TÜM REM LER">🔌 Tüm REM Panolarını Birleştir</option>
            <optgroup label="Tekil Panolar">
              <option v-for="pano in ['ADP 1', 'MCC 1', 'MCC 2', 'MCC 3', 'MCC 4', 'MCC 5', 'REM 100', 'REM 200', 'REM 300', 'REM 400', 'REM 500', 'KONTROL S.', 'SAHA']" :key="pano" :value="pano">{{ pano }}</option>
            </optgroup>
          </select>
        </div>

        <div class="input-grubu flex-alt">
          <button @click="panoIcerigiGetir" class="btn-filtrele">
            🔍 Kayıtları Getir
          </button>
        </div>
      </div>
    </div>

    <!-- VERİLER GELDİĞİNDE AÇILAN ALAN -->
    <transition name="fade">
      <div v-if="panoIcerigi.length > 0" class="sonuc-alani">
        
        <div class="aksiyon-paneli">
          <h4 class="sonuc-baslik">{{ incelePanoTuru }} İçeriği:</h4>
          
          <div class="buton-grubu">
            <button @click="excelIndir" class="btn-excel">
              📊 Excel İndir
            </button>
            <button v-if="kullaniciRolu !== 'saha_ekibi'" @click="pdfIndir" class="btn-pdf">
              📄 Resmi Teklif (PDF) Çıkar
            </button>
          </div>
        </div>

        <!-- MODERN SEKME (TAB) MENÜSÜ -->
        <div v-if="kullaniciRolu === 'yonetici' || kullaniciRolu === 'teklif_ekibi'" class="sekme-menusu">
          <button 
            :class="{ aktif: seciliTablo === 'satis' }" 
            @click="seciliTablo = 'satis'">
            🛍️ Müşteri Satış Tablosu
          </button>
          <button 
            v-if="kullaniciRolu === 'yonetici'" 
            :class="{ aktif: seciliTablo === 'maliyet', yonetici: seciliTablo === 'maliyet' }" 
            @click="seciliTablo = 'maliyet'">
            💼 Yönetici Maliyet ve Simülasyon
          </button>
          <button 
            :class="{ aktif: seciliTablo === 'grafik', grafik: seciliTablo === 'grafik' }" 
            @click="seciliTablo = 'grafik'">
            📈 Döviz ve Kâr Analizi
          </button>
        </div>

        <!-- 1. MÜŞTERİ SATIŞ TABLOSU -->
        <div class="tablo-kart" v-if="kullaniciRolu === 'teklif_ekibi' || (kullaniciRolu === 'yonetici' && seciliTablo === 'satis')">
          <table class="kurumsal-tablo">
            <thead>
              <tr class="tablo-ana-baslik"><th colspan="9">PROJE SATIŞ VE FİYATLANDIRMA LİSTESİ</th></tr>
              <tr class="tablo-alt-baslik">
                <th>PANO TÜRÜ</th><th>MALZEME ADI</th><th>LİSTE FİYATI</th><th>İSKONTO</th>
                <th>NET FİYAT</th><th>ADET</th><th>TOPLAM</th><th>KUR</th><th>NOTLAR</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in filtrelenmisPanoIcerigi" :key="index">
                <!-- 1. PANO TÜRÜ -->
                <td @dblclick="duzenlemeyiAc(index, 'pano')" :class="{ 'manuel-duzenlendi': item.degistirildi }">
                  <span v-if="duzenlenenHucre !== index + '-pano'">{{ item.pano }}</span>
                  <input v-else v-model="item.pano" type="text" @blur="kaydetVeKapat(item, index, 'pano')" @keyup.enter="kaydetVeKapat(item, index, 'pano')" class="hucre-input" autofocus>
                </td>
                <!-- 2. MALZEME ADI -->
                <td @dblclick="duzenlemeyiAc(index, 'malzeme')" :class="{ 'manuel-duzenlendi': item.degistirildi }" style="text-align: left;">
                  <span v-if="duzenlenenHucre !== index + '-malzeme'">{{ item.malzeme }}</span>
                  <input v-else v-model="item.malzeme" type="text" @blur="kaydetVeKapat(item, index, 'malzeme')" @keyup.enter="kaydetVeKapat(item, index, 'malzeme')" class="hucre-input" autofocus>
                </td>
                <!-- 3. LİSTE FİYATI -->
                <td @dblclick="duzenlemeyiAc(index, 'liste_fiyati')" :class="{ 'manuel-duzenlendi': item.degistirildi }" class="kalin">
                  <span v-if="duzenlenenHucre !== index + '-liste_fiyati'">{{ item.liste_fiyati }} {{ item.para_birimi }}</span>
                  <input v-else v-model="item.liste_fiyati" type="number" step="0.01" @blur="kaydetVeKapat(item, index, 'liste_fiyati')" @keyup.enter="kaydetVeKapat(item, index, 'liste_fiyati')" class="hucre-input" autofocus>
                </td>
                <!-- 4. İSKONTO -->
                <td @dblclick="duzenlemeyiAc(index, 'iskonto_orani')" :class="{ 'manuel-duzenlendi': item.degistirildi }" class="vurgu-sari">
                  <span v-if="duzenlenenHucre !== index + '-iskonto_orani'">% {{ item.iskonto_orani ? (item.iskonto_orani * 100).toFixed(0) : '0' }}</span>
                  <input v-else v-model="item.iskonto_orani" type="number" step="0.01" @blur="kaydetVeKapat(item, index, 'iskonto_orani')" @keyup.enter="kaydetVeKapat(item, index, 'iskonto_orani')" class="hucre-input" autofocus>
                </td>
                <!-- 5. NET FİYAT -->
                <td @dblclick="duzenlemeyiAc(index, 'birim_proje_tl')" :class="{ 'manuel-duzenlendi': item.degistirildi }" class="vurgu-kirmizi">
                  <span v-if="duzenlenenHucre !== index + '-birim_proje_tl'">{{ item.birim_proje_tl }} ₺</span>
                  <input v-else v-model="item.birim_proje_tl" type="number" step="0.01" @blur="kaydetVeKapat(item, index, 'birim_proje_tl')" @keyup.enter="kaydetVeKapat(item, index, 'birim_proje_tl')" class="hucre-input" autofocus>
                </td>
                <!-- 6. ADET -->
                <td @dblclick="duzenlemeyiAc(index, 'adet')" :class="{ 'manuel-duzenlendi': item.degistirildi }" class="vurgu-yesil">
                  <span v-if="duzenlenenHucre !== index + '-adet'">{{ item.adet }}</span>
                  <input v-else v-model="item.adet" type="number" @blur="kaydetVeKapat(item, index)" @keyup.enter="kaydetVeKapat(item, index)" class="hucre-input" autofocus>
                </td>
                <!-- 7. TOPLAM -->
                <td @dblclick="duzenlemeyiAc(index, 'toplam_proje_tl')" :class="{ 'manuel-duzenlendi': item.degistirildi }" class="vurgu-kirmizi">
                  <span v-if="duzenlenenHucre !== index + '-toplam_proje_tl'">{{ item.toplam_proje_tl }} ₺</span>
                  <input v-else v-model="item.toplam_proje_tl" type="number" step="0.01" @blur="kaydetVeKapat(item, index, 'toplam_proje_tl')" @keyup.enter="kaydetVeKapat(item, index, 'toplam_proje_tl')" class="hucre-input" autofocus>
                </td>
                <!-- 8. KUR -->
                <td @dblclick="duzenlemeyiAc(index, 'kur_degeri')" :class="{ 'manuel-duzenlendi': item.degistirildi }" class="vurgu-sari">
                  <span v-if="duzenlenenHucre !== index + '-kur_degeri'">{{ item.kur_degeri }} ({{ item.para_birimi }})</span>
                  <input v-else v-model="item.kur_degeri" type="number" step="0.0001" @blur="kaydetVeKapat(item, index, 'kur_degeri')" @keyup.enter="kaydetVeKapat(item, index, 'kur_degeri')" class="hucre-input" autofocus>
                </td>
                <!-- 9. NOTLAR -->
                <td @dblclick="duzenlemeyiAc(index, 'notlar')" :class="{ 'manuel-duzenlendi': item.degistirildi }">
                  <span v-if="duzenlenenHucre !== index + '-notlar'">{{ item.notlar || '-' }}</span>
                  <input v-else v-model="item.notlar" type="text" @blur="kaydetVeKapat(item, index, 'notlar')" @keyup.enter="kaydetVeKapat(item, index, 'notlar')" class="hucre-input" autofocus>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 2. YÖNETİCİ MALİYET VE SİMÜLASYON -->
        <div v-if="kullaniciRolu === 'yonetici' && seciliTablo === 'maliyet'">
          <div class="simulasyon-paneli">
            <div class="sim-input">
              <label>🎯 Genel Kâr Marjı (%):</label>
              <input type="number" v-model="genelKarMarji">
            </div>
            <div class="sim-input">
              <label>👷‍♂️ İşçilik / Saha Gideri (₺):</label>
              <input type="number" v-model="iscilikGideri">
            </div>
            <div class="sim-durum">
              <span class="sim-baslik">⚡ Simülasyon Aktif</span>
              <span class="sim-alt">Değerleri değiştirdiğiniz an tablo f(x) güncellenir.</span>
            </div>
          </div>

          <div class="tablo-kart ozel-scroll">
            <table class="kurumsal-tablo detayli-tablo">
              <thead>
                <tr class="tablo-ana-baslik"><th colspan="13">PROJEYE SATIŞ ŞARTLARI GEÇERLİ (MALİYET ANALİZİ)</th></tr>
                <tr class="tablo-alt-baslik">
                  <th>SIRA</th><th>MALİYET KALEMİ</th><th>MALİYET GRUBU</th><th>MALİYET TRY</th>
                  <th>MALİYET EUR</th><th>MALİYET USD</th><th>TEKLİF BEDELİ</th><th>± % İSK.</th>
                  <th class="fx-kirmizi">f(x) NET FİYAT</th><th>ADET</th><th class="fx-kirmizi">f(x) TOPLAM</th>
                  <th>KUR</th><th>NOTLAR</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in filtrelenmisPanoIcerigi" :key="index" class="satir-gri">
                  <!-- SIRA -->
                  <td>{{ index + 1 }}</td>
                  <!-- MALİYET KALEMİ -->
                  <td @dblclick="duzenlemeyiAc(index, 'malzeme')" :class="{ 'manuel-duzenlendi': item.degistirildi }" style="text-align: left; background: white;">
                    <span v-if="duzenlenenHucre !== index + '-malzeme'">{{ item.malzeme }}</span>
                    <input v-else v-model="item.malzeme" type="text" @blur="kaydetVeKapat(item, index, 'malzeme')" @keyup.enter="kaydetVeKapat(item, index, 'malzeme')" class="hucre-input" autofocus>
                  </td>
                  <!-- MALİYET GRUBU -->
                  <td @dblclick="duzenlemeyiAc(index, 'pano')" :class="{ 'manuel-duzenlendi': item.degistirildi }" style="background: white;">
                    <span v-if="duzenlenenHucre !== index + '-pano'">{{ item.pano }}</span>
                    <input v-else v-model="item.pano" type="text" @blur="kaydetVeKapat(item, index, 'pano')" @keyup.enter="kaydetVeKapat(item, index, 'pano')" class="hucre-input" autofocus>
                  </td>
                  <!-- MALİYET TRY -->
                  <td @dblclick="duzenlemeyiAc(index, 'birim_proje_tl')" :class="{ 'manuel-duzenlendi': item.degistirildi }" class="kalin">
                    <span v-if="duzenlenenHucre !== index + '-birim_proje_tl'">
                      {{ item.para_birimi === 'TRY' ? item.birim_proje_tl : (item.birim_proje_tl * item.kur_degeri).toFixed(2) }} ₺
                    </span>
                    <input v-else v-model="item.birim_proje_tl" type="number" step="0.01" @blur="kaydetVeKapat(item, index, 'birim_proje_tl')" @keyup.enter="kaydetVeKapat(item, index, 'birim_proje_tl')" class="hucre-input" autofocus>
                  </td>
                  <!-- EUR / USD -->
                  <td>{{ item.para_birimi === 'EUR' ? item.birim_proje_tl + ' €' : '-' }}</td>
                  <td>{{ item.para_birimi === 'USD' ? item.birim_proje_tl + ' $' : '-' }}</td>
                  
                  <!-- f(x) TEKLİF BEDELİ -->
                  <td class="vurgu-yesil kalin">
                    {{ (item.birim_proje_tl * (1 + (genelKarMarji || 0) / 100)).toFixed(2) }} ₺
                  </td>
                  
                  <!-- İSKONTO -->
                  <td @dblclick="duzenlemeyiAc(index, 'iskonto_orani')" :class="{ 'manuel-duzenlendi': item.degistirildi }">
                    <span v-if="duzenlenenHucre !== index + '-iskonto_orani'">% {{ item.iskonto_orani ? (item.iskonto_orani * 100).toFixed(0) : '0' }}</span>
                    <input v-else v-model="item.iskonto_orani" type="number" step="0.01" @blur="kaydetVeKapat(item, index, 'iskonto_orani')" @keyup.enter="kaydetVeKapat(item, index, 'iskonto_orani')" class="hucre-input" autofocus>
                  </td>
                  
                  <!-- f(x) NET FİYAT -->
                  <td class="fx-sari kalin fx-kirmizi-yazi">
                    {{ ((item.birim_proje_tl * (1 + (genelKarMarji || 0) / 100)) * (1 - (item.iskonto_orani || 0))).toFixed(2) }} ₺
                  </td>
                  
                  <!-- ADET -->
                  <td @dblclick="duzenlemeyiAc(index, 'adet')" :class="{ 'manuel-duzenlendi': item.degistirildi }" class="kalin">
                    <span v-if="duzenlenenHucre !== index + '-adet'">{{ item.adet }}</span>
                    <input v-else v-model="item.adet" type="number" @blur="kaydetVeKapat(item, index)" @keyup.enter="kaydetVeKapat(item, index)" class="hucre-input" autofocus>
                  </td> 
                  
                  <!-- f(x) TOPLAM -->
                  <td class="fx-sari kalin fx-kirmizi-yazi">
                    {{ (((item.birim_proje_tl * (1 + (genelKarMarji || 0) / 100)) * (1 - (item.iskonto_orani || 0))) * item.adet).toFixed(2) }} ₺
                  </td>
                  
                  <!-- KUR -->
                  <td @dblclick="duzenlemeyiAc(index, 'kur_degeri')" :class="{ 'manuel-duzenlendi': item.degistirildi }">
                    <span v-if="duzenlenenHucre !== index + '-kur_degeri'">{{ item.kur_degeri }} ({{ item.para_birimi }})</span>
                    <input v-else v-model="item.kur_degeri" type="number" step="0.0001" @blur="kaydetVeKapat(item, index, 'kur_degeri')" @keyup.enter="kaydetVeKapat(item, index, 'kur_degeri')" class="hucre-input" style="width: 70px;" autofocus>
                  </td>
                  
                  <!-- NOTLAR -->
                  <td @dblclick="duzenlemeyiAc(index, 'notlar')" :class="{ 'manuel-duzenlendi': item.degistirildi }" style="background: white;">
                    <span v-if="duzenlenenHucre !== index + '-notlar'">{{ item.notlar || '-' }}</span>
                    <input v-else v-model="item.notlar" type="text" @blur="kaydetVeKapat(item, index, 'notlar')" @keyup.enter="kaydetVeKapat(item, index, 'notlar')" class="hucre-input" autofocus>
                  </td>
                </tr>
              </tbody>
              
              <!-- DİNAMİK ARA TOPLAM / FOOTER -->
              <tfoot v-if="filtrelenmisPanoIcerigi.length > 0">
                <tr class="footer-koyu">
                  <td colspan="10">ARA TOPLAM (MALZEME):</td>
                  <td>{{ dinamikAraToplam.toFixed(2) }} ₺</td>
                  <td colspan="2"></td>
                </tr>
                <tr class="footer-orta">
                  <td colspan="10">İŞÇİLİK / SAHA GİDERİ:</td>
                  <td>+ {{ iscilikGideri || 0 }} ₺</td>
                  <td colspan="2"></td>
                </tr>
                <tr class="footer-kirmizi">
                  <td colspan="10">GENEL PROJE SATIŞ BEDELİ:</td>
                  <td class="vurgu-altin">{{ (dinamikAraToplam + (iscilikGideri || 0)).toFixed(2) }} ₺</td>
                  <td colspan="2"></td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>

        <!-- 3. SAHA / İMALAT TABLOSU (SADECE SAHA EKİBİ) -->
        <div class="tablo-kart" v-if="kullaniciRolu === 'saha_ekibi'">
          <table class="kurumsal-tablo">
            <thead>
              <tr class="tablo-ana-baslik koyu"><th colspan="5">TEKNİK KONFİGÜRASYON VE MALZEME LİSTESİ (İMALAT)</th></tr>
              <tr class="tablo-alt-baslik">
                <th>SIRA</th><th>PANO TÜRÜ</th><th>SİPARİŞ KODU</th><th>MALZEME ADI</th><th>ADET</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in filtrelenmisPanoIcerigi" :key="index">
                <td>{{ index + 1 }}</td>
                <td class="kalin">{{ item.pano }}</td>
                <td class="kod-font">{{ item.siparis_kodu || 'M-CODE-' + index }}</td>
                <td style="text-align: left;">{{ item.malzeme }}</td>
                <td class="vurgu-yesil kalin">{{ item.adet }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 4. GRAFİK / KÂR ANALİZİ EKRANI -->
        <div class="grafik-karti" v-if="(kullaniciRolu === 'yonetici' || kullaniciRolu === 'teklif_ekibi') && seciliTablo === 'grafik'">
          <h3>📈 Proje Risk ve Kâr Simülasyonu</h3>
          <div class="grafik-grid">
            
            <div class="pasta-karti">
              <h4>Maliyetlerin Döviz Dağılımı (₺ Karşılığı)</h4>
              <div class="pasta-grafik" :style="{ background: dovizDagilimi.pastaCss }"></div>
              <div class="pasta-lejant">
                <span class="try">🟦 TRY: %{{ dovizDagilimi.tryYuzde.toFixed(1) }}</span>
                <span class="eur">🟥 EUR: %{{ dovizDagilimi.eurYuzde.toFixed(1) }}</span>
                <span class="usd">🟨 USD: %{{ dovizDagilimi.usdYuzde.toFixed(1) }}</span>
              </div>
            </div>

            <div class="analiz-karti">
              <h4>Satış Fiyatı ve Kâr Belirleme</h4>
              <div class="analiz-form">
                <label>🎯 Uygulanacak Kâr Marjı (%):</label>
                <input type="number" v-model="genelKarMarji">
                <label>👷‍♂️ İşçilik / Saha Gideri (₺):</label>
                <input type="number" v-model="iscilikGideri">
              </div>
              <div class="analiz-sonuc">
                <p>Saf Malzeme Maliyeti: <span>{{ dovizDagilimi.genelToplam.toFixed(2) }} ₺</span></p>
                <p>Kâr + İşçilik Hedefi: <span class="yesil-arti">+ {{ ((dinamikAraToplam + iscilikGideri) - dovizDagilimi.genelToplam).toFixed(2) }} ₺</span></p>
                <hr>
                <h3>TEKLİF BEDELİ: {{ (dinamikAraToplam + iscilikGideri).toFixed(2) }} ₺</h3>
              </div>
            </div>

          </div>
        </div>

      </div>
      <div v-else-if="panoAcildi" class="bos-durum">
        ⚠️ Seçilen kriterlere uygun malzeme bulunamadı.
      </div>
    </transition>

    <!-- HİÇBİR ŞEKİLDE DOKUNULMAYAN / BOZULMAYAN PDF HTML YAPISI (GİZLİ) -->
    <div style="display: none;">
      <div id="p1-teklif-sablonu" class="pdf-container">

        <!-- SAYFA 1: KAPAK -->
        <div class="pdf-sayfa" style="page-break-after: always; display: flex; flex-direction: column; justify-content: space-between; height: 280mm; padding-top: 15mm; padding-bottom: 10mm; box-sizing: border-box; overflow: hidden;">
          <div>
            <div class="kapak-logo-alani">
              <h1 class="temkon-logo">TEM<span style="color:red">K</span>ON</h1>
              <div class="kirmizi-cizgi"></div>
              <p class="kapak-alt-baslik">proje teklif dosyası</p>
            </div>
            <div class="kapak-bilgiler">
              <table class="kapak-tablo">
                <tbody>
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
                </tbody>
              </table>
            </div>
          </div>
          
          <!-- FOOTER -->
          <div style="padding-left: 40px; padding-right: 40px;">
            <div style="font-weight: bold; color: #2c3e50; font-size: 12px; text-align: left; margin-bottom: 2px;">
              TEMKON Endüstriyel Elektrik San. Tic. Ltd. Şti.
            </div>
            <div style="border-top: 2px solid #c00000; width: 100%; margin-bottom: 5px;"></div>
            <div style="display: flex; justify-content: space-between; align-items: flex-end; color: #7f8c8d; font-size: 10px; text-align: left; line-height: 1.4;">
              <div>
                Özsan Sanayi Sitesi 30. Blok NO:25 Yeşilyurt / MALATYA<br>
                t: +90 (422) 238 55 11 &nbsp;&nbsp;&nbsp; f: +90 (422) 238 55 22 &nbsp;&nbsp;&nbsp; temkon.com.tr
              </div>
            </div>
          </div>
        </div>

        <!-- SAYFA 2: HAKKINDA -->
        <div class="pdf-sayfa" style="page-break-after: always; display: flex; flex-direction: column; justify-content: space-between; height: 280mm; padding-top: 15mm; padding-bottom: 10mm; box-sizing: border-box; overflow: hidden;">
          <div>
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
          
          <!-- FOOTER -->
          <div style="padding-left: 40px; padding-right: 40px;">
            <div style="font-weight: bold; color: #2c3e50; font-size: 12px; text-align: left; margin-bottom: 2px;">
              TEMKON Endüstriyel Elektrik San. Tic. Ltd. Şti.
            </div>
            <div style="border-top: 2px solid #c00000; width: 100%; margin-bottom: 5px;"></div>
            <div style="display: flex; justify-content: space-between; align-items: flex-end; color: #7f8c8d; font-size: 10px; text-align: left; line-height: 1.4;">
              <div>
                Özsan Sanayi Sitesi 30. Blok NO:25 Yeşilyurt / MALATYA<br>
                t: +90 (422) 238 55 11 &nbsp;&nbsp;&nbsp; f: +90 (422) 238 55 22 &nbsp;&nbsp;&nbsp; temkon.com.tr
              </div>
            </div>
          </div>
        </div>

        <!-- SAYFA 3: FİYAT TEKLİF TABLOSU -->
        <div class="pdf-sayfa" style="page-break-after: always; display: flex; flex-direction: column; justify-content: space-between; height: 280mm; padding-top: 15mm; padding-bottom: 10mm; box-sizing: border-box; overflow: hidden;">
          <div>
            <div class="sayfa-ust-bilgi">
              <span class="sol-soluk">proje teklifi</span>
              <h2 class="temkon-logo-kucuk">TEM<span style="color:red">K</span>ON</h2>
            </div>
            <div class="kirmizi-cizgi"></div>
            <div class="teklif-giris">
              Fiyat teklifimiz aşağıdaki tablo ve ticari maddelerden ibarettir. Teklifimizin olumlu karşılanacağını umuyoruz. TEMKON olarak <strong>{{ aktifProje.musteri || 'Değerli Müşterimiz' }}</strong> ile çalışmaktan kıvanç duyacağız.
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
                  <td>{{ aktifProje.proje_adi || 'Proje' }} - Kontrol Sistemi Panolarının Projelendirilmesi ve İmalatı İçin Gerekli Malzeme Temini</td>
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
          
          <!-- FOOTER -->
          <div style="padding-left: 40px; padding-right: 40px;">
            <div style="font-weight: bold; color: #2c3e50; font-size: 12px; text-align: left; margin-bottom: 2px;">
              TEMKON Endüstriyel Elektrik San. Tic. Ltd. Şti.
            </div>
            <div style="border-top: 2px solid #c00000; width: 100%; margin-bottom: 5px;"></div>
            <div style="display: flex; justify-content: space-between; align-items: flex-end; color: #7f8c8d; font-size: 10px; text-align: left; line-height: 1.4;">
              <div>
                Özsan Sanayi Sitesi 30. Blok NO:25 Yeşilyurt / MALATYA<br>
                t: +90 (422) 238 55 11 &nbsp;&nbsp;&nbsp; f: +90 (422) 238 55 22 &nbsp;&nbsp;&nbsp; temkon.com.tr
              </div>
            </div>
          </div>
        </div>

        <!-- SAYFA 4: TİCARİ ŞARTLAR -->
        <div class="pdf-sayfa" style="page-break-after: always; display: flex; flex-direction: column; justify-content: space-between; height: 280mm; padding-top: 15mm; padding-bottom: 10mm; box-sizing: border-box; overflow: hidden;">
          <div>
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
          
          <!-- FOOTER -->
          <div style="padding-left: 40px; padding-right: 40px;">
            <div style="font-weight: bold; color: #2c3e50; font-size: 12px; text-align: left; margin-bottom: 2px;">
              TEMKON Endüstriyel Elektrik San. Tic. Ltd. Şti.
            </div>
            <div style="border-top: 2px solid #c00000; width: 100%; margin-bottom: 5px;"></div>
            <div style="display: flex; justify-content: space-between; align-items: flex-end; color: #7f8c8d; font-size: 10px; text-align: left; line-height: 1.4;">
              <div>
                Özsan Sanayi Sitesi 30. Blok NO:25 Yeşilyurt / MALATYA<br>
                t: +90 (422) 238 55 11 &nbsp;&nbsp;&nbsp; f: +90 (422) 238 55 22 &nbsp;&nbsp;&nbsp; temkon.com.tr
              </div>
            </div>
          </div>
        </div>

        <!-- SAYFA 5: MALZEME DETAY LİSTESİ -->
        <div class="pdf-sayfa" v-if="filtrelenmisPanoIcerigi && filtrelenmisPanoIcerigi.length > 0" style="page-break-after: always; display: flex; flex-direction: column; justify-content: space-between; height: 280mm; padding-top: 15mm; padding-bottom: 10mm; box-sizing: border-box; overflow: hidden;">
          <div>
            <div class="sayfa-ust-bilgi">
              <span class="sol-soluk">detay bilgiler</span>
              <h2 class="temkon-logo-kucuk">TEM<span style="color:red">K</span>ON</h2>
            </div>
            <div class="kirmizi-cizgi"></div>
            <h3 class="siyah-baslik-ortali">PROJE DETAYLARI</h3>
            
            <div class="detay-tablo-kapsayici" style="margin-top: 20px;">
              <div style="background-color: #a9c4e4 !important; padding: 10px; text-align: center; font-weight: bold; border: 2px solid #2c3e50; border-bottom: none; font-size: 14px; color: #000 !important; -webkit-print-color-adjust: exact; print-color-adjust: exact;">
                PANOLAR DETAYLI MALZEME LİSTESİ
              </div>
              <table class="detay-tablosu" style="width: 100%; border-collapse: collapse; font-size: 13px; color: #000; border: 2px solid #2c3e50;">
                <thead>
                  <tr style="background-color: #34495e !important; color: white !important; -webkit-print-color-adjust: exact; print-color-adjust: exact;">
                    <th style="padding: 10px; border: 1px solid #2c3e50; width: 8%; text-align: center;">NU.</th>
                    <th style="padding: 10px; border: 1px solid #2c3e50; width: 42%; text-align: left;">MALZEME ADI</th>
                    <th style="padding: 10px; border: 1px solid #2c3e50; width: 15%; text-align: center;">MARKA</th>
                    <th style="padding: 10px; border: 1px solid #2c3e50; width: 25%; text-align: center;">SİPARİŞ NUMARASI</th>
                    <th style="padding: 10px; border: 1px solid #2c3e50; width: 10%; text-align: center;">ADET</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, index) in filtrelenmisPanoIcerigi" :key="index" style="page-break-inside: avoid;">
                    <td style="padding: 8px; border: 1px solid #2c3e50; text-align: center;">{{ index + 1 }}</td>
                    <td style="padding: 8px; border: 1px solid #2c3e50; text-align: left;">{{ item.malzeme }}</td>
                    <td style="padding: 8px; border: 1px solid #2c3e50; text-align: center;">{{ item.marka || '-' }}</td>
                    <td style="padding: 8px; border: 1px solid #2c3e50; text-align: center;">{{ item.siparis_kodu || item.siparis_no || '-' }}</td>
                    <td style="padding: 8px; border: 1px solid #2c3e50; text-align: center; font-weight: bold;">{{ item.adet }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          
          <!-- FOOTER -->
          <div style="padding-left: 40px; padding-right: 40px;">
            <div style="font-weight: bold; color: #2c3e50; font-size: 12px; text-align: left; margin-bottom: 2px;">
              TEMKON Endüstriyel Elektrik San. Tic. Ltd. Şti.
            </div>
            <div style="border-top: 2px solid #c00000; width: 100%; margin-bottom: 5px;"></div>
            <div style="display: flex; justify-content: space-between; align-items: flex-end; color: #7f8c8d; font-size: 10px; text-align: left; line-height: 1.4;">
              <div>
                Özsan Sanayi Sitesi 30. Blok NO:25 Yeşilyurt / MALATYA<br>
                t: +90 (422) 238 55 11 &nbsp;&nbsp;&nbsp; f: +90 (422) 238 55 22 &nbsp;&nbsp;&nbsp; temkon.com.tr
              </div>
            </div>
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
import { API_BASE } from '../config.js'

const router = useRouter();

onMounted(() => {
  if (!localStorage.getItem('girisYapildi')) {
    router.push('/');
    return;
  }
  verileriYukle();
});

const kullaniciRolu = ref(localStorage.getItem('kullaniciRolu') || 'saha_ekibi');
const seciliTablo = ref('satis');

const projeler = ref([]);
const inceleProjeId = ref('');
const incelePanoTuru = ref('');
const panoIcerigi = ref([]);
const panoAcildi = ref(false);

const genelKarMarji = ref(20); 
const iscilikGideri = ref(0);

const yeniProje = ref({ musteri: '', son_kullanici: '', lokasyon: '', proje_adi: '', teklif_konusu: '', hazirlayan: '', teklif_tarihi: '', teklif_referans_no: '' })

const aktifProje = computed(() => {
  if (!projeler.value || !inceleProjeId.value) return {};
  const safListe = JSON.parse(JSON.stringify(projeler.value));
  const arananId = String(inceleProjeId.value).trim();
  const bulunan = safListe.find(x => String(x.id).trim() === arananId || String(x.proje_id).trim() === arananId);
  return bulunan || {};
});

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
  let tryMaliyet = 0; let eurMaliyetTL = 0; let usdMaliyetTL = 0;
  let eurRaw = 0; let usdRaw = 0;

  (filtrelenmisPanoIcerigi.value || []).forEach(item => {
    const safTutar = item.birim_proje_tl * item.adet;
    if (item.para_birimi === 'TRY') { tryMaliyet += safTutar; } 
    else if (item.para_birimi === 'EUR') { eurMaliyetTL += (safTutar * item.kur_degeri); eurRaw += safTutar; } 
    else if (item.para_birimi === 'USD') { usdMaliyetTL += (safTutar * item.kur_degeri); usdRaw += safTutar; }
  });

  const genelToplam = tryMaliyet + eurMaliyetTL + usdMaliyetTL;
  const tryYuzde = genelToplam ? (tryMaliyet / genelToplam) * 100 : 0;
  const eurYuzde = genelToplam ? (eurMaliyetTL / genelToplam) * 100 : 0;
  const usdYuzde = genelToplam ? (usdMaliyetTL / genelToplam) * 100 : 0;
  const pastaCss = `conic-gradient(#3498db 0% ${tryYuzde}%, #e74c3c ${tryYuzde}% ${tryYuzde + eurYuzde}%, #f1c40f ${tryYuzde + eurYuzde}% 100%)`;

  return { tryMaliyet, eurMaliyetTL, usdMaliyetTL, eurRaw, usdRaw, genelToplam, tryYuzde, eurYuzde, usdYuzde, pastaCss };
});

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
  let indirilecekVeri = []; let sekmeAdi = ""; let dosyaAdi = "";
  if (kullaniciRolu.value === 'saha_ekibi') {
    indirilecekVeri = filtrelenmisPanoIcerigi.value.map((item, index) => ({
      "Sıra": index + 1, "Pano Türü": item.pano, "Sipariş Kodu": item.siparis_kodu || 'M-CODE-' + index, "Malzeme Adı": item.malzeme, "Adet": item.adet
    }));
    sekmeAdi = "Malzeme Listesi"; dosyaAdi = "TEMKON_Saha_Malzeme_Listesi.xlsx";
  } else if (kullaniciRolu.value === 'yonetici' && seciliTablo.value === 'maliyet') {
    const karCani = 1 + (genelKarMarji.value || 0) / 100;
    indirilecekVeri = filtrelenmisPanoIcerigi.value.map((item, index) => {
      const teklifBedeli = item.birim_proje_tl * karCani;
      const netFiyat = teklifBedeli * (1 - (item.iskonto_orani || 0));
      return {
        "Sıra": index + 1, "Maliyet Kalemi": item.malzeme, "Maliyet Grubu": item.pano,
        "Maliyet TRY": item.para_birimi === 'TRY' ? item.birim_proje_tl + " ₺" : (item.birim_proje_tl * item.kur_degeri).toFixed(2) + " ₺",
        "Maliyet EUR": item.para_birimi === 'EUR' ? item.birim_proje_tl + " €" : '-',
        "Maliyet USD": item.para_birimi === 'USD' ? item.birim_proje_tl + " $" : '-',
        "Teklif Bedeli (₺)": teklifBedeli.toFixed(2) + " ₺", "İskonto (%)": "% " + (item.iskonto_orani ? (item.iskonto_orani * 100).toFixed(0) : '0'),
        "Net Fiyat (₺)": netFiyat.toFixed(2) + " ₺", "Adet/Set": item.adet, "Toplam (₺)": (netFiyat * item.adet).toFixed(2) + " ₺",
        "Kur": `${item.kur_degeri} (${item.para_birimi})`
      };
    });
    indirilecekVeri.push({});
    indirilecekVeri.push({ "Adet/Set": "ARA TOPLAM:", "Toplam (₺)": dinamikAraToplam.value.toFixed(2) + " ₺" });
    indirilecekVeri.push({ "Adet/Set": "İŞÇİLİK/SAHA GİDERİ:", "Toplam (₺)": "+ " + (iscilikGideri.value || 0).toString() + " ₺" });
    indirilecekVeri.push({ "Adet/Set": "GENEL SATIŞ BEDELİ:", "Toplam (₺)": (dinamikAraToplam.value + (iscilikGideri.value || 0)).toFixed(2) + " ₺" });
    sekmeAdi = "Simülasyon Analizi"; dosyaAdi = "TEMKON_Yonetim_Maliyet_Simulasyonu.xlsx";
  } else {
    indirilecekVeri = filtrelenmisPanoIcerigi.value.map(item => ({
      "Pano Türü": item.pano, "Malzeme Adı": item.malzeme, "Liste Fiyatı": `${item.liste_fiyati} ${item.para_birimi}`,
      "İskonto (%)": item.iskonto_orani ? (item.iskonto_orani * 100).toFixed(0) : '0', "Net Fiyat (₺)": item.birim_proje_tl,
      "Adet": item.adet, "Toplam (₺)": item.toplam_proje_tl, "Kur": item.kur_degeri
    }));
    sekmeAdi = "Maliyet Analizi"; dosyaAdi = "TEMKON_Satis_Fiyatlandirma.xlsx";
  }
  const worksheet = XLSX.utils.json_to_sheet(indirilecekVeri);
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, sekmeAdi);
  XLSX.writeFile(workbook, dosyaAdi);
};

const duzenlenenHucre = ref(null);
const duzenlemeyiAc = (index, sutunAdi) => { duzenlenenHucre.value = index + '-' + sutunAdi; };

const kaydetVeKapat = async (item, index, sutunAdi) => {
  duzenlenenHucre.value = null; 
  try {
    const guncellenecekVeri = {};
    guncellenecekVeri[sutunAdi] = item[sutunAdi];
    await axios.put(`${API_BASE}/pano-malzeme-guncelle/${item.id}`, guncellenecekVeri);
    item.degistirildi = true; 
  } catch (error) {
    console.error("Güncelleme hatası:", error);
    alert("Kayıt sırasında bir hata oluştu.");
  }
};

const pdfIndir = () => {
  if (kullaniciRolu.value === 'saha_ekibi') return;
  const element = document.getElementById('p1-teklif-sablonu');
  if (!element) return alert("Şablon bulunamadı.");
  const p = aktifProje.value; 
  if (!p || Object.keys(p).length === 0) {
    alert("DİKKAT: Proje bulunamadı!");
    return;
  }
  const musteriAdi = p.musteri ? String(p.musteri).replace(/\s+/g, '_') : 'Musteri';
  const refNo = p.referans_no ? String(p.referans_no) : 'Teklif_Dosyasi';
  const secenekler = {
    margin: 0, filename: `${musteriAdi}_${refNo}.pdf`, image: { type: 'jpeg', quality: 0.98 },
    html2canvas: { scale: 2, useCORS: true }, jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
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

onMounted(verileriYukle);
</script>

<style scoped>
/* YENİ NESİL KURUMSAL ARAYÜZ (SAAS) */
.sistem-container {
  max-width: 1300px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  color: #2c3e50;
}

.header-alani { margin-bottom: 25px; }
.header-alani h2 { margin: 0; font-size: 24px; font-weight: 800; color: #2c3e50; }
.header-alani p { margin: 5px 0 0 0; color: #7f8c8d; font-size: 14px; }

/* FİLTRE KARTI */
.filtre-karti { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 5px 15px rgba(0,0,0,0.05); border-top: 4px solid #8e44ad; margin-bottom: 30px; }
.filtre-grid { display: grid; grid-template-columns: 2fr 2fr 1fr; gap: 20px; align-items: end; }
.input-grubu label { display: block; font-size: 13px; font-weight: 600; color: #34495e; margin-bottom: 8px; }
.modern-select { width: 100%; padding: 12px 15px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 14px; outline: none; transition: border-color 0.2s; background-color: #f8fafc; }
.modern-select:focus { border-color: #8e44ad; box-shadow: 0 0 0 3px rgba(142, 68, 173, 0.1); }
.btn-filtrele { background: #8e44ad; color: white; border: none; padding: 13px 20px; width: 100%; border-radius: 8px; font-weight: bold; cursor: pointer; transition: 0.2s; }
.btn-filtrele:hover { background: #732d91; transform: translateY(-2px); }

/* SONUÇ ALANI & AKSİYON BUTONLARI */
.sonuc-alani { animation: fadeIn 0.4s ease; }
.aksiyon-paneli { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.sonuc-baslik { margin: 0; color: #34495e; font-size: 18px; font-weight: 700; border-left: 4px solid #8e44ad; padding-left: 10px; }
.buton-grubu { display: flex; gap: 10px; }
.btn-excel { background: #27ae60; color: white; padding: 10px 15px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; }
.btn-excel:hover { background: #219653; }
.btn-pdf { background: #e74c3c; color: white; padding: 10px 15px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; }
.btn-pdf:hover { background: #c0392b; }

/* SEKME MENÜSÜ */
.sekme-menusu { display: flex; gap: 10px; margin-bottom: 20px; border-bottom: 2px solid #e1e8ed; padding-bottom: 15px; }
.sekme-menusu button { background: transparent; border: none; padding: 10px 20px; font-size: 14px; font-weight: 600; color: #7f8c8d; cursor: pointer; border-radius: 8px; transition: all 0.3s ease; }
.sekme-menusu button:hover { background: #f1f2f6; color: #2c3e50; }
.sekme-menusu button.aktif { background: #34495e; color: white; box-shadow: 0 4px 10px rgba(52, 73, 94, 0.2); }
.sekme-menusu button.yonetici { background: #c0392b; color: white; }
.sekme-menusu button.grafik { background: #8e44ad; color: white; }

/* TABLOLAR */
.tablo-kart { background: white; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); overflow-x: auto; margin-bottom: 30px; border: 1px solid #f1f2f6; }
.kurumsal-tablo { width: 100%; border-collapse: collapse; font-size: 13px; text-align: center; }
.tablo-ana-baslik th { background: #f39c12; color: white; padding: 12px; font-size: 15px; letter-spacing: 1px; }
.tablo-ana-baslik.koyu th { background: #34495e; }
.tablo-alt-baslik th { background: #f8f9fa; color: #34495e; padding: 12px; border-bottom: 2px solid #e1e8ed; font-size: 11px; text-transform: uppercase; }
.kurumsal-tablo td { padding: 12px 10px; border-bottom: 1px solid #f1f2f6; vertical-align: middle; }
.kurumsal-tablo tbody tr:hover { background: #fcfcfc; }
.satir-gri { background: #fafafa; }

/* HÜCRE DÜZENLEME VE RENKLER */
td[title] { cursor: pointer; }
.hucre-input { width: 100%; padding: 6px; border: 2px solid #3498db; border-radius: 4px; box-sizing: border-box; font-size: 13px; text-align: center; font-weight: bold; }
.manuel-duzenlendi { background-color: #fff3cd !important; transition: 0.3s; }
.kalin { font-weight: bold; }
.kod-font { font-family: monospace; color: #7f8c8d; }
.vurgu-sari { background-color: #fff9e6; }
.vurgu-kirmizi { color: #c0392b; font-weight: bold; }
.vurgu-yesil { background-color: #e8f8f5; color: #16a085; font-weight: bold; }
.vurgu-altin { color: #f1c40f; font-size: 15px; }
.fx-sari { background-color: #fef9e7; }
.fx-kirmizi-yazi { color: #c0392b; }

/* SİMÜLASYON KARTI */
.simulasyon-paneli { background: #fdf2e9; padding: 20px; border-radius: 12px; border-left: 5px solid #d35400; margin-bottom: 20px; display: flex; gap: 30px; align-items: center; box-shadow: 0 4px 10px rgba(0,0,0,0.03); }
.sim-input label { display: block; font-weight: 700; color: #d35400; font-size: 13px; margin-bottom: 8px; }
.sim-input input { padding: 10px; border: 1px solid #e67e22; border-radius: 6px; width: 150px; font-weight: bold; font-size: 15px; outline: none; }
.sim-durum { margin-left: auto; text-align: right; background: white; padding: 12px 20px; border-radius: 8px; border: 1px dashed #d35400; }
.sim-baslik { display: block; font-size: 14px; color: #d35400; font-weight: bold; }
.sim-alt { font-size: 11px; color: #7f8c8d; }

/* TABLO ALTI TOPLAMLAR (FOOTER) */
.footer-koyu td { background: #34495e; color: white; font-weight: bold; padding: 12px; border: none; text-align: right; }
.footer-orta td { background: #2c3e50; color: white; font-weight: bold; padding: 12px; border: none; text-align: right; }
.footer-kirmizi td { background: #c0392b; color: white; font-weight: bold; padding: 15px 12px; border: none; text-align: right; font-size: 14px; }

/* GRAFİK VE ANALİZ */
.grafik-karti { background: #f8f9fa; padding: 30px; border-radius: 12px; border: 1px solid #e1e8ed; }
.grafik-karti h3 { margin: 0 0 20px 0; color: #2c3e50; border-bottom: 2px solid #8e44ad; padding-bottom: 10px; }
.grafik-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }
.pasta-karti, .analiz-karti { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.04); }
.pasta-karti { display: flex; flex-direction: column; align-items: center; }
.pasta-karti h4, .analiz-karti h4 { margin: 0 0 20px 0; color: #34495e; }
.pasta-grafik { width: 220px; height: 220px; border-radius: 50%; border: 5px solid white; box-shadow: 0 5px 15px rgba(0,0,0,0.1); margin-bottom: 25px; }
.pasta-lejant { display: flex; justify-content: space-between; width: 100%; font-weight: bold; font-size: 13px; }
.try { color: #2980b9; } .eur { color: #c0392b; } .usd { color: #f39c12; }
.analiz-form { background: #fdf2e9; padding: 20px; border-radius: 8px; border-left: 4px solid #d35400; margin-bottom: 25px; }
.analiz-form label { font-weight: bold; color: #d35400; font-size: 13px; display: block; margin-top: 15px; }
.analiz-form label:first-child { margin-top: 0; }
.analiz-form input { width: 100%; padding: 12px; margin-top: 8px; font-weight: bold; border: 1px solid #e67e22; border-radius: 6px; box-sizing: border-box; }
.analiz-sonuc { border: 2px dashed #27ae60; padding: 20px; border-radius: 8px; text-align: right; background: #f9fff9; }
.analiz-sonuc p { margin: 0 0 10px 0; font-size: 14px; color: #555; }
.yesil-arti { color: #27ae60; font-weight: bold; }
.analiz-sonuc h3 { margin: 15px 0 0 0; color: #27ae60; font-size: 24px; }

.bos-durum { text-align: center; color: #e74c3c; font-weight: bold; padding: 30px; background: #fdf2f2; border-radius: 8px; margin-top: 20px; }

/* PDF HTML KISMI İÇİN DOKUNULMAYAN CSS KODLARI BURADA BAŞLAR */
.pdf-container { width: 210mm; background: white; color: black; font-family: Arial, sans-serif; font-size: 13px; }
.pdf-sayfa { padding: 15mm; page-break-after: always; min-height: 260mm; position: relative; }
.pdf-sayfa:last-child { page-break-after: auto; }
.temkon-logo { font-size: 28px; font-weight: 900; margin: 0; text-align: right; }
.temkon-logo-kucuk { font-size: 20px; font-weight: 900; margin: 0; text-align: right; }
.kirmizi-cizgi { border-bottom: 3px solid #e30613; margin-top: 5px; margin-bottom: 20px; }
.sayfa-ust-bilgi { display: flex; justify-content: space-between; align-items: flex-end; }
.sol-soluk { color: #95a5a6; font-style: italic; font-size: 11px; }
.kapak-logo-alani { margin-top: 150px; }
.kapak-alt-baslik { color: #7f8c8d; font-size: 14px; text-align: right; margin-top: -15px; }
.kapak-bilgiler { margin-top: 100px; }
.kapak-tablo { width: 100%; border-collapse: collapse; }
.kapak-tablo td { padding: 8px; border: 1px solid #bdc3c7; }
.kapak-tablo .baslik { width: 40%; color: #7f8c8d; font-size: 12px; }
.kapak-tablo .iki-nokta { width: 2%; text-align: center; border-left: none; border-right: none; }
.kapak-tablo .deger { font-weight: bold; }
.hakkinda-icerik { padding: 40px; text-align: center; }
.hakkinda-baslik { font-size: 18px; color: #555; margin-bottom: 30px; }
.hakkinda-metin { color: #7f8c8d; line-height: 1.6; text-align: justify; }
.mt-4 { margin-top: 20px; }
.hakkinda-vizyon { margin-top: 50px; font-size: 12px; color: #333; text-align: center; }
.teklif-giris { border: 1px solid #ccc; padding: 15px; text-align: center; margin-bottom: 30px; font-weight: bold; }
.kirmizi-baslik-ortali { color: #e30613; text-align: center; margin-bottom: 10px; }
.teklif-tablosu { width: 100%; border-collapse: collapse; border: 2px solid black; }
.teklif-tablosu th { background-color: white; border: 2px solid black; border-bottom: 3px solid black; padding: 10px; font-size: 11px; }
.teklif-tablosu td { border: 1px solid black; padding: 10px; vertical-align: top; }
.sag-hizala { text-align: right; }
.siyah-baslik-ortali { text-align: center; border-top: 2px solid black; border-bottom: 2px solid black; padding: 5px 0; margin-bottom: 20px; }
.sartlar-listesi { line-height: 1.8; margin-bottom: 50px; }
.imza-alani { margin-top: 80px; text-align: center; }
.imza-sirket-adi { font-size: 14px; margin-bottom: 20px; }
.kase-kutusu { border: 1px dashed #ccc; width: 300px; height: 150px; margin: 0 auto; display: flex; align-items: center; justify-content: center; }
.soluk-yazi { color: #bdc3c7; font-style: italic; }
.mavi-baslik { background-color: #a9cce3; padding: 8px; text-align: center; font-weight: bold; border: 2px solid #2c3e50; border-bottom: none; }
.detay-tablosu { width: 100%; border-collapse: collapse; border: 2px solid #2c3e50; }
.detay-tablosu th { background-color: #2c3e50; color: white; padding: 8px; font-size: 10px; border: 1px solid #2c3e50; }
.detay-tablosu td { border: 1px solid #2c3e50; padding: 6px; font-size: 11px; }

@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
@media (max-width: 900px) { .filtre-grid { grid-template-columns: 1fr; } .grafik-grid { grid-template-columns: 1fr; } .sekme-menusu { flex-direction: column; } }
</style>