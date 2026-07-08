<template>
  <div class="container" style="display: flex; justify-content: center; align-items: center; min-height: 100vh; background-color: #ecf0f1;">
    
    <div class="login-form" style="background: white; padding: 40px; border-radius: 12px; box-shadow: 0 8px 20px rgba(0,0,0,0.1); width: 100%; max-width: 400px; text-align: center; border-top: 6px solid #2c3e50;">
      
      <div style="margin-bottom: 30px;">
        <h1 style="font-size: 36px; margin: 0; color: #2c3e50;">TEM<span style="color: #e74c3c;">K</span>ON</h1>
        <h2 style="font-size: 14px; margin: 5px 0 0 0; color: #7f8c8d;">Maliyet Yönetim Paneli</h2>
      </div>

      <div class="form-grubu" style="margin-bottom: 20px; text-align: left;">
        <label style="font-weight: bold; color: #34495e; font-size: 14px; display: block; margin-bottom: 5px;">Kullanıcı Adı / E-Posta</label>
        <input 
          v-model="kullaniciAdi" 
          type="text" 
          placeholder="Adınızı giriniz..." 
          @keyup.enter="girisKontrol"
          style="width: 100%; padding: 12px; border: 1px solid #bdc3c7; border-radius: 6px; box-sizing: border-box; font-size: 14px;"
        />
      </div>

      <div class="form-grubu" style="margin-bottom: 10px; text-align: left;">
        <label style="font-weight: bold; color: #34495e; font-size: 14px; display: block; margin-bottom: 5px;">Şifre</label>
        <input 
          v-model="sifre" 
          type="password" 
          placeholder="••••••••" 
          @keyup.enter="girisKontrol"
          style="width: 100%; padding: 12px; border: 1px solid #bdc3c7; border-radius: 6px; box-sizing: border-box; font-size: 14px;"
        />
        
        <p v-if="girisHatasi" style="color: #e74c3c; font-size: 13px; font-weight: bold; margin-top: 5px; margin-bottom: 0;">
          Hatalı kullanıcı adı veya şifre girdiniz!
        </p>
      </div>

      <div style="text-align: right; margin-bottom: 25px;">
        <a href="#" @click.prevent="sifreModalAcik = true" style="color: #8e44ad; font-size: 13px; text-decoration: none; font-weight: bold; transition: 0.2s;">
          Şifremi Unuttum?
        </a>
      </div>

      <button @click="girisKontrol" style="width: 100%; background-color: #2c3e50; color: white; padding: 14px; border: none; border-radius: 6px; font-weight: bold; font-size: 16px; cursor: pointer; transition: 0.3s;">
        Sisteme Giriş Yap
      </button>

    </div>

    <div v-if="sifreModalAcik" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); display: flex; justify-content: center; align-items: center; z-index: 999; backdrop-filter: blur(4px);">
      <div style="background: white; padding: 30px; border-radius: 10px; width: 380px; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.2); border-top: 5px solid #e74c3c;">
        
        <div style="font-size: 45px; margin-bottom: 10px;">🔒</div>
        <h3 style="margin-top: 0; color: #2c3e50; font-size: 20px;">Sistem Erişimi Kilitli</h3>
        
        <div style="background: #fdf2e9; padding: 15px; border-radius: 6px; border-left: 4px solid #e74c3c; text-align: left; margin-bottom: 20px;">
          <p style="color: #7f8c8d; font-size: 13px; line-height: 1.6; margin: 0;">
            Kurumsal güvenlik politikalarımız gereği otomatik şifre sıfırlama işlemi <b>yapılamamaktadır.</b>
            <br><br>
            Sisteme yeniden erişim sağlamak ve şifrenizi yenilemek için lütfen <b>Sistem Yöneticisi</b> ile iletişime geçiniz.
          </p>
        </div>

        <button @click="sifreModalAcik = false" style="width: 100%; background-color: #e74c3c; color: white; padding: 12px; border: none; border-radius: 6px; font-weight: bold; font-size: 14px; cursor: pointer; transition: 0.3s;">
          Anladım, Kapat
        </button>
        
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'; // ref ve onMounted'ı burada birleştirdik
import { useRouter } from 'vue-router';
import axios from 'axios';
import { API_BASE } from '../config';

const router = useRouter();


// Değişkenlerimiz
const kullaniciAdi = ref('');
const sifre = ref('');
const girisHatasi = ref(false);
const sifreModalAcik = ref(false);


onMounted(() => {
  if (!localStorage.getItem('girisYapildi')) {
    router.push('/'); // Giriş yapmadıysa zorla login sayfasına at
  }
});

// Python (FastAPI) Arka Ucuna Bağlanan Güvenlik Kapısı
const girisKontrol = async () => {
  // Her denemede hata mesajını önce bir gizleyelim
  girisHatasi.value = false;

  try {

    // Sabit URL yerine API_BASE yerleştirildi
     const response = await axios.post(`${API_BASE}/giris-yap`, {
      kullanici_adi: kullaniciAdi.value,
      sifre: sifre.value
    });

    // Şifre doğruysa backend bize kullanıcının rolünü yollayacak (Örn: 'yonetici')
    const gelenRol = response.data.rol;
    
    // Tarayıcı hafızasına yetkileri kaydediyoruz
    localStorage.setItem('girisYapildi', 'true');
    localStorage.setItem('kullaniciRolu', gelenRol);
    
    // Panolar sayfasına geçiş yapıyoruz
    router.push('/panel');
    
  } catch (error) {
    // Backend hata fırlatırsa (yanlış şifre) burası çalışır ve ekrana kırmızı yazı çıkar
    girisHatasi.value = true;
    console.error("Giriş başarısız oldu:", error);
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

/* YENİ EKLENEN: Şifremi unuttum linkinin üzerine gelince parlaması için */
a {
  transition: opacity 0.2s;
}
a:hover {
  opacity: 0.7;
}
</style>