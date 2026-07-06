import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import Panolar from '../views/Panolar.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'Login', component: Login },
    { path: '/panel', name: 'Dashboard', component: Dashboard },
    { path: '/panolar', name: 'Panolar', component: Panolar }
  ]
})

// MODERN GÜVENLİK KİLİDİ (Hanging/Kilitlenme Yapmayan Versiyon)
router.beforeEach((to) => {
  const isLogged = localStorage.getItem('girisYapildi') === 'evet'
  const rol = localStorage.getItem('kullaniciRolu')

  // Kural 1: Giriş yapılmamışsa kapı dışarı
  if (!isLogged && to.path !== '/') {
    return '/' 
  }

  // Kural 2: Giriş yapılmışsa ve tekrar Login'e dönülmeye çalışılıyorsa panele at
  if (isLogged && to.path === '/') {
    return '/panel' 
  }

  // Kural 3: ROL BAZLI GÜVENLİK - Standart personel Panolar'a girmeye çalışırsa Ana Panel'e geri fırlat
  if (to.path === '/panolar' && rol === 'standart') {
    alert('Bu sayfayı görüntüleme yetkiniz bulunmamaktadır!')
    return '/panel'
  }

  return true
})

export default router