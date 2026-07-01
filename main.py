import psycopg2
import os
from dotenv import load_dotenv
#birden fazla dosya açtık sınıflama oluşturduk ki her table gelip main.py da yığılmasın
# .env dosyasındaki şifreyi oku
load_dotenv()
db_password = os.getenv("DB_PASSWORD")

# Bağlantı kur
#hata yönetimi
try:
    conn = psycopg2.connect(
        #şifreleri .env dosyasında okuduğu için güvenli olur
        dbname="postgres",
        user="postgres",
        password=db_password,
        host="localhost",
        port="5432"
    )
    print("Bağlantı başarılı! Veritabanı ile konuşabiliyoruz.")
    conn.close()
except Exception as e:
    print(f"Hata oluştu: {e}")
