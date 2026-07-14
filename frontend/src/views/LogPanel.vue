<template>
  <div class="sistem-container">
    <div style="width: 100%; max-width: 1200px; margin: 0 auto;">
      
      <UstMenu /> 

      <div class="sayfa-karti">
        <div class="karti-header">
          <div class="baslik-alani">
            <h3>📋 Sistem Hareket Kayıtları (Log)</h3>
            <p>Tüm kullanıcı işlemleri, güvenlik olayları ve veri değişikliklerinin detaylı geçmişi.</p>
          </div>
          <div class="istatistik-rozetler">
            <div class="rozet-kutu">Toplam Kayıt: <strong>{{ loglar.length }}</strong></div>
          </div>
        </div>

        <!-- AKILLI ARAMA ALANI -->
        <div class="filtre-alani">
          <div class="input-grubu arama">
            <span class="ikon">🔍</span>
            <input 
              v-model="aramaMetni" 
              type="text" 
              placeholder="İşlem detayı, kullanıcı adı veya olay türü ara..." 
            />
          </div>
        </div>
        
        <!-- LOG TABLOSU -->
        <div class="tablo-sarmalayici">
          <table class="kurumsal-tablo">
            <thead>
              <tr>
                <th>Tarih & Saat</th>
                <th>Kullanıcı (Aktör)</th>
                <th>İşlem Türü</th>
                <th class="genis-sutun">İşlem Detayı</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="filtrelenmisLoglar.length === 0">
                <td colspan="4" class="bos-durum">
                  <span v-if="loglar.length === 0">Henüz kaydedilmiş bir sistem hareketi bulunmuyor...</span>
                  <span v-else>Arama kriterlerinize uygun kayıt bulunamadı.</span>
                </td>
              </tr>
              
              <tr v-for="log in filtrelenmisLoglar" :key="log.id">
                <td class="tarih-sutunu">
                  <span class="ikon">🕒</span> {{ logTarihiFormatla(log.tarih) }}
                </td>
                <td class="kullanici-adi">
                  {{ log.kullanici_adi }}
                </td>
                <td>
                  <span :class="['islem-rozeti', islemRengiBelirle(log.islem_turu)]">
                    {{ log.islem_turu }}
                  </span>
                </td>
                <td class="detay-sutunu">
                  {{ log.detay }}
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
import { useRouter } from 'vue-router';
import axios from 'axios';
import UstMenu from '../components/UstMenu.vue';

const router = useRouter();
const loglar = ref([]);
const aramaMetni = ref('');

onMounted(() => {
  // Yönetici veya yetkili değilse girişe geri gönder
  if (!localStorage.getItem('girisYapildi')) {
    router.push('/');
    return;
  }
  loglariGetir();
});

const loglariGetir = async () => {
  try {
    const res = await axios.get("http://127.0.0.1:8000/api/loglar");
    loglar.value = res.data; 
  } catch (error) {
    console.error("Loglar yüklenemedi:", error);
  }
};

// --- YENİ EKLENEN VİTRİN ZEKALARI (Frontend Logic) ---

// 1. Akıllı Arama Filtresi
const filtrelenmisLoglar = computed(() => {
  if (!aramaMetni.value) return loglar.value;
  
  const arama = aramaMetni.value.toLowerCase();
  return loglar.value.filter(log => 
    (log.kullanici_adi && log.kullanici_adi.toLowerCase().includes(arama)) ||
    (log.islem_turu && log.islem_turu.toLowerCase().includes(arama)) ||
    (log.detay && log.detay.toLowerCase().includes(arama))
  );
});

// 2. Tarihi Daha Şık Gösterme Formatı
const logTarihiFormatla = (tarihString) => {
  if (!tarihString) return '-';
  const secenekler = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute:'2-digit', second:'2-digit' };
  return new Date(tarihString).toLocaleString('tr-TR', secenekler);
};

// 3. İşlem Türüne Göre Akıllı Rozet Rengi
const islemRengiBelirle = (islem) => {
  if (!islem) return 'gri';
  const kelime = islem.toLowerCase();
  
  if (kelime.includes('ekle') || kelime.includes('onay') || kelime.includes('başarılı') || kelime.includes('giriş')) return 'yesil';
  if (kelime.includes('sil') || kelime.includes('kapat') || kelime.includes('red') || kelime.includes('hata')) return 'kirmizi';
  if (kelime.includes('güncelle') || kelime.includes('değiştir') || kelime.includes('düzenle')) return 'mavi';
  
  return 'gri'; // Varsayılan renk
};
</script>

<style scoped>
/* KURUMSAL TASARIM (SaaS Mimarisi) */
.sistem-container { min-height: 100vh; background-color: #f8fafc; padding-bottom: 40px; font-family: 'Segoe UI', system-ui, sans-serif; color: #334155; }

.sayfa-karti { background: #ffffff; padding: 35px; border-radius: 12px; border-top: 4px solid #0f172a; box-shadow: 0 4px 15px rgba(0,0,0,0.03); margin-top: 25px; }

.karti-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 25px; border-bottom: 1px solid #e2e8f0; padding-bottom: 15px; }
.baslik-alani h3 { margin: 0; color: #0f172a; font-size: 20px; font-weight: 600; }
.baslik-alani p { margin: 5px 0 0 0; color: #64748b; font-size: 13px; }

.istatistik-rozetler { display: flex; gap: 10px; }
.rozet-kutu { background: #f8fafc; border: 1px solid #e2e8f0; color: #475569; padding: 6px 12px; border-radius: 6px; font-size: 12px; }
.rozet-kutu strong { font-size: 14px; margin-left: 5px; color: #0f172a; }

/* Arama Alanı */
.filtre-alani { display: flex; background: #f8fafc; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 25px; }
.input-grubu.arama { position: relative; width: 100%; }
.input-grubu .ikon { position: absolute; left: 12px; top: 11px; color: #94a3b8; font-size: 14px; }
.input-grubu input { 
  width: 100%; padding: 10px 10px 10px 35px; border: 1px solid #cbd5e1; border-radius: 6px; 
  font-size: 13px; box-sizing: border-box; background-color: #ffffff; outline: none; transition: 0.2s;
}
.input-grubu input:focus { border-color: #0f172a; box-shadow: 0 0 0 2px rgba(15, 23, 42, 0.1); }

/* Tablo Yapısı */
.tablo-sarmalayici { overflow-x: auto; border: 1px solid #e2e8f0; border-radius: 8px; }
.kurumsal-tablo { width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; }
.kurumsal-tablo th { background-color: #f1f5f9; color: #475569; padding: 15px 20px; font-weight: 600; font-size: 12px; text-transform: uppercase; border-bottom: 1px solid #e2e8f0; }
.kurumsal-tablo td { padding: 15px 20px; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }
.kurumsal-tablo tr:last-child td { border-bottom: none; }
.kurumsal-tablo tr:hover td { background-color: #f8fafc; }

.genis-sutun { width: 45%; } /* Detayların sığması için */

.tarih-sutunu { color: #64748b; font-size: 12px; white-space: nowrap; }
.tarih-sutunu .ikon { font-size: 10px; margin-right: 4px; color: #94a3b8; }
.kullanici-adi { font-weight: 600; color: #0f172a; }
.detay-sutunu { color: #475569; line-height: 1.4; }

/* İşlem Rozetleri (Otomatik Renklenen) */
.islem-rozeti { padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; display: inline-block; white-space: nowrap; border: 1px solid; }
.islem-rozeti.yesil { background: #ecfdf5; color: #059669; border-color: #a7f3d0; }
.islem-rozeti.kirmizi { background: #fef2f2; color: #e11d48; border-color: #fecdd3; }
.islem-rozeti.mavi { background: #eff6ff; color: #2563eb; border-color: #bfdbfe; }
.islem-rozeti.gri { background: #f1f5f9; color: #475569; border-color: #cbd5e1; }

.bos-durum { text-align: center; color: #94a3b8; font-style: italic; padding: 40px !important; }

@media (max-width: 768px) {
  .karti-header { flex-direction: column; align-items: flex-start; gap: 15px; }
}
</style>