<template>
  <div class="sistem-container">
    <div style="width: 100%; max-width: 1200px; margin: 0 auto;">
      
      <UstMenu />

      <div class="sayfa-karti">
        <div class="karti-header">
          <div class="baslik-alani">
            <h3>⚠️ Revizyon ve Onay Merkezi</h3>
            <p>Sahadaki imalatı durdurun, proje değişikliklerini işleyin ve yönetici onayıyla yeni reçeteyi sahaya iletin.</p>
          </div>
          <div class="istatistik-rozetler">
            <div class="rozet-kutu">Onay Bekleyen: <strong>{{ onayBekleyenSayisi }}</strong></div>
            <div class="rozet-kutu kirmizi">Aktif Revizyon: <strong>{{ aktifRevizyonSayisi }}</strong></div>
          </div>
        </div>

        <!-- YENİ REVİZYON BAŞLATMA BUTONU VE FİLTRELER -->
        <div class="kontrol-paneli">
          <button @click="yeniRevizyonModal = true" class="btn-islem btn-koyu ana-aksiyon">
            <span class="ikon">➕</span> Sahada Yeni Revizyon Başlat
          </button>
          
          <div class="filtre-grubu">
            <select v-model="seciliDurum" class="durum-select">
              <option value="HEPSI">Tüm Revizyon Kayıtları</option>
              <option value="ONAY_BEKLIYOR">⏳ Yönetici Onayı Bekleyenler</option>
              <option value="ONAYLANDI">✅ Onaylanıp Sahaya İletilenler</option>
              <option value="REDDEDILDI">❌ Reddedilenler</option>
            </select>
            <div class="arama-kutusu">
              <span class="ikon">🔍</span>
              <input v-model="aramaMetni" type="text" placeholder="Proje, dosya kodu veya not ara..." />
            </div>
          </div>
        </div>

        <!-- REVİZYON GEÇMİŞİ VE ONAY TABLOSU -->
        <div class="tablo-sarmalayici">
          <table class="kurumsal-tablo">
            <thead>
              <tr>
                <th>İş Emri & Proje</th>
                <th>Otomatik Dosya Adı</th>
                <th>Revizyonu Başlatan</th>
                <th>Revizyon Sebebi / Notu</th>
                <th>Durum</th>
                <th class="sag-hizali">Yönetici İşlemleri</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="filtrelenmisRevizyonlar.length === 0">
                <td colspan="6" class="bos-durum">Aktif bir revizyon talebi bulunmuyor.</td>
              </tr>
              
              <tr v-for="rev in filtrelenmisRevizyonlar" :key="rev.id" :class="{'onay-bekleyen': rev.durum === 'ONAY_BEKLIYOR'}">
                <td>
                  <div class="kod">#WORK-{{ rev.is_emri_id }}</div>
                  <div class="proje-adi">{{ rev.proje_adi }}</div>
                  <span class="pano-rozeti">{{ rev.pano_turu }}</span>
                </td>
                <td>
                  <!-- OTOMATİK OLUŞTURULAN DOSYA İSMİ -->
                  <div class="dosya-kodu">
                    <span class="ikon">📄</span> {{ rev.dosya_adi }}
                  </div>
                </td>
                <td>
                  <div class="kullanici-adi">{{ rev.talep_eden }}</div>
                  <div class="tarih-detay">{{ tarihFormatla(rev.tarih) }}</div>
                </td>
                <td class="not-sutunu">
                  "{{ rev.revizyon_notu }}"
                </td>
                <td>
                  <span :class="['durum-rozeti', rev.durum.toLowerCase()]">
                    {{ durumMetniGetir(rev.durum) }}
                  </span>
                </td>
                <td class="islemler">
                  <!-- YALNIZCA YÖNETİCİ ONAYLAYABİLİR/REDDEDEBİLİR -->
                  <template v-if="rev.durum === 'ONAY_BEKLIYOR'">
                    <template v-if="kullaniciRolu === 'yonetici'">
                      <button @click="revizyonOnayla(rev.id)" class="btn-islem btn-yesil">Onayla & İlet</button>
                      <button @click="revizyonReddet(rev.id)" class="btn-islem btn-kirmizi-cizgili">Reddet</button>
                    </template>
                    <template v-else>
                      <span class="kilitli-uyari">👑 Yönetici Onayı Bekleniyor</span>
                    </template>
                  </template>
                  
                  <template v-else>
                    <span class="islem-kapali">Süreç Tamamlandı</span>
                  </template>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

      </div>
    </div>

    <!-- YENİ REVİZYON BAŞLATMA MODALI -->
    <transition name="fade">
      <div v-if="yeniRevizyonModal" class="modal-overlay">
        <div class="modal-kutu">
          <div class="modal-header">
            <h4>⚠️ İmalatı Durdur & Revizyon Başlat</h4>
            <button @click="yeniRevizyonModal = false" class="kapat-btn">✕</button>
          </div>
          <div class="modal-body">
            <p class="uyari-metni">İlgili iş emri sahadaki personelin ekranında kilitlenecektir.</p>
            
            <div class="input-grubu">
              <label>Revizyona Girecek İş Emri</label>
              <select v-model="yeniTaleb.is_emri_id" class="tam-genislik-input">
                <option disabled value="">Seçiniz...</option>
                <option v-for="isEmri in aktifIsEmirleri" :key="isEmri.id" :value="isEmri.id">
                  #WORK-{{ isEmri.id }} | {{ isEmri.proje_adi }} ({{ isEmri.pano_turu }})
                </option>
              </select>
            </div>

            <!-- SİSTEMİN OTOMATİK HESAPLADIĞI DOSYA ADI -->
            <div v-if="yeniTaleb.is_emri_id" class="otomatik-dosya-uyarisi">
              <span class="etiket">Oluşturulacak Revizyon Dosyası:</span>
              <strong class="dosya-adi">{{ hesaplananDosyaAdi }}</strong>
            </div>

            <div class="input-grubu">
              <label>Değişiklik Sebebi ve Yeni Reçete Notları</label>
              <textarea 
                v-model="yeniTaleb.revizyon_notu" 
                rows="4" 
                placeholder="Örn: Müşteri talebi üzerine 15kW motor yerine 22kW motor kullanılacak."
                class="tam-genislik-textarea"
              ></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button @click="yeniRevizyonModal = false" class="btn-islem btn-gri">İptal</button>
            <button @click="revizyonTalebiOlustur" class="btn-islem btn-kirmizi">Talebi Yarat & Sahayı Kilitle</button>
          </div>
        </div>
      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import UstMenu from '../components/UstMenu.vue';
import { API_BASE } from '../config';

const kullaniciRolu = ref(localStorage.getItem('kullaniciRolu') || 'standart');
const aktifKullanici = ref(localStorage.getItem('kullanici_adi') || 'Sistem');

const revizyonlar = ref([]);
const aktifIsEmirleri = ref([]); 
const aramaMetni = ref('');
const seciliDurum = ref('HEPSI');

const yeniRevizyonModal = ref(false);
const yeniTaleb = ref({ is_emri_id: '', revizyon_notu: '' });

// İstatistikler
const onayBekleyenSayisi = computed(() => revizyonlar.value.filter(r => r.durum === 'ONAY_BEKLIYOR').length);
const aktifRevizyonSayisi = computed(() => revizyonlar.value.filter(r => r.durum === 'ONAYLANDI' || r.durum === 'ONAY_BEKLIYOR').length);

// -------------------------------------------------------------
// OTOMATİK DOSYA İSİMLENDİRME ALGORİTMASI (_R01, _R02)
// -------------------------------------------------------------
const hesaplananDosyaAdi = computed(() => {
  if (!yeniTaleb.value.is_emri_id) return '';
  
  // Önce seçilen iş emrinin referansını buluyoruz
  const seciliIsEmri = aktifIsEmirleri.value.find(i => i.id === yeniTaleb.value.is_emri_id);
  if (!seciliIsEmri) return '';

  // Bu iş emrine ait geçmişteki revizyon sayısını hesaplıyoruz
  const gecmisRevizyonSayisi = revizyonlar.value.filter(r => r.is_emri_id === yeniTaleb.value.is_emri_id).length;
  
  // +1 ekleyerek sıradaki numarayı buluyoruz (01, 02 formatında)
  const siradakiNumara = gecmisRevizyonSayisi + 1;
  const formatliNumara = String(siradakiNumara).padStart(2, '0');
  
  // Dosya adını birleştiriyoruz (Örn: TKLF-103_R01)
  return `TKLF-${seciliIsEmri.id}_R${formatliNumara}`;
});
// -------------------------------------------------------------

const filtrelenmisRevizyonlar = computed(() => {
  let sonuc = revizyonlar.value;
  if (seciliDurum.value !== 'HEPSI') sonuc = sonuc.filter(r => r.durum === seciliDurum.value);
  if (aramaMetni.value) {
    const arama = aramaMetni.value.toLowerCase();
    sonuc = sonuc.filter(r => 
      r.proje_adi?.toLowerCase().includes(arama) || 
      r.revizyon_notu?.toLowerCase().includes(arama) ||
      r.dosya_adi?.toLowerCase().includes(arama)
    );
  }
  return sonuc;
});

onMounted(() => {
  revizyonlariGetir();
  aktifIsleriGetir();
});

const revizyonlariGetir = async () => {
  try {
    const res = await axios.get(`${API_BASE}/revizyonlar`);
    revizyonlar.value = res.data;
  } catch (error) {
    console.error("Revizyonlar yüklenemedi:", error);
    revizyonlar.value = [];
  }
};

const aktifIsleriGetir = async () => {
  try {
    const res = await axios.get(`${API_BASE}/imalat/is-emirleri/aktif`);
    aktifIsEmirleri.value = res.data;
  } catch (error) {
    console.error("Aktif iş emirleri yüklenemedi:", error);
    aktifIsEmirleri.value = [];
  }
};

const tarihFormatla = (tarihStr) => {
  return new Date(tarihStr).toLocaleString('tr-TR', { day: '2-digit', month: 'short', hour: '2-digit', minute:'2-digit' });
};

const durumMetniGetir = (durum) => {
  const durumlar = {
    'ONAY_BEKLIYOR': '⏳ Yönetici Onayı Bekliyor',
    'ONAYLANDI': '✅ Sahaya İletildi',
    'REDDEDILDI': '❌ Talep Reddedildi'
  };
  return durumlar[durum] || durum;
};

const revizyonTalebiOlustur = async () => {
  if (!yeniTaleb.value.is_emri_id || !yeniTaleb.value.revizyon_notu) {
    return alert("Lütfen iş emrini seçin ve revizyon notunu yazın.");
  }
  
  // Gönderilecek veriye sistemin otomatik ürettiği dosya adını da ekliyoruz
  const gonderilecekVeri = {
    ...yeniTaleb.value,
    dosya_adi: hesaplananDosyaAdi.value
  };
  
  try {
    await axios.post(`${API_BASE}/revizyonlar/talep-et`, gonderilecekVeri, {
      headers: { 'islem-yapan': aktifKullanici.value }
    });
    alert(`Revizyon talebi "${hesaplananDosyaAdi.value}" adıyla oluşturuldu. Saha ekranı kilitlendi, Yönetici onayı bekleniyor.`);
    yeniRevizyonModal.value = false;
    yeniTaleb.value = { is_emri_id: '', revizyon_notu: '' };
    revizyonlariGetir();
  } catch (error) {
    alert("Talep oluşturulurken hata yaşandı.");
  }
};

const revizyonOnayla = async (revizyonId) => {
  if(!confirm("Bu revizyonu onaylayıp sahaya yeni talimatı iletmek istediğinize emin misiniz?")) return;
  
  try {
    await axios.put(`${API_BASE}/revizyonlar/${revizyonId}/onayla`, {}, {
      headers: { 'islem-yapan': aktifKullanici.value }
    });
    const rev = revizyonlar.value.find(r => r.id === revizyonId);
    if(rev) rev.durum = 'ONAYLANDI';
  } catch (error) {
    alert("Onay işlemi başarısız.");
  }
};

const revizyonReddet = async (revizyonId) => {
  try {
    await axios.put(`${API_BASE}/revizyonlar/${revizyonId}/reddet`, {}, {
      headers: { 'islem-yapan': aktifKullanici.value }
    });
    const rev = revizyonlar.value.find(r => r.id === revizyonId);
    if(rev) rev.durum = 'REDDEDILDI';
  } catch (error) {
    alert("İşlem başarısız.");
  }
};
</script>

<style scoped>
/* KURUMSAL SAAS TASARIMI */
.sistem-container { min-height: 100vh; background-color: #f8fafc; padding-bottom: 40px; font-family: 'Segoe UI', system-ui, sans-serif; color: #334155; }
.sayfa-karti { background: #ffffff; padding: 35px; border-radius: 12px; border-top: 4px solid #0f172a; box-shadow: 0 4px 15px rgba(0,0,0,0.03); margin-top: 25px; }
.karti-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 25px; border-bottom: 1px solid #e2e8f0; padding-bottom: 15px; }
.baslik-alani h3 { margin: 0; color: #0f172a; font-size: 20px; font-weight: 600; }
.baslik-alani p { margin: 5px 0 0 0; color: #64748b; font-size: 13px; }

.istatistik-rozetler { display: flex; gap: 10px; }
.rozet-kutu { background: #fffbeb; border: 1px solid #fde68a; color: #d97706; padding: 6px 12px; border-radius: 6px; font-size: 12px; }
.rozet-kutu.kirmizi { background: #fef2f2; border-color: #fecdd3; color: #e11d48; }
.rozet-kutu strong { font-size: 14px; margin-left: 5px; }

/* Kontrol Paneli */
.kontrol-paneli { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; background: #f8fafc; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0; }
.filtre-grubu { display: flex; gap: 15px; flex: 1; justify-content: flex-end; }
.ana-aksiyon { padding: 10px 20px; font-size: 13px; }
.durum-select { padding: 10px 15px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 13px; outline: none; background: #fff; cursor: pointer; }
.arama-kutusu { position: relative; width: 300px; }
.arama-kutusu .ikon { position: absolute; left: 12px; top: 11px; color: #94a3b8; font-size: 14px; }
.arama-kutusu input { width: 100%; padding: 10px 10px 10px 35px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 13px; outline: none; box-sizing: border-box; }
.durum-select:focus, .arama-kutusu input:focus { border-color: #0f172a; }

/* Tablo Yapısı */
.tablo-sarmalayici { overflow-x: auto; border: 1px solid #e2e8f0; border-radius: 8px; }
.kurumsal-tablo { width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; }
.kurumsal-tablo th { background-color: #f1f5f9; color: #475569; padding: 15px 20px; font-weight: 600; font-size: 12px; text-transform: uppercase; border-bottom: 1px solid #e2e8f0; }
.kurumsal-tablo td { padding: 15px 20px; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }

.onay-bekleyen td { background-color: #fffbeb !important; }

.kod { font-family: monospace; color: #64748b; font-weight: 500; font-size: 12px; }
.proje-adi { font-weight: 600; color: #0f172a; margin: 4px 0; }
.pano-rozeti { background: #e2e8f0; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 600; }
.dosya-kodu { background: #eff6ff; color: #2563eb; padding: 4px 8px; border-radius: 4px; font-family: monospace; font-size: 12px; font-weight: 700; display: inline-block; border: 1px solid #bfdbfe; }
.kullanici-adi { font-weight: 600; color: #3b82f6; font-size: 12px; }
.tarih-detay { font-size: 11px; color: #94a3b8; margin-top: 2px; }
.not-sutunu { color: #475569; font-style: italic; max-width: 250px; line-height: 1.4; }

/* Durum Rozetleri */
.durum-rozeti { padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; display: inline-block; border: 1px solid; }
.durum-rozeti.onay_bekliyor { background: #fffbeb; color: #d97706; border-color: #fcd34d; }
.durum-rozeti.onaylandi { background: #ecfdf5; color: #059669; border-color: #a7f3d0; }
.durum-rozeti.reddedildi { background: #fef2f2; color: #e11d48; border-color: #fecdd3; }

/* İşlemler */
.sag-hizali { text-align: right; }
.islemler { text-align: right; white-space: nowrap; }
.btn-islem { padding: 8px 15px; border: none; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; transition: 0.2s; margin-left: 5px; }
.btn-koyu { background: #0f172a; color: white; }
.btn-koyu:hover { background: #1e293b; }
.btn-yesil { background: #10b981; color: white; }
.btn-yesil:hover { background: #059669; }
.btn-kirmizi-cizgili { background: transparent; border: 1px solid #ef4444; color: #ef4444; }
.btn-kirmizi-cizgili:hover { background: #ef4444; color: white; }
.btn-gri { background: #e2e8f0; color: #475569; }
.btn-gri:hover { background: #cbd5e1; }
.btn-kirmizi { background: #e11d48; color: white; }
.btn-kirmizi:hover { background: #be123c; }

.kilitli-uyari { font-size: 11px; font-weight: 600; color: #d97706; }
.islem-kapali { font-size: 11px; color: #94a3b8; font-style: italic; }
.bos-durum { text-align: center; color: #94a3b8; font-style: italic; padding: 40px !important; }

/* MODAL TASARIMI */
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(15, 23, 42, 0.6); display: flex; justify-content: center; align-items: center; z-index: 1000; backdrop-filter: blur(3px); }
.modal-kutu { background: white; width: 100%; max-width: 500px; border-radius: 12px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); overflow: hidden; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 20px; border-bottom: 1px solid #e2e8f0; background: #fff1f2; }
.modal-header h4 { margin: 0; color: #be123c; font-size: 16px; font-weight: 600; }
.kapat-btn { background: none; border: none; font-size: 18px; color: #94a3b8; cursor: pointer; }
.modal-body { padding: 20px; }
.uyari-metni { font-weight: 600; color: #d97706; font-size: 12px; margin-top: 0; margin-bottom: 20px; }
.otomatik-dosya-uyarisi { background: #eff6ff; padding: 12px 15px; border-radius: 6px; border: 1px dashed #3b82f6; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center; }
.otomatik-dosya-uyarisi .etiket { font-size: 12px; color: #1d4ed8; }
.otomatik-dosya-uyarisi .dosya-adi { font-size: 14px; color: #1e3a8a; font-family: monospace; }
.input-grubu { margin-bottom: 15px; }
.input-grubu label { display: block; font-size: 12px; font-weight: 600; color: #475569; margin-bottom: 6px; }
.tam-genislik-input, .tam-genislik-textarea { width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 13px; outline: none; font-family: inherit; box-sizing: border-box; }
.tam-genislik-textarea { resize: vertical; }
.tam-genislik-input:focus, .tam-genislik-textarea:focus { border-color: #0f172a; }
.modal-footer { padding: 15px 20px; border-top: 1px solid #e2e8f0; display: flex; justify-content: flex-end; gap: 10px; background: #f8fafc; }

@media (max-width: 768px) { .karti-header, .kontrol-paneli { flex-direction: column; align-items: flex-start; gap: 15px; } .filtre-grubu { width: 100%; flex-direction: column; } .arama-kutusu { width: 100%; } }
</style>