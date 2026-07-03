<template>
  <div class="container">
    <div class="baslik-alani">
      <h1 class="logo-yazisi">TEM<span class="kirmizi">K</span>ON</h1>
      <h2>CPQ (Maliyet ve Teklif) Yönetim Paneli</h2>
    </div>

    <div class="ozet-kartlari">
      <div class="kart maliyet-karti">
        <h4>Toplam Maliyet</h4>
        <p>{{ rapor ? rapor.toplam_maliyet + ' ' + rapor.para_birimi : '--' }}</p>
      </div>
      <div class="kart proje-karti">
        <h4>Kayıtlı Projeler</h4>
        <p>{{ projeler.length }}</p>
      </div>
      <div class="kart satis-karti">
        <h4>Kayıtlı Malzemeler</h4>
        <p>{{ malzemeler.length }}</p>
      </div>
    </div>

    <div class="dikey-form-alani">
      
      <div class="form-kutusu">
        <h3>Proje Kimlik Bilgileri</h3>
        <div class="form-grubu">
          <div class="ikili-sutun">
            <input v-model="yeniProje.musteri" placeholder="Müşteri" />
            <input v-model="yeniProje.son_kullanici" placeholder="Son Kullanıcı" />
          </div>
          <div class="ikili-sutun">
            <input v-model="yeniProje.lokasyon" placeholder="Lokasyon" />
            <input v-model="yeniProje.proje_adi" placeholder="Proje Adı" />
          </div>
          <input v-model="yeniProje.teklif_konusu" placeholder="Teklif Konusu" class="tam-genislik" />
          <div class="ikili-sutun">
            <input v-model="yeniProje.teklif_tarihi" type="date" />
            <input v-model="yeniProje.teklif_referans_no" placeholder="Referans No" />
          </div>
          <input v-model="yeniProje.hazirlayan" placeholder="Teklifi Hazırlayan" class="tam-genislik" />
          <button @click="projeOlustur" class="btn-kaydet">Projeyi Oluştur</button>
        </div>
      </div>

      <div class="form-kutusu depo-formu">
        <h3>Depoya Yeni Malzeme Ekle</h3>
        <div class="form-grubu">
          <div class="ikili-sutun">
            <input v-model="yeniMalzeme.siparis_kodu" placeholder="Sipariş Kodu" />
            <input v-model="yeniMalzeme.urun_adi" placeholder="Ürün Adı" />
          </div>
          <div class="uclu-sutun">
            <input v-model="yeniMalzeme.marka" placeholder="Marka" />
            <input v-model="yeniMalzeme.urun_grubu" placeholder="Grup" />
            <input v-model="yeniMalzeme.tedarikci" placeholder="Tedarikçi" />
          </div>
          <div class="ikili-sutun">
            <input v-model="yeniMalzeme.liste_fiyati" type="number" placeholder="Liste Fiyatı" />
            <select v-model="yeniMalzeme.para_birimi">
              <option value="USD">USD</option>
              <option value="EUR">EUR</option>
              <option value="TRY">TRY</option>
            </select>
          </div>
          <button @click="malzemeEkle" class="btn-kaydet depo-btn">Envantere Kaydet</button>
        </div>
      </div>

      <div class="form-kutusu" style="border-left-color: #8e44ad;">
        <h3>Kayıtlı Panoyu Aç ve İncele</h3>
        <div class="form-grubu">
          <div class="ikili-sutun">
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
          <button @click="panoIcerigiGetir" class="btn-kaydet" style="background-color: #8e44ad;">Kayıtları Excel Gibi Aç</button>
        </div>

        <div v-if="panoIcerigi.length > 0" class="tablo-wrapper" style="margin-top: 25px;">
          <h4 style="margin-top: 0; margin-bottom: 15px; color: #8e44ad;">{{ incelePanoTuru }} İçeriği:</h4>
          <table class="excel-tablosu">
            <thead>
              <tr>
                <th>Pano Türü</th>
                <th>Malzeme Adı</th>
                <th>Sipariş Kodu</th>
                <th>Adet</th>
                <th>Birim Fiyat</th>
                <th>Toplam Maliyet</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in panoIcerigi" :key="index">
                <td style="font-weight: bold; color: #8e44ad;">{{ item.pano_turu }}</td>
                <td>{{ item.urun_adi }}</td>
                <td>{{ item.siparis_kodu }}</td>
                <td style="text-align: center; font-weight: bold;">{{ item.adet }}</td>
                <td class="td-maliyet">{{ item.birim_fiyat }}</td>
                <td class="td-maliyet">{{ item.toplam_fiyat }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div v-else-if="panoAcildi" style="margin-top: 20px; color: #c0392b; font-weight: bold;">
          Seçilen kriterde henüz kayıtlı malzeme yok.
        </div>
      </div>

      <div v-if="mesaj" :class="['bildirim', { hata: hataVar }]">{{ mesaj }}</div>
    </div>


      <div class="form-kutusu pano-konfig-formu">
        <h3>Panoya Malzeme Atama</h3>
        <div class="form-grubu">
          <input list="projeListesi" v-model="secilenProjeIsmi" placeholder="Proje Ara..." @change="projeBul" />
          <datalist id="projeListesi">
            <option v-for="p in projeler" :key="p.id" :value="p.proje_adi + ' | ' + p.musteri"></option>
          </datalist>

          <input list="malzemeListesi" v-model="secilenMalzemeIsmi" placeholder="Malzeme Adı veya Kodu Yazın..." @change="malzemeBul" />
          <datalist id="malzemeListesi">
            <option v-for="m in malzemeler" :key="m.id" :value="m.urun_adi + ' | ' + m.siparis_kodu"></option>
          </datalist>

          <div class="ikili-sutun">
            <select v-model="yeniPanoMalzeme.pano_turu">
              <option v-for="pano in ['ADP 1', 'MCC 1', 'MCC 2', 'MCC 3', 'MCC 4', 'MCC 5', 'REM 100', 'REM 200', 'REM 300', 'REM 400', 'REM 500', 'KONTROL S.', 'SAHA']" :key="pano" :value="pano">{{ pano }}</option>
            </select>
            <input v-model="yeniPanoMalzeme.adet" type="number" placeholder="Adet" />
          </div>
          <button @click="panoyaEkle" class="btn-kaydet btn-pano">Malzemeyi Panoya Ekle</button>
        </div>
      </div>

      <div v-if="mesaj" :class="['bildirim', { hata: hataVar }]">{{ mesaj }}</div>
    </div>

    <div class="rapor-alani">
      <div class="rapor-baslik-satiri">
        <h3>Proje Raporu</h3>
        <div class="rapor-aksiyon">
        <select v-model="seciliProjeId" class="kucuk-input" style="width: 250px; text-align: left;">
  <option disabled value="">Raporlanacak Proyeyi Seçin...</option>
  <option v-for="p in projeler" :key="p.id" :value="p.id">
    {{ p.proje_adi }} - {{ p.musteri }}
  </option>
</select>
          <button @click="raporuGetir" class="btn-hesapla">Raporu Göster</button>
        </div>
      </div>

      <div v-if="rapor && rapor.malzemeler" class="tablo-wrapper">
        <table class="excel-tablosu">
          <thead>
            <tr>
              <th>Pano Türü</th>
              <th>Malzeme Adı</th>
              <th>Sipariş Kodu</th>
              <th>Adet</th>
              <th>Birim Fiyat</th>
              <th>Toplam Maliyet</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in rapor.malzemeler" :key="index">
              <td>{{ item.pano_turu }}</td>
              <td>{{ item.urun_adi }}</td>
              <td>{{ item.siparis_kodu }}</td>
              <td style="text-align: center;">{{ item.adet }}</td>
              <td class="td-maliyet">{{ item.birim_fiyat }}</td>
              <td class="td-maliyet">{{ item.toplam_fiyat }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

// DURUM DEĞİŞKENLERİ
const mesaj = ref('')
const hataVar = ref(false)
const seciliProjeId = ref(1)
const rapor = ref(null)
const secilenProjeIsmi = ref('')
const secilenMalzemeIsmi = ref('')
const projeler = ref([])
const malzemeler = ref([])

// MODELLER
const yeniProje = ref({ proje_adi: '', musteri: '', son_kullanici: '', lokasyon: '', teklif_konusu: '', teklif_tarihi: '', teklif_referans_no: '', hazirlayan: '' })
const yeniMalzeme = ref({ siparis_kodu: '', urun_adi: '', marka: '', urun_grubu: '', tedarikci: '', liste_fiyati: null, para_birimi: 'USD', grup_iskonto_id: 1 })
const yeniPanoMalzeme = ref({ proje_id: '', malzeme_id: '', pano_turu: 'ADP 1', adet: 1 })


// PANO İNCELEME İÇİN DEĞİŞKENLER
const inceleProjeId = ref('');
const incelePanoTuru = ref('');
const panoIcerigi = ref([]);
const panoAcildi = ref(false);

// SADECE SEÇİLİ VEYA GRUPLANMIŞ PANO LİSTESİNİ ÇEKEN FONKSİYON
const panoIcerigiGetir = async () => {
  if (!inceleProjeId.value || !incelePanoTuru.value) {
    return bildirimGoster("Lütfen proje ve görünüm seçin!", true);
  }
  try {
    const response = await axios.get(`http://127.0.0.1:8000/projeler/${inceleProjeId.value}/maliyet-raporu`);
    const tumMalzemeler = response.data.malzemeler || [];
    
    // Seçime Göre Excel'i Filtrele
    if (incelePanoTuru.value === "TÜM PANOLAR") {
      panoIcerigi.value = tumMalzemeler;
    } else if (incelePanoTuru.value === "TÜM MCC LER") {
      panoIcerigi.value = tumMalzemeler.filter(m => m.pano_turu.includes('MCC'));
    } else if (incelePanoTuru.value === "TÜM REM LER") {
      panoIcerigi.value = tumMalzemeler.filter(m => m.pano_turu.includes('REM'));
    } else {
      panoIcerigi.value = tumMalzemeler.filter(m => m.pano_turu === incelePanoTuru.value);
    }
    
    panoAcildi.value = true;
  } catch (error) {
    bildirimGoster("Kayıtlar getirilemedi!", true);
  }
}
// YARDIMCI FONKSİYONLAR
const bildirimGoster = (metin, hata = false) => {
  mesaj.value = metin; hataVar.value = hata;
  setTimeout(() => { mesaj.value = '' }, 4000);
}

const projeBul = () => {
  const p = projeler.value.find(x => (x.proje_adi + ' | ' + x.musteri) === secilenProjeIsmi.value)
  if (p) yeniPanoMalzeme.value.proje_id = p.id
}

const malzemeBul = () => {
  const m = malzemeler.value.find(x => (x.urun_adi + ' | ' + x.siparis_kodu) === secilenMalzemeIsmi.value)
  if (m) yeniPanoMalzeme.value.malzeme_id = m.id
}

// API ÇAĞRILARI
const verileriYukle = async () => {
  try {
    const [p, m] = await Promise.all([
      axios.get('http://127.0.0.1:8000/projeler/listele'),
      axios.get('http://127.0.0.1:8000/malzemeler/listele')
    ]);
    projeler.value = p.data;
    malzemeler.value = m.data;
  } catch (error) { console.error("Veriler yüklenemedi:", error); }
}

const projeOlustur = async () => {
  if (!yeniProje.value.proje_adi) return bildirimGoster("Lütfen Proje Adı girin!", true);
  try {
    await axios.post('http://127.0.0.1:8000/projeler', yeniProje.value)
    bildirimGoster("Proje başarıyla oluşturuldu! ✅")
    yeniProje.value = { proje_adi: '', musteri: '', son_kullanici: '', lokasyon: '', teklif_konusu: '', teklif_tarihi: '', teklif_referans_no: '', hazirlayan: '' }
    verileriYukle()
  } catch (error) { bildirimGoster("Proje oluşturulurken bir hata oluştu.", true) }
}

const malzemeEkle = async () => {
  if (!yeniMalzeme.value.siparis_kodu || !yeniMalzeme.value.urun_adi || !yeniMalzeme.value.liste_fiyati) {
    return bildirimGoster("Zorunlu alanları (Kod, Ad, Fiyat) doldurun!", true);
  }
  try {
    await axios.post('http://127.0.0.1:8000/malzemeler', yeniMalzeme.value)
    bildirimGoster("Malzeme depoya eklendi! ✅")
    yeniMalzeme.value = { siparis_kodu: '', urun_adi: '', marka: '', urun_grubu: '', tedarikci: '', liste_fiyati: null, para_birimi: 'USD', grup_iskonto_id: 1 }
    verileriYukle()
  } catch (error) { bildirimGoster("Malzeme eklenemedi.", true) }
}

const panoyaEkle = async () => {
  if (!yeniPanoMalzeme.value.proje_id || !yeniPanoMalzeme.value.malzeme_id) {
    return bildirimGoster("Lütfen önce Proje ve Malzeme seçin!", true);
  }
  try {
    await axios.post('http://127.0.0.1:8000/projeler/pano-malzeme-ekle', yeniPanoMalzeme.value);
    bildirimGoster(`Başarıyla atandı: ${yeniPanoMalzeme.value.pano_turu} ✅`);
    await raporuGetir();
  } catch (error) { bildirimGoster("Ekleme başarısız!", true) }
}

const raporuGetir = async () => {
  try {
    const response = await axios.get(`http://127.0.0.1:8000/projeler/${seciliProjeId.value}/maliyet-raporu`)
    rapor.value = response.data
  } catch (error) { bildirimGoster("Bu projede malzeme yok veya bağlantı hatası!", true) }
}

onMounted(verileriYukle)
</script>
<style scoped>
/* 1. GENEL YAPISI VE LOGO */
body { background-color: #f0f2f5; margin: 0; font-family: 'Segoe UI', Tahoma, sans-serif; }
.container { max-width: 1000px; margin: 20px auto; padding: 20px; color: #2c3e50; }
.baslik-alani { text-align: center; margin-bottom: 40px; }
.logo-yazisi { font-size: 48px; font-weight: 900; margin: 0; letter-spacing: 2px; }
.kirmizi { color: #c0392b; }
.baslik-alani h2 { font-size: 18px; color: #7f8c8d; font-weight: 400; margin-top: 5px; }

/* 2. ÖZET KARTLARI */
.ozet-kartlari { display: flex; gap: 20px; margin-bottom: 30px; }
.kart { flex: 1; padding: 20px; border-radius: 10px; color: white; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
.kart h4 { margin: 0 0 10px 0; font-size: 16px; opacity: 0.9; }
.kart p { margin: 0; font-size: 24px; font-weight: bold; }
.maliyet-karti { background-color: #c0392b; }
.proje-karti { background-color: #d35400; }
.satis-karti { background-color: #27ae60; }

/* 3. DİKEY FORM VE KUTULAR */
.dikey-form-alani { display: flex; flex-direction: column; gap: 25px; }
.form-kutusu { background-color: #ffffff; padding: 30px; border-radius: 10px; border-left: 8px solid #34495e; box-shadow: 0 6px 12px rgba(0,0,0,0.08); }
.depo-formu { border-left-color: #2980b9; }
.pano-konfig-formu { border-left-color: #27ae60; }

/* 4. TİPOGRAFİ VE IZGARA (GRID) */
h3 { color: #2c3e50 !important; font-weight: 700 !important; font-size: 18px; border-bottom: 2px solid #bdc3c7; padding-bottom: 8px; margin-bottom: 20px; }
.form-grubu { display: flex; flex-direction: column; gap: 15px; }
.ikili-sutun { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; width: 100%; }
.uclu-sutun { display: grid; grid-template-columns: 2fr 1fr 2fr; gap: 15px; width: 100%; }
.tam-genislik { width: 100%; display: block; box-sizing: border-box; }

/* 5. INPUT VE BUTONLAR */
input, select { padding: 12px; border: 1px solid #bdc3c7; border-radius: 6px; width: 100%; box-sizing: border-box; color: #2c3e50; font-size: 14px; transition: border-color 0.2s; }
input:focus, select:focus { border-color: #3498db; outline: none; }
.btn-kaydet { background-color: #34495e; color: white; padding: 12px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; width: 100%; transition: background-color 0.2s; }
.btn-kaydet:hover { background-color: #2c3e50; }
.depo-btn { background-color: #2980b9; }
.depo-btn:hover { background-color: #1c5980; }
.btn-pano { background-color: #27ae60; margin-top: 10px; }
.btn-pano:hover { background-color: #1e8449; }
.btn-hesapla { padding: 10px 20px; background-color: #27ae60; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; }

/* 6. BİLDİRİM KUTULARI */
.bildirim { margin-top: 25px; padding: 15px 20px; background-color: #e8f8f2; color: #27ae60; border-radius: 6px; font-weight: 600; text-align: center; border: 1px solid #d5f5e3; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
.bildirim.hata { background-color: #fdf2f2; color: #c0392b; border: 1px solid #fadbd8; }

/* 7. RAPOR VE EXCEL TABLOSU */
.rapor-baslik-satiri { display: flex; justify-content: space-between; align-items: center; margin: 30px 0 20px 0; border-bottom: 1px solid #eee; padding-bottom: 10px; }
.rapor-aksiyon { display: flex; gap: 12px; align-items: center; }
.kucuk-input { width: 100px; padding: 8px; text-align: center; font-weight: bold; border: 1px solid #bdc3c7; border-radius: 4px; }
.tablo-wrapper { overflow-x: auto; background: white; padding: 10px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
.excel-tablosu { width: 100%; border-collapse: collapse; font-size: 13px; background-color: white; border: 1px solid #bdc3c7; }
.excel-tablosu th { background-color: #f8f9fa; color: #2c3e50; font-weight: 700; text-transform: uppercase; padding: 14px 10px; border: 1px solid #dee2e6; }
.excel-tablosu td { border: 1px solid #dee2e6; padding: 10px; color: #34495e; }
.td-maliyet { background-color: #fff5f5; color: #c0392b; text-align: right; font-weight: 500; }
.excel-tablosu tbody tr:hover { background-color: #f1f4f8; }
</style>