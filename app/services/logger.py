import psycopg2
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def log_islem(kullanici, islem, detay):
    """Kritik işlemleri veritabanına kalıcı olarak kaydeder."""
    conn = None
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO loglar (kullanici_adi, islem_turu, detay, tarih) VALUES (%s, %s, %s, %s);",
            (kullanici, islem, detay, datetime.now())
        )
        conn.commit()
    except Exception as e:
        print(f"Loglama hatası (Sistem çalışmaya devam edecek): {e}")
    finally:
        if conn:
            conn.close()