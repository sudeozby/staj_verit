<template>
  <div class="sistem-container">
    <div style="width: 100%; max-width: 1400px; margin: 0 auto;">
      
      <UstMenu />

      <div class="sayfa-karti">
        <div class="karti-header">
          <div class="baslik-alani">
            <h3>⚖️ Çoklu Revizyon Karşılaştırma Matrisi</h3>
            <p>İstediğin kadar revizyonu seç, değişimleri tek bir matris üzerinde analiz et.</p>
          </div>
        </div>

        <!-- ÇOKLU SEÇİM PANELİ -->
        <div class="kontrol-paneli-multi">
          <div class="revizyon-secim-listesi">
            <label v-for="rev in tumRevizyonlar" :key="rev.id" class="secim-checkbox">
              <input type="checkbox" :value="rev" v-model="secilenRevizyonlar">
              <span>{{ rev.dosya_adi }}</span>
            </label>
          </div>
          <button @click="karsilastir" class="btn-islem btn-koyu">Matrisi Oluştur</button>
        </div>

        <!-- DİNAMİK KARŞILAŞTIRMA MATRİSİ -->
        <div v-if="matrisVeri.length > 0" class="tablo-sarmalayici">
          <table class="kurumsal-tablo matris-tablo">
            <thead>
              <tr>
                <th>Özellik / Malzeme</th>
                <th v-for="rev in secilenRevizyonlar" :key="rev.id">{{ rev.dosya_adi }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="satir in matrisVeri" :key="satir.ozellik">
                <td><strong>{{ satir.ozellik }}</strong></td>
                <td v-for="(val, idx) in satir.degerler" :key="idx" 
                    :class="{'degisti': satir.is_different}">
                  {{ val }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="bos-durum">
          Karşılaştırmak için en az iki revizyon seçin ve Matrisi Oluştur'a tıklayın.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import UstMenu from '../components/UstMenu.vue';

const secilenRevizyonlar = ref([]);
const matrisVeri = ref([]);

// Backend'den gelecek tüm revizyonlar
const tumRevizyonlar = ref([
  { id: 1, dosya_adi: 'TKLF-103_R01', tarih: '2026-07-14' },
  { id: 2, dosya_adi: 'TKLF-103_R02', tarih: '2026-07-15' },
  { id: 3, dosya_adi: 'TKLF-103_R03', tarih: '2026-07-16' }
]);

const karsilastir = () => {
  if (secilenRevizyonlar.value.length < 2) {
    alert("Lütfen en az 2 revizyon seçin.");
    return;
  }

  // Burada backend'den gelen karşılaştırma verisi işlenir
  // Her bir özellik için seçilen revizyonlardaki değerleri dizeceğiz
  const rawData = [
    { ozellik: 'Motor Gücü', degerler: ['15kW', '22kW', '22kW'] }, // Örnek: R02 ve R03'te 22kW olmuş
    { ozellik: 'Kablo Kanalı', degerler: ['Plastik', 'Metal', 'Metal'] },
    { ozellik: 'Teslim Süresi', degerler: ['30 Gün', '30 Gün', '25 Gün'] }
  ];

  matrisVeri.value = rawData.map(item => ({
    ...item,
    // Eğer dizideki tüm değerler birbirine eşit değilse, bu satır değişmiş demektir
    is_different: new Set(item.degerler).size > 1
  }));
};
</script>

<style scoped>
.kontrol-paneli-multi { background: #f8fafc; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 25px; }
.revizyon-secim-listesi { display: flex; gap: 20px; margin-bottom: 15px; flex-wrap: wrap; }
.secim-checkbox { display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 600; color: #475569; cursor: pointer; }
.matris-tablo td.degisti { background-color: #fff1f2; color: #e11d48; font-weight: 700; }
.btn-koyu { background: #0f172a; color: white; padding: 10px 20px; border-radius: 6px; border: none; cursor: pointer; }
</style>