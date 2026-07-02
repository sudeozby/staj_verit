import psycopg2
import os
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

@contextmanager
def get_db_session():
    """Veritabanı bağlantısını güvenli bir şekilde açar ve iş bitince kapatır."""
    conn = None
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        conn.set_client_encoding('UTF8')
        cur = conn.cursor()
        yield cur  # İşlemleri yapması için imleci dışarı aktar
        conn.commit()  # Hata yoksa veritabanına kalıcı olarak kaydet
    except Exception as e:
        if conn:
            conn.rollback()  # Hata varsa işlemi geri al (veriyi koru)
        raise Exception(f"Veritabanı İşlem Hatası: {e}")
    finally:
        if conn:
            conn.close()  # İş bitince kapıyı otomatik olarak kapat