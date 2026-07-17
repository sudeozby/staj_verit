<template>
  <div class="kurumsal-dashboard">
    <UstMenu />

    <main class="icerik-alani">
      <div class="karsilama-header">
        <div>
          <h2>İş İstasyonu (To-Do)</h2>
          <p class="tarih">{{ bugunTarih }}</p>
        </div>
      </div>

      <div class="dashboard-grid">
        <!-- SOL KOLON: BEKLEYEN İŞLER (TO-DO) -->
        <div class="sol-kolon-wrapper">
          
          <!-- 1. PANEL: SATIN ALMA ONAYLARI -->
          <div class="panel sol-panel">
            <div class="panel-header">
              <h3>📌 Yönetici Onayı Bekleyen Satın Almalar</h3>
              <span class="rozete">{{ talepler.length }} Kayıt</span>
            </div>
            
            <div class="tablo-wrapper">
              <table class="zarif-tablo">
                <thead>
                  <tr>
                    <th>Talep Kodu</th>
                    <th>Malzeme</th>
                    <th>Adet</th>
                    <th class="islem-sutun">İşlem</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="talep in talepler" :key="'talep-'+talep.id">
                    <td class="kod">#REQ-{{ talep.id }}</td>
                    <td>{{ talep.malzeme_adi || talep.malzeme_kodu }}</td>
                    <td class="kalin">{{ talep.adet || talep.talep_edilen_adet }}</td>
                    <td class="islem-sutun">
                      <button class="btn-ince btn-onay" @click="durumGuncelle(talep.id, 'ONAYLANDI')">Onayla</button>
                      <button class="btn-ince btn-red" @click="durumGuncelle(talep.id, 'REDDEDILDI')">Reddet</button>
                    </td>
                  </tr>
                  <tr v-if="talepler.length === 0">
                    <td colspan="4" class="bos-mesaj">Şu an onayınızı bekleyen satın alma işlemi bulunmamaktadır.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- 2. PANEL: YENİ EKLENEN REVİZYON ONAYLARI -->
          <div class="panel sol-panel">
            <div class="panel-header">
              <h3>⚠️ Onay Bekleyen Saha Revizyonları</h3>
              <span class="rozete rozet-sari">{{ bekleyenRevizyonlar.length }} Kayıt</span>
            </div>
            
            <div class="tablo-wrapper">
              <table class="zarif-tablo">
                <thead>
                  <tr>
                    <th>İş Emri / Proje</th>
                    <th>Dosya Adı</th>
                    <th>Revizyon Notu</th>
                    <th class="islem-sutun">İşlem</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="rev in bekleyenRevizyonlar" :key="'rev-'+rev.id">
                    <td>
                      <div class="kod">#WORK-{{ rev.is_emri_id }}</div>
                      <div class="proje-kucuk">{{ rev.proje_adi }}</div>
                    </td>
                    <td><span class="dosya-kodu">📄 {{ rev.dosya_adi }}</span></td>
                    <td class="not-sutunu" :title="rev.revizyon_notu">
                      {{ rev.revizyon_notu.length > 40 ? rev.revizyon_notu.substring(0, 40) + '...' : rev.revizyon_notu }}
                    </td>
                    <td class="islem-sutun">
                      <button class="btn-ince btn-onay" @click="revizyonOnayla(rev.id)">Onayla</button>
                      <button class="btn-ince btn-red" @click="revizyonReddet(rev.id)">Reddet</button>
                    </td>
                  </tr>
                  <tr v-if="bekleyenRevizyonlar.length === 0">
                    <td colspan="4" class="bos-mesaj">Şu an onayınızı bekleyen saha revizyonu bulunmamaktadır.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

        </div>

        <!-- SAĞ PANEL: SİSTEM ÖZETİ VE LOGLAR -->
        <div class="sag-kolon">
          <div class="panel ozel-ozet">
            <div class="panel-header">
              <h3>Genel Durum</h3>
            </div>
            <div class="ozet-liste">
              <div class="ozet-satir">
                <span class="etiket">Kayıtlı Projeler</span>
                <span class="deger">{{ ozet.aktif_projeler }}</span>
              </div>
              <div class="ozet-satir">
                <span class="etiket">Aktif Personel</span>
                <span class="deger">{{ ozet.aktif_personel }}</span>
              </div>
            </div>
          </div>

          <div class="panel">
            <div class="panel-header">
              <h3>⚡ Son Hareketler</h3>
            </div>
            <ul class="mini-log">
              <li v-for="(log, index) in ozet.son_hareketler" :key="index">
                <div class="log-nokta"></div>
                <div class="log-icerik">
                  <span class="log-kisi">{{ log.kullanici_adi }}</span>
                  <span class="log-yazi">{{ log.detay }}</span>
                  <span class="log-saat">{{ log.saat }}</span>
                </div>
              </li>
              <li v-if="!ozet.son_hareketler.length" class="bos-mesaj">Hareket yok.</li>
            </ul>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { API_BASE } from '../config';
import UstMenu from '../components/UstMenu.vue';

const bugunTarih = new Date().toLocaleDateString('tr-TR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });

const ozet = ref({ aktif_projeler: 0, aktif_personel: 0, son_hareketler: [] });
const talepler = ref([]);
const bekleyenRevizyonlar = ref([]); // YENİ: Revizyonları tutacak dizi

const verileriGetir = async () => {
  try {
    const rol = localStorage.getItem('kullaniciRolu') || 'standart';
    
    // 1. Özet ve Logları getir
    const ozetRes = await axios.get(`${API_BASE}/dashboard/ozet`, { headers: { 'current-user-role': rol } });
    ozet.value = ozetRes.data;

    // 2. Bekleyen Satın Alma (To-Do) taleplerini getir
    const talepRes = await axios.get(`${API_BASE}/satin-alma/talepler`, { headers: { 'current-user-role': rol } });
    talepler.value = talepRes.data.filter(t => t.durum === 'BEKLIYOR');

    // 3. YENİ: Bekleyen Revizyon Taleplerini getir
    const revRes = await axios.get(`${API_BASE}/revizyonlar`, { headers: { 'current-user-role': rol } });
    bekleyenRevizyonlar.value = revRes.data.filter(r => r.durum === 'ONAY_BEKLIYOR');
    
  } catch (error) {
    console.error("Veriler çekilirken hata:", error);
  }
};

// --- SATIN ALMA İŞLEMLERİ ---
const durumGuncelle = async (id, yeniDurum) => {
  try {
    const rol = localStorage.getItem('kullaniciRolu') || 'standart';
    const aktifKullanici = localStorage.getItem("kullanici_adi") || "Sistem";
    await axios.put(`${API_BASE}/satin-alma/talepler/${id}/durum`, { durum: yeniDurum }, {
      headers: { 'current-user-role': rol, 'islem-yapan': aktifKullanici }
    });
    verileriGetir(); 
  } catch (error) {
    alert("İşlem başarısız oldu.");
  }
};

// --- REVİZYON İŞLEMLERİ ---
const revizyonOnayla = async (revizyonId) => {
  if(!confirm("Bu revizyonu onaylayıp sahaya yeni talimatı iletmek istediğinize emin misiniz?")) return;
  try {
    const aktifKullanici = localStorage.getItem("kullanici_adi") || "Sistem";
    await axios.put(`${API_BASE}/revizyonlar/${revizyonId}/onayla`, {}, {
      headers: { 'islem-yapan': aktifKullanici }
    });
    verileriGetir();
  } catch (error) {
    alert("Revizyon onayı başarısız.");
  }
};

const revizyonReddet = async (revizyonId) => {
  try {
    const aktifKullanici = localStorage.getItem("kullanici_adi") || "Sistem";
    await axios.put(`${API_BASE}/revizyonlar/${revizyonId}/reddet`, {}, {
      headers: { 'islem-yapan': aktifKullanici }
    });
    verileriGetir();
  } catch (error) {
    alert("Revizyon reddi başarısız.");
  }
};

onMounted(() => { verileriGetir(); });
</script>

<style scoped>
/* KURUMSAL VE ZARİF TASARIM SİSTEMİ */
.kurumsal-dashboard { background-color: #f8fafc; min-height: 100vh; font-family: 'Segoe UI', system-ui, sans-serif; color: #334155; }
.icerik-alani { padding: 30px; max-width: 1200px; margin: 0 auto; }

.karsilama-header { margin-bottom: 25px; border-bottom: 1px solid #e2e8f0; padding-bottom: 15px; }
.karsilama-header h2 { margin: 0; font-size: 20px; font-weight: 600; color: #0f172a; }
.tarih { margin: 4px 0 0 0; font-size: 13px; color: #64748b; }

.dashboard-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; align-items: start; }
.sol-kolon-wrapper { display: flex; flex-direction: column; gap: 20px; } /* İki tablo arası boşluk */

/* Paneller */
.panel { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); overflow: hidden; }
.panel-header { background: #f8fafc; padding: 12px 20px; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; }
.panel-header h3 { margin: 0; font-size: 13px; font-weight: 600; color: #475569; text-transform: uppercase; letter-spacing: 0.5px; }

.rozete { background: #e11d48; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: bold; }
.rozet-sari { background: #d97706; } /* Revizyonlar için sarı rozet */

/* Zarif Tablo */
.tablo-wrapper { padding: 0; }
.zarif-tablo { width: 100%; border-collapse: collapse; font-size: 13px; }
.zarif-tablo th { text-align: left; padding: 10px 20px; color: #64748b; font-weight: 500; border-bottom: 1px solid #e2e8f0; }
.zarif-tablo td { padding: 12px 20px; border-bottom: 1px solid #f1f5f9; color: #334155; vertical-align: middle; }
.zarif-tablo tr:last-child td { border-bottom: none; }
.zarif-tablo tr:hover td { background-color: #f8fafc; }

.kod { font-family: monospace; color: #64748b; font-weight: 600;}
.kalin { font-weight: 600; }
.proje-kucuk { font-size: 11px; color: #94a3b8; margin-top: 2px; }
.dosya-kodu { background: #eff6ff; color: #2563eb; padding: 3px 6px; border-radius: 4px; font-family: monospace; font-size: 11px; font-weight: 700; border: 1px solid #bfdbfe; }
.not-sutunu { font-style: italic; color: #64748b; font-size: 12px; }
.islem-sutun { text-align: right; white-space: nowrap; }

/* İnce ve Kibar Butonlar */
.btn-ince { padding: 4px 10px; font-size: 11px; font-weight: 600; border-radius: 4px; border: 1px solid; cursor: pointer; transition: 0.2s; margin-left: 5px; }
.btn-onay { background: #fff; border-color: #10b981; color: #10b981; }
.btn-onay:hover { background: #10b981; color: #fff; }
.btn-red { background: #fff; border-color: #ef4444; color: #ef4444; }
.btn-red:hover { background: #ef4444; color: #fff; }

.sag-kolon { display: flex; flex-direction: column; gap: 20px; }

/* Özet Liste */
.ozet-liste { padding: 15px 20px; }
.ozet-satir { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px dashed #e2e8f0; }
.ozet-satir:last-child { border-bottom: none; }
.ozet-satir .etiket { color: #64748b; font-size: 13px; }
.ozet-satir .deger { font-weight: 600; color: #0f172a; font-size: 14px; }

/* Mini Log */
.mini-log { list-style: none; padding: 15px 20px; margin: 0; }
.mini-log li { display: flex; gap: 10px; margin-bottom: 12px; position: relative; }
.mini-log li:last-child { margin-bottom: 0; }
.log-nokta { width: 8px; height: 8px; background: #cbd5e1; border-radius: 50%; margin-top: 4px; }
.log-icerik { display: flex; flex-direction: column; }
.log-kisi { font-size: 11px; font-weight: 600; color: #475569; }
.log-yazi { font-size: 12px; color: #334155; margin-top: 2px; }
.log-saat { font-size: 10px; color: #94a3b8; margin-top: 2px; }

.bos-mesaj { text-align: center; color: #94a3b8; font-size: 13px; font-style: italic; padding: 30px !important; }

@media (max-width: 900px) { .dashboard-grid { grid-template-columns: 1fr; } }
</style>