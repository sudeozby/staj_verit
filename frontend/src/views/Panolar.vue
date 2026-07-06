<template>
  <div class="container">
    <div class="ust-menu" style="display: flex; justify-content: space-between; align-items: center; background: white; padding: 15px 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 30px; border-top: 5px solid #2c3e50;">
      <div class="logo-alani">
        <h1 class="logo-yazisi" style="font-size: 28px; margin: 0;">TEM<span class="kirmizi">K</span>ON</h1>
        <h2 style="font-size: 14px; margin: 0; color: #7f8c8d;">Maliyet Yönetim Paneli</h2>
      </div>
      
      <div class="menu-butonlari" style="display: flex; gap: 15px;">
        <button v-if="kullaniciRolu !== 'saha_ekibi'" @click="router.push('/panel')" class="btn-menu" style="background-color: #ecf0f1; color: #2c3e50; padding: 10px 20px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer;">Ana Panel</button>
        <button class="btn-menu aktif" style="background-color: #34495e; color: white; padding: 10px 20px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer;">Panolar</button> 
        <button @click="cikisYap" class="btn-cikis" style="background-color: #c0392b; color: white; padding: 10px 20px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer;">Çıkış Yap</button>
      </div>
    </div>

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
          <button v-if="kullaniciRolu === 'yonetici'" @click="excelIndir" style="background-color: #27ae60; color: white; padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; display: flex; align-items: center; gap: 8px;">
            📊 Excel Olarak İndir
          </button>

          <button v-if="kullaniciRolu === 'yonetici' || kullaniciRolu === 'teklif_ekibi'" @click="pdfIndir" style="background-color: #e74c3c; color: white; padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; display: flex; align-items: center; gap: 8px;">
            📄 Müşteri Teklifi (PDF) İndir
          </button>
        </div>

        <table v-if="kullaniciRolu === 'yonetici'" class="maliyet-tablosu" style="width: 100%; border-collapse: collapse; font-size: 13px; border: 1px solid #000;">
          <thead>
            <tr>
              <th colspan="9" style="background-color: #ffc000; color: #000; text-align: center; border: 1px solid #000; padding: 8px; font-weight: bold; font-size: 14px;">
                PROJEYE SATIŞ ŞARTLARI GEÇERLİ (YÖNETİCİ EKRANI)
              </th>
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

        <table v-else class="maliyet-tablosu" style="width: 100%; border-collapse: collapse; font-size: 13px; border: 1px solid #000;">
          <thead>
            <tr>
              <th colspan="5" style="background-color: #34495e; color: white; text-align: center; border: 1px solid #000; padding: 8px; font-weight: bold; font-size: 14px;">
                TEKNİK KONFİGÜRASYON VE MALZEME LİSTESİ (İMALAT / TEKLİF)
              </th>
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

const router = useRouter();

// ROL KONTROLÜ (yonetici, teklif_ekibi, saha_ekibi)
const kullaniciRolu = ref(localStorage.getItem('kullaniciRolu') || 'saha_ekibi');

const projeler = ref([]);
const inceleProjeId = ref('');
const incelePanoTuru = ref('');
const panoIcerigi = ref([]);
const panoAcildi = ref(false);

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

const filtrelenmisPanoIcerigi = computed(() => {
  if (!panoIcerigi.value || panoIcerigi.value.length === 0) return [];
  if (incelePanoTuru.value === 'TÜM PANOLAR' || !incelePanoTuru.value) return panoIcerigi.value;
  if (incelePanoTuru.value === 'TÜM MCC LER') return panoIcerigi.value.filter(item => item.pano && item.pano.startsWith('MCC'));
  if (incelePanoTuru.value === 'TÜM REM LER') return panoIcerigi.value.filter(item => item.pano && item.pano.startsWith('REM'));
  return panoIcerigi.value.filter(item => item.pano === incelePanoTuru.value);
});

const panoIcerigiGetir = async () => {
  if (!inceleProjeId.value || !incelePanoTuru.value) return;
  try {
    const response = await axios.get(`http://127.0.0.1:8000/projeler/${inceleProjeId.value}/maliyet-raporu`);
    const tumMalzemeler = response.data.detaylar || []; 
    
    if (incelePanoTuru.value === "TÜM PANOLAR") {
      panoIcerigi.value = tumMalzemeler;
    } else if (incelePanoTuru.value === "TÜM MCC LER") {
      panoIcerigi.value = tumMalzemeler.filter(m => m.pano.includes('MCC'));
    } else if (incelePanoTuru.value === "TÜM REM LER") {
      panoIcerigi.value = tumMalzemeler.filter(m => m.pano.includes('REM'));
    } else {
      panoIcerigi.value = tumMalzemeler.filter(m => m.pano === incelePanoTuru.value);
    }
    panoAcildi.value = true;
  } catch (error) { 
    console.error("Kayıtlar çekilemedi", error);
  }
};

const excelIndir = () => {
  if (kullaniciRolu.value !== 'yonetici') return;
  const worksheet = XLSX.utils.json_to_sheet(filtrelenmisPanoIcerigi.value);
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, "Maliyet Analizi");
  XLSX.writeFile(workbook, "TEMKON_Maliyet_Analizi.xlsx");
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