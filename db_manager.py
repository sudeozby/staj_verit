import os
import psycopg2
from dotenv import load_dotenv
from psycopg2 import OperationalError

# .env dosyasındaki değişkenleri yükle
load_dotenv()

# Hiçbir varsayılan şifre yok, sadece .env'den okur
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except OperationalError as e:
        print(f"Veritabanı bağlantı hatası: {e}")
        return None