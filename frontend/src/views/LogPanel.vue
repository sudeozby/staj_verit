<template>
  <div class="container" style="padding: 20px; background-color: #f0f2f5; min-height: 100vh;">
    
    <UstMenu /> 

    <div style="background: white; padding: 30px; border-radius: 10px; box-shadow: 0 6px 12px rgba(0,0,0,0.08);">
      <h2 style="color: #2c3e50; margin-bottom: 20px;">📋 Tüm Sistem Hareket Kayıtları</h2>
      
      <div style="overflow-x: auto;">
        <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 14px;">
          <thead>
            <tr style="background-color: #2c3e50; color: white;">
              <th style="padding: 15px;">Tarih</th>
              <th style="padding: 15px;">Kullanıcı</th>
              <th style="padding: 15px;">İşlem</th>
              <th style="padding: 15px;">Detay</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in loglar" :key="log.id" style="border-bottom: 1px solid #eee;">
              <td style="padding: 15px;">{{ new Date(log.tarih).toLocaleString() }}</td>
              <td style="padding: 15px;">{{ log.kullanici_adi }}</td>
              <td style="padding: 15px; font-weight: bold;">{{ log.islem_turu }}</td>
              <td style="padding: 15px;">{{ log.detay }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import UstMenu from '../components/UstMenu.vue';

const router = useRouter();
const loglar = ref([]);

const loglariGetir = async () => {
  try {
    const res = await axios.get('http://127.0.0.1:8000/loglar');
    // Veritabanından gelen veriyi ters çevirerek en son işlemin en üstte görünmesini sağla
    loglar.value = res.data.reverse(); 
  } catch (error) {
    console.error("Loglar yüklenemedi:", error);
    alert("Loglar yüklenirken bir sorun oluştu.");
  }
};

onMounted(loglariGetir);

const cikisYap = () => {
  localStorage.removeItem('girisYapildi');
  localStorage.removeItem('kullaniciRolu');
  router.push('/');
};
</script>