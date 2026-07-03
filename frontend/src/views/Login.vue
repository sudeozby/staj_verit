<template>
  <div class="login-container">
    <div class="login-box">
      <div class="logo-alani">
        <h1 class="logo-yazisi">TEM<span class="kirmizi">K</span>ON</h1>
        <p class="alt-baslik">Sistem Girişi</p>
      </div>

      <div class="form-grubu">
        <div class="input-kutusu">
          <label>Kullanıcı Adı</label>
          <input v-model="kullaniciAdi" type="text" placeholder="Kullanıcı adınızı girin" />
        </div>
        
        <div class="input-kutusu">
          <label>Şifre</label>
          <input v-model="sifre" type="password" placeholder="Şifrenizi girin" />
        </div>

        <button @click="girisYap" class="btn-giris">Giriş Yap</button>
        
        <div v-if="hataMesaji" class="hata-mesaji">{{ hataMesaji }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const kullaniciAdi = ref('')
const sifre = ref('')
const hataMesaji = ref('')

const girisYap = () => {
  // Şimdilik basit bir kontrol yapıyoruz, backend'e bağlamadan önce
  if (kullaniciAdi.value === 'admin' && sifre.value === '1234') {
    // Şifre doğruysa yönlendirici bizi Panele atacak
    router.push('/panel')
  } else {
    hataMesaji.value = 'Kullanıcı adı veya şifre hatalı!'
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #2c3e50; /* Kurumsal Lacivert Arka Plan */
}

.login-box {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.2);
  width: 100%;
  max-width: 400px;
  border-top: 6px solid #c0392b; /* Kırmızı Vurgu */
}

.logo-alani {
  text-align: center;
  margin-bottom: 30px;
}

.logo-yazisi {
  font-size: 42px;
  font-weight: 900;
  margin: 0;
  color: #2c3e50;
  letter-spacing: 2px;
}

.kirmizi {
  color: #c0392b;
}

.alt-baslik {
  color: #7f8c8d;
  margin-top: 5px;
  font-weight: 500;
}

.form-grubu {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-kutusu label {
  display: block;
  font-weight: bold;
  color: #34495e;
  margin-bottom: 8px;
  font-size: 14px;
}

input {
  width: 100%;
  padding: 12px;
  border: 1px solid #bdc3c7;
  border-radius: 6px;
  box-sizing: border-box;
  font-size: 15px;
  transition: border-color 0.2s;
}

input:focus {
  border-color: #3498db;
  outline: none;
}

.btn-giris {
  background-color: #c0392b;
  color: white;
  padding: 14px;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-top: 10px;
}

.btn-giris:hover {
  background-color: #a53125;
}

.hata-mesaji {
  color: #c0392b;
  text-align: center;
  font-weight: bold;
  font-size: 14px;
}
</style>