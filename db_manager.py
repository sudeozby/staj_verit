import psycopg2
from psycopg2.extras import RealDictCursor

# VERİTABANI AYARLARI
DB_CONFIG = {
    "host": "localhost",
    "database": "postgres", 
    "user": "postgres",     
    "password": "123456"      
}


def save_log(username, islem, detay):
    conn = get_db_connection()
    cur = conn.cursor()
    # "tarih" sütununu ve dördüncü %s'i sildik. 
    # Veritabanı "tarih" değerini otomatik atayacak.
    cur.execute(
        "INSERT INTO loglar (kullanici_adi, islem_turu, detay) VALUES (%s, %s, %s);",
        (username, islem, detay)
    )
    conn.commit()
    cur.close()
    conn.close()
    
def fetch_all_logs():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM loglar ORDER BY tarih DESC;") # En yeniler en üstte
    logs = cur.fetchall()
    cur.close()
    conn.close()
    return logs

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def fetch_all_users():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, kullanici_adi, rol FROM kullanicilar;")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return users

def add_user(username, password, role):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO kullanicilar (kullanici_adi, sifre, rol) VALUES (%s, %s, %s);",
        (username, password, role)
    )
    conn.commit()
    cur.close()
    conn.close()

def update_user_password(username, new_password):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE kullanicilar SET sifre = %s WHERE kullanici_adi = %s;",
        (new_password, username)
    )
    conn.commit()
    cur.close()
    conn.close()

def delete_user(username):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM kullanicilar WHERE kullanici_adi = %s;", (username,))
    conn.commit()
    cur.close()
    conn.close()