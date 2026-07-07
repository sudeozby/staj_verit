<template>
  <div class="ust-menu" style="display: flex; justify-content: space-between; align-items: center; background: white; padding: 15px 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 30px; border-top: 5px solid #2c3e50;">
    
    <div class="logo-alani">
      <h1 style="font-size: 28px; margin: 0; color: #2c3e50; font-weight: 900;">TEM<span style="color: #c0392b;">K</span>ON</h1>
      <h2 style="font-size: 14px; margin: 0; color: #7f8c8d; font-weight: 400;">CPQ Maliyet Yönetim Paneli</h2>
    </div>

    <div class="menu-butonlari" style="display: flex; gap: 15px;">
      
      <button @click="router.push('/panel')" style="background-color: #ecf0f1; color: #2c3e50; padding: 10px 20px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer;">Ana Panel</button>

      <button v-if="rol === 'yonetici' || rol === 'teklif_ekibi'" @click="router.push('/panolar')" style="background-color: #ecf0f1; color: #2c3e50; padding: 10px 20px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer;">Panolar</button>

      <button v-if="rol === 'yonetici'" @click="router.push('/ekip')" style="background-color: #ecf0f1; color: #2c3e50; padding: 10px 20px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer;">👥 Ekip Yönetimi</button>
      
      <button v-if="rol === 'yonetici'" @click="router.push('/loglar')" style="background-color: #34495e; color: white; padding: 10px 20px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer;">📋 Sistem Logları</button>

      <button @click="cikisYap" style="background-color: #c0392b; color: white; padding: 10px 20px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer;">Çıkış Yap</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
// Kullanıcının rolünü localStorage'dan alıyoruz
const rol = ref(localStorage.getItem('kullaniciRolu'));

const cikisYap = () => {
  localStorage.clear();
  router.push('/');
};
</script>