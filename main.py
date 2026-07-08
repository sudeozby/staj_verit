from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from psycopg2.extras import RealDictCursor
from app.models.schemas import Kullanici 
from app.db import crud 
from db_manager import get_db_connection # Sadece bağlantı için
from app.api.endpoints import router as api_router



# 1. ÖNCE 'APP' OLUŞTURULUR
app = FastAPI(title="Kurumsal API v1.0")

# 2. GÜVENLİK/CORS AYARLARI EKLENİR
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. EN SON ROUTER (YOLLAR) EKLENİR
app.include_router(api_router, prefix="/api")

# Artık tüm rotaların /api/projeler gibi çalışacak
#Frontend-Backend İlişkisi: Senin Vue uygulaman localhost:5173 gibi bir adreste çalışıyor, API'n ise 127.0.0.1:8000 adresinde. 
# Tarayıcılar, farklı portlardan gelen bu istekleri "yabancı" kabul eder.

#allow_origins=["*"]: Bu, "Her yerden gelen isteği kabul et" demektir. Projeni canlı server'a (şirket server'ına) taşıdığında 
# burayı ["*"] yerine ["https://sirketdomainin.com"] gibi kısıtlayarak daha güvenli hale getireceğiz.




#Hatalı: fetch_all_users() ve add_user(...) doğrudan çağrılıyor. Bu fonksiyonlar kendi bağlantılarını (conn) kendi içlerinde açıyorlar. 
# Bu da bağlantı yönetimini imkansız kılıyor (bir hata olsa rollback yapamazsın, bağlantı sızıntısı olur).
@app.get("/kullanicilar")
def get_users():
    conn = get_db_connection() # 1. Fabrikayı aç
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        return crud.fetch_all_users(cur) # 2. Uzman işi yapsın
    finally:
        cur.close() # 3. Her durumda temizle
        conn.close()

@app.post("/kullanici-ekle")
def post_user(kullanici: Kullanici):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # 1. Kullanıcıyı ekle
        crud.add_user(cur, kullanici.kullanici_adi, kullanici.sifre, kullanici.rol)
        # 2. Log tut
        crud.save_log(cur, "Admin", "KULLANICI_EKLEME", f"{kullanici.kullanici_adi} eklendi.")
        
        conn.commit() # 3. İkisini birden onayla (Transaction)
        return {"mesaj": "Başarıyla eklendi"}
    except Exception as e:
        conn.rollback() # Bir hata olursa hiçbirini yapma (Güvenlik!)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

#Bağlantı Bütünlüğü: Her iki rotada da try...finally kullanarak bağlantıyı (conn) açıp, işin biter bitmez garantili bir şekilde (finally ile) kapatıyorsun. 
# Bu, projen server'a çıktığında 7/24 çalışırken veritabanının "connection leak" (bağlantı sızıntısı) yüzünden kitlenmesini engeller.

#CRUD Uyumu: crud.py dosyasında yazdığımız fonksiyonlara cur parametresini gönderiyorsun. 
# Artık crud.py sadece sorgu yapan bir "uzman", main.py ise bu uzmanı yöneten bir "orijinal orkestra şefi" konumunda.

#Hata Yönetimi (Transaction): update_pano rotasında conn.commit() kullanman harika. 
# Eğer güncelleme sorgusu bir sebeple hata verirse (örneğin veritabanı kilitlenirse), conn.commit() çağrılmayacak ve veri bozulmayacaktır.

#Güvenlik: @app.put içindeki rol: str = Header(...) kontrolü, saha ekibini kapıda tutacak olan o mekanizmanın anahtarı.
@app.get("/pano-detay/{proje_id}")
def get_pano_detay(proje_id: int, pano_turu: str = "Tüm Panoları Getir"):
    # Bağlantıyı aç (db_manager üzerinden)
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor) # Veya normal cursor
    try:
        sonuc = crud.get_pano_detay_by_id(cur, proje_id, pano_turu)
        return sonuc
    finally:
        cur.close()
        conn.close()

@app.put("/pano-guncelle/{id}")
def update_pano(id: int, yeni_adet: int, rol: str = Header(...)):
    if rol != "yonetici":
        raise HTTPException(status_code=403, detail="Yetkisiz işlem!")
    
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        crud.update_pano_malzeme_adet(cur, id, yeni_adet)
        conn.commit()
        return {"mesaj": "Güncellendi"}
    except Exception as e:
        conn.rollback() # Hata varsa işlemi tamamen geri al!
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()
    
@app.put("/kullanici-sifre-guncelle")
def put_sifre(data: dict):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        crud.update_user_password(cur, data["kullanici_adi"], data["yeni_sifre"])
        crud.save_log(cur, data["kullanici_adi"], "ŞİFRE_GÜNCELLEME", "Şifre güncellendi.")
        conn.commit()
        return {"mesaj": "Şifre başarıyla güncellendi"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()


#Güvenlik: log_islem fonksiyonunu crud.save_log ile birleştirerek, "kullanıcıyı silerken aynı anda logunu da at"
# mantığını tek bir try bloğuna soktuk. Eğer silme başarılı olur ama log atılamazsa, conn.rollback() sayesinde ikisi de gerçekleşmez ve veritabanı tutarlı kalır.

#Bağlantı Yönetimi: get_db_connection artık sadece main.py içinde çağrılıyor. Bu, veritabanı bağlantılarını (connection pool)
#  ileride çok daha kolay optimize etmemi<i sağlayacak.
@app.delete("/kullanici-sil/{kullanici_adi}")
def delete_user_route(kullanici_adi: str):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        crud.delete_user(cur, kullanici_adi)
        crud.save_log(cur, "Admin", "KULLANICI_SİLME", f"{kullanici_adi} silindi.")
        conn.commit()
        return {"mesaj": "Kullanıcı silindi"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

#Bu bir SELECT işlemi olduğu için sadece veriyi çekip döndürmemiz yeterli.
@app.get("/loglar")
def get_logs():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        return crud.fetch_all_logs(cur)
    finally:
        cur.close()
        conn.close()
    


# --- PROJE LİSTELEME ---
@app.get("/projeler/listele")
def get_projeler():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        return crud.fetch_all_projects(cur)
    finally:
        cur.close()
        conn.close()

# --- GİRİŞ YAP ---
@app.post("/giris-yap")
def login(data: dict):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # crud içindeki güncel fonksiyonumuzu kullanıyoruz
        user = crud.get_user_by_username(cur, data["kullanici_adi"])
        
        if user and user["sifre"] == data["sifre"]:
            return {"rol": user["rol"]}
        else:
            raise HTTPException(status_code=401, detail="Hatalı kullanıcı adı veya şifre")
    finally:
        cur.close()
        conn.close()
    
    # MALZEMELERİ LİSTELEME 
@app.get("/malzemeler/listele")
def get_malzemeler():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        return crud.fetch_all_malzemeler(cur)
    finally:
        cur.close()
        conn.close()

# PROJE EKLEME
@app.post("/projeler")
def post_proje(proje: dict):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        crud.add_proje(cur, proje)
        conn.commit() # İşlemi onayla
        return {"mesaj": "Proje başarıyla eklendi"}
    except Exception as e:
        conn.rollback() # Hata durumunda güvenle geri al
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/dashboard-ozet")
def get_dashboard_ozet():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        # Burada crud.py içinde basit SELECT SUM(...) sorguları yapan fonksiyonların olmalı
        # Örnek: crud.fetch_dashboard_stats(cur)
        return crud.fetch_dashboard_stats(cur)
    finally:
        cur.close()
        conn.close()

# MALZEME EKLEME 
@app.post("/malzemeler")
def post_malzeme(malzeme: dict):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        crud.add_malzeme(cur, malzeme)
        conn.commit() # İşlemi onayla
        return {"mesaj": "Malzeme başarıyla eklendi"}
    except Exception as e:
        conn.rollback() # Hata durumunda güvenle geri al
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()