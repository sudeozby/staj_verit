<template>
  <div class="container" style="display: flex; justify-content: center; padding-top: 20px; min-height: 100vh; background-color: #f0f2f5;">
    <div style="width: 100%; max-width: 1200px;">
      
      <UstMenu /> 

      <div style="background: white; padding: 30px; border-radius: 10px; border-left: 8px solid #f39c12; box-shadow: 0 6px 12px rgba(0,0,0,0.08);">
        <h3 style="margin-top: 0; margin-bottom: 25px; color: #2c3e50; font-size: 22px; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px;">Yönetici Paneli: Ekip ve Yetki Kontrolü</h3>
        
        <div style="background: #fdf2e9; padding: 20px; border-radius: 8px; border: 1px solid #fce4d6; margin-bottom: 30px;">
          <h4 style="margin-top: 0; color: #d35400; font-size: 15px; margin-bottom: 15px;">➕ Yeni Personel Ekle</h4>
          <div style="display: flex; gap: 15px; align-items: flex-end;">
            <div style="flex: 1;">
              <label style="font-size: 13px; font-weight: bold; color: #555; display: block; margin-bottom: 5px;">Kullanıcı Adı</label>
              <input v-model="yeniKullanici.kullanici_adi" type="text" placeholder="Örn: ahmet_saha" style="width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box;">
            </div>
            <div style="flex: 1;">
              <label style="font-size: 13px; font-weight: bold; color: #555; display: block; margin-bottom: 5px;">Geçici Şifre</label>
              <input v-model="yeniKullanici.sifre" type="text" placeholder="En az 5 karakter" style="width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box;">
            </div>
            <div style="flex: 1;">
              <label style="font-size: 13px; font-weight: bold; color: #555; display: block; margin-bottom: 5px;">Sistem Yetkisi (Rol)</label>
              <select v-model="yeniKullanici.rol" style="width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box;">
                <option value="saha_ekibi">Saha / İmalat Ekibi</option>
                <option value="teklif_ekibi">Satış / Teklif Ekibi</option>
                <option value="yonetici">Yönetici</option>
              </select>
            </div>
            <button @click="kullaniciEkle" style="background-color: #27ae60; color: white; padding: 10px 25px; height: 40px; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; transition: 0.2s;">Kayıt Oluştur</button>
          </div>
        </div>

        <h4 style="margin-top: 0; color: #34495e; font-size: 16px; margin-bottom: 15px;">Kayıtlı Sistem Kullanıcıları</h4>
        <div style="overflow-x: auto; border: 1px solid #ecf0f1; border-radius: 8px;">
          <table style="width: 100%; border-collapse: collapse; font-size: 14px; text-align: left;">
            <thead>
              <tr style="background-color: #f8f9fa; color: #2c3e50;">
                <th style="padding: 15px; border-bottom: 2px solid #bdc3c7;">#ID</th>
                <th style="padding: 15px; border-bottom: 2px solid #bdc3c7;">Kullanıcı Adı</th>
                <th style="padding: 15px; border-bottom: 2px solid #bdc3c7;">Yetki Rolü</th>
                <th style="padding: 15px; border-bottom: 2px solid #bdc3c7;">Durum</th>
                <th style="padding: 15px; border-bottom: 2px solid #bdc3c7; text-align: right;">Güvenlik İşlemleri</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="kullanicilarListesi.length === 0">
                <td colspan="5" style="text-align: center; padding: 20px; color: #7f8c8d; font-weight: bold;">
                  Veriler bekleniyor veya henüz kayıtlı personel yok... 
                  (Veritabanı bağlantısı kuruluyor)
                </td>
              </tr>
              
              <tr v-for="user in kullanicilarListesi" :key="user.id" :style="{ opacity: user.aktif_mi === false ? '0.6' : '1', borderBottom: '1px solid #ecf0f1' }">
                <td style="padding: 15px; color: #7f8c8d;">{{ user.id }}</td>
                <td style="padding: 15px; font-weight: bold; color: #2c3e50;">
                  <span v-if="user.aktif_mi === false" style="text-decoration: line-through; color: #95a5a6;">{{ user.kullanici_adi }}</span>
                  <span v-else>{{ user.kullanici_adi }}</span>
                </td>
                <td style="padding: 15px;">
                  <span style="padding: 5px 10px; border-radius: 12px; font-size: 12px; font-weight: bold;" 
                        :style="user.rol === 'yonetici' ? 'background: #fadbd8; color: #c0392b;' : (user.rol === 'teklif_ekibi' ? 'background: #d6eaf8; color: #2980b9;' : 'background: #d5f5e3; color: #27ae60;')">
                    {{ user.rol === 'yonetici' ? '👑 Yönetici' : (user.rol === 'teklif_ekibi' ? '💼 Teklif Ekibi' : '👷‍♂️ Saha Ekibi') }}
                  </span>
                </td>
                <td style="padding: 15px;">
                  <span v-if="user.aktif_mi" style="color: #27ae60; font-weight: bold;">🟢 Aktif</span>
                  <span v-else style="color: #e74c3c; font-weight: bold;">🔴 Pasif</span>
                </td>
                <td style="padding: 15px; text-align: right; display: flex; gap: 10px; justify-content: flex-end;">
                  <template v-if="user.aktif_mi">
                    <button @click="sifreSifirla(user.kullanici_adi)" style="background-color: #f39c12; color: white; padding: 8px 12px; border: none; border-radius: 4px; cursor: pointer; font-size: 12px; font-weight: bold; transition: 0.2s;" title="Şifreyi sıfırlar">🔑 Şifre Sıfırla</button>
                    <button @click="kullaniciSil(user.id, user.kullanici_adi)" style="background-color: #e74c3c; color: white; padding: 8px 12px; border: none; border-radius: 4px; cursor: pointer; font-size: 12px; font-weight: bold; transition: 0.2s;">🚫 Erişimi Kapat</button>
                  </template>
                  <span v-else style="font-size: 12px; color: #7f8c8d; font-style: italic; padding: 8px;">Erişim Kapatıldı</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

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
const kullaniciRolu = ref(localStorage.getItem('kullaniciRolu'));

// Eğer bu sayfaya yönetici olmayan biri gizlice girmeye çalışırsa onu geri postala
onMounted(() => {
  if (kullaniciRolu.value !== 'yonetici') {
    router.push('/panel');
  } else {
    kullanicilariGetir();
  }
});

const kullanicilarListesi = ref([]);
const yeniKullanici = ref({ kullanici_adi: '', sifre: '', rol: 'saha_ekibi' });

// 1. LİSTELEME (Güncel)
const kullanicilariGetir = async () => {
  try {
const response = await axios.get("http://127.0.0.1:8000/api/ekip"); // <-- /api eklendi!    
 kullanicilarListesi.value = response.data;
  } catch (error) {
    console.error("Kullanıcılar getirilemedi:", error);
  }
};

// YENİ VE KULLANICI DOSTU EKLEME FONKSİYONU
const kullaniciEkle = async () => {
  // 1. ÖNDEN KONTROL (Frontend - Sunucuyu yormadan uyar!)
  if (!yeniKullanici.value.kullanici_adi || !yeniKullanici.value.sifre) {
    return alert("Lütfen kullanıcı adı ve şifre girin!");
  }

  if (yeniKullanici.value.sifre.length < 5) {
    return alert("Güvenlik Uyarısı: Şifre en az 5 karakter olmalıdır!");
  }

  try {
    // Kuralları geçtiyse Backend'e gönder
    await axios.post('http://127.0.0.1:8000/api/ekip/ekle', yeniKullanici.value);
    
    // Formu temizle ve listeyi yenile
    yeniKullanici.value = { kullanici_adi: '', sifre: '', rol: 'saha_ekibi' };
    await kullanicilariGetir(); 
    alert("Yeni personel başarıyla eklendi!");
    
  } catch (error) {
    // 2. BACKEND'DEN GELEN 422 GİBİ HATALARI YAKALAMA
    if (error.response && error.response.status === 422) {
      alert("Hata: Girdiğiniz bilgiler sistem kurallarıyla uyuşmuyor. Lütfen kontrol edin.");
    } else {
      alert(`İşlem başarısız: ${error.response?.data?.detail || 'Sistemde geçici bir sorun var.'}`);
    }
  }
};

// 3. SİLME / PASİFE ALMA (Kullanıcı adı yerine ID kullanıyoruz)
const kullaniciSil = async (id, kullanici_adi) => {
  if (!confirm(`${kullanici_adi} adlı kullanıcının erişimini kapatmak istediğinize emin misiniz?`)) return;
  
  try {
    // ESKİ: /kullanici-sil/${kullanici_adi} -> YENİ: /ekip/${id}
    const response = await axios.delete(`http://127.0.0.1:8000/api/ekip/${id}`);
    
    if (response.status === 200) {
      alert("Kullanıcının sisteme erişimi kapatıldı (Pasife alındı).");
      await kullanicilariGetir(); 
    }
  } catch (error) {
    console.error(error);
    alert("İşlem başarısız oldu.");
  }
};

// 4. ŞİFRE SIFIRLAMA (Aktif Edildi!)
const sifreSifirla = async (kullanici_adi) => {
  const yeniSifre = prompt(`${kullanici_adi} adlı kullanıcı için yeni şifreyi giriniz (En az 5 karakter):`);
  
  // Kullanıcı "İptal"e basarsa veya boş bırakırsa işlemi durdur
  if (!yeniSifre) return; 

  if (yeniSifre.length < 5) {
    return alert("Güvenlik Uyarısı: Şifre en az 5 karakter olmalıdır!");
  }

  try {
    await axios.put('http://127.0.0.1:8000/api/ekip/sifre-guncelle', {
      kullanici_adi: kullanici_adi,
      sifre: yeniSifre
    });
    alert(`🔑 ${kullanici_adi} kullanıcısının şifresi başarıyla güncellendi!`);
  } catch (error) {
    alert(`İşlem başarısız: ${error.response?.data?.detail || 'Sunucu hatası'}`);
  }
};
const cikisYap = () => {
  localStorage.removeItem('girisYapildi');
  localStorage.removeItem('kullaniciRolu');
  router.push('/');
};
</script>