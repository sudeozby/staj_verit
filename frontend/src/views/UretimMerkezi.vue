<template>
  <div class="sistem-container">
    <div style="width: 100%; max-width: 1200px; margin: 0 auto;">
      
      <UstMenu />

      <div class="sayfa-karti">
        <div class="karti-header">
          <div class="baslik-alani">
            <h3>🏭 Üretim, Depo ve Proje Yönetimi</h3>
            <p>Yeni proje başlatın, envantere malzeme ekleyin veya panolara malzeme ataması yapın.</p>
          </div>
          <div class="istatistik-rozetler">
            <div class="rozet-kutu">Kayıtlı Proje: <strong>{{ projeler.length }}</strong></div>
          </div>
        </div>

        <!-- KURUMSAL SEKME (TAB) MENÜSÜ -->
        <div class="sekme-menusu">
          <button :class="{ aktif: aktifSekme === 'proje' }" @click="aktifSekme = 'proje'">
            <span class="ikon">📁</span> Yeni Proje Oluştur
          </button>
          <button :class="{ aktif: aktifSekme === 'depo' }" @click="aktifSekme = 'depo'">
            <span class="ikon">📦</span> Depo & İskonto Yönetimi
          </button>
          <button :class="{ aktif: aktifSekme === 'pano' }" @click="aktifSekme = 'pano'">
            <span class="ikon">⚙️</span> Pano Konfigürasyonu
          </button>
        </div>

        <div class="dikey-form-alani">
          
          <!-- 1. SEKME: PROJE KİMLİK BİLGİLERİ -->
          <transition name="fade" mode="out-in">
            <div v-if="aktifSekme === 'proje'" class="form-alani proje-formu">
              <h4 class="form-baslik">Proje Kimlik Bilgileri</h4>
              
              <div class="form-grid">
                <div class="ikili-sutun">
                  <div class="input-grubu">
                    <label>Müşteri Adı *</label>
                    <input v-model="yeniProje.musteri" placeholder="Firma / Müşteri adı giriniz" required />
                  </div>
                  <div class="input-grubu">
                    <label>Son Kullanıcı</label>
                    <input v-model="yeniProje.son_kullanici" placeholder="Sistemi kullanacak asıl firma" />
                  </div>
                </div>

                <div class="ikili-sutun">
                  <div class="input-grubu">
                    <label>Lokasyon (Şehir/Ülke)</label>
                    <input v-model="yeniProje.lokasyon" placeholder="Örn: Malatya / Türkiye" />
                  </div>
                  <div class="input-grubu">
                    <label class="zorunlu">Proje Adı *</label>
                    <input v-model="yeniProje.proje_adi" placeholder="Resmi proje adını giriniz" required class="vurgulu-input" />
                  </div>
                </div>
                
                <div class="input-grubu">
                  <label>Teklif Konusu</label>
                  <input v-model="yeniProje.teklif_konusu" placeholder="Örn: MCC Panoları Yenileme İşi" class="tam-genislik" />
                </div>
                
                <div class="ikili-sutun">
                  <div class="input-grubu">
                    <label>Teklif Tarihi</label>
                    <input v-model="yeniProje.teklif_tarihi" type="date" />
                  </div>
                  <div class="input-grubu">
                    <label>Referans No</label>
                    <input 
                      v-model="yeniProje.teklif_referans_no" 
                      placeholder="Sistem otomatik atayacak..." 
                      disabled 
                      class="disabled-input"
                    />
                  </div>
                </div>
                
                <div class="input-grubu">
                  <label>Hazırlayan Personel</label>
                  <input v-model="yeniProje.hazirlayan" placeholder="Teklifi hazırlayan yetkili" class="tam-genislik" />
                </div>
                
                <div class="input-grubu">
                  <label>📝 Proje Notları</label>
                  <textarea 
                    v-model="yeniProje.notlar" 
                    rows="3" 
                    placeholder="Proje ile ilgili ekstra bilgileri veya özel talepleri buraya girebilirsiniz..."
                  ></textarea>
                </div>
                
                <div class="buton-grubu-sag">
                  <button @click="projeOlustur" :disabled="isSubmitting" class="btn-islem btn-koyu ana-buton">
                    {{ isSubmitting ? 'Sisteme Kaydediliyor...' : 'Projeyi Oluştur ve Başlat' }}
                  </button>
                </div>
              </div>
            </div>
          </transition>

          <!-- 2. SEKME: DEPO VE İSKONTO YÖNETİMİ -->
          <transition name="fade" mode="out-in">
            <div v-if="aktifSekme === 'depo'">
              <div class="form-alani depo-formu">
                <h4 class="form-baslik">Depoya Yeni Malzeme Ekle</h4>
                
                <div class="form-grid">
                  <div class="ikili-sutun">
                    <div class="input-grubu">
                      <label>Sipariş Kodu *</label>
                      <input v-model="yeniMalzeme.siparis_kodu" placeholder="Örn: 1SDA067131R1" required />
                    </div>
                    <div class="input-grubu">
                      <label>Ürün Adı *</label>
                      <input v-model="yeniMalzeme.urun_adi" placeholder="Örn: 3 Fazlı Motor 15kW" required />
                    </div>
                  </div>
                  
                  <div class="uclu-sutun">
                    <div class="input-grubu">
                      <label>Marka</label>
                      <input v-model="yeniMalzeme.marka" placeholder="Örn: ABB, Siemens" />
                    </div>
                    <div class="input-grubu">
                      <label>Ürün Grubu</label>
                      <input v-model="yeniMalzeme.urun_grubu" placeholder="Örn: Şalt Malzemeleri" />
                    </div>
                    <div class="input-grubu">
                      <label>Tedarikçi Firma</label>
                      <input v-model="yeniMalzeme.tedarikci" placeholder="Örn: X Elektrik A.Ş." />
                    </div>
                  </div>
                  

                  

                  <div class="ayrac">Stok ve Tedarik Parametreleri</div>

                  <div class="uclu-sutun">
                    <div class="input-grubu">
                      <label>Mevcut Stok *</label>
                      <input v-model="yeniMalzeme.mevcut_stok" type="number" placeholder="0" required />
                    </div>
                    <div class="input-grubu">
                      <label>Kritik Eşik *</label>
                      <input v-model="yeniMalzeme.kritik_esik" type="number" placeholder="5" required />
                      <small class="ipucu-metni">Altına düşerse satın alma tetiklenir.</small>
                    </div>
                    <div class="input-grubu">
                      <label>Temin Süresi (Gün) *</label>
                      <input v-model="yeniMalzeme.temin_suresi_gun" type="number" placeholder="0" required />
                      <small class="ipucu-metni">BOM analizinde kullanılır.</small>
                    </div>
                  </div>


                  <div class="ikili-sutun">
                    <div class="input-grubu">
                      <label>Liste Fiyatı *</label>
                      <input v-model="yeniMalzeme.liste_fiyati" type="number" placeholder="0.00" required />
                    </div>
                    <div class="input-grubu">
                      <label>Para Birimi *</label>
                      <select v-model="yeniMalzeme.para_birimi" required>
                        <option value="TRY">TRY (Türk Lirası)</option>
                        <option value="USD">USD (Dolar)</option>
                        <option value="EUR">EUR (Euro)</option>
                      </select>
                    </div>
                  </div>
                  
                  <div class="input-grubu">
                    <label>📊 İskonto Grubu (Marka/Grup Eşleşmesi):</label>
                    <select v-model="yeniMalzeme.grup_iskonto_id">
                      <option :value="null">Grup Seçin (Zorunlu Değil)</option>
                      <option v-for="grup in iskontoGruplari" :key="grup.id" :value="grup.id">
                        {{ grup.grup_adi }}
                      </option>
                    </select>
                    <small class="ipucu-metni">Eğer seçilirse, malzeme fiyatı bu grubun kurallarına göre hesaplanır.</small>
                  </div>

                  <div class="input-grubu">
                    <label>Malzeme Notları (Opsiyonel)</label>
                    <textarea 
                      v-model="yeniMalzeme.notlar" 
                      placeholder="Teknik özellikler veya depo raf bilgisi..." 
                      rows="2"
                    ></textarea>
                  </div>
                  
                  <div class="buton-grubu-sag">
                    <button @click="malzemeEkle" class="btn-islem btn-yesil">Malzemeyi Envantere Kaydet</button>
                  </div>
                </div>
              </div>

              <!-- Yalnızca Yöneticiye Görünen İskonto Paneli -->
              <div v-if="kullaniciRolu === 'yonetici'" class="admin-panel">
                <div class="admin-header">
                  <h4>🛠 İskonto Grubu Yönetimi (Yönetici Ayrıcalığı)</h4>
                  <p>Yeni bir iskonto kuralı oluşturarak malzemelere toplu indirim şablonu tanımlayın.</p>
                </div>
                
                <div class="admin-grid">
                  <div class="input-grubu">
                    <label>Grup Adı</label>
                    <input v-model="yeniGrup.grup_adi" placeholder="Örn: ABB Sürücü">
                  </div>
                  <div class="input-grubu">
                    <label>Maliyet İsk.</label>
                    <input v-model.number="yeniGrup.maliyet_iskonto" placeholder="Örn: 0.15">
                  </div>
                  <div class="input-grubu">
                    <label>Proje İsk.</label>
                    <input v-model.number="yeniGrup.proje_iskonto" placeholder="Örn: 0.10">
                  </div>
                  <div class="input-grubu">
                    <label>Satış İsk.</label>
                    <input v-model.number="yeniGrup.satis_iskonto" placeholder="Örn: 0.05">
                  </div>
                  <div class="input-grubu">
                    <label>Notlar</label>
                    <input v-model="yeniGrup.notlar" placeholder="Opsiyonel açıklama">
                  </div>
                  <div class="admin-btn-alani">
                    <button @click.prevent="grupEkle" type="button" class="btn-islem btn-kirmizi">
                      Grubu Kaydet
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </transition>

          <!-- 3. SEKME: PANO KONFİGÜRASYONU (ATAMA) -->
          <transition name="fade" mode="out-in">
            <div v-if="aktifSekme === 'pano'" class="form-alani pano-formu">
              <h4 class="form-baslik">Panoya Malzeme Atama İstasyonu</h4>
              <p class="form-aciklama">Envanterdeki bir malzemeyi, belirli bir projenin panosuna dahil edin.</p>
              
              <div class="form-grid">
                <div class="input-grubu">
                  <label>Hedef Proje</label>
                  <select v-model="yeniPanoMalzeme.proje_id" class="vurgulu-select">
                    <option disabled value="">Projeyi Seçin...</option>
                    <option v-for="p in projeler" :key="p.id" :value="p.id">#{{ p.referans_no || p.id }} - {{ p.proje_adi }}</option>
                  </select>
                </div>

                <div class="input-grubu">
                  <label>Kullanılacak Malzeme</label>
                  <select v-model="yeniPanoMalzeme.malzeme_id" class="vurgulu-select">
                    <option disabled value="">Malzemeyi Seçin...</option>
                    <option v-for="m in malzemeler" :key="m.id" :value="m.id">{{ m.urun_adi }} ({{ m.siparis_kodu }})</option>
                  </select>
                </div>

                <div class="ikili-sutun">
                  <div class="input-grubu">
                    <label>Pano Türü (Konum)</label>
                    <select v-model="yeniPanoMalzeme.pano_turu">
                      <option value="ADP 1">ADP 1</option>
                      <option value="MCC 1">MCC 1</option>
                      <option value="MCC 2">MCC 2</option>
                      <option value="MCC 3">MCC 3</option>
                      <option value="MCC 4">MCC 4</option>
                      <option value="MCC 5">MCC 5</option>
                      <option value="REM 100">REM 100</option>
                      <option value="REM 200">REM 200</option>
                      <option value="REM 300">REM 300</option>
                      <option value="REM 400">REM 400</option>
                      <option value="REM 500">REM 500</option>
                      <option value="KONTROL S.">KONTROL S.</option>
                      <option value="SAHA">SAHA</option>
                    </select>
                  </div>
                  <div class="input-grubu">
                    <label>Kullanılacak Adet</label>
                    <input v-model="yeniPanoMalzeme.adet" type="number" placeholder="Örn: 2" />
                  </div>
                </div>
                
                <div class="input-grubu ozel-iskonto-alani">
                  <label class="vurgu-baslik">🎯 Özel İskonto (Opsiyonel):</label>
                  <input 
                    v-model.number="yeniPanoMalzeme.ozel_iskonto" 
                    type="number"
                    step="0.01"
                    placeholder="Örn: 0.05 (%5 indirim)" 
                  >
                  <small class="ipucu-metni">Sadece bu panodaki bu malzemeye özel ekstra indirim oranı uygular.</small>
                </div>

                <div class="buton-grubu-sag">
                  <button @click="panoyaEkle" class="btn-islem btn-mavi">Malzemeyi Panoya Atamayı Onayla</button>
                </div>
              </div>
            </div>
          </transition>

        </div>
      </div>
    </div>

    <!-- CANLI BİLDİRİM EKRANI -->
    <transition name="slide-up">
      <div 
        v-if="mesaj" 
        :class="['bildirim', hataVar ? 'hata' : 'bilgi']"
        @click="mesaj = ''" 
      >
        <span class="bildirim-ikon">{{ hataVar ? '⚠️' : '✅' }}</span>
        {{ mesaj }}
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import UstMenu from '../components/UstMenu.vue'
import { API_BASE } from '../config'

const aktifSekme = ref('proje')
const router = useRouter()
const kullaniciRolu = ref(localStorage.getItem('kullaniciRolu') || 'standart')
const isSubmitting = ref(false)
const iskontoGruplari = ref([])

const mesaj = ref('')
const hataVar = ref(false)

const projeler = ref([])
const malzemeler = ref([])

const yeniGrup = ref({ grup_adi: '', maliyet_iskonto: null, proje_iskonto: null, satis_iskonto: null, notlar: '' });

const yeniMalzeme = ref({ 
  siparis_kodu: '', 
  urun_adi: '', 
  marka: '', 
  urun_grubu: '', 
  tedarikci: '', 
  liste_fiyati: null, 
  para_birimi: 'TRY', 
  notlar: '', 
  grup_iskonto_id: null,
  // EKLENEN KRİTİK ALANLAR
  mevcut_stok: 0,
  kritik_esik: 5, // Bu seviyenin altına düşünce otomatik talep açılacak
  temin_suresi_gun: 0 // BOM analizindeki darboğaz hesabı için
})

const yeniProje = ref({ 
  proje_adi: '', musteri: '', son_kullanici: '', lokasyon: '', 
  teklif_konusu: '', teklif_tarihi: '', teklif_referans_no: '', hazirlayan: '' 
})

const yeniPanoMalzeme = ref({ 
  proje_id: '', malzeme_id: '', pano_turu: 'ADP 1', adet: 1, ozel_iskonto: 0
})

const bildirimGoster = (metin, hata = false) => {
  mesaj.value = metin
  hataVar.value = hata
  setTimeout(() => { mesaj.value = ''; hataVar.value = false }, 5000)
}

const grupEkle = async () => {
  try {
    const gonderilecekVeri = {
      grup_adi: yeniGrup.value.grup_adi,
      maliyet_iskonto: parseFloat(yeniGrup.value.maliyet_iskonto || 0),
      proje_iskonto: parseFloat(yeniGrup.value.proje_iskonto || 0),
      satis_iskonto: parseFloat(yeniGrup.value.satis_iskonto || 0),
      notlar: yeniGrup.value.notlar || "-"
    };
    const aktifKullanici = localStorage.getItem("kullanici_adi") || "Sistem";
    await axios.post(`${API_BASE}/iskonto-gruplari`, gonderilecekVeri, {
      headers: { 'current-user-role': 'yonetici', 'islem-yapan': aktifKullanici }
    });
    bildirimGoster("Yeni grup başarıyla eklendi! ✅");
    yeniGrup.value = { grup_adi: '', maliyet_iskonto: null, proje_iskonto: null, satis_iskonto: null, notlar: '' };
    await verileriYukle(); 
  } catch (error) {
    bildirimGoster("Hata! İşlem tamamlanamadı.", true);
  }
};

const verileriYukle = async () => {
  try {
    const [p, m, i] = await Promise.all([
      axios.get(`${API_BASE}/projeler/listele`),
      axios.get(`${API_BASE}/malzemeler/listele`),
      axios.get(`${API_BASE}/iskonto-gruplari`) 
    ])
    projeler.value = p.data
    malzemeler.value = m.data
    iskontoGruplari.value = i.data 
  } catch (error) { 
    bildirimGoster("Veriler yüklenirken bağlantı hatası!", true) 
  }
}

const projeOlustur = async () => {
  if (!yeniProje.value.proje_adi) return bildirimGoster("Lütfen Proje Adı girin!", true)
  isSubmitting.value = true
  try {
    const aktifKullanici = localStorage.getItem("kullanici_adi") || "Sistem";
    const res = await axios.post(`${API_BASE}/projeler`, yeniProje.value, {
      headers: { 'islem-yapan': aktifKullanici }
    });
    bildirimGoster(res.data.mesaj || "Proje başarıyla oluşturuldu! ✅")
    yeniProje.value = { proje_adi: '', musteri: '', son_kullanici: '', lokasyon: '', teklif_konusu: '', teklif_tarihi: '', teklif_referans_no: '', hazirlayan: '' }
    await verileriYukle()
  } catch (error) { 
    bildirimGoster(error.response?.data?.detail || "Proje oluşturulamadı.", true) 
  } finally { isSubmitting.value = false }
}

const malzemeEkle = async () => {
  if (!yeniMalzeme.value.siparis_kodu || !yeniMalzeme.value.urun_adi) {
    return bildirimGoster("Zorunlu alanları doldurun!", true)
  }
  try {
    const aktifKullanici = localStorage.getItem("kullanici_adi") || "Sistem";
    const res = await axios.post(`${API_BASE}/malzemeler`, yeniMalzeme.value, {
      headers: { 'islem-yapan': aktifKullanici }
    });
    bildirimGoster(res.data.mesaj || "Malzeme depoya eklendi! ✅")
    yeniMalzeme.value = { 
      siparis_kodu: '', urun_adi: '', marka: '', urun_grubu: '', tedarikci: '', 
      liste_fiyati: null, para_birimi: 'TRY', grup_iskonto_id: null, notlar: '' 
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
    const aktifKullanici = localStorage.getItem("kullanici_adi") || "Sistem";
    const res = await axios.post(`${API_BASE}/projeler/pano-malzeme-ekle`, yeniPanoMalzeme.value, {
      headers: { 'islem-yapan': aktifKullanici }
    })
    bildirimGoster(res.data.mesaj || `Başarıyla atandı: ${yeniPanoMalzeme.value.pano_turu} ✅`)
    yeniPanoMalzeme.value.adet = 1;
    yeniPanoMalzeme.value.ozel_iskonto = 0; 
  } catch (error) { 
    bildirimGoster(error.response?.data?.detail || "Malzeme panoya atanamadı!", true) 
  }
}

onMounted(verileriYukle)
</script>

<style scoped>
/* KURUMSAL SAAS TASARIMI (UI/UX) */
.sistem-container { min-height: 100vh; background-color: #f8fafc; padding-bottom: 40px; font-family: 'Segoe UI', system-ui, sans-serif; color: #334155; }

.sayfa-karti { background: #ffffff; padding: 35px; border-radius: 12px; border-top: 4px solid #0f172a; box-shadow: 0 4px 15px rgba(0,0,0,0.03); margin-top: 25px; }

.karti-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 25px; border-bottom: 1px solid #e2e8f0; padding-bottom: 15px; }
.baslik-alani h3 { margin: 0; color: #0f172a; font-size: 20px; font-weight: 600; }
.baslik-alani p { margin: 5px 0 0 0; color: #64748b; font-size: 13px; }

.istatistik-rozetler { display: flex; gap: 10px; }
.rozet-kutu { background: #eff6ff; border: 1px solid #bfdbfe; color: #1d4ed8; padding: 6px 12px; border-radius: 6px; font-size: 12px; }
.rozet-kutu strong { font-size: 14px; margin-left: 5px; }

/* SEKME MENÜSÜ */
.sekme-menusu { display: flex; gap: 10px; margin-bottom: 25px; border-bottom: 1px solid #e2e8f0; padding-bottom: 15px; }
.sekme-menusu button { background: transparent; border: none; padding: 10px 20px; font-size: 13px; font-weight: 600; color: #64748b; cursor: pointer; border-radius: 8px; transition: all 0.2s; display: flex; align-items: center; gap: 8px; }
.sekme-menusu button:hover { background: #f1f5f9; color: #0f172a; }
.sekme-menusu button.aktif { background: #0f172a; color: white; box-shadow: 0 4px 10px rgba(15, 23, 42, 0.15); }
.sekme-menusu button .ikon { font-size: 16px; }

/* FORM ALANLARI */
.form-alani { background: #f8fafc; padding: 25px; border-radius: 8px; border: 1px solid #e2e8f0; }
.form-baslik { margin: 0 0 20px 0; color: #0f172a; font-size: 16px; font-weight: 600; border-bottom: 1px dashed #cbd5e1; padding-bottom: 10px; }
.form-aciklama { font-size: 12px; color: #64748b; margin-top: -10px; margin-bottom: 20px; }

.form-grid { display: flex; flex-direction: column; gap: 20px; }
.ikili-sutun { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.uclu-sutun { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; }

.input-grubu label { display: block; font-size: 12px; font-weight: 600; color: #475569; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px; }
.input-grubu label.zorunlu::after { content: ' *'; color: #e11d48; }
.vurgu-baslik { color: #d97706 !important; }

.input-grubu input, .input-grubu select, .input-grubu textarea { 
  width: 100%; padding: 12px; border: 1px solid #cbd5e1; border-radius: 6px; 
  font-size: 13px; box-sizing: border-box; background-color: #ffffff;
  transition: all 0.2s; outline: none; font-family: inherit;
}
.input-grubu input:focus, .input-grubu select:focus, .input-grubu textarea:focus { 
  border-color: #0f172a; box-shadow: 0 0 0 2px rgba(15, 23, 42, 0.1); 
}

.vurgulu-input { border-left: 3px solid #3b82f6 !important; font-weight: 600;}
.vurgulu-select { border-left: 3px solid #10b981 !important; font-weight: 600;}
.disabled-input { background-color: #f1f5f9 !important; color: #94a3b8; cursor: not-allowed; }

.ipucu-metni { display: block; font-size: 11px; color: #64748b; margin-top: 6px; font-style: italic; }
.ozel-iskonto-alani { background: #fffbeb; padding: 15px; border-radius: 6px; border: 1px dashed #f59e0b; }

/* Butonlar */
.buton-grubu-sag { display: flex; justify-content: flex-end; margin-top: 10px; }
.btn-islem { padding: 12px 25px; border: none; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; transition: 0.2s; }
.btn-koyu { background-color: #0f172a; color: white; }
.btn-koyu:hover { background-color: #1e293b; transform: translateY(-1px); }
.btn-yesil { background-color: #10b981; color: white; }
.btn-yesil:hover { background-color: #059669; transform: translateY(-1px); }
.btn-mavi { background-color: #3b82f6; color: white; }
.btn-mavi:hover { background-color: #2563eb; transform: translateY(-1px); }
.btn-kirmizi { background-color: #ef4444; color: white; }
.btn-kirmizi:hover { background-color: #dc2626; transform: translateY(-1px); }

/* Yönetici Paneli */
.admin-panel { background: #fff1f2; padding: 25px; border-radius: 8px; border-left: 4px solid #e11d48; margin-top: 30px; }
.admin-header h4 { margin: 0 0 5px 0; color: #be123c; font-size: 15px; font-weight: 600; }
.admin-header p { margin: 0 0 20px 0; color: #9f1239; font-size: 12px; }
.admin-grid { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr 2fr auto; gap: 15px; align-items: end; }
.admin-btn-alani { margin-bottom: 2px; } /* Buton hizalaması için */

/* Bildirim Alert */
.bildirim { position: fixed; bottom: 30px; right: 30px; padding: 16px 24px; border-radius: 8px; font-size: 14px; font-weight: 600; color: white; box-shadow: 0 10px 25px rgba(0,0,0,0.15); display: flex; align-items: center; gap: 10px; z-index: 1000; cursor: pointer; }
.bildirim.bilgi { background-color: #10b981; }
.bildirim.hata { background-color: #e11d48; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease, transform 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(10px); }
.slide-up-enter-active, .slide-up-leave-active { transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
.slide-up-enter-from, .slide-up-leave-to { opacity: 0; transform: translateY(30px); }

@media (max-width: 900px) {
  .ikili-sutun, .uclu-sutun { grid-template-columns: 1fr; gap: 15px; }
  .sekme-menusu { flex-direction: column; }
  .admin-grid { grid-template-columns: 1fr 1fr; }
  .admin-grid .btn-islem { grid-column: span 2; width: 100%; }
}
</style>