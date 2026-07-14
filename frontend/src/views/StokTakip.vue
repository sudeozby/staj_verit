<template>
  <div class="sistem-container">
    <div style="width: 100%; max-width: 1200px; margin: 0 auto;">
      
      <UstMenu />

      <div class="sayfa-karti">
        <div class="karti-header">
          <div class="baslik-alani">
            <h3>📦 Dinamik Stok ve Envanter Takibi</h3>
            <p>Depodaki malzemelerin güncel durumunu izleyin, azalan stoklar için satın alma talebi oluşturun.</p>
          </div>
          <div class="istatistik-rozetler">
            <div class="rozet-kutu">Toplam Kalem: <strong>{{ malzemeler.length }}</strong></div>
            <div class="rozet-kutu kirmizi" v-if="kritikStokSayisi > 0">
              ⚠️ Kritik Stok: <strong>{{ kritikStokSayisi }}</strong>
            </div>
            <div class="rozet-kutu yesil" v-else>
              ✅ Tüm Stoklar Yeterli
            </div>
          </div>
        </div>

        <!-- FİLTRELEME ALANI -->
        <div class="filtre-alani">
          <div class="input-grubu select-kutu">
            <select v-model="seciliDurum">
              <option value="HEPSI">Tüm Envanter</option>
              <option value="YETERLI">🟢 Stoğu Yeterli Olanlar</option>
              <option value="KRITIK">🔴 Kritik Seviyede Olanlar</option>
              <option value="TUKENDI">⚫ Stoğu Tükenenler (0)</option>
            </select>
          </div>
          <div class="input-grubu arama">
            <span class="ikon">🔍</span>
            <input v-model="aramaMetni" type="text" placeholder="Ürün adı, marka veya sipariş kodu ara..." />
          </div>
        </div>

        <!-- STOK LİSTESİ TABLOSU -->
        <div class="tablo-sarmalayici">
          <table class="kurumsal-tablo">
            <thead>
              <tr>
                <th>Ürün Kodu</th>
                <th>Marka & Malzeme Adı</th>
                <th class="merkez-hizali">Mevcut Stok</th>
                <th class="merkez-hizali">Kritik Eşik</th>
                <th>Durum</th>
                <th class="sag-hizali">Stok İşlemleri</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="filtrelenmisMalzemeler.length === 0">
                <td colspan="6" class="bos-durum">Aranan kritere uygun malzeme bulunamadı.</td>
              </tr>
              
              <tr 
                v-for="urun in filtrelenmisMalzemeler" 
                :key="urun.id" 
                :class="{'kritik-satir': urun.mevcut_stok <= urun.kritik_esik && urun.mevcut_stok > 0, 'tukenmis-satir': urun.mevcut_stok === 0}"
              >
                <td class="kod">{{ urun.siparis_kodu }}</td>
                <td>
                  <div class="urun-adi">{{ urun.urun_adi }}</div>
                  <div class="urun-marka">{{ urun.marka || 'Markasız' }} - {{ urun.urun_grubu || 'Genel' }}</div>
                </td>
                <td class="merkez-hizali">
                  <span class="stok-miktari">{{ urun.mevcut_stok }}</span>
                </td>
                <td class="merkez-hizali">
                  <span class="esik-miktari">{{ urun.kritik_esik }}</span>
                </td>
                <td>
                  <span :class="['durum-rozeti', stokDurumRengi(urun)]">
                    {{ stokDurumMetni(urun) }}
                  </span>
                </td>
                <td class="islemler">
                  <!-- HIZLI STOK GÜNCELLEME (GİRİŞ/ÇIKIŞ) -->
                  <button @click="stokGuncelle(urun, 'Ekle')" class="btn-islem btn-kucuk btn-yesil" title="Depoya Malzeme Girişi">+</button>
                  <button @click="stokGuncelle(urun, 'Cikar')" class="btn-islem btn-kucuk btn-kirmizi" title="Depodan Malzeme Çıkışı" :disabled="urun.mevcut_stok === 0">-</button>
                  
                  <!-- EĞER STOK KRİTİKSE SATIN ALMA'YA GÖNDERME BUTONU ÇIKAR -->
                  <button 
                    v-if="urun.mevcut_stok <= urun.kritik_esik" 
                    @click="satinAlmaTalebiAc(urun)" 
                    class="btn-islem btn-sari-cizgili"
                  >
                    🛒 Talep Aç
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import UstMenu from '../components/UstMenu.vue';
import { API_BASE } from '../config';

const malzemeler = ref([]);
const aramaMetni = ref('');
const seciliDurum = ref('HEPSI');
const aktifKullanici = ref(localStorage.getItem('kullanici_adi') || 'Sistem');

// İstatistikler
const kritikStokSayisi = computed(() => malzemeler.value.filter(m => m.mevcut_stok <= m.kritik_esik).length);

// Filtreleme Algoritması
const filtrelenmisMalzemeler = computed(() => {
  let sonuc = malzemeler.value;
  
  if (seciliDurum.value === 'YETERLI') {
    sonuc = sonuc.filter(m => m.mevcut_stok > m.kritik_esik);
  } else if (seciliDurum.value === 'KRITIK') {
    sonuc = sonuc.filter(m => m.mevcut_stok <= m.kritik_esik && m.mevcut_stok > 0);
  } else if (seciliDurum.value === 'TUKENDI') {
    sonuc = sonuc.filter(m => m.mevcut_stok === 0);
  }

  if (aramaMetni.value) {
    const arama = aramaMetni.value.toLowerCase();
    sonuc = sonuc.filter(m => 
      m.urun_adi?.toLowerCase().includes(arama) || 
      m.siparis_kodu?.toLowerCase().includes(arama) ||
      m.marka?.toLowerCase().includes(arama)
    );
  }
  return sonuc;
});

onMounted(() => {
  stoklariGetir();
});

const stoklariGetir = async () => {
  try {
    const res = await axios.get(`${API_BASE}/depo/stoklar`);
    malzemeler.value = res.data;
  } catch (error) {
    // Backend yapılana kadar Demo Veri
    if (malzemeler.value.length === 0) {
      malzemeler.value = [
        { id: 1, siparis_kodu: '1SDA067131R1', urun_adi: '3 Fazlı Motor 15kW', marka: 'ABB', urun_grubu: 'Şalt', mevcut_stok: 12, kritik_esik: 5 },
        { id: 2, siparis_kodu: 'S7-1200', urun_adi: 'PLC İşlemci Modülü', marka: 'Siemens', urun_grubu: 'Otomasyon', mevcut_stok: 3, kritik_esik: 5 },
        { id: 3, siparis_kodu: 'RLY-24V', urun_adi: '24V Röle', marka: 'Finder', urun_grubu: 'Şalt', mevcut_stok: 0, kritik_esik: 20 },
        { id: 4, siparis_kodu: 'CBL-3X2.5', urun_adi: '3x2.5 NYAF Kablo (Metre)', marka: 'Hes', urun_grubu: 'Kablo', mevcut_stok: 450, kritik_esik: 100 }
      ];
    }
  }
};

const stokDurumRengi = (urun) => {
  if (urun.mevcut_stok === 0) return 'siyah';
  if (urun.mevcut_stok <= urun.kritik_esik) return 'kirmizi';
  return 'yesil';
};

const stokDurumMetni = (urun) => {
  if (urun.mevcut_stok === 0) return '⚫ Tükendi';
  if (urun.mevcut_stok <= urun.kritik_esik) return '⚠️ Kritik Stok';
  return '🟢 Yeterli';
};

// Hızlı Manuel Stok Güncelleme
const stokGuncelle = async (urun, islemTuru) => {
  const islemAdi = islemTuru === 'Ekle' ? 'Girişi' : 'Çıkışı';
  const miktar = parseInt(prompt(`"${urun.urun_adi}" için stok ${islemAdi} miktarını giriniz:`));
  
  if (isNaN(miktar) || miktar <= 0) return;
  
  if (islemTuru === 'Cikar' && miktar > urun.mevcut_stok) {
    return alert("Mevcut stoktan daha fazla çıkış yapamazsınız!");
  }

  try {
    const yeniStok = islemTuru === 'Ekle' ? urun.mevcut_stok + miktar : urun.mevcut_stok - miktar;
    
    await axios.put(`${API_BASE}/depo/stoklar/${urun.id}`, { mevcut_stok: yeniStok }, {
      headers: { 'islem-yapan': aktifKullanici.value }
    });
    
    urun.mevcut_stok = yeniStok; // Ekranda anında güncelle
  } catch (error) {
    alert("Stok güncellenirken hata oluştu.");
  }
};

// Sistemler Arası Bağlantı: Satın Almaya Gönder!
const satinAlmaTalebiAc = async (urun) => {
  const miktar = prompt(`Satın Alma ekibine "${urun.urun_adi}" için kaç adetlik sipariş talebi geçmek istiyorsunuz?`, urun.kritik_esik * 2);
  if (!miktar || isNaN(miktar) || miktar <= 0) return;

  try {
    await axios.post(`${API_BASE}/satin-alma/talepler`, {
      malzeme_id: urun.id,
      malzeme_adi: urun.urun_adi,
      adet: parseInt(miktar),
      talep_eden: aktifKullanici.value,
      durum: 'BEKLIYOR'
    });
    
    alert(`Başarılı! ${miktar} adet ${urun.urun_adi} için Satın Alma Onay Merkezine talep düşmüştür.`);
  } catch (error) {
    alert("Talep iletilemedi. Satın alma servisi yanıt vermiyor.");
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
.rozet-kutu.kirmizi { background: #fef2f2; border-color: #fecdd3; color: #e11d48; }
.rozet-kutu.yesil { background: #ecfdf5; border-color: #a7f3d0; color: #059669; }
.rozet-kutu strong { font-size: 14px; margin-left: 5px; }

/* Filtre Alanı */
.filtre-alani { display: flex; gap: 15px; background: #f8fafc; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 25px; }
.input-grubu { position: relative; flex: 1; }
.input-grubu.arama { flex: 2; }
.input-grubu .ikon { position: absolute; left: 12px; top: 11px; color: #94a3b8; font-size: 14px; }
.input-grubu input, .input-grubu select { 
  width: 100%; padding: 10px 10px 10px 35px; border: 1px solid #cbd5e1; border-radius: 6px; 
  font-size: 13px; box-sizing: border-box; background-color: #ffffff; outline: none;
}
.input-grubu select { padding-left: 15px; cursor: pointer; }
.input-grubu input:focus, .input-grubu select:focus { border-color: #0f172a; }

/* Tablo Yapısı */
.tablo-sarmalayici { overflow-x: auto; border: 1px solid #e2e8f0; border-radius: 8px; }
.kurumsal-tablo { width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; }
.kurumsal-tablo th { background-color: #f1f5f9; color: #475569; padding: 15px 20px; font-weight: 600; font-size: 12px; text-transform: uppercase; border-bottom: 1px solid #e2e8f0; }
.kurumsal-tablo td { padding: 15px 20px; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }

/* Satır Renklendirmeleri */
.kurumsal-tablo tr:hover td { background-color: #f8fafc; }
.kritik-satir td { background-color: #fff1f2 !important; }
.tukenmis-satir td { background-color: #f1f5f9 !important; opacity: 0.6; }
.tukenmis-satir .urun-adi { text-decoration: line-through; }

.kod { font-family: monospace; color: #64748b; font-weight: 500; }
.urun-adi { font-weight: 600; color: #0f172a; }
.urun-marka { font-size: 11px; color: #64748b; margin-top: 2px; }

.merkez-hizali { text-align: center; }
.stok-miktari { font-size: 15px; font-weight: 700; color: #0f172a; }
.esik-miktari { font-size: 13px; font-weight: 600; color: #94a3b8; }
.kritik-satir .stok-miktari, .tukenmis-satir .stok-miktari { color: #e11d48; }

/* Durum Rozetleri */
.durum-rozeti { padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; display: inline-block; border: 1px solid; }
.durum-rozeti.yesil { background: #ecfdf5; color: #059669; border-color: #a7f3d0; }
.durum-rozeti.kirmizi { background: #fef2f2; color: #e11d48; border-color: #fecdd3; }
.durum-rozeti.siyah { background: #e2e8f0; color: #475569; border-color: #cbd5e1; }

/* Butonlar */
.sag-hizali { text-align: right; }
.islemler { text-align: right; white-space: nowrap; }
.btn-islem { padding: 8px 12px; border: none; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; transition: 0.2s; margin-left: 5px; }
.btn-kucuk { padding: 6px 10px; font-size: 14px; }
.btn-yesil { background: #10b981; color: white; }
.btn-yesil:hover { background: #059669; }
.btn-kirmizi { background: #ef4444; color: white; }
.btn-kirmizi:hover { background: #dc2626; }
.btn-kirmizi:disabled { background: #fca5a5; cursor: not-allowed; }
.btn-sari-cizgili { background: transparent; border: 1px solid #f59e0b; color: #d97706; margin-left: 15px; }
.btn-sari-cizgili:hover { background: #fffbeb; }

.bos-durum { text-align: center; color: #94a3b8; font-style: italic; padding: 40px !important; }

@media (max-width: 768px) { .karti-header { flex-direction: column; align-items: flex-start; gap: 15px; } .filtre-alani { flex-direction: column; } .input-grubu { width: 100%; } }
</style>