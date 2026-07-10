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
            <tr v-if="loglar.length === 0">
              <td colspan="4" style="text-align: center; padding: 20px; color: #7f8c8d;">Henüz kaydedilmiş bir sistem hareketi yok...</td>
            </tr>
            <tr v-for="log in loglar" :key="log.id" style="border-bottom: 1px solid #eee;">
              <td style="padding: 15px;">{{ new Date(log.tarih).toLocaleString() }}</td>
              <td style="padding: 15px;">{{ log.kullanici_adi }}</td>
              <td style="padding: 15px; font-weight: bold; color: #2980b9;">{{ log.islem_turu }}</td>
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

onMounted(() => {
  if (!localStorage.getItem('girisYapildi')) {
    router.push('/');
    return;
  }
  loglariGetir();
});

const loglariGetir = async () => {
  try {
    // Adres, önceki kapı uyuşmazlığını yaşamamak için doğrudan tam adres olarak yazıldı
    const res = await axios.get("http://127.0.0.1:8000/api/loglar");
    
    // Reverse işlemi kaldırıldı çünkü backend zaten DESC (ters) sıralı gönderiyor
    loglar.value = res.data; 
  } catch (error) {
    console.error("Loglar yüklenemedi:", error);
    alert("Loglar yüklenirken bir sorun oluştu.");
  }
};

const cikisYap = () => {
  localStorage.removeItem('girisYapildi');
  localStorage.removeItem('kullaniciRolu');
  router.push('/');
};
</script>