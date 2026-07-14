<template>
  <div class="sistem-container">
    <div style="width: 100%; max-width: 1200px; margin: 0 auto;">
      
      <UstMenu /> 

      <div class="sayfa-karti">
        <div class="karti-header">
          <div class="baslik-alani">
            <h3>Tedarik ve Satın Alma Onay Merkezi</h3>
            <p>Sahadan ve sistemden gelen malzeme taleplerini yönetin, sipariş fişlerini oluşturun.</p>
          </div>
          <div class="istatistik-rozetler">
            <div class="rozet-kutu">Bekleyen: <strong>{{ bekleyenSayisi }}</strong></div>
            <div class="rozet-kutu onayli">Onaylanan: <strong>{{ onayliSayisi }}</strong></div>
          </div>
        </div>
        
        <!-- FİLTRELEME ALANI -->
        <div class="filtre-alani">
          <div class="input-grubu arama">
            <span class="ikon">🔍</span>
            <input 
              v-model="aramaMetni" 
              type="text" 
              placeholder="Malzeme ara (Örn: Raspberry Pi Global Shutter Camera, TF02-Pro LiDAR...)" 
            />
          </div>
          <div class="input-grubu select-kutu">
            <select v-model="seciliDurum">
              <option value="HEPSI">Tüm Talepler</option>
              <option value="BEKLIYOR">⏳ Onay Bekleyenler</option>
              <option value="ONAYLANDI">✅ Onaylanıp Siparişi Geçilenler</option>
              <option value="REDDEDILDI">❌ Reddedilenler</option>
            </select>
          </div>
          <button @click="talepleriGetir" class="btn-islem btn-koyu">Filtrele</button>
        </div>

        <!-- TEDARİK LİSTESİ TABLOSU -->
        <div class="tablo-sarmalayici">
          <table class="kurumsal-tablo">
            <thead>
              <tr>
                <th>Talep ID</th>
                <th>Tarih</th>
                <th>Talep Eden / Proje</th>
                <th>Malzeme / Parça Tanımı</th>
                <th>Miktar</th>
                <th>Durum</th>
                <th class="sag-hizali">Karar İşlemleri</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="filtrelenmisTalepler.length === 0">
                <td colspan="7" class="bos-durum">
                  Seçilen kriterlere uygun satın alma talebi bulunamadı.
                </td>
              </tr>
              
              <tr v-for="talep in filtrelenmisTalepler" :key="talep.id" :class="{ 'reddedilmis': talep.durum === 'REDDEDILDI' }">
                <td class="kod">#REQ-{{ talep.id }}</td>
                <td class="tarih-sutunu">{{ talep.tarih || 'Bugün' }}</td>
                <td>
                  <div class="talep-eden">{{ talep.talep_eden }}</div>
                  <div class="proje-adi">{{ talep.proje_adi || 'Genel Stok' }}</div>
                </td>
                <td class="malzeme-adi">{{ talep.malzeme_adi }}</td>
                <td class="miktar">{{ talep.adet }} {{ talep.birim || 'Adet' }}</td>
                <td>
                  <span :class="['durum-rozeti', talep.durum.toLowerCase()]">
                    {{ talep.durum === 'BEKLIYOR' ? '⏳ Bekliyor' : (talep.durum === 'ONAYLANDI' ? '✅ Onaylandı' : '🔴 Reddedildi') }}
                  </span>
                </td>
                <td class="islemler">
                  <!-- Bekleyenler İçin Onay/Ret Butonları -->
                  <template v-if="talep.durum === 'BEKLIYOR'">
                    <button @click="durumGuncelle(talep.id, 'ONAYLANDI')" class="btn-islem btn-yesil">Onayla</button>
                    <button @click="durumGuncelle(talep.id, 'REDDEDILDI')" class="btn-islem btn-kirmizi">Reddet</button>
                  </template>
                  
                  <!-- Onaylananlar İçin Satın Alma Fişi Butonu -->
                  <template v-else-if="talep.durum === 'ONAYLANDI'">
                    <button @click="siparisFisiCikar(talep)" class="btn-islem btn-sari">📄 Sipariş Fişi (PDF)</button>
                  </template>
                  
                  <span v-else class="pasif-mesaj">İşlem Kapalı</span>
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

const talepler = ref([]);
const seciliDurum = ref('BEKLIYOR');
const aramaMetni = ref('');

// Computed Özellikler (İstatistikler için)
const bekleyenSayisi = computed(() => talepler.value.filter(t => t.durum === 'BEKLIYOR').length);
const onayliSayisi = computed(() => talepler.value.filter(t => t.durum === 'ONAYLANDI').length);

const filtrelenmisTalepler = computed(() => {
  let sonuc = talepler.value;
  
  if (seciliDurum.value !== 'HEPSI') {
    sonuc = sonuc.filter(t => t.durum === seciliDurum.value);
  }
  
  if (aramaMetni.value.trim() !== '') {
    const arama = aramaMetni.value.toLowerCase();
    sonuc = sonuc.filter(t => 
      (t.malzeme_adi && t.malzeme_adi.toLowerCase().includes(arama)) ||
      (t.proje_adi && t.proje_adi.toLowerCase().includes(arama))
    );
  }
  
  return sonuc;
});

const talepleriGetir = async () => {
  try {
    const rol = localStorage.getItem('kullaniciRolu') || 'standart';
    const response = await axios.get(`${API_BASE}/satin-alma/talepler`, {
      headers: { 'current-user-role': rol }
    });
    talepler.value = response.data;
  } catch (error) {
    console.error("Satın alma talepleri çekilemedi:", error);
  }
};

const durumGuncelle = async (talepId, yeniDurum) => {
  try {
    const rol = localStorage.getItem('kullaniciRolu') || 'standart';
    const aktifKullanici = localStorage.getItem("kullanici_adi") || "Sistem";
    
    await axios.put(`${API_BASE}/satin-alma/talepler/${talepId}/durum`, {
      durum: yeniDurum
    }, {
      headers: { 'current-user-role': rol, 'islem-yapan': aktifKullanici }
    });
    
    // İşlem başarılıysa verileri tazele
    await talepleriGetir();
  } catch (error) {
    alert("Talep durumu güncellenirken hata oluştu.");
  }
};

const siparisFisiCikar = (talep) => {
  // Burada tıpkı teklif ekranında yaptığın gibi HTML2PDF motoru tetiklenebilir
  alert(`Sipariş No: #REQ-${talep.id}\n${talep.malzeme_adi} için Proforma/Sipariş fişi hazırlanıyor...`);
};

onMounted(() => {
  talepleriGetir();
});
</script>

<style scoped>
/* KURUMSAL TASARIM (SaaS Mimarisi) */
.sistem-container { min-height: 100vh; background-color: #f8fafc; padding-bottom: 40px; font-family: 'Segoe UI', system-ui, sans-serif; color: #334155; }

.sayfa-karti { background: #ffffff; padding: 35px; border-radius: 12px; border-top: 4px solid #0f172a; box-shadow: 0 4px 15px rgba(0,0,0,0.03); margin-top: 25px; }

.karti-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 25px; border-bottom: 1px solid #e2e8f0; padding-bottom: 15px; }
.baslik-alani h3 { margin: 0; color: #0f172a; font-size: 20px; font-weight: 600; }
.baslik-alani p { margin: 5px 0 0 0; color: #64748b; font-size: 13px; }

.istatistik-rozetler { display: flex; gap: 10px; }
.rozet-kutu { background: #fef2f2; border: 1px solid #fecdd3; color: #e11d48; padding: 6px 12px; border-radius: 6px; font-size: 12px; }
.rozet-kutu.onayli { background: #ecfdf5; border-color: #a7f3d0; color: #059669; }
.rozet-kutu strong { font-size: 14px; margin-left: 5px; }

/* Filtre Alanı */
.filtre-alani { display: flex; gap: 15px; background: #f8fafc; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 25px; align-items: center; }
.input-grubu { position: relative; flex: 1; }
.input-grubu.arama { flex: 2; }
.input-grubu .ikon { position: absolute; left: 12px; top: 10px; color: #94a3b8; font-size: 14px; }
.input-grubu input, .input-grubu select { 
  width: 100%; padding: 10px 10px 10px 35px; border: 1px solid #cbd5e1; border-radius: 6px; 
  font-size: 13px; box-sizing: border-box; background-color: #ffffff; outline: none;
}
.input-grubu select { padding-left: 10px; cursor: pointer; }
.input-grubu input:focus, .input-grubu select:focus { border-color: #0f172a; }

/* Tablo Yapısı */
.tablo-sarmalayici { overflow-x: auto; border: 1px solid #e2e8f0; border-radius: 8px; }
.kurumsal-tablo { width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; }
.kurumsal-tablo th { background-color: #f1f5f9; color: #475569; padding: 15px 20px; font-weight: 600; font-size: 12px; text-transform: uppercase; border-bottom: 1px solid #e2e8f0; }
.kurumsal-tablo td { padding: 15px 20px; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }
.kurumsal-tablo tr:last-child td { border-bottom: none; }
.kurumsal-tablo tr:hover td { background-color: #f8fafc; }

.reddedilmis td { background-color: #fcfcfc; opacity: 0.6; }
.reddedilmis:hover td { opacity: 0.8; }

.kod { font-family: monospace; color: #64748b; font-weight: 500; }
.tarih-sutunu { color: #94a3b8; font-size: 12px; }
.talep-eden { font-weight: 600; color: #0f172a; }
.proje-adi { font-size: 11px; color: #64748b; margin-top: 2px; }
.malzeme-adi { font-weight: 500; color: #334155; }
.miktar { font-weight: 700; color: #0f172a; }

/* Durum Rozetleri */
.durum-rozeti { padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; display: inline-block; border: 1px solid; }
.durum-rozeti.bekliyor { background: #fffbeb; color: #d97706; border-color: #fde68a; }
.durum-rozeti.onaylandi { background: #ecfdf5; color: #059669; border-color: #a7f3d0; }
.durum-rozeti.reddedildi { background: #fef2f2; color: #e11d48; border-color: #fecdd3; }

/* İşlem Butonları */
.sag-hizali { text-align: right; }
.islemler { text-align: right; white-space: nowrap; }
.btn-islem { padding: 6px 12px; border: 1px solid; border-radius: 4px; cursor: pointer; font-size: 11px; font-weight: 600; transition: 0.2s; margin-left: 8px; }
.btn-yesil { background: #fff; border-color: #10b981; color: #10b981; }
.btn-yesil:hover { background: #10b981; color: #fff; }
.btn-kirmizi { background: #fff; border-color: #ef4444; color: #ef4444; }
.btn-kirmizi:hover { background: #ef4444; color: #fff; }
.btn-sari { background: #fff; border-color: #f59e0b; color: #d97706; }
.btn-sari:hover { background: #f59e0b; color: #fff; }
.btn-koyu { background: #0f172a; border-color: #0f172a; color: #fff; padding: 10px 20px; font-size: 12px; }
.btn-koyu:hover { background: #1e293b; }

.pasif-mesaj { font-size: 11px; color: #94a3b8; font-style: italic; }
.bos-durum { text-align: center; color: #94a3b8; font-style: italic; padding: 40px !important; }

@media (max-width: 900px) {
  .karti-header { flex-direction: column; align-items: flex-start; gap: 15px; }
  .filtre-alani { flex-direction: column; }
  .input-grubu { width: 100%; }
}
</style>