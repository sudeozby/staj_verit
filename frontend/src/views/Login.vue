<template>
  <div class="login-wrapper">
    <div class="login-card">
      <!-- Logo ve Başlık Alanı -->
      <div class="logo-alani">
        <h1 class="temkon-logo">TEM<span class="kirmizi">K</span>ON</h1>
        <div class="ayrac"></div>
        <p class="logo-text">Kurumsal ERP & Üretim Yönetim Sistemi</p>
      </div>

      <!-- Giriş Formu -->
      <form @submit.prevent="girisYap" class="login-form">
        <div class="input-grup">
          <label>Kullanıcı Adı</label>
          <div class="input-kutu">
            <span class="ikon">👤</span>
            <input 
              v-model="kullanici.kullanici_adi" 
              type="text" 
              placeholder="Sistem kullanıcı adınız" 
              required 
            />
          </div>
        </div>

        <div class="input-grup">
          <label>Şifre</label>
          <div class="input-kutu">
            <span class="ikon">🔒</span>
            <input 
              v-model="kullanici.sifre" 
              type="password" 
              placeholder="Şifreniz" 
              required 
            />
          </div>
        </div>

        <div class="ek-ayarlar">
          <label class="hatirla">
            <input type="checkbox" /> Beni Hatırla
          </label>
          <!-- Şifremi Unuttum Butonu -->
          <a href="#" @click.prevent="sifremiUnuttum" class="sifre-unuttum">Şifremi Unuttum?</a>
        </div>

        <button type="submit" class="btn-giris" :disabled="yukleniyor">
          {{ yukleniyor ? 'Sisteme Bağlanılıyor...' : 'Giriş Yap' }}
        </button>
      </form>

      <!-- Alt Bilgi -->
      <div class="login-footer">
        <p>Giriş yaparak sistem <a href="#">Güvenlik Politikası</a>'nı kabul etmiş sayılırsınız.</p>
        <p class="versiyon">v1.0.0 © 2026 TEMKON Yazılım</p>
      </div>
    </div>

    <!-- Sistem Bildirimleri (Hata veya Uyarılar) -->
    <transition name="slide-up">
      <div v-if="mesaj" :class="['bildirim', hataVar ? 'hata' : 'bilgi']">
        {{ mesaj }}
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { API_BASE } from '../config';

const router = useRouter();

const kullanici = ref({
  kullanici_adi: '',
  sifre: ''
});

const yukleniyor = ref(false);
const mesaj = ref('');
const hataVar = ref(false);

const bildirimGoster = (metin, hata = false) => {
  mesaj.value = metin;
  hataVar.value = hata;
  setTimeout(() => { mesaj.value = ''; hataVar.value = false; }, 5000);
};

// YÖNETİCİNİN BAHSETTİĞİ O GÜVENLİK KURALI BURADA
const sifremiUnuttum = () => {
  bildirimGoster("Güvenlik prosedürleri gereği şifreniz otomatik sıfırlanamaz. Lütfen Sistem Yöneticinizle iletişime geçin.", true);
};

const girisYap = async () => {
  yukleniyor.value = true;
  try {
    // Backend'e giriş isteği atıyoruz
    const response = await axios.post(`${API_BASE}/ekip/login`, kullanici.value);
    
    // API'den dönen verileri alıyoruz
    const rol = response.data.rol || 'saha_ekibi';
    const ad = response.data.kullanici_adi || kullanici.value.kullanici_adi;

    // Sisteme (Tarayıcı Hafızasına) kaydediyoruz
    localStorage.setItem('girisYapildi', 'true');
    localStorage.setItem('kullaniciRolu', rol);
    localStorage.setItem('kullanici_adi', ad);

    // 🔥 İŞTE O AKILLI YÖNLENDİRME (ROUTING) 🔥
  if (rol === 'yonetici') {
  router.push('/dashboard'); // Yöneticiyi olması gerektiği gibi Ana Ekrana (Özet'e) gönder!
} else {
  router.push('/panolar'); 
}
    
  } catch (error) {
    bildirimGoster(error.response?.data?.detail || "Giriş başarısız. Kullanıcı adı veya şifre hatalı.", true);
  } finally {
    yukleniyor.value = false;
  }
};
</script>

<style scoped>
/* KURUMSAL LOGİN TASARIMI */
.login-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f1f5f9; /* Zarif gri/mavi arka plan */
  font-family: 'Segoe UI', system-ui, sans-serif;
  padding: 20px;
}

.login-card {
  background: #ffffff;
  width: 100%;
  max-width: 420px;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(15, 23, 42, 0.08);
  border-top: 4px solid #0f172a; /* Kurumsal Lacivert Çizgi */
}

/* Logo Tasarımı */
.logo-alani {
  text-align: center;
  margin-bottom: 35px;
}
.temkon-logo {
  font-size: 32px;
  font-weight: 900;
  color: #0f172a;
  margin: 0;
  letter-spacing: 1px;
}
.temkon-logo .kirmizi { color: #e11d48; }
.ayrac {
  width: 40px;
  height: 3px;
  background-color: #e11d48;
  margin: 10px auto;
  border-radius: 2px;
}
.logo-text {
  color: #64748b;
  font-size: 13px;
  font-weight: 500;
  margin: 0;
}

/* Form Tasarımı */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.input-grup label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  margin-bottom: 8px;
}
.input-kutu {
  position: relative;
  display: flex;
  align-items: center;
}
.input-kutu .ikon {
  position: absolute;
  left: 12px;
  color: #94a3b8;
  font-size: 16px;
}
.input-kutu input {
  width: 100%;
  padding: 12px 12px 12px 40px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 14px;
  color: #334155;
  transition: all 0.2s;
  background-color: #f8fafc;
}
.input-kutu input:focus {
  border-color: #0f172a;
  outline: none;
  background-color: #ffffff;
  box-shadow: 0 0 0 3px rgba(15, 23, 42, 0.05);
}

/* Ek Ayarlar (Hatırla & Unuttum) */
.ek-ayarlar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}
.hatirla {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #475569;
  cursor: pointer;
}
.sifre-unuttum {
  color: #e11d48;
  text-decoration: none;
  font-weight: 600;
  transition: 0.2s;
}
.sifre-unuttum:hover {
  text-decoration: underline;
  color: #be123c;
}

/* Buton */
.btn-giris {
  background-color: #0f172a;
  color: #ffffff;
  border: none;
  padding: 14px;
  border-radius: 6px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: 0.2s;
  margin-top: 10px;
}
.btn-giris:hover:not(:disabled) {
  background-color: #1e293b;
  transform: translateY(-1px);
}
.btn-giris:disabled {
  background-color: #94a3b8;
  cursor: not-allowed;
}

/* Alt Bilgi */
.login-footer {
  text-align: center;
  margin-top: 30px;
  font-size: 12px;
  color: #94a3b8;
}
.login-footer a { color: #64748b; text-decoration: underline; }
.versiyon { margin-top: 5px; font-weight: 600; }

/* Bildirim Alert */
.bildirim {
  position: fixed;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  color: white;
  box-shadow: 0 4px 15px rgba(0,0,0,0.15);
  z-index: 1000;
  text-align: center;
}
.bildirim.hata { background-color: #e11d48; }
.bildirim.bilgi { background-color: #10b981; }

.slide-up-enter-active, .slide-up-leave-active { transition: all 0.3s ease; }
.slide-up-enter-from, .slide-up-leave-to { opacity: 0; transform: translate(-50%, 20px); }
</style>