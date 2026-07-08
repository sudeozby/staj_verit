import psycopg2
import os
from contextlib import contextmanager
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor # Sözlük (dict) formatında veri almak için

# .env dosyasını yükle
load_dotenv()

@contextmanager
def get_db_session():
    """Veritabanı bağlantısını güvenli bir şekilde yönetir ve sonuçları sözlük olarak döndürür."""
    conn = None
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT", "5432")
        )
        conn.set_client_encoding('UTF8')
        
        # RealDictCursor burada devreye giriyor: Sorgular artık dict dönüyor
        cur = conn.cursor(cursor_factory=RealDictCursor) 
        
        yield cur  # İşlemleri yapması için imleci (cursor) dışarı ver
        
        conn.commit()  # Hata yoksa işlemi kalıcı kaydet
        
    except Exception as e:
        if conn:
            conn.rollback()  # Hata durumunda veritabanını temizle
        raise Exception(f"Veritabanı İşlem Hatası: {e}")
        
    finally:
        if conn:
            conn.close()  # İşi bitince bağlantıyı kapat