# app/services/logger.py
import psycopg2
from datetime import datetime

def log_islem(kullanici, islem, detay):
    # Veritabanı bağlantı bilgilerin (kendi bilgilerini kullan)
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="sifre"
    )
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO loglar (kullanici, islem, detay, tarih) VALUES (%s, %s, %s, %s);",
        (kullanici, islem, detay, datetime.now())
    )
    conn.commit()
    cur.close()
    conn.close()