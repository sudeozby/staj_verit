<template>
  <div class="sistem-container">
    <div style="width: 100%; max-width: 1200px; margin: 0 auto;">
      <UstMenu />

      <div class="sayfa-karti">
        <div class="karti-header">
          <div class="baslik-alani">
            <h3>🗂️ Katalog ve Ürün Ağacı (BOM) Merkezi</h3>
            <p>Tüm envanterin anlık durumu, stok seviyeleri ve pano reçetelerine göre temin süresi analizleri.</p>
          </div>
        </div>

        <!-- SEKME MENÜSÜ -->
        <div class="sekme-menusu">
          <button :class="{ aktif: aktifSekme === 'malzemeler' }" @click="aktifSekme = 'malzemeler'">📦 Tüm Malzemeler & Stok</button>
          <button :class="{ aktif: aktifSekme === 'panolar' }" @click="aktifSekme = 'panolar'">⚙️ Pano Reçeteleri (BOM)</button>
        </div>

        <!-- 1. SEKME: MALZEME VE STOK LİSTESİ -->
        <div v-if="aktifSekme === 'malzemeler'" class="sekme-icerik">
          <div class="filtre-alani">
            <div class="input-grubu arama">
              <span class="ikon">🔍</span>
              <input v-model="aramaMetni" type="text" placeholder="Ürün adı, marka veya kod ara..." />
            </div>
          </div>

          <div class="tablo-sarmalayici">
            <table class="kurumsal-tablo">
              <thead>
                <tr>
                  <th>Ürün Kodu</th>
                  <th>Malzeme Bilgisi</th>
                  <th class="merkez-hizali">Stok</th>
                  <th class="merkez-hizali">⏳ Temin Süresi</th>
                  <th class="sag-hizali">Fiyat</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="urun in filtrelenmisMalzemeler" :key="urun.id">
                  <td class="kod">{{ urun.siparis_kodu }}</td>
                  <td>
                    <div class="urun-adi">{{ urun.urun_adi }}</div>
                    <div class="urun-marka">{{ urun.marka }} | {{ urun.urun_grubu }}</div>
                  </td>
                  <td class="merkez-hizali">
                    <span :class="['stok-rozeti', urun.mevcut_stok > urun.kritik_esik ? 'stok-var' : 'stok-kritik']">
                      {{ urun.mevcut_stok }} Adet
                    </span>
                  </td>
                  <td class="merkez-hizali">
                    <span class="temin-rozeti">{{ urun.temin_suresi_gun }} Gün</span>
                  </td>
                  <td class="sag-hizali tutar">{{ formatPara(urun.liste_fiyati) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 2. SEKME: PANO REÇETELERİ (BOM) ANALİZİ -->
        <div v-if="aktifSekme === 'panolar'" class="sekme-icerik">
          <div class="pano-grid">
            <div v-for="pano in panoSablonlari" :key="pano.id" class="pano-karti">
              <div class="pano-header">
                <h4>{{ pano.pano_turu }}</h4>
                <!-- SİSTEMİN OTOMATİK HESAPLADIĞI KRİTİK TEMİN SÜRESİ -->
                <div class="kritik-sure">
                  Max Temin: <strong>{{ pano.maks_temin_suresi }} Gün</strong>
                </div>
              </div>
              <table class="recete-tablosu">
                <thead>
                  <tr><th>Malzeme</th><th>Adet</th><th>Temin</th></tr>
                </thead>
                <tbody>
                  <tr v-for="malzeme in pano.malzemeler" :key="malzeme.urun_id">
                    <td>{{ malzeme.urun_adi }}</td>
                    <td class="adet">x{{ malzeme.adet }}</td>
                    <td :class="['temin-gun', malzeme.temin_suresi_gun === pano.maks_temin_suresi ? 'darbogaz' : '']">
                      {{ malzeme.temin_suresi_gun }}g
                    </td>
                  </tr>
                </tbody>
              </table>
              <div class="pano-footer">
                Toplam Maliyet: <strong>{{ formatPara(pano.toplam_maliyet) }}</strong>
              </div>
            </div>
          </div>
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

const aktifSekme = ref('malzemeler');
const aramaMetni = ref('');
const malzemeler = ref([]);
const panoSablonlari = ref([]);

onMounted(async () => {
  // Backend'den hem stokları hem de reçeteleri tek seferde çekiyoruz
  try {
    const [malzemeRes, panoRes] = await Promise.all([
      axios.get(`${API_BASE}/katalog/malzemeler`),
      axios.get(`${API_BASE}/katalog/panolar`)
    ]);
    malzemeler.value = malzemeRes.data;
    panoSablonlari.value = panoRes.data;
  } catch (err) {
    console.error("Katalog yüklenemedi", err);
  }
});

const filtrelenmisMalzemeler = computed(() => {
  return malzemeler.value.filter(m => 
    m.urun_adi.toLowerCase().includes(aramaMetni.value.toLowerCase()) || 
    m.siparis_kodu.toLowerCase().includes(aramaMetni.value.toLowerCase())
  );
});

const formatPara = (deger) => {
  return new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' }).format(deger);
};
</script>

<style scoped>
/* Genel Tasarım */
.sistem-container { min-height: 100vh; background-color: #f8fafc; padding-bottom: 40px; font-family: 'Segoe UI', system-ui, sans-serif; color: #334155; }
.sayfa-karti { background: #ffffff; padding: 35px; border-radius: 12px; border-top: 4px solid #0f172a; box-shadow: 0 4px 15px rgba(0,0,0,0.03); margin-top: 25px; }

/* Sekme Stili */
.sekme-menusu { display: flex; gap: 10px; margin-bottom: 25px; border-bottom: 1px solid #e2e8f0; }
.sekme-menusu button { background: none; border: none; padding: 10px 20px; font-weight: 600; cursor: pointer; color: #64748b; }
.sekme-menusu button.aktif { border-bottom: 2px solid #0f172a; color: #0f172a; }

/* Tablo Stili */
.kurumsal-tablo { width: 100%; border-collapse: collapse; font-size: 13px; }
.kurumsal-tablo th { background: #f1f5f9; padding: 15px; text-align: left; }
.kurumsal-tablo td { padding: 15px; border-bottom: 1px solid #f1f5f9; }
.stok-rozeti { padding: 4px 8px; border-radius: 4px; font-weight: 700; }
.stok-var { background: #ecfdf5; color: #059669; }
.stok-kritik { background: #fef2f2; color: #e11d48; }

/* Pano Grid */
.pano-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
.pano-karti { border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; }
.pano-header { background: #f8fafc; padding: 15px; display: flex; justify-content: space-between; align-items: center; }
.darbogaz { color: #e11d48; font-weight: 700; }
</style>