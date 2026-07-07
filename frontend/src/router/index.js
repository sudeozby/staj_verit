import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import Panolar from '../views/Panolar.vue'
import EkipYonetimi from '../views/EkipYonetimi.vue' // Klasör yolun farklıysa ona göre ayarla

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'Login', component: Login },
    { path: '/panel', name: 'Dashboard', component: Dashboard },
    { path: '/panolar', name: 'Panolar', component: Panolar },
  {path: '/ekip',name: 'EkipYonetimi',component: EkipYonetimi},
  {path: '/loglar',name: 'LogPaneli',component: () => import('../views/LogPanel.vue')}
  ]
})

// YENİ 3 KATMANLI GÜVENLİK KİLİDİ (Yönetici, Teklif, Saha)
router.beforeEach((to) => {
  // Login dosyamızdaki 'true' kaydıyla eşleştirdik
  const isLogged = localStorage.getItem('girisYapildi') === 'true'
  const rol = localStorage.getItem('kullaniciRolu')

  // KURAL 1: Giriş yapılmamışsa nereye tıklarsa tıklasın Login'e (/) gönder
  if (!isLogged && to.path !== '/') {
    return '/' 
  }

  // KURAL 2: Giriş yapılmışken tekrar Login sayfasına dönülmeye çalışılıyorsa
  if (isLogged && to.path === '/') {
    // Saha ekibi ise onu doğrudan sadece kendi paneline (Panolar) at
    if (rol === 'saha_ekibi') {
      return '/panolar'
    }
    // Yönetici veya Teklif Ekibi ise onları Ana Panel'e at
    return '/panel' 
  }

  // KURAL 3: SAHA EKİBİ KORUMA DUVARI
  // Saha/İmalat ekibi url'ye elle /panel yazıp girmeye çalışırsa engelle
  if (to.path === '/panel' && rol === 'saha_ekibi') {
    alert('Erişim Reddedildi: Saha/İmalat ekibinin Ana Panel (Maliyet) ekranına erişim yetkisi yoktur!')
    return '/panolar'
  }

  return true
})

export default router