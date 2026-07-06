<template>
  <div class="container">
    
    <div class="ust-menu" style="display: flex; justify-content: space-between; align-items: center; background: white; padding: 15px 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 30px; border-top: 5px solid #2c3e50;">
      <div class="logo-alani">
        <h1 class="logo-yazisi" style="font-size: 28px; margin: 0;">TEM<span class="kirmizi">K</span>ON</h1>
        <h2 style="font-size: 14px; margin: 0; color: #7f8c8d;">CPQ Maliyet Yönetim Paneli</h2>
      </div>
      
      <div class="menu-butonlari" style="display: flex; gap: 15px;">
        <button class="btn-menu aktif" style="background-color: #34495e; color: white; padding: 10px 20px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer;">Ana Panel</button>
        <button v-if="kullaniciRolu === 'yonetici' || kullaniciRolu === 'iletisim_baskani'" @click="$router.push('/panolar')" class="btn-menu" style="background-color: #ecf0f1; color: #2c3e50; padding: 10px 20px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer;">Panolar</button> 
        <button @click="cikisYap" class="btn-cikis" style="background-color: #c0392b; color: white; padding: 10px 20px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer;">Çıkış Yap</button>
      </div>
    </div>

    <div class="ozet-kartlari-wrapper">
      <div class="kart maliyet-karti">
        <span class="baslik">TOPLAM MALİYET</span>
        <span class="deger">{{ genelToplamlar.maliyet_tl || 0 }} ₺</span>
      </div>
      <div class="kart proje-karti">
        <span class="baslik">TOPLAM PROJE</span>
        <span class="deger">{{ genelToplamlar.proje_tl || 0 }} ₺</span>
      </div>
      <div class="kart satis-karti">
        <span class="baslik">TOPLAM SATIŞ</span>
        <span class="deger">{{ genelToplamlar.satis_tl || 0 }} ₺</span>
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

      <div class="form-kutusu pano-konfig-formu">
        <h3>Panoya Malzeme Atama</h3>
        <div class="form-grubu" style="display: flex; flex-direction: column; gap: 15px;">
          <select v-model="yeniPanoMalzeme.proje_id" style="padding: 10px; border: 1px solid #ccc; border-radius: 5px;">
            <option disabled value="">Proje Seçin...</option>
            <option v-for="p in projeler" :key="p.id || p[0]" :value="p.id || p[0]">
              {{ p.proje_adi || p[1] }}
            </option>
          </select>

          <select v-model="yeniPanoMalzeme.malzeme_id" style="padding: 10px; border: 1px solid #ccc; border-radius: 5px;">
            <option disabled value="">Malzeme Seçin...</option>
            <option v-for="m in malzemeler" :key="m.id || m[0]" :value="m.id || m[0]">
              {{ m.urun_adi || m[1] }}
            </option>
          </select>

          <div class="ikili-sutun">
            <select v-model="yeniPanoMalzeme.pano_turu" style="padding: 10px; border: 1px solid #ccc; border-radius: 5px;">
              <option disabled value="">Pano Türü Seçin</option>
              <option v-for="pano in ['ADP 1', 'MCC 1', 'MCC 2', 'MCC 3', 'MCC 4', 'MCC 5', 'REM 100', 'REM 200', 'REM 300', 'REM 400', 'REM 500', 'KONTROL S.', 'SAHA']" :key="pano" :value="pano">{{ pano }}</option>
            </select>
            <input v-model="yeniPanoMalzeme.adet" type="number" placeholder="Adet" style="padding: 10px; border: 1px solid #ccc; border-radius: 5px;"/>
          </div>
          
          <button @click="panoyaEkle" class="btn-kaydet btn-pano">Malzemeyi Panoya Ekle</button>
        </div>
      </div>

      <div v-if="mesaj" :class="['bildirim', { hata: hataVar }]">{{ mesaj }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const kullaniciRolu = ref(localStorage.getItem('kullaniciRolu') || 'standart')
const router = useRouter()

// EKSİK OLAN DEĞİŞKENİ BURAYA EKLEDİK (BEYAZ EKRANIN SEBEBİ BUYDU)
const genelToplamlar = ref({ maliyet_tl: 0, proje_tl: 0, satis_tl: 0 });

const cikisYap = () => {
  localStorage.removeItem('girisYapildi')
  router.push('/') 
}

const mesaj = ref('')
const hataVar = ref(false)
const seciliProjeId = ref(1)
const rapor = ref(null)
const secilenProjeIsmi = ref('')
const secilenMalzemeIsmi = ref('')
const projeler = ref([])
const malzemeler = ref([])

const yeniProje = ref({ proje_adi: '', musteri: '', son_kullanici: '', lokasyon: '', teklif_konusu: '', teklif_tarihi: '', teklif_referans_no: '', hazirlayan: '' })
const yeniMalzeme = ref({ siparis_kodu: '', urun_adi: '', marka: '', urun_grubu: '', tedarikci: '', liste_fiyati: null, para_birimi: 'USD', grup_iskonto_id: 1 })
const yeniPanoMalzeme = ref({ proje_id: '', malzeme_id: '', pano_turu: 'ADP 1', adet: 1 })

const bildirimGoster = (metin, hata = false) => {
  mesaj.value = metin; hataVar.value = hata;
  setTimeout(() => { mesaj.value = '' }, 4000);
}

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
    return bildirimGoster("Zorunlu alanları doldurun!", true);
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
  } catch (error) { bildirimGoster("Ekleme başarısız!", true) }
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
/* --- ÖZET KARTLARI DÜZENİ VE BOŞLUKLARI --- */
.ozet-kartlari-wrapper {
  display: flex;
  justify-content: flex-end; /* Kartları sağ köşeye yaslar (Sola almak istersen 'flex-start' yap) */
  
  /* İŞTE BOŞLUK AYARLARI BURADA: */
  gap: 20px;           /* KARTLARIN BİRBİRİ ARASINDAKİ BOŞLUK */
  margin-top: 25px;    /* Üstteki diğer elementlerle arasındaki boşluk */
  margin-bottom: 30px; /* Alttaki diğer elementlerle arasındaki boşluk */
  
  flex-wrap: wrap;     /* Ekran küçülünce (mobilde) kartların taşmayıp alt alta inmesini sağlar */
}

.kart {
  /* KARTIN KENDİ İÇ BOŞLUĞU (Yukarı/Aşağı 15px, Sağ/Sol 20px) */
  padding: 15px 20px; 
  
  border-radius: 8px;
  color: white;
  min-width: 150px;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  transition: transform 0.2s; /* Mouse ile üzerine gelince hafifçe büyüme animasyonu */
}

.kart:hover {
  transform: translateY(-4px);
}

.kart .baslik { 
  font-size: 11px; 
  opacity: 0.9; 
  letter-spacing: 1px; 
}

.kart .deger { 
  font-size: 19px; 
  font-weight: bold; 
  margin-top: 8px; /* Başlık ile rakam arasındaki boşluk */
}

/* KART RENKLERİ */
.maliyet-karti { background-color: #e74c3c; } /* Kırmızı */
.proje-karti { background-color: #f39c12; }   /* Turuncu */
.satis-karti { background-color: #27ae60; }   /* Yeşil */

/* MOBİL (TELEFON) EKRANI İÇİN BOŞLUK AYARI */
@media (max-width: 768px) {
  .ozet-kartlari-wrapper {
    justify-content: center; /* Mobilde kartları ortala */
  }
  .kart {
    width: 100%; /* Mobilde kartlar ekranı tam kaplasın */
  }
}
</style>