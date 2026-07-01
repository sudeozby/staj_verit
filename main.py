#business logic layer(veri işleyen yer)
import psycopg2
import os
from dotenv import load_dotenv
#birden fazla dosya açtık sınıflama oluşturduk ki her table gelip main.py da yığılmasın
# .env dosyasındaki şifreyi oku
load_dotenv()
db_password = os.getenv("DB_PASSWORD")


# Fonksiyonun tanımı
def veri_ekle(hiz, irtifa):
    try:
        
# Bağlantı kur
#hata yönetimi
        conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"), # Burası sunucuya geçince 'db' veya IP adresi olacak
    port=os.getenv("DB_PORT")
)
          #şifreleri .env dosyasında okuduğu için güvenli olur
        cur = conn.cursor()
        # SQL komutu: %s olan yerlere hiz ve irtifa değerlerini takıyoruz
        cur.execute("INSERT INTO telemetri (hiz, irtifa) VALUES (%s, %s)", (hiz, irtifa))
        conn.commit() 
        print(f"Başarıyla eklendi: Hız={hiz}, İrtifa={irtifa}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Hata oluştu: {e}")

# Fonksiyonu burada çağırıyoruz
veri_ekle(150.5, 500.0)
