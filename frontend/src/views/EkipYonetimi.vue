<template>
  <div class="sistem-container">
    <div style="width: 100%; max-width: 1200px; margin: 0 auto;">
      
      <UstMenu /> 

      <div class="sayfa-karti">
        <div class="karti-header">
          <h3>Sistem Erişim ve Personel Yönetimi</h3>
          <p>Kullanıcı yetkilendirmeleri, yeni personel kayıtları ve şifre işlemleri.</p>
        </div>
        
        <!-- YENİ PERSONEL EKLEME ALANI -->
        <div class="islem-alani">
          <div class="islem-baslik">
            <span class="ikon">➕</span> Yeni Sistem Kullanıcısı Tanımla
          </div>
          
          <div class="form-grid">
            <div class="input-grubu">
              <label>Kullanıcı Adı (Benzersiz)</label>
              <input v-model="yeniKullanici.kullanici_adi" type="text" placeholder="Örn: ahmet_saha">
            </div>
            
            <div class="input-grubu">
              <label>Geçici Erişim Şifresi</label>
              <input v-model="yeniKullanici.sifre" type="text" placeholder="En az 5 karakter">
            </div>
            
            <div class="input-grubu">
              <label>Sistem Yetki Profili</label>
              <select v-model="yeniKullanici.rol">
                <option value="saha_ekibi">Saha / İmalat Ekibi</option>
                <option value="teklif_ekibi">Satış / Teklif Ekibi</option>
                <option value="yonetici">Yönetici (Tam Erişim)</option>
              </select>
            </div>
            
            <button @click="kullaniciEkle" class="btn-kaydet">Kullanıcıyı Kaydet</button>
          </div>
        </div>

        <!-- PERSONEL LİSTESİ TABLOSU -->
        <div class="liste-alani">
          <div class="liste-baslik">
            <h4>Kayıtlı Sistem Kullanıcıları</h4>
          </div>
          
          <div class="tablo-sarmalayici">
            <table class="kurumsal-tablo">
              <thead>
                <tr>
                  <th>Personel ID</th>
                  <th>Kullanıcı Adı</th>
                  <th>Yetki Rolü</th>
                  <th>Sistem Durumu</th>
                  <th class="sag-hizali">Güvenlik İşlemleri</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="kullanicilarListesi.length === 0">
                  <td colspan="5" class="bos-durum">
                    Veriler yükleniyor veya sistemde kayıtlı personel bulunmuyor...
                  </td>
                </tr>
                
                <tr v-for="user in kullanicilarListesi" :key="user.id" :class="{ 'pasif-kullanici': !user.aktif_mi }">
                  <td class="kod">#UID-{{ user.id }}</td>
                  <td class="kullanici-adi">
                    {{ user.kullanici_adi }}
                  </td>
                  <td>
                    <span :class="['rol-rozeti', user.rol]">
                      {{ user.rol === 'yonetici' ? '👑 Yönetici' : (user.rol === 'teklif_ekibi' ? '💼 Teklif Ekibi' : '👷‍♂️ Saha Ekibi') }}
                    </span>
                  </td>
                  <td>
                    <span :class="['durum-rozeti', user.aktif_mi ? 'aktif' : 'pasif']">
                      {{ user.aktif_mi ? '🟢 Aktif' : '🔴 Kapatıldı' }}
                    </span>
                  </td>
                  <td class="islemler">
                    <template v-if="user.aktif_mi">
                      <button @click="sifreSifirla(user.kullanici_adi)" class="btn-islem btn-sari" title="Şifreyi sıfırlar">🔑 Şifre Sıfırla</button>
                      <button @click="kullaniciSil(user.id, user.kullanici_adi)" class="btn-islem btn-kirmizi">🚫 Erişimi Kapat</button>
                    </template>
                    <span v-else class="pasif-mesaj">Erişim yetkisi durduruldu</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
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
const aktifKullanici = localStorage.getItem("kullanici_adi") || "Sistem";

// Güvenlik: Yönetici olmayan birini postala
onMounted(() => {
  if (kullaniciRolu.value !== 'yonetici') {
    router.push('/dashboard'); // Yönlendirmeyi yeni giriş sayfamıza uydurduk
  } else {
    kullanicilariGetir();
  }
});

const kullanicilarListesi = ref([]);
const yeniKullanici = ref({ kullanici_adi: '', sifre: '', rol: 'saha_ekibi' });

// 1. LİSTELEME
const kullanicilariGetir = async () => {
  try {
    const response = await axios.get("http://127.0.0.1:8000/api/ekip"); 
    kullanicilarListesi.value = response.data;
  } catch (error) {
    console.error("Kullanıcılar getirilemedi:", error);
  }
};

// 2. YENİ PERSONEL EKLEME
const kullaniciEkle = async () => {
  if (!yeniKullanici.value.kullanici_adi || !yeniKullanici.value.sifre) {
    return alert("Lütfen kullanıcı adı ve şifre girin!");
  }

  try {
    const anlikKullanici = localStorage.getItem("kullanici_adi") || "Sistem";
    await axios.post('http://127.0.0.1:8000/api/ekip/ekle', yeniKullanici.value, {
      headers: { 'islem-yapan': anlikKullanici }
    });
    
    yeniKullanici.value = { kullanici_adi: '', sifre: '', rol: 'saha_ekibi' };
    await kullanicilariGetir(); 
    alert("Yeni personel başarıyla eklendi!");
  } catch (error) {
    if (error.response && error.response.status === 400) {
      // İŞTE BURASI: Arka plandan gönderdiğimiz o yönlendirici mesajı direkt basıyoruz
      alert(error.response.data.detail);
    } else if (error.response && error.response.status === 422) {
      alert("Hata: Girdiğiniz bilgiler sistem kurallarıyla uyuşmuyor.(Kayıtlı kullanıcı adı kullanmadığınıza emin olunuz.)");
    } else {
      alert("Sisteme bağlanılamadı. Lütfen internet bağlantınızı ve sunucuyu kontrol edin.");
      console.error(error);
    }
  }
};

// 3. SİLME / PASİFE ALMA
const kullaniciSil = async (id, kullanici_adi) => {
  if (!confirm(`${kullanici_adi} adlı kullanıcının erişimini kapatmak istediğinize emin misiniz?`)) return;
  
  try {
    const anlikKullanici = localStorage.getItem("kullanici_adi") || "Sistem";
    const response = await axios.delete(`http://127.0.0.1:8000/api/ekip/${id}`, {
      headers: { 'islem-yapan': anlikKullanici }
    });
    
    if (response.status === 200) {
      alert("Kullanıcının sisteme erişimi kapatıldı.");
      await kullanicilariGetir(); 
    }
  } catch (error) {
    console.error(error);
    alert("İşlem başarısız oldu.");
  }
};

// 4. ŞİFRE SIFIRLAMA
const sifreSifirla = async (kullanici_adi) => {
  const yeniSifre = prompt(`${kullanici_adi} adlı kullanıcı için yeni şifreyi giriniz:`);
  if (!yeniSifre) return; 

  try {
    const anlikKullanici = localStorage.getItem("kullanici_adi") || "Sistem";
    await axios.put('http://127.0.0.1:8000/api/ekip/sifre-guncelle', {
      kullanici_adi: kullanici_adi,
      sifre: yeniSifre
    }, {
      headers: { 'islem-yapan': anlikKullanici }
    });
    alert(`🔑 Şifre başarıyla güncellendi!`);
  } catch (error) {
    alert(`İşlem başarısız.`);
  }
};
</script>

<style scoped>
/* KURUMSAL TASARIM (SaaS Mimarisi) */
.sistem-container {
  min-height: 100vh;
  background-color: #f8fafc;
  padding-bottom: 40px;
  font-family: 'Segoe UI', system-ui, sans-serif;
  color: #334155;
}

.sayfa-karti {
  background: #ffffff;
  padding: 35px;
  border-radius: 12px;
  border-top: 4px solid #0f172a;
  box-shadow: 0 4px 15px rgba(0,0,0,0.03);
  margin-top: 25px;
}

.karti-header { margin-bottom: 30px; border-bottom: 1px solid #e2e8f0; padding-bottom: 15px; }
.karti-header h3 { margin: 0; color: #0f172a; font-size: 20px; font-weight: 600; }
.karti-header p { margin: 5px 0 0 0; color: #64748b; font-size: 13px; }

/* Yeni Kayıt Formu Alanı */
.islem-alani { background: #f8fafc; padding: 25px; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 35px; }
.islem-baslik { font-size: 14px; font-weight: 600; color: #0f172a; margin-bottom: 20px; display: flex; align-items: center; gap: 8px; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr 1fr auto; gap: 20px; align-items: end; }

.input-grubu label { display: block; font-size: 12px; font-weight: 600; color: #475569; margin-bottom: 8px; text-transform: uppercase; }
.input-grubu input, .input-grubu select { 
  width: 100%; padding: 12px; border: 1px solid #cbd5e1; border-radius: 6px; 
  font-size: 13px; box-sizing: border-box; background-color: #ffffff;
  transition: all 0.2s; outline: none;
}
.input-grubu input:focus, .input-grubu select:focus { border-color: #0f172a; box-shadow: 0 0 0 2px rgba(15, 23, 42, 0.1); }

.btn-kaydet {
  background-color: #0f172a; color: white; padding: 12px 25px; height: 43px;
  border: none; border-radius: 6px; font-weight: 600; cursor: pointer; transition: 0.2s; font-size: 13px;
}
.btn-kaydet:hover { background-color: #1e293b; transform: translateY(-1px); }

/* Tablo Listesi Alanı */
.liste-baslik { margin-bottom: 15px; }
.liste-baslik h4 { margin: 0; color: #334155; font-size: 15px; font-weight: 600; }

.tablo-sarmalayici { overflow-x: auto; border: 1px solid #e2e8f0; border-radius: 8px; }
.kurumsal-tablo { width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; }
.kurumsal-tablo th { background-color: #f1f5f9; color: #475569; padding: 15px 20px; font-weight: 600; font-size: 12px; text-transform: uppercase; border-bottom: 1px solid #e2e8f0; }
.kurumsal-tablo td { padding: 15px 20px; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }
.kurumsal-tablo tr:last-child td { border-bottom: none; }
.kurumsal-tablo tr:hover td { background-color: #f8fafc; }

/* Durum ve Renkler */
.pasif-kullanici td { background-color: #fdf2f2 !important; color: #94a3b8; }
.pasif-kullanici .kullanici-adi { text-decoration: line-through; color: #94a3b8; }
.kullanici-adi { font-weight: 600; color: #0f172a; }
.kod { font-family: monospace; color: #64748b; }

.rol-rozeti { padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; display: inline-block; }
.rol-rozeti.yonetici { background: #fef2f2; color: #e11d48; }
.rol-rozeti.teklif_ekibi { background: #eff6ff; color: #2563eb; }
.rol-rozeti.saha_ekibi { background: #ecfdf5; color: #059669; }

.durum-rozeti { font-weight: 600; font-size: 12px; }
.durum-rozeti.aktif { color: #059669; }
.durum-rozeti.pasif { color: #e11d48; }

.sag-hizali { text-align: right; }
.islemler { text-align: right; white-space: nowrap; }
.btn-islem { padding: 6px 12px; border: 1px solid; border-radius: 4px; cursor: pointer; font-size: 11px; font-weight: 600; transition: 0.2s; margin-left: 8px; background: #fff; }
.btn-sari { border-color: #f59e0b; color: #d97706; }
.btn-sari:hover { background: #f59e0b; color: #fff; }
.btn-kirmizi { border-color: #ef4444; color: #dc2626; }
.btn-kirmizi:hover { background: #ef4444; color: #fff; }

.pasif-mesaj { font-size: 11px; color: #94a3b8; font-style: italic; }
.bos-durum { text-align: center; color: #94a3b8; font-style: italic; padding: 30px !important; }

@media (max-width: 900px) { .form-grid { grid-template-columns: 1fr; gap: 15px; } .btn-kaydet { width: 100%; } }
</style>