import os
import psycopg2
from dotenv import load_dotenv

# .env dosyasındaki değişkenleri yükle
load_dotenv()

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", "5432") # Port girilmezse varsayılan 5432 olsun
    )

def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except OperationalError as e:
        print(f"Veritabanı bağlantı hatası: {e}")
        raise  # Hata durumunda main.py bunu yakalayıp 500 hatası döndürebilmeli