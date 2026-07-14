<template>
  <div class="sistem-container">
    <div style="width: 100%; max-width: 1200px; margin: 0 auto;">
      
      <UstMenu />

      <div class="sayfa-karti">
        <!-- MÜŞTERİ KİMLİK KARTI -->
        <div class="musteri-header">
          <div class="header-bilgi">
            <h3>🏢 {{ musteri.firma_adi }}</h3>
            <p>Yetkili: {{ musteri.yetkili_kisi }} | İletişim: {{ musteri.telefon }}</p>
          </div>
          <button @click="router.back()" class="btn-islem btn-gri">← Geri Dön</button>
        </div>

        <!-- İKİLİ EKRAN: PROJELER VE REVİZYONLAR -->
        <div class="detay-grid">
          
          <!-- SOL: AKTİF PROJELER VE NOTLAR -->
          <div class="panel">
            <div class="panel-header">📋 Aktif Projeler</div>
            <div v-for="proje in musteri.projeler" :key="proje.id" class="proje-karti">
              <div class="proje-ana-bilgi">
                <strong>{{ proje.ad }}</strong>
                <span :class="['durum', proje.durum]">{{ proje.durum }}</span>
              </div>
            </div>
          </div>

          <!-- SAĞ: TÜM REVİZYONLAR VE İSTEKLER GEÇMİŞİ -->
          <div class="panel">
            <div class="panel-header">⚠️ Revizyon ve İstek Tarihçesi</div>
            <div class="revizyon-zaman-tüneli">
              <div v-for="rev in musteri.revizyonlar" :key="rev.id" class="rev-madde">
                <div class="rev-tarih">{{ tarihFormatla(rev.tarih) }}</div>
                <div class="rev-detay">
                  <strong>#WORK-{{ rev.is_emri_id }}</strong> - {{ rev.notu }}
                  <span class="dosya-adi">{{ rev.dosya_adi }}</span>
                </div>
              </div>
              <div v-if="musteri.revizyonlar.length === 0" class="bos-durum">
                Bu cari için herhangi bir revizyon talebi bulunmuyor.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import UstMenu from '../components/UstMenu.vue';
import { API_BASE } from '../config';

const route = useRoute();
const router = useRouter();
const musteri = ref({ projeler: [], revizyonlar: [] });

onMounted(async () => {
  const musteriId = route.params.id; // URL'den ID'yi alıyoruz
  try {
    const res = await axios.get(`${API_BASE}/musteriler/${musteriId}/detay`);
    musteri.value = res.data;
  } catch (err) {
    // DEMO VERİ
    musteri.value = {
      firma_adi: 'Rönesans Holding', yetkili_kisi: 'Hasan Yurt', telefon: '0532 123 4567',
      projeler: [{ id: 1, ad: 'Malatya Şehir Hastanesi', durum: 'Montajda' }],
      revizyonlar: [
        { id: 1, is_emri_id: 103, tarih: '2026-07-14T09:30:00', notu: 'Şalt malzemesi Siemens olacak.', dosya_adi: 'TKLF-103_R01' },
        { id: 2, is_emri_id: 103, tarih: '2026-06-10T11:00:00', notu: 'Kablo kanalları metal yapılacak.', dosya_adi: 'TKLF-103_R02' }
      ]
    };
  }
});

const tarihFormatla = (tarih) => new Date(tarih).toLocaleDateString('tr-TR');
</script>

<style scoped>
.musteri-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; }
.detay-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.panel { border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; }
.panel-header { background: #f1f5f9; padding: 12px; font-weight: 600; font-size: 13px; color: #0f172a; }
.proje-karti { padding: 15px; border-bottom: 1px solid #e2e8f0; }
.revizyon-zaman-tüneli { padding: 15px; }
.rev-madde { padding: 10px 0; border-bottom: 1px dashed #e2e8f0; font-size: 13px; }
.rev-tarih { font-size: 11px; color: #94a3b8; margin-bottom: 4px; }
.dosya-adi { font-family: monospace; color: #2563eb; margin-left: 10px; font-weight: 600; }
.bos-durum { text-align: center; color: #94a3b8; font-style: italic; padding: 20px; }
</style>