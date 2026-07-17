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
              <!-- Gerçek veritabanından gelen dosya isimleri -->
              <span>{{ rev.dosya_adi }} ({{ rev.pano_turu || 'Pano' }})</span>
            </label>
            <div v-if="tumRevizyonlar.length === 0" style="color: #64748b; font-size: 13px; font-style: italic;">
              Sistemde henüz hiç revizyon kaydı bulunmuyor.
            </div>
          </div>
          <button @click="karsilastir" class="btn-islem btn-koyu" :disabled="tumRevizyonlar.length === 0">
            Matrisi Oluştur
          </button>
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
import { ref, onMounted } from 'vue';
import axios from 'axios';
import UstMenu from '../components/UstMenu.vue';
import { API_BASE } from '../config';

const secilenRevizyonlar = ref([]);
const matrisVeri = ref([]);

// YENİ: Başlangıçta boş, veritabanından dolacak!
const tumRevizyonlar = ref([]); 

onMounted(() => {
  revizyonlariGetir();
});

// YENİ: Gerçek veritabanına bağlanıp senin oluşturduğun revizyonları çeken fonksiyon
const revizyonlariGetir = async () => {
  try {
    const res = await axios.get(`${API_BASE}/revizyonlar`);
    // Sadece senin oluşturduğun ve veritabanında olan verileri listeye atar
    tumRevizyonlar.value = res.data;
  } catch (error) {
    console.error("Revizyonlar yüklenemedi:", error);
  }
};

const karsilastir = () => {
  if (secilenRevizyonlar.value.length < 2) {
    alert("Lütfen en az 2 revizyon seçin.");
    return;
  }

  // Not: Buradaki rawData şu an hala test amaçlı sabit bir veridir. 
  // Gerçek bir karşılaştırma için arka planda (FastAPI) revizyon_detay tablosu gibi bir yapı kurulup 
  // her revizyonun içindeki malzemelerin axios ile çekilmesi gerekir.
  const rawData = [
    { ozellik: 'Motor Gücü', degerler: ['15kW', '22kW', '22kW'] }, 
    { ozellik: 'Kablo Kanalı', degerler: ['Plastik', 'Metal', 'Metal'] },
    { ozellik: 'Teslim Süresi', degerler: ['30 Gün', '30 Gün', '25 Gün'] }
  ];

  matrisVeri.value = rawData.map(item => ({
    ...item,
    is_different: new Set(item.degerler).size > 1
  }));
};
</script>

<style scoped>
.sistem-container { min-height: 100vh; background-color: #f8fafc; padding-bottom: 40px; font-family: 'Segoe UI', system-ui, sans-serif; color: #334155; }
.sayfa-karti { background: #ffffff; padding: 35px; border-radius: 12px; border-top: 4px solid #0f172a; box-shadow: 0 4px 15px rgba(0,0,0,0.03); margin-top: 25px; }
.karti-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 25px; border-bottom: 1px solid #e2e8f0; padding-bottom: 15px; }
.baslik-alani h3 { margin: 0; color: #0f172a; font-size: 20px; font-weight: 600; }
.baslik-alani p { margin: 5px 0 0 0; color: #64748b; font-size: 13px; }

.kontrol-paneli-multi { background: #f8fafc; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 25px; }
.revizyon-secim-listesi { display: flex; gap: 20px; margin-bottom: 15px; flex-wrap: wrap; }
.secim-checkbox { display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 600; color: #475569; cursor: pointer; }
.secim-checkbox input { cursor: pointer; }

.tablo-sarmalayici { overflow-x: auto; border: 1px solid #e2e8f0; border-radius: 8px; }
.kurumsal-tablo { width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; }
.kurumsal-tablo th { background-color: #f1f5f9; color: #475569; padding: 15px 20px; font-weight: 600; font-size: 12px; text-transform: uppercase; border-bottom: 1px solid #e2e8f0; }
.kurumsal-tablo td { padding: 15px 20px; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }

.matris-tablo td.degisti { background-color: #fff1f2; color: #e11d48; font-weight: 700; }
.btn-islem { padding: 10px 20px; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; border: none; transition: 0.2s; }
.btn-koyu { background: #0f172a; color: white; }
.btn-koyu:hover { background: #1e293b; }
.btn-koyu:disabled { background: #cbd5e1; cursor: not-allowed; }

.bos-durum { text-align: center; color: #94a3b8; font-style: italic; padding: 40px !important; }
</style>