import psycopg2
import os
from dotenv import load_dotenv

# .env dosyasındaki değişkenleri sisteme yükle
load_dotenv()

def get_db_connection():
    """
    Veritabanına bağlanır ve bağlantı nesnesini döndürür.
    """
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        # İŞTE TÜRKÇE KARAKTER HATASINI ÇÖZEN SİHİRLİ SATIR:
        conn.set_client_encoding('UTF8')
        
        return conn
    except Exception as e:
        print(f"Veritabanı bağlantı hatası: {e}")
        return None