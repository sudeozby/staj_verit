<template>
  <div class="login-wrapper">
    <div class="login-kart">
      
      <div class="logo-alani">
        <h1 class="logo-yazisi">TEM<span class="kirmizi">K</span>ON</h1>
        <h2>CPQ Merkezi Giriş Platformu</h2>
      </div>

      <div class="login-form">
        
        <div class="form-grubu">
          <label>Kullanıcı Adı / E-Posta</label>
          <input 
            v-model="kullaniciAdi" 
            type="text" 
            placeholder="Adınızı giriniz..." 
            @keyup.enter="girisKontrol"
          />
        </div>

        <div class="form-grubu">
          <label>Şifre</label>
          <input 
            v-model="sifre" 
            type="password" 
            placeholder="••••••••" 
            @keyup.enter="girisKontrol"
          />
        </div>

        <div class="form-grubu">
          <label>Sistem Yetki Katmanı (Rol)</label>
          <select v-model="seciliRol" class="rol-seçici">
            <option value="yonetici">👑 Yönetici (Tam Erişim / Maliyet Analizi)</option>
            <option value="teklif_ekibi">💼 Teklif Ekibi (Veri Girişi / P1 PDF Çıktısı)</option>
            <option value="saha_ekibi">🔧 Saha & İmalat Ekibi (Sadece Fiyatsız Teknik Liste)</option>
          </select>
        </div>

        <button type="button" @click="girisKontrol" class="btn-giris">
          Sisteme Güvenli Giriş Yap
        </button>
      </div>

      <div v-if="hataMesaji" class="hata-kutusu">
        {{ hataMesaji }}
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const kullaniciAdi = ref('');
const sifre = ref('');
const seciliRol = ref('saha_ekibi'); 
const hataMesaji = ref('');

const girisKontrol = () => {
  // Boşluk Kontrolü
  if (!kullaniciAdi.value.trim() || !sifre.value.trim()) {
    hataMesaji.value = "Lütfen kullanıcı adı ve şifre alanlarını doldurun!";
    return;
  }

  // Yetki ve Kimlik Kaydı
  localStorage.setItem('girisYapildi', 'true');
  localStorage.setItem('kullaniciRolu', seciliRol.value);
  hataMesaji.value = '';

  // Kesin Yönlendirme
  if (seciliRol.value === 'saha_ekibi') {
    window.location.href = '/panolar'; 
  } else {
    window.location.href = '/panel'; 
  }
};
</script>

<style scoped>
.login-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f0f2f5;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  margin: 0;
}

.login-kart {
  background: #ffffff;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  width: 100%;
  max-width: 420px;
  border-top: 6px solid #2c3e50;
  box-sizing: border-box;
}

.logo-alani {
  text-align: center;
  margin-bottom: 30px;
}

.logo-yazisi {
  font-size: 36px;
  font-weight: 900;
  margin: 0;
  letter-spacing: 2px;
  color: #2c3e50;
}

.kirmizi {
  color: #c0392b;
}

.logo-alani h2 {
  font-size: 14px;
  color: #7f8c8d;
  margin-top: 5px;
  font-weight: 400;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-grubu {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-grubu label {
  font-size: 13px;
  font-weight: 600;
  color: #34495e;
}

input, select {
  padding: 12px;
  border: 1px solid #bdc3c7;
  border-radius: 6px;
  font-size: 14px;
  color: #2c3e50;
  width: 100%;
  box-sizing: border-box;
  transition: border-color 0.2s;
}

input:focus, select:focus {
  border-color: #3498db;
  outline: none;
}

.btn-giris {
  background-color: #2c3e50;
  color: white;
  padding: 14px;
  border: none;
  border-radius: 6px;
  font-weight: bold;
  font-size: 15px;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-top: 10px;
  width: 100%;
}

.btn-giris:hover {
  background-color: #1a252f;
}

.hata-kutusu {
  margin-top: 20px;
  padding: 12px;
  background-color: #fdf2f2;
  color: #c0392b;
  border: 1px solid #fadbd8;
  border-radius: 6px;
  text-align: center;
  font-size: 13px;
  font-weight: 600;
}
</style>