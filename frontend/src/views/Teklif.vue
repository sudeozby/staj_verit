<template>
  <div class="sistem-container">
    <div style="width: 100%; max-width: 1200px; margin: 0 auto;">
      
      <UstMenu />

      <div class="sayfa-karti">
        <div class="karti-header">
          <div class="baslik-alani">
            <h3>📄 Teklif Hazırlama ve Simülasyon Merkezi</h3>
            <p>Projelerin maliyetlerini analiz edin, iskonto uygulayın ve müşteriye özel resmi PDF teklifi oluşturun.</p>
          </div>
        </div>

        <div class="teklif-grid">
          <!-- SOL PANEL: PROJE LİSTESİ -->
          <div class="panel sol-panel">
            <div class="panel-baslik">
              <span class="ikon">📁</span> Teklif Bekleyen Projeler
            </div>
            <div class="proje-listesi">
              <div 
                v-for="proje in projeler" 
                :key="proje.id" 
                :class="['proje-karti', seciliProje?.id === proje.id ? 'aktif' : '']"
                @click="projeSec(proje)"
              >
                <div class="proje-kodu">#{{ proje.referans_no || proje.id }}</div>
                <div class="proje-adi">{{ proje.proje_adi }}</div>
                <div class="proje-musteri">{{ proje.musteri }}</div>
              </div>
              <div v-if="projeler.length === 0" class="bos-durum">
                Maliyetlendirilecek proje bulunmuyor.
              </div>
            </div>
          </div>

          <!-- SAĞ PANEL: SİMÜLASYON VE HESAPLAMA -->
          <div class="panel sag-panel">
            <div v-if="!seciliProje" class="secim-yapiniz">
              <span class="dev-ikon">👈</span>
              <p>Maliyet analizi ve PDF teklifi hazırlamak için sol taraftan bir proje seçiniz.</p>
            </div>
            
            <div v-else class="simulasyon-alani">
              <div class="simulasyon-header">
                <h4>{{ seciliProje.proje_adi }}</h4>
                <button @click="pdfOlustur" class="btn-islem btn-kirmizi pdf-btn">
                  <span class="ikon">🖨️</span> Resmi PDF Çıktısı Al
                </button>
              </div>

              <!-- Pano ve Malzeme Tablosu -->
              <div class="tablo-sarmalayici">
                <table class="kurumsal-tablo">
                  <thead>
                    <tr>
                      <th>Pano Türü</th>
                      <th>Malzeme (Ürün Kodu)</th>
                      <th>Birim Fiyat</th>
                      <th>Adet</th>
                      <th>İskonto</th>
                      <th class="sag-hizali">Net Toplam</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-if="panoMalzemeleri.length === 0">
                      <td colspan="6" class="bos-durum">Bu projeye henüz malzeme veya pano atanmamış.</td>
                    </tr>
                    <tr v-for="(malzeme, index) in panoMalzemeleri" :key="index">
                      <td class="pano-turu">{{ malzeme.pano_turu }}</td>
                      <td>
                        <div class="urun-adi">{{ malzeme.urun_adi }}</div>
                        <div class="urun-kodu">{{ malzeme.siparis_kodu }}</div>
                      </td>
                      <td>{{ formatPara(malzeme.liste_fiyati) }}</td>
                      <td class="adet-sutun">x{{ malzeme.adet }}</td>
                      <td class="iskonto-sutun">
                        %{{ ((malzeme.iskonto_orani || 0) * 100).toFixed(0) }}
                      </td>
                      <td class="sag-hizali net-tutar">
                        {{ formatPara(hesaplaNetTutar(malzeme)) }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Finansal Özet Tablosu -->
              <div class="finansal-ozet">
                <div class="ozet-satiri">
                  <span>Brüt Malzeme Toplamı:</span>
                  <span>{{ formatPara(ozet.brut_toplam) }}</span>
                </div>
                <div class="ozet-satiri iskonto">
                  <span>Uygulanan Toplam İskonto:</span>
                  <span>- {{ formatPara(ozet.toplam_iskonto) }}</span>
                </div>
                <div class="ozet-satiri">
                  <span>Ara Toplam:</span>
                  <span>{{ formatPara(ozet.ara_toplam) }}</span>
                </div>
                <div class="ozet-satiri kdv">
                  <span>KDV (%20):</span>
                  <span>+ {{ formatPara(ozet.kdv) }}</span>
                </div>
                <div class="ozet-satiri genel-toplam">
                  <span>Genel Toplam:</span>
                  <span>{{ formatPara(ozet.genel_toplam) }}</span>
                </div>
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
import axios from 'axios';
import UstMenu from '../components/UstMenu.vue';
import { API_BASE } from '../config';

const projeler = ref([]);
const seciliProje = ref(null);
const panoMalzemeleri = ref([]);
const ozet = ref({ brut_toplam: 0, toplam_iskonto: 0, ara_toplam: 0, kdv: 0, genel_toplam: 0 });

onMounted(() => {
  projeleriGetir();
});

const projeleriGetir = async () => {
  try {
    const res = await axios.get(`${API_BASE}/projeler/listele`);
    projeler.value = res.data;
  } catch (error) {
    console.error("Projeler yüklenirken hata:", error);
  }
};

const projeSec = async (proje) => {
  seciliProje.value = proje;
  try {
    // Projeye atanmış panoları ve malzemeleri getir
    // (Python tarafında bu endpointi oluşturacağız: /projeler/{id}/malzemeler)
    const res = await axios.get(`${API_BASE}/projeler/${proje.id}/malzemeler`);
    panoMalzemeleri.value = res.data;
    maliyetSimulasyonuYap();
  } catch (error) {
    panoMalzemeleri.value = []; // Endpoint henüz yoksa tabloyu boş göster
    maliyetSimulasyonuYap();
  }
};

const hesaplaNetTutar = (malzeme) => {
  const brut = malzeme.liste_fiyati * malzeme.adet;
  const indirimMiktari = brut * (malzeme.iskonto_orani || 0);
  return brut - indirimMiktari;
};

const maliyetSimulasyonuYap = () => {
  let brut = 0;
  let net = 0;

  panoMalzemeleri.value.forEach(m => {
    brut += m.liste_fiyati * m.adet;
    net += hesaplaNetTutar(m);
  });

  ozet.value.brut_toplam = brut;
  ozet.value.toplam_iskonto = brut - net;
  ozet.value.ara_toplam = net;
  ozet.value.kdv = net * 0.20;
  ozet.value.genel_toplam = net * 1.20;
};

const formatPara = (deger) => {
  if (!deger && deger !== 0) return '₺0.00';
  return new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' }).format(deger);
};

// Teklif Oluştururken Stok Rezervasyonu (Yeni Mantık)
const teklifOlusturVeRezerveEt = async (teklifDetaylari) => {
  try {
    // 1. Stok kontrolü ve Rezervasyon
    const stokKontrol = await axios.post(`${API_BASE}/depo/rezerve-et`, {
      proje_id: teklifDetaylari.proje_id,
      malzemeler: teklifDetaylari.malzemeler
    });

    if (stokKontrol.data.status === 'success') {
      alert("Teklif oluşturuldu ve malzemeler rezerve edildi! Stok kilitlendi.");
    }
  } catch (error) {
    if (error.response.status === 409) {
      alert("HATA: Stok yetersiz! Başka bir teklif tarafından rezerve edilmiş olabilir.");
    }
  }
};

// Teklif İptal Edilirse veya Reddedilirse (İade Mantığı)
const teklifIptalVeStokIade = async (teklifId) => {
  if (!confirm("Teklif iptal edilecek ve rezerve edilen stoklar depoya iade edilecek. Onaylıyor musun?")) return;

  try {
    await axios.post(`${API_BASE}/teklifler/${teklifId}/iptal-et-iade-al`);
    alert("Teklif iptal edildi, malzemeler tekrar depoya eklendi.");
    // Ekranı güncelle...
  } catch (error) {
    alert("İade işlemi sırasında hata oluştu!");
  }
};
const pdfOlustur = () => {
  alert(`"${seciliProje.value.proje_adi}" projesi için resmi teklif PDF dosyası oluşturuluyor...\n(Bu özellik HTML2PDF veya Backend PDF kütüphanesi ile entegre edilecektir.)`);
};
</script>

<style scoped>
/* KURUMSAL SAAS TASARIMI */
.sistem-container { min-height: 100vh; background-color: #f8fafc; padding-bottom: 40px; font-family: 'Segoe UI', system-ui, sans-serif; color: #334155; }
.sayfa-karti { background: #ffffff; padding: 35px; border-radius: 12px; border-top: 4px solid #0f172a; box-shadow: 0 4px 15px rgba(0,0,0,0.03); margin-top: 25px; }
.karti-header { margin-bottom: 25px; border-bottom: 1px solid #e2e8f0; padding-bottom: 15px; }
.baslik-alani h3 { margin: 0; color: #0f172a; font-size: 20px; font-weight: 600; }
.baslik-alani p { margin: 5px 0 0 0; color: #64748b; font-size: 13px; }

.teklif-grid { display: grid; grid-template-columns: 300px 1fr; gap: 25px; align-items: start; }

/* Sol Panel (Projeler) */
.panel { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; }
.panel-baslik { background: #f1f5f9; padding: 15px; font-size: 13px; font-weight: 600; color: #0f172a; border-bottom: 1px solid #e2e8f0; text-transform: uppercase; letter-spacing: 0.5px; }
.proje-listesi { max-height: 600px; overflow-y: auto; }
.proje-karti { padding: 15px; border-bottom: 1px solid #e2e8f0; cursor: pointer; transition: 0.2s; background: #ffffff; }
.proje-karti:hover { background: #f1f5f9; }
.proje-karti.aktif { background: #eff6ff; border-left: 4px solid #2563eb; }
.proje-kodu { font-family: monospace; font-size: 11px; color: #64748b; margin-bottom: 4px; }
.proje-adi { font-size: 13px; font-weight: 600; color: #0f172a; margin-bottom: 4px; }
.proje-musteri { font-size: 11px; color: #94a3b8; }

/* Sağ Panel (Simülasyon) */
.sag-panel { background: #ffffff; min-height: 400px; padding: 25px; }
.secim-yapiniz { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; color: #94a3b8; text-align: center; margin-top: 50px; }
.dev-ikon { font-size: 40px; margin-bottom: 15px; opacity: 0.5; }

.simulasyon-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px dashed #cbd5e1; }
.simulasyon-header h4 { margin: 0; font-size: 18px; color: #0f172a; }
.pdf-btn { display: flex; align-items: center; gap: 8px; }

/* Tablo */
.tablo-sarmalayici { overflow-x: auto; border: 1px solid #e2e8f0; border-radius: 8px; margin-bottom: 25px; }
.kurumsal-tablo { width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; }
.kurumsal-tablo th { background-color: #f1f5f9; color: #475569; padding: 12px 15px; font-weight: 600; font-size: 11px; text-transform: uppercase; border-bottom: 1px solid #e2e8f0; }
.kurumsal-tablo td { padding: 12px 15px; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }
.kurumsal-tablo tr:hover td { background-color: #f8fafc; }

.pano-turu { font-weight: 600; color: #2563eb; font-size: 11px; }
.urun-adi { font-weight: 500; color: #334155; }
.urun-kodu { font-family: monospace; font-size: 11px; color: #94a3b8; }
.adet-sutun { font-weight: 600; color: #0f172a; }
.iskonto-sutun { color: #d97706; font-weight: 600; }
.sag-hizali { text-align: right; }
.net-tutar { font-weight: 700; color: #0f172a; }

/* Finansal Özet */
.finansal-ozet { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; width: 350px; margin-left: auto; }
.ozet-satiri { display: flex; justify-content: space-between; padding: 8px 0; font-size: 13px; color: #475569; border-bottom: 1px dashed #cbd5e1; }
.ozet-satiri:last-child { border-bottom: none; }
.ozet-satiri.iskonto { color: #e11d48; }
.ozet-satiri.kdv { color: #64748b; }
.ozet-satiri.genel-toplam { font-size: 16px; font-weight: 700; color: #0f172a; margin-top: 10px; padding-top: 15px; border-top: 2px solid #cbd5e1; }

.btn-islem { padding: 10px 20px; border: none; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; transition: 0.2s; }
.btn-kirmizi { background-color: #e11d48; color: white; }
.btn-kirmizi:hover { background-color: #be123c; transform: translateY(-1px); box-shadow: 0 4px 10px rgba(225, 29, 72, 0.2); }
.bos-durum { text-align: center; color: #94a3b8; font-style: italic; padding: 30px !important; }

@media (max-width: 900px) { .teklif-grid { grid-template-columns: 1fr; } .finansal-ozet { width: 100%; } }
</style>