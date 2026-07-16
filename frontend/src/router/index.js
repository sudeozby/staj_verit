import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'Login', component: () => import('../views/Login.vue') },
    
    // YÖNETİM VE ÜRETİM
    { path: '/panolar', name: 'UretimMerkezi', component: () => import('../views/UretimMerkezi.vue') }, 
    { path: '/ekip-yonetimi', name: 'EkipYonetimi', component: () => import('../views/EkipYonetimi.vue') },
    { path: '/loglar', name: 'LogPaneli', component: () => import('../views/LogPanel.vue') },
    
    // SATIN ALMA VE DEPO
    { path: '/satin-alma', name: 'SatinAlma', component: () => import('../views/SatinAlma.vue') },
    { path: '/katalog-bom', name: 'KatalogBOM', component: () => import('../views/MalzemeKatalog.vue') },
    
    // TEKLİF VE REVİZYON
    { path: '/teklif-ekrani', name: 'TeklifEkrani', component: () => import('../views/Teklif.vue') },
    { path: '/revizyon-merkezi', name: 'RevizyonMerkezi', component: () => import('../views/RevizyonMerkezi.vue') },
    { path: '/revizyon-karsilastir', name: 'RevizyonKarsilastir', component: () => import('../views/RevizyonCompare.vue') },
    
    
    // ÖZET EKRANI (ANA SAYFA)
    { path: '/dashboard', name: 'Dashboard', component: () => import('../views/Ozet.vue') },
    
    // İMALAT VE CRM
    { path: '/imalat', name: 'Imalat', component: () => import('../views/Imalat.vue') },
    { path: '/musteriler', name: 'Musteriler', component: () => import('../views/Musteriler.vue') },
    { path: '/musteri/:id', name: 'MusteriDetay', component: () => import('../views/MusteriDetay.vue') }
  ]
})

// 4 KATMANLI GÜVENLİK KİLİDİ
router.beforeEach((to) => {
  const isLogged = localStorage.getItem('girisYapildi') === 'true'
  const rol = localStorage.getItem('kullaniciRolu')

  // KURAL 1: Girişsiz giriş yasak
  if (!isLogged && to.path !== '/') return '/'

  // KURAL 2: Girişli tekrar login yasak
  if (isLogged && to.path === '/') {
    return rol === 'saha_ekibi' ? '/imalat' : '/dashboard'
  }

  // KURAL 3: SAHA EKİBİ KORUMA (Yönetim panellerine giremez)
  const yonetimSayfalari = ['/dashboard', '/panolar', '/ekip-yonetimi', '/satin-alma', '/revizyon-merkezi', '/loglar']
  if (rol === 'saha_ekibi' && yonetimSayfalari.includes(to.path)) {
    alert('Erişim Reddedildi: Burası imalat yetkililerine kapalıdır!')
    return '/imalat'
  }

  // KURAL 4: SATIN ALMA YETKİ KONTROLÜ
  if (to.path === '/satin-alma' && rol !== 'yonetici') {
    alert('Erişim Reddedildi: Satın alma sadece yöneticilere özeldir!')
    return rol === 'saha_ekibi' ? '/imalat' : '/dashboard'
  }

  return true
})

export default router