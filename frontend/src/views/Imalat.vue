<template>
  <div class="sistem-container">
    <div style="width: 100%; max-width: 1200px; margin: 0 auto;">
      
      <UstMenu />

      <div class="sayfa-karti">
        <div class="karti-header">
          <div class="baslik-alani">
            <h3>👷‍♂️ Saha ve İmalat Operasyonları</h3>
            <p>Size atanan onaylı pano montaj işlerini takip edin ve güncelleyin.</p>
          </div>
          <div class="istatistik-rozetler">
            <div class="rozet-kutu">Bekleyen: <strong>{{ bekleyenIsSayisi }}</strong></div>
            <div class="rozet-kutu montajda">Montajda: <strong>{{ montajdakiSayisi }}</strong></div>
          </div>
        </div>

        <!-- Filtreleme Alanı -->
        <div class="filtre-alani">
          <div class="input-grubu select-kutu">
            <select v-model="seciliDurum">
              <option value="HEPSI">Tüm İş Emirleri</option>
              <option value="MONTAJ_BEKLIYOR">⏳ Montaj Bekleyenler</option>
              <option value="MONTAJDA">🔧 Montajı Devam Edenler</option>
              <option value="MERKEZ_REVIZYON">⚠️ Merkezde Revizyonda Olanlar</option>
              <option value="TAMAMLANDI">✅ Tamamlananlar</option>
            </select>
          </div>
          <div class="input-grubu arama">
            <span class="ikon">🔍</span>
            <input v-model="aramaMetni" type="text" placeholder="Proje kodu veya pano türü ara..." />
          </div>
        </div>

        <!-- İŞ EMİRLERİ TABLOSU -->
        <div class="tablo-sarmalayici">
          <table class="kurumsal-tablo">
            <thead>
              <tr>
                <th>İş Emri Kodu</th>
                <th>Proje & Müşteri</th>
                <th>Pano Türü</th>
                <th>Reçete</th>
                <th>Güncel Durum</th>
                <th class="sag-hizali">İşlem</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="filtrelenmisIsler.length === 0">
                <td colspan="6" class="bos-durum">Şu an size atanmış bir iş emri bulunmuyor.</td>
              </tr>
              
              <tr v-for="isEmri in filtrelenmisIsler" :key="isEmri.id" :class="{'kilitli-satir': isEmri.durum === 'MERKEZ_REVIZYON'}">
                <td class="kod">#WORK-{{ isEmri.id }}</td>
                <td>
                  <div class="proje-adi">{{ isEmri.proje_adi }}</div>
                  <div class="proje-musteri">{{ isEmri.musteri }}</div>
                </td>
                <td>
                  <span class="pano-rozeti">{{ isEmri.pano_turu }}</span>
                </td>
                <td class="malzeme-ozet">
                  <span class="malzeme-sayisi">{{ isEmri.malzeme_sayisi }} Kalem</span>
                  <button @click="malzemeDetayGoster(isEmri)" class="btn-link">Listeyi Gör</button>
                </td>
                <td>
                  <span :class="['durum-rozeti', isEmri.durum.toLowerCase()]">
                    {{ durumMetniGetir(isEmri.durum) }}
                  </span>
                </td>
                <td class="islemler">
                  <!-- EĞER MERKEZDE REVİZYONDAYSA SAHA EKİBİ HİÇBİR ŞEY YAPAMAZ -->
                  <div v-if="isEmri.durum === 'MERKEZ_REVIZYON'" class="kilitli-uyari">
                    🔒 Ofis Onayı Bekleniyor
                  </div>
                  
                  <!-- EĞER İŞ TAMAMLANDIYSA SADECE İZLER -->
                  <div v-else-if="isEmri.durum === 'TAMAMLANDI'" class="kilitli-uyari yetki-yok">
                    İşlem Kapatıldı
                  </div>

                  <!-- SAHA EKİBİ SADECE İŞE BAŞLAYABİLİR VEYA BİTİREBİLİR -->
                  <select 
                    v-else
                    class="hizli-islem-select" 
                    @change="durumDegistir(isEmri, $event.target.value)" 
                    :value="isEmri.durum"
                  >
                    <option value="MONTAJ_BEKLIYOR" disabled>⏳ Montaj Bekliyor</option>
                    <option value="MONTAJDA">🔧 Montaja Başla</option>
                    <option value="TAMAMLANDI">✅ İşlemi Tamamla</option>
                  </select>
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

const isEmirleri = ref([]);
const aramaMetni = ref('');
const seciliDurum = ref('HEPSI');

// Computed Özellikler
const bekleyenIsSayisi = computed(() => isEmirleri.value.filter(i => i.durum === 'MONTAJ_BEKLIYOR').length);
const montajdakiSayisi = computed(() => isEmirleri.value.filter(i => i.durum === 'MONTAJDA').length);

const filtrelenmisIsler = computed(() => {
  let sonuc = isEmirleri.value;
  if (seciliDurum.value !== 'HEPSI') sonuc = sonuc.filter(i => i.durum === seciliDurum.value);
  if (aramaMetni.value) {
    const arama = aramaMetni.value.toLowerCase();
    sonuc = sonuc.filter(i => 
      i.proje_adi?.toLowerCase().includes(arama) || 
      i.pano_turu?.toLowerCase().includes(arama)
    );
  }
  return sonuc;
});

onMounted(() => {
  isEmirleriniGetir();
});

const isEmirleriniGetir = async () => {
  try {
    const res = await axios.get(`${API_BASE}/imalat/is-emirleri`);
    isEmirleri.value = res.data;
  } catch (error) {
    console.error("İş emirleri yüklenemedi:", error);
    isEmirleri.value = []; // Demo veri yerine sadece boş dizi bırakıyoruz
  }
};

const durumMetniGetir = (durum) => {
  const durumlar = {
    'MONTAJ_BEKLIYOR': '⏳ Bekliyor',
    'MONTAJDA': '🔧 Montajda',
    'MERKEZ_REVIZYON': '⚠️ Merkezde Revizyonda',
    'TAMAMLANDI': '✅ Tamamlandı'
  };
  return durumlar[durum] || durum;
};

// Saha Ekibi Sadece Başla/Bitir Yapabilir
const durumDegistir = async (isEmri, yeniDurum) => {
  try {
    const aktifKullanici = localStorage.getItem("kullanici_adi") || "Sistem";
    await axios.put(`${API_BASE}/imalat/is-emirleri/${isEmri.id}/durum`, {
      durum: yeniDurum
    }, {
      headers: { 'islem-yapan': aktifKullanici }
    });
    
    const index = isEmirleri.value.findIndex(i => i.id === isEmri.id);
    if(index !== -1) {
      isEmirleri.value[index].durum = yeniDurum;
    }
    
  } catch (error) {
    alert("Durum güncellenemedi.");
  }
};

const malzemeDetayGoster = (isEmri) => {
  alert(`Burası tıklandığında #${isEmri.id} nolu işin malzeme reçetesi açılacaktır.`);
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
.rozet-kutu.montajda { background: #eff6ff; border-color: #bfdbfe; color: #1d4ed8; }
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

/* Merkezde Revizyonda Olan Satır (Kilitli) */
.kilitli-satir td { background-color: #fffbeb !important; opacity: 0.8; }
.kilitli-uyari { font-size: 11px; font-weight: 600; color: #d97706; }
.yetki-yok { color: #94a3b8; }

.kod { font-family: monospace; color: #64748b; font-weight: 500; }
.proje-adi { font-weight: 600; color: #0f172a; }
.proje-musteri { font-size: 11px; color: #64748b; margin-top: 2px; }
.pano-rozeti { background: #f1f5f9; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; border: 1px solid #cbd5e1; }

.malzeme-ozet { display: flex; flex-direction: column; align-items: flex-start; }
.malzeme-sayisi { font-weight: 600; color: #334155; font-size: 12px; }
.btn-link { background: none; border: none; color: #2563eb; font-size: 11px; font-weight: 600; cursor: pointer; padding: 0; margin-top: 4px; text-decoration: underline; }

/* Durum Rozetleri */
.durum-rozeti { padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; display: inline-block; border: 1px solid; }
.durum-rozeti.montaj_bekliyor { background: #f8fafc; color: #475569; border-color: #cbd5e1; }
.durum-rozeti.montajda { background: #eff6ff; color: #2563eb; border-color: #bfdbfe; }
.durum-rozeti.merkez_revizyon { background: #fffbeb; color: #d97706; border-color: #fcd34d; }
.durum-rozeti.tamamlandi { background: #ecfdf5; color: #059669; border-color: #a7f3d0; }

/* İşlem Select */
.sag-hizali { text-align: right; }
.islemler { text-align: right; }
.hizli-islem-select { padding: 8px 12px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 12px; font-weight: 600; color: #0f172a; cursor: pointer; outline: none; background: #fff; }
.hizli-islem-select:focus { border-color: #0f172a; }

.bos-durum { text-align: center; color: #94a3b8; font-style: italic; padding: 40px !important; }

@media (max-width: 768px) { .karti-header { flex-direction: column; align-items: flex-start; gap: 15px; } .filtre-alani { flex-direction: column; } .input-grubu { width: 100%; } }
</style>