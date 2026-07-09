<template>
  <div class="container">
    <UstMenu />

    <div class="ozet-kartlari-wrapper">
      <div 
        v-for="kart in ozetKartlari" 
        :key="kart.baslik" 
        :class="['kart', kart.sinif]"
      >
        <span class="baslik">{{ kart.baslik }}</span>
        <span class="deger">{{ kart.deger || 0 }} ₺</span>
      </div>
    </div>

    <div class="dikey-form-alani">
      
      <div class="form-kutusu">
        <h3>Proje Kimlik Bilgileri</h3>
        <div class="form-grubu">
          <div class="ikili-sutun">
            <input v-model="yeniProje.musteri" placeholder="Müşteri" required />
            <input v-model="yeniProje.son_kullanici" placeholder="Son Kullanıcı" />
          </div>
          <div class="ikili-sutun">
            <input v-model="yeniProje.lokasyon" placeholder="Lokasyon" />
            <input v-model="yeniProje.proje_adi" placeholder="Proje Adı" required />
          </div>
          <input v-model="yeniProje.teklif_konusu" placeholder="Teklif Konusu" class="tam-genislik" />
          <div class="ikili-sutun">
            <input v-model="yeniProje.teklif_tarihi" type="date" />
            <input v-model="yeniProje.teklif_referans_no" placeholder="Referans No" />
          </div>
          <input v-model="yeniProje.hazirlayan" placeholder="Teklifi Hazırlayan" class="tam-genislik" />
          
          <button @click="projeOlustur" :disabled="isSubmitting" class="btn-kaydet">
            {{ isSubmitting ? 'Kaydediliyor...' : 'Projeyi Oluştur' }}
          </button>
        </div>
      </div>

      <div class="form-kutusu depo-formu">
  <h3>Depoya Yeni Malzeme Ekle</h3>
  <div class="form-grubu">
    <div class="ikili-sutun">
      <input v-model="yeniMalzeme.siparis_kodu" placeholder="Sipariş Kodu" required />
      <input v-model="yeniMalzeme.urun_adi" placeholder="Ürün Adı" required />
    </div>
    <div class="uclu-sutun">
      <input v-model="yeniMalzeme.marka" placeholder="Marka" />
      <input v-model="yeniMalzeme.urun_grubu" placeholder="Grup" />
      <input v-model="yeniMalzeme.tedarikci" placeholder="Tedarikçi" />
    </div>
    <div class="ikili-sutun">
      <input v-model="yeniMalzeme.liste_fiyati" type="number" placeholder="Liste Fiyatı" required />
      <select v-model="yeniMalzeme.para_birimi" required>
        <option value="USD">USD</option>
        <option value="EUR">EUR</option>
        <option value="TRY">TRY</option>
      </select>
    </div>
    <div style="margin-top: 10px; margin-bottom: 10px;">
      <label style="font-size: 13px; color: #2980b9; font-weight: bold;">📊 İskonto Grubu (Excel'deki Marka/Grup):</label>
      <select 
        v-model="yeniMalzeme.grup_iskonto_id" 
        style="width: 100%; padding: 10px; margin-top: 5px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box;"
      >
        <option :value="null">Grup Seçin (Zorunlu Değil)</option>
        
        <option v-for="grup in iskontoGruplari" :key="grup.id" :value="grup.id">
          {{ grup.grup_adi }}
        </option>
      </select>
    </div>

    <div style="margin-top: 10px; margin-bottom: 15px;">
      <textarea 
        v-model="yeniMalzeme.notlar" 
        placeholder="Malzeme için notlar (Opsiyonel)" 
        style="width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; font-family: inherit; resize: vertical; min-height: 60px;"
      ></textarea>
    </div>
    
    <button @click="malzemeEkle" class="btn-kaydet depo-btn">Envantere Kaydet</button>
  </div>
</div>


<div v-if="kullaniciRolu === 'yonetici'" class="admin-panel" style="background: #f9f9f9; padding: 20px; border-radius: 8px; border: 1px solid #ddd; margin-top: 30px;">
  <h3 style="color: #c0392b;">🛠 İskonto Grubu Yönetimi (Yönetici)</h3>
  <div style="display: grid; grid-template-columns: repeat(5, 1fr) auto; gap: 10px; align-items: end;">
    <div>
      <label>Grup Adı</label>
      <input v-model="yeniGrup.grup_adi" placeholder="Örn: ABB Sürücü" style="width: 100%; padding: 8px;">
    </div>
    <div>
      <label>Maliyet İsk.</label>
      <input v-model.number="yeniGrup.maliyet_iskonto" placeholder="0.15" style="width: 100%; padding: 8px;">
    </div>
    <div>
      <label>Proje İsk.</label>
      <input v-model.number="yeniGrup.proje_iskonto" placeholder="0.10" style="width: 100%; padding: 8px;">
    </div>
    <div>
      <label>Satış İsk.</label>
      <input v-model.number="yeniGrup.satis_iskonto" placeholder="0.05" style="width: 100%; padding: 8px;">
    </div>
    <div>
      <label>Notlar</label>
      <input v-model="yeniGrup.notlar" placeholder="Opsiyonel not" style="width: 100%; padding: 8px;">
    </div>
    <button @click.prevent="grupEkle" type="button" style="background: #27ae60; color: white; padding: 10px 20px; border: none; cursor: pointer;">
      Kaydet
    </button>
</div>
</div>
      <div class="form-kutusu pano-konfig-formu">
        <h3>Panoya Malzeme Atama</h3>
        <div class="form-grubu">
          <select v-model="yeniPanoMalzeme.proje_id">
            <option disabled value="">Proje Seçin...</option>
            <option v-for="p in projeler" :key="p.id" :value="p.id">{{ p.proje_adi }}</option>
          </select>

          <select v-model="yeniPanoMalzeme.malzeme_id">
            <option disabled value="">Malzeme Seçin...</option>
            <option v-for="m in malzemeler" :key="m.id" :value="m.id">{{ m.urun_adi }} ({{ m.siparis_kodu }})</option>
          </select>

          <div class="ikili-sutun">
            <select v-model="yeniPanoMalzeme.pano_turu">
              <option value="ADP 1">ADP 1</option>
              <option value="MCC 1">MCC 1</option>
              <option value="SAHA">SAHA</option>
            </select>
            <input v-model="yeniPanoMalzeme.adet" type="number" placeholder="Adet" />
          </div>
          

        <div style="margin-top: 10px; margin-bottom: 15px;">
  <label style="font-size: 13px; color: #2980b9; font-weight: bold;">🎯 Özel İskonto (Opsiyonel):</label>
  <input 
    v-model.number="yeniPanoMalzeme.ozel_iskonto" 
    type="number"
    step="0.01"
    placeholder="Örn: 0.05 (%5 indirim)" 
    style="width: 100%; padding: 10px; margin-top: 5px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box;"
  >
  <small style="color: #7f8c8d;">Sadece bu atamaya özel ekstra indirim oranı (Örn: 0.05)</small>
</div>

          <button @click="panoyaEkle" class="btn-kaydet btn-pano">Malzemeyi Panoya Ekle</button>
        </div>
      </div>
    </div>

    <transition name="fade">
      <div 
        v-if="mesaj" 
        :class="['bildirim', hataVar ? 'hata' : '']"
        @click="mesaj = ''" 
      >
        {{ mesaj }}
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import UstMenu from '../components/UstMenu.vue'
import { API_BASE } from '../config' // Klasör yapına göre '@/config' de olabilir


// --- ROUTER VE ROL YÖNETİMİ ---
const router = useRouter()
const kullaniciRolu = ref(localStorage.getItem('kullaniciRolu') || 'standart')
const isSubmitting = ref(false)
const iskontoGruplari = ref([]);
// --- DATA ---
const genelToplamlar = ref({ maliyet_tl: 0, proje_tl: 0, satis_tl: 0 })
const mesaj = ref('')
const hataVar = ref(false)

const projeler = ref([])
const malzemeler = ref([])


const yeniGrup = ref({
  grup_adi: '',
  maliyet_iskonto: null,
  proje_iskonto: null,
  satis_iskonto: null,
  notlar: '' // <-- Bu alanı mutlaka ekle
});

const yeniMalzeme = ref({ 
  siparis_kodu: '', 
  urun_adi: '', 
  marka: '', 
  urun_grubu: '', 
  tedarikci: '', 
  liste_fiyati: null, 
  para_birimi: 'TRY',
  notlar: '' ,
  grup_iskonto_id: null
})

// --- ÖZET KARTLARI (Dinamik) ---
const ozetKartlari = computed(() => [
  { baslik: 'TOPLAM MALİYET', deger: genelToplamlar.value?.maliyet_tl || 0, sinif: 'maliyet-karti' },
  { baslik: 'TOPLAM PROJE', deger: genelToplamlar.value?.proje_tl || 0, sinif: 'proje-karti' },
  { baslik: 'TOPLAM SATIŞ', deger: genelToplamlar.value?.satis_tl || 0, sinif: 'satis-karti' }
])

// --- FORM VERİLERİ ---
const yeniProje = ref({ 
  proje_adi: '', musteri: '', son_kullanici: '', lokasyon: '', 
  teklif_konusu: '', teklif_tarihi: '', teklif_referans_no: '', hazirlayan: '' 
})

const grupEkle = async () => {
  try {
    // 1. Veriyi hazırla
    const gonderilecekVeri = {
      grup_adi: yeniGrup.value.grup_adi,
      maliyet_iskonto: parseFloat(yeniGrup.value.maliyet_iskonto || 0),
      proje_iskonto: parseFloat(yeniGrup.value.proje_iskonto || 0),
      satis_iskonto: parseFloat(yeniGrup.value.satis_iskonto || 0),
      notlar: yeniGrup.value.notlar || "-"
    };

    console.log("Gönderilen Veri:", gonderilecekVeri);

    // 2. İsteği gönder
    await axios.post(`${API_BASE}/iskonto-gruplari/ekle`, gonderilecekVeri, {
      headers: { 'current-user-role': 'yonetici' }
    });

    // 3. Başarılıysa kullanıcıya bildir
    bildirimGoster("Yeni grup başarıyla eklendi! ✅");
    
    // 4. Formu sıfırla
    yeniGrup.value = { 
      grup_adi: '', 
      maliyet_iskonto: null, 
      proje_iskonto: null, 
      satis_iskonto: null,
      notlar: '' 
    };
    
    // 5. Listeyi tazele
    await verileriYukle(); 
    
  } catch (error) {
    // 6. Hata yakalama
    console.error("Hata Detayı:", error.response?.data || error);
    bildirimGoster("Hata! İşlem tamamlanamadı. Konsolu kontrol et.", true);
  }
};


const yeniPanoMalzeme = ref({ 
  proje_id: '',
  malzeme_id: '',
  pano_turu: 'ADP 1',
  adet: 1 ,
  ozel_iskonto: 0,
})

// --- FONKSİYONLAR ---
const bildirimGoster = (metin, hata = false) => {
  mesaj.value = metin
  hataVar.value = hata
  setTimeout(() => { mesaj.value = ''; hataVar.value = false }, 5000)
}

const cikisYap = () => {
  localStorage.removeItem('girisYapildi')
  localStorage.removeItem('kullaniciRolu')
  router.push('/')
}

// --- API İSTEKLERİ ---
//tek tek çekmek yerine promise all kullanıp beklemedn tum vrılerı cekmesı ıcın
const verileriYukle = async () => {
  try {
    // p: projeler, m: malzemeler, i: iskonto grupları
    const [p, m, i] = await Promise.all([
      axios.get(`${API_BASE}/projeler/listele`),
      axios.get(`${API_BASE}/malzemeler/listele`),
      axios.get(`${API_BASE}/iskonto-gruplari`) // <-- 3. KAPI BURAYA EKLENDİ
    ])
    projeler.value = p.data
    malzemeler.value = m.data
    iskontoGruplari.value = i.data // <-- GELEN VERİYİ HAFIZAYA ALDIK
  } catch (error) { 
    bildirimGoster("Veriler yüklenirken bağlantı hatası!", true) 
  }
}

const projeOlustur = async () => {
  if (!yeniProje.value.proje_adi) return bildirimGoster("Lütfen Proje Adı girin!", true)
  isSubmitting.value = true
  try {
    const res = await axios.post(`${API_BASE}/projeler`, yeniProje.value)
    bildirimGoster(res.data.mesaj || "Proje başarıyla oluşturuldu! ✅")
    yeniProje.value = { proje_adi: '', musteri: '', son_kullanici: '', lokasyon: '', teklif_konusu: '', teklif_tarihi: '', teklif_referans_no: '', hazirlayan: '' }
    await verileriYukle()
  } catch (error) { 
    bildirimGoster(error.response?.data?.detail || "Proje oluşturulamadı.", true) 
  } finally {
    isSubmitting.value = false
  }
}

const malzemeEkle = async () => {
  if (!yeniMalzeme.value.siparis_kodu || !yeniMalzeme.value.urun_adi) {
    return bildirimGoster("Zorunlu alanları doldurun!", true)
  }
  try {
    const res = await axios.post(`${API_BASE}/malzemeler`, yeniMalzeme.value)
    bildirimGoster(res.data.mesaj || "Malzeme depoya eklendi! ✅")
    
    // BURASI GÜNCELLENDİ: Form temizlenirken notlar alanı da sıfırlanıyor (8. alan)
    yeniMalzeme.value = { 
      siparis_kodu: '', 
      urun_adi: '', 
      marka: '', 
      urun_grubu: '', 
      tedarikci: '', 
      liste_fiyati: null, 
      para_birimi: 'TRY',
      grup_iskonto_id: null,
      notlar: '' ,
      grup_iskonto_id: null
    }
    
    await verileriYukle()
  } catch (error) { 
    bildirimGoster(error.response?.data?.detail || "Malzeme eklenemedi.", true) 
  }
}

const panoyaEkle = async () => {
  if (!yeniPanoMalzeme.value.proje_id || !yeniPanoMalzeme.value.malzeme_id) {
    return bildirimGoster("Lütfen önce Proje ve Malzeme seçin!", true)
  }
  try {
    const res = await axios.post(`${API_BASE}/projeler/pano-malzeme-ekle`, yeniPanoMalzeme.value)
    bildirimGoster(res.data.mesaj || `Başarıyla atandı: ${yeniPanoMalzeme.value.pano_turu} ✅`)
    yeniPanoMalzeme.value.adet = 1;
    yeniPanoMalzeme.value.ozel_iskonto = 0; // <-- Bunu da sıfırla
  } catch (error) { 
    bildirimGoster(error.response?.data?.detail || "Malzeme panoya atanamadı!", true) 
  }
}

onMounted(verileriYukle)
</script>
<style scoped>
/* 1. KÖK DEĞİŞKENLER (Renk ve Font Yönetimi) */
.container {
  --bg-body: #f0f2f5;
  --text-main: #2c3e50;
  --text-muted: #7f8c8d;
  --primary-brand: #c0392b; 
  --maliyet-color: #e74c3c;
  --proje-color: #f39c12;
  --satis-color: #27ae60;
  --font-main: 'Segoe UI', Tahoma, sans-serif;
}

body { background-color: var(--bg-body); margin: 0; font-family: var(--font-main); color: var(--text-main); }
.container { max-width: 1000px; margin: 20px auto; padding: 20px; }

/* 2. BAŞLIK ALANI */
.baslik-alani { text-align: center; margin-bottom: 40px; }
.logo-yazisi { font-size: 48px; font-weight: 900; margin: 0; letter-spacing: 2px; color: var(--text-main); }
.kirmizi { color: var(--primary-brand); }
.baslik-alani h2 { font-size: 18px; color: var(--text-muted); font-weight: 400; margin-top: 5px; }

/* 3. ÖZET KARTLARI */
.ozet-kartlari-wrapper { display: flex; justify-content: flex-end; gap: 20px; margin: 25px 0 30px 0; flex-wrap: wrap; }
.kart { padding: 15px 20px; border-radius: 8px; color: white; min-width: 150px; display: flex; flex-direction: column; align-items: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: transform 0.2s; }
.kart:hover { transform: translateY(-4px); }
.kart .baslik { font-size: 11px; opacity: 0.9; letter-spacing: 1px; text-transform: uppercase; }
.kart .deger { font-size: 19px; font-weight: bold; margin-top: 8px; }

.maliyet-karti { background-color: var(--maliyet-color); }
.proje-karti   { background-color: var(--proje-color); }
.satis-karti   { background-color: var(--satis-color); }

/* 4. DİKEY FORM VE KUTULAR */
.dikey-form-alani { display: flex; flex-direction: column; gap: 25px; }
.form-kutusu { background-color: #ffffff; padding: 30px; border-radius: 10px; border-left: 8px solid var(--primary-brand); box-shadow: 0 6px 12px rgba(0,0,0,0.08); }
.depo-formu { border-left-color: #2980b9; }
.pano-konfig-formu { border-left-color: var(--satis-color); }
.form-kutusu h3 { color: #2c3e50; font-weight: 700; font-size: 18px; border-bottom: 2px solid #bdc3c7; padding-bottom: 8px; margin-bottom: 20px; }
.form-grubu { display: flex; flex-direction: column; gap: 15px; }

/* 5. IZGARA VE INPUTLAR */
.ikili-sutun { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; width: 100%; }
.uclu-sutun { display: grid; grid-template-columns: 2fr 1fr 2fr; gap: 15px; width: 100%; }
.tam-genislik { width: 100%; display: block; box-sizing: border-box; }

input, select { padding: 12px; border: 1px solid #bdc3c7; border-radius: 6px; width: 100%; box-sizing: border-box; color: var(--text-main); font-size: 14px; transition: border-color 0.3s; }
input:focus, select:focus { border-color: #3498db; outline: none; box-shadow: 0 0 5px rgba(52, 152, 219, 0.3); }

/* 6. BUTONLAR */
.btn-kaydet { background-color: var(--primary-brand); color: white; padding: 12px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; width: 100%; transition: all 0.2s; }
.btn-kaydet:hover { opacity: 0.9; transform: translateY(-1px); }
.depo-btn { background-color: #2980b9; }
.btn-pano { background-color: var(--satis-color); margin-top: 10px; }

/* 7. BİLDİRİM VE TABLO */
.bildirim { margin-top: 25px; padding: 15px 20px; background-color: #e8f8f2; color: var(--satis-color); border-radius: 6px; font-weight: 600; text-align: center; border: 1px solid #d5f5e3; }
.bildirim.hata { background-color: #fdf2f2; color: var(--primary-brand); border: 1px solid #fadbd8; }

.tablo-wrapper { overflow-x: auto; background: white; padding: 15px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
.excel-tablosu { width: 100%; border-collapse: collapse; font-size: 13px; }
.excel-tablosu th { background-color: #f8f9fa; padding: 14px 10px; border: 1px solid #dee2e6; text-align: left; }
.excel-tablosu td { border: 1px solid #dee2e6; padding: 10px; color: var(--text-main); }
.td-maliyet { background-color: #fff5f5; color: var(--primary-brand); text-align: right; font-weight: 600; }

@media (max-width: 768px) {
  .ozet-kartlari-wrapper { justify-content: center; }
  .kart { width: 100%; }
}
</style>