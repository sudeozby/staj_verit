<template>
  <div>
    <!-- ŞIK VE İNCE ÜST BAR -->
    <header class="kurumsal-topbar">
      <div class="sol-kisim">
        <button class="hamburger-btn" @click="menuAcik = true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16"></path></svg>
        </button>
        <span class="logo">TEM<span class="kirmizi">K</span>ON <span class="logo-text">ERP Sistemi</span></span>
      </div>
      
      <div class="sag-kisim">
        <span class="kullanici-bilgi">Hoş Geldiniz, <strong style="text-transform: capitalize;">{{ kullaniciRolu.replace('_', ' ') }}</strong></span>
        <button class="btn-cikis" @click="cikisYap">Çıkış</button>
      </div>
    </header>

    <!-- ARKA PLAN KARARTMASI -->
    <transition name="fade">
      <div v-if="menuAcik" class="menu-overlay" @click="menuAcik = false"></div>
    </transition>

    <!-- YANDAN AÇILAN ZARİF MENÜ (DRAWER) -->
    <transition name="slide">
      <aside v-if="menuAcik" class="kurumsal-sidebar">
        <div class="sidebar-header">
          <h3>Modüller</h3>
          <button class="kapat-btn" @click="menuAcik = false">✕</button>
        </div>
        
        <nav class="sidebar-nav">
          <!-- HERKESİN GÖREBİLECEĞİ SAHA/İMALAT KISMI -->
          <div class="menu-ayrac">SAHA OPERASYONLARI</div>
          <router-link to="/imalat" class="nav-link" @click="menuAcik = false">
            <span class="ikon">🏭</span> İmalat Panosu
          </router-link>

          <!-- SADECE YÖNETİCİLERE ÖZEL DEV MENÜ -->
          <template v-if="kullaniciRolu === 'yonetici'">
            <div class="menu-ayrac">GENEL BAKIŞ</div>
            <router-link to="/dashboard" class="nav-link" @click="menuAcik = false">
              <span class="ikon">📊</span> Yönetici Özeti (To-Do)
            </router-link>

            <div class="menu-ayrac">MÜHENDİSLİK & ÜRETİM</div>
            <router-link to="/panolar" class="nav-link" @click="menuAcik = false">
              <span class="ikon">📁</span> Üretim Merkezi
            </router-link>
            <router-link to="/katalog-bom" class="nav-link" @click="menuAcik = false">
              <span class="ikon">📦</span> Malzeme & BOM Kataloğu
            </router-link>
            <router-link to="/revizyon-merkezi" class="nav-link" @click="menuAcik = false">
              <span class="ikon">🔄</span> Revizyon Merkezi
            </router-link>
            <router-link to="/revizyon-karsilastir" class="nav-link" @click="menuAcik = false">
              <span class="ikon">⚖️</span> Revizyon Karşılaştırma
            </router-link>

            <div class="menu-ayrac">TİCARİ & TEDARİK</div>
            <!-- 5 SAYFALIK ASIL PDF ŞABLONU LİNKİ -->
            <router-link to="/analiz-merkezi" class="nav-link" @click="menuAcik = false">
              <span class="ikon">📈</span> Analiz & Resmi Teklif (PDF)
            </router-link>
            
            <router-link to="/teklif-ekrani" class="nav-link" @click="menuAcik = false">
              <span class="ikon">📝</span> Teklif Yönetimi
            </router-link>
            <router-link to="/musteriler" class="nav-link" @click="menuAcik = false">
              <span class="ikon">🤝</span> Müşteri Yönetimi (CRM)
            </router-link>
            <router-link to="/satin-alma" class="nav-link" @click="menuAcik = false">
              <span class="ikon">🛒</span> Satın Alma Onayları
            </router-link>

            <div class="menu-ayrac">SİSTEM AYARLARI</div>
            <router-link to="/ekip-yonetimi" class="nav-link" @click="menuAcik = false">
              <span class="ikon">👥</span> Ekip & Kullanıcı Yönetimi
            </router-link>
            <router-link to="/loglar" class="nav-link" @click="menuAcik = false">
              <span class="ikon">📋</span> Sistem Logları
            </router-link>
          </template>
        </nav>
        
        <div class="sidebar-footer">
          <p>TEMKON Yazılım v1.0.0</p>
        </div>
      </aside>
    </transition>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const kullaniciRolu = ref(localStorage.getItem('kullaniciRolu') || 'standart');
const menuAcik = ref(false);

const cikisYap = () => {
  localStorage.removeItem('girisYapildi');
  localStorage.removeItem('kullaniciRolu');
  router.push('/');
};
</script>

<style scoped>
/* ZARİF VE KURUMSAL TASARIM */
.kurumsal-topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #ffffff;
  height: 50px;
  padding: 0 20px;
  border-bottom: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}
.menu-ayrac { 
  font-size: 10px; 
  font-weight: 700; 
  color: #475569; 
  margin: 15px 10px 5px 10px; 
  letter-spacing: 1px; 
}
.sol-kisim, .sag-kisim { display: flex; align-items: center; gap: 15px; }

.hamburger-btn {
  background: none; border: none; cursor: pointer; color: #475569;
  width: 32px; height: 32px; padding: 4px; border-radius: 4px; transition: 0.2s;
}
.hamburger-btn:hover { background: #f1f5f9; color: #0f172a; }

.logo { font-weight: 800; font-size: 16px; color: #0f172a; letter-spacing: 0.5px; }
.logo .kirmizi { color: #e11d48; }
.logo-text { font-weight: 500; font-size: 12px; color: #64748b; margin-left: 5px; border-left: 1px solid #cbd5e1; padding-left: 8px; }

.kullanici-bilgi { font-size: 12px; color: #475569; }
.btn-cikis {
  background: #fff; border: 1px solid #cbd5e1; color: #475569;
  padding: 4px 10px; font-size: 11px; font-weight: 600; border-radius: 4px; cursor: pointer; transition: 0.2s;
}
.btn-cikis:hover { background: #f8fafc; border-color: #94a3b8; color: #0f172a; }

/* SIDEBAR (YAN MENÜ) - KAYDIRMA ÇUBUĞU EKLENDİ */
.menu-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(15, 23, 42, 0.4); z-index: 998; backdrop-filter: blur(2px); }
.kurumsal-sidebar { 
  position: fixed; top: 0; left: 0; bottom: 0; width: 260px; 
  background: #0f172a; color: #f8fafc; z-index: 999; display: flex; flex-direction: column; 
  box-shadow: 4px 0 15px rgba(0,0,0,0.1); 
}
.sidebar-header { display: flex; justify-content: space-between; align-items: center; padding: 20px; border-bottom: 1px solid #1e293b; }
.sidebar-header h3 { margin: 0; font-size: 14px; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; }
.kapat-btn { background: none; border: none; color: #64748b; font-size: 18px; cursor: pointer; transition: 0.2s; }
.kapat-btn:hover { color: #f8fafc; }

/* NAV KISMINA SCROLL EKLENDİ (Menü uzun olursa taşmasın diye) */
.sidebar-nav { 
  padding: 15px 10px; display: flex; flex-direction: column; gap: 5px; flex: 1; 
  overflow-y: auto; 
}
.sidebar-nav::-webkit-scrollbar { width: 4px; }
.sidebar-nav::-webkit-scrollbar-thumb { background: #475569; border-radius: 4px; }

.nav-link { display: flex; align-items: center; padding: 10px 15px; color: #cbd5e1; text-decoration: none; font-size: 13px; font-weight: 500; border-radius: 6px; transition: 0.2s; }
.nav-link .ikon { margin-right: 12px; font-size: 15px; }
.nav-link:hover, .nav-link.router-link-active { background: #1e293b; color: #ffffff; }

.sidebar-footer { padding: 15px; text-align: center; font-size: 10px; color: #475569; border-top: 1px solid #1e293b; }

/* Animasyonlar */
.slide-enter-active, .slide-leave-active { transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
.slide-enter-from, .slide-leave-to { transform: translateX(-100%); }
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>