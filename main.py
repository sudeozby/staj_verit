#business logic layer(veri işleyen yer)

#birden fazla dosya açtık sınıflama oluşturduk ki her table gelip main.py da yığılmasın

from fastapi import FastAPI, HTTPException
from database import get_db_connection

# FastAPI uygulamasını başlat
app = FastAPI(title="Envanter ve Proje Takip API")

@app.get("/")
def ana_sayfa():
    return {"mesaj": "Sistem başarıyla çalışıyor. Arayüz buradan veri çekebilir."}

@app.get("/projeler")
def projeleri_getir():
    """
    Veritabanındaki tüm projeleri çeker ve arayüze liste olarak gönderir.
    """
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Veritabanına bağlanılamadı.")
    
    try:
        cur = conn.cursor()
        # Projeler tablosundaki verileri çek
        cur.execute("SELECT id, proje_adi, musteri, lokasyon FROM projeler;")
        kayitlar = cur.fetchall()
        
        # Arayüzün anlayacağı JSON (sözlük) formatına çevir
        projeler_listesi = []
        for kayit in kayitlar:
            projeler_listesi.append({
                "id": kayit[0],
                "proje_adi": kayit[1],
                "musteri": kayit[2],
                "lokasyon": kayit[3]
            })
            
        cur.close()
        conn.close()
        return {"projeler": projeler_listesi}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))