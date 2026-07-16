<template>
  <div class="sistem-container">
    <div style="width: 100%; max-width: 1200px; margin: 0 auto;">
      
      <UstMenu />

      <div class="sayfa-karti">
        <div class="karti-header">
          <div class="baslik-alani">
            <h3>🤝 Müşteri ve Cari Yönetimi (CRM)</h3>
            <p>Çalıştığınız firmaları, yetkili iletişim bilgilerini ve geçmiş projelerinizi tek merkezden yönetin.</p>
          </div>
          <div class="istatistik-rozetler">
            <div class="rozet-kutu">Toplam Cari: <strong>{{ musteriler.length }}</strong></div>
            <div class="rozet-kutu yesil">Aktif Çalışılan: <strong>{{ aktifMusteriSayisi }}</strong></div>
          </div>
        </div>

        <!-- FİLTRELEME VE YENİ MÜŞTERİ EKLEME -->
        <div class="kontrol-paneli">
          <button @click="yeniMusteriModal = true" class="btn-islem btn-koyu ana-aksiyon">
            <span class="ikon">➕</span> Yeni Cari/Firma Ekle
          </button>
          
          <div class="filtre-grubu">
            <select v-model="seciliDurum" class="durum-select">
              <option value="HEPSI">Tüm Firmalar</option>
              <option value="AKTIF">🟢 Aktif Çalışılanlar</option>
              <option value="PASIF">⚪ Pasif/Eski Müşteriler</option>
            </select>
            <div class="arama-kutusu">
              <span class="ikon">🔍</span>
              <input v-model="aramaMetni" type="text" placeholder="Firma, yetkili veya vergi no ara..." />
            </div>
          </div>
        </div>

        <!-- MÜŞTERİ LİSTESİ TABLOSU -->
        <div class="tablo-sarmalayici">
          <table class="kurumsal-tablo">
            <thead>
              <tr>
                <th>Firma / Cari Unvanı</th>
                <th>Yetkili Kişi & İletişim</th>
                <th>Vergi / Cari No</th>
                <th class="merkez-hizali">Aktif Proje</th>
                <th>Durum</th>
                <th class="sag-hizali">Cari İşlemler</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="filtrelenmisMusteriler.length === 0">
                <td colspan="6" class="bos-durum">Arama kriterinize uygun müşteri kaydı bulunamadı.</td>
              </tr>
              
              <tr v-for="musteri in filtrelenmisMusteriler" :key="musteri.id" :class="{'pasif-satir': !musteri.aktif_mi}">
                <td>
                  <div class="firma-adi"><span class="ikon">🏢</span> {{ musteri.firma_adi }}</div>
                  <div class="sehir-bilgisi">{{ musteri.sehir || 'Lokasyon Belirtilmedi' }}</div>
                </td>
                <td>
                  <div class="yetkili-adi"><span class="ikon">👤</span> {{ musteri.yetkili_kisi || '-' }}</div>
                  <div class="iletisim-bilgisi">
                    <span v-if="musteri.telefon">📞 {{ musteri.telefon }}</span>
                    <span v-if="musteri.email">✉️ {{ musteri.email }}</span>
                  </div>
                </td>
                <td class="kod">
                  {{ musteri.vergi_no || 'Tanimlanmadi' }}
                </td>
                <td class="merkez-hizali">
                  <span v-if="musteri.aktif_proje_sayisi > 0" class="proje-sayaci">{{ musteri.aktif_proje_sayisi }} Proje</span>
                  <span v-else class="pasif-yazi">-</span>
                </td>
                <td>
                  <span :class="['durum-rozeti', musteri.aktif_mi ? 'yesil' : 'gri']">
                    {{ musteri.aktif_mi ? '🟢 Aktif' : '⚪ Pasif' }}
                  </span>
                </td>
                <td class="islemler">
                  <button @click="musteriDuzenle(musteri)" class="btn-islem btn-mavi-cizgili">Düzenle</button>
                  <button v-if="musteri.aktif_mi" @click="durumDegistir(musteri, false)" class="btn-islem btn-kirmizi-cizgili">Pasife Al</button>
                  <button v-else @click="durumDegistir(musteri, true)" class="btn-islem btn-yesil-cizgili">Aktifleştir</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

      </div>
    </div>

    <!-- YENİ/DÜZENLE MÜŞTERİ MODALI -->
    <transition name="fade">
      <div v-if="yeniMusteriModal" class="modal-overlay">
        <div class="modal-kutu">
          <div class="modal-header">
            <h4>{{ duzenlenenMusteriId ? '✏️ Cari Bilgilerini Güncelle' : '🏢 Yeni Cari/Firma Tanımla' }}</h4>
            <button @click="modalKapat" class="kapat-btn">✕</button>
          </div>
          <div class="modal-body">
            
            <div class="form-grid">
              <div class="input-grubu tam-genislik">
                <label>Firma / Şirket Resmi Unvanı *</label>
                <input v-model="form.firma_adi" type="text" placeholder="Örn: Rönesans Holding A.Ş." class="vurgulu-input" />
              </div>

              <div class="ikili-sutun">
                <div class="input-grubu">
                  <label>Vergi Dairesi & No</label>
                  <input v-model="form.vergi_no" type="text" placeholder="Örn: 1234567890" />
                </div>
                <div class="input-grubu">
                  <label>Şehir / Ülke</label>
                  <input v-model="form.sehir" type="text" placeholder="Örn: Ankara / Türkiye" />
                </div>
              </div>
              
              <div class="ayrac">İletişim Bilgileri</div>

              <div class="input-grubu tam-genislik">
                <label>Yetkili Kişi / İrtibat Noktası</label>
                <input v-model="form.yetkili_kisi" type="text" placeholder="Örn: Ahmet Yılmaz (Satın Alma Müdürü)" />
              </div>

              <div class="ikili-sutun">
                <div class="input-grubu">
                  <label>Telefon Numarası</label>
                  <input v-model="form.telefon" type="text" placeholder="+90 555 123 45 67" />
                </div>
                <div class="input-grubu">
                  <label>E-Posta Adresi</label>
                  <input v-model="form.email" type="email" placeholder="ornek@firma.com" />
                </div>
              </div>

              <div class="input-grubu tam-genislik">
                <label>Firma Adresi / Şantiye Lokasyonu</label>
                <textarea v-model="form.adres" rows="2" placeholder="Tam adresi buraya girebilirsiniz..."></textarea>
              </div>
            </div>

          </div>
          <div class="modal-footer">
            <button @click="modalKapat" class="btn-islem btn-gri">İptal</button>
            <button @click="musteriKaydet" class="btn-islem btn-koyu">
              {{ duzenlenenMusteriId ? 'Değişiklikleri Kaydet' : 'Sisteme Ekle' }}
            </button>
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

const aktifKullanici = ref(localStorage.getItem('kullanici_adi') || 'Sistem');
const musteriler = ref([]);
const aramaMetni = ref('');
const seciliDurum = ref('HEPSI');

const yeniMusteriModal = ref(false);
const duzenlenenMusteriId = ref(null);
const form = ref({ firma_adi: '', vergi_no: '', sehir: '', yetkili_kisi: '', telefon: '', email: '', adres: '' });

// İstatistikler
const aktifMusteriSayisi = computed(() => musteriler.value.filter(m => m.aktif_mi).length);

const filtrelenmisMusteriler = computed(() => {
  let sonuc = musteriler.value;
  if (seciliDurum.value === 'AKTIF') sonuc = sonuc.filter(m => m.aktif_mi);
  if (seciliDurum.value === 'PASIF') sonuc = sonuc.filter(m => !m.aktif_mi);

  if (aramaMetni.value) {
    const arama = aramaMetni.value.toLowerCase();
    sonuc = sonuc.filter(m => 
      m.firma_adi?.toLowerCase().includes(arama) || 
      m.yetkili_kisi?.toLowerCase().includes(arama) ||
      m.vergi_no?.toLowerCase().includes(arama)
    );
  }
  return sonuc;
});

onMounted(() => {
  musterileriGetir();
});

const musterileriGetir = async () => {
  try {
    const res = await axios.get(`${API_BASE}/musteriler`);
    musteriler.value = res.data;
  } catch (error) {
    console.error("Müşteriler yüklenemedi:", error);
    musteriler.value = [];
  }
};
const modalKapat = () => {
  yeniMusteriModal.value = false;
  duzenlenenMusteriId.value = null;
  form.value = { firma_adi: '', vergi_no: '', sehir: '', yetkili_kisi: '', telefon: '', email: '', adres: '' };
};

const musteriDuzenle = (musteri) => {
  duzenlenenMusteriId.value = musteri.id;
  form.value = { ...musteri }; // Veriyi kopyala
  yeniMusteriModal.value = true;
};

const durumDegistir = async (musteri, durum) => {
  const islemAdi = durum ? 'Aktifleştirmek' : 'Pasife Almak';
  if (!confirm(`${musteri.firma_adi} adlı cariyi ${islemAdi} istediğinize emin misiniz?`)) return;

  try {
    await axios.put(`${API_BASE}/musteriler/${musteri.id}/durum`, { aktif_mi: durum }, {
      headers: { 'islem-yapan': aktifKullanici.value }
    });
    musteri.aktif_mi = durum; // Ekranda anında güncelle
  } catch (error) {
    alert("Durum güncellenemedi.");
  }
};

const musteriKaydet = async () => {
  if (!form.value.firma_adi) {
    return alert("Firma resmi unvanı girmek zorunludur!");
  }

  try {
    if (duzenlenenMusteriId.value) {
      // Güncelleme İşlemi (PUT)
      await axios.put(`${API_BASE}/musteriler/${duzenlenenMusteriId.value}`, form.value, {
        headers: { 'islem-yapan': aktifKullanici.value }
      });
      alert("Cari bilgileri başarıyla güncellendi.");
    } else {
      // Yeni Ekleme İşlemi (POST)
      await axios.post(`${API_BASE}/musteriler`, form.value, {
        headers: { 'islem-yapan': aktifKullanici.value }
      });
      alert("Yeni müşteri sisteme başarıyla eklendi.");
    }
    modalKapat();
    musterileriGetir();
  } catch (error) {
    alert("İşlem sırasında bir hata oluştu.");
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
.rozet-kutu { background: #f8fafc; border: 1px solid #e2e8f0; color: #475569; padding: 6px 12px; border-radius: 6px; font-size: 12px; }
.rozet-kutu.yesil { background: #ecfdf5; border-color: #a7f3d0; color: #059669; }
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

/* Satır Renklendirmeleri */
.kurumsal-tablo tr:hover td { background-color: #f8fafc; }
.pasif-satir td { background-color: #f8fafc !important; opacity: 0.6; }

.firma-adi { font-weight: 600; color: #0f172a; font-size: 14px; margin-bottom: 4px; }
.firma-adi .ikon { font-size: 12px; color: #64748b; margin-right: 4px; }
.sehir-bilgisi { font-size: 11px; color: #64748b; }
.yetkili-adi { font-weight: 500; color: #334155; margin-bottom: 4px; }
.yetkili-adi .ikon { font-size: 11px; color: #94a3b8; }
.iletisim-bilgisi { font-size: 11px; color: #64748b; display: flex; gap: 10px; }
.kod { font-family: monospace; color: #64748b; font-weight: 500; }

.merkez-hizali { text-align: center; }
.proje-sayaci { background: #eff6ff; color: #2563eb; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 700; border: 1px solid #bfdbfe; display: inline-block; }
.pasif-yazi { color: #cbd5e1; font-weight: 600; }

/* Durum Rozetleri */
.durum-rozeti { padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; display: inline-block; border: 1px solid; }
.durum-rozeti.yesil { background: #ecfdf5; color: #059669; border-color: #a7f3d0; }
.durum-rozeti.gri { background: #f1f5f9; color: #64748b; border-color: #cbd5e1; }

/* Butonlar */
.sag-hizali { text-align: right; }
.islemler { text-align: right; white-space: nowrap; }
.btn-islem { padding: 6px 12px; border: none; border-radius: 6px; font-size: 11px; font-weight: 600; cursor: pointer; transition: 0.2s; margin-left: 5px; }
.btn-koyu { background: #0f172a; color: white; }
.btn-koyu:hover { background: #1e293b; }
.btn-gri { background: #e2e8f0; color: #475569; }
.btn-gri:hover { background: #cbd5e1; }
.btn-mavi-cizgili { background: transparent; border: 1px solid #3b82f6; color: #3b82f6; }
.btn-mavi-cizgili:hover { background: #eff6ff; }
.btn-kirmizi-cizgili { background: transparent; border: 1px solid #ef4444; color: #ef4444; }
.btn-kirmizi-cizgili:hover { background: #fef2f2; }
.btn-yesil-cizgili { background: transparent; border: 1px solid #10b981; color: #10b981; }
.btn-yesil-cizgili:hover { background: #ecfdf5; }

.bos-durum { text-align: center; color: #94a3b8; font-style: italic; padding: 40px !important; }

/* MODAL TASARIMI */
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(15, 23, 42, 0.6); display: flex; justify-content: center; align-items: center; z-index: 1000; backdrop-filter: blur(3px); }
.modal-kutu { background: white; width: 100%; max-width: 600px; border-radius: 12px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); overflow: hidden; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 20px; border-bottom: 1px solid #e2e8f0; background: #f8fafc; }
.modal-header h4 { margin: 0; color: #0f172a; font-size: 16px; font-weight: 600; }
.kapat-btn { background: none; border: none; font-size: 18px; color: #94a3b8; cursor: pointer; }
.modal-body { padding: 25px; }

.form-grid { display: flex; flex-direction: column; gap: 15px; }
.ikili-sutun { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
.input-grubu label { display: block; font-size: 12px; font-weight: 600; color: #475569; margin-bottom: 6px; }
.input-grubu input, .input-grubu textarea { width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 13px; outline: none; font-family: inherit; box-sizing: border-box; }
.input-grubu textarea { resize: vertical; }
.input-grubu input:focus, .input-grubu textarea:focus { border-color: #0f172a; }
.vurgulu-input { border-left: 3px solid #3b82f6 !important; font-weight: 600; }
.ayrac { margin: 15px 0 5px 0; font-size: 12px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px dashed #e2e8f0; padding-bottom: 5px; }

.modal-footer { padding: 15px 20px; border-top: 1px solid #e2e8f0; display: flex; justify-content: flex-end; gap: 10px; background: #f8fafc; }

@media (max-width: 768px) { .karti-header, .kontrol-paneli { flex-direction: column; align-items: flex-start; gap: 15px; } .filtre-grubu { width: 100%; flex-direction: column; } .arama-kutusu { width: 100%; } .ikili-sutun { grid-template-columns: 1fr; } }
</style>