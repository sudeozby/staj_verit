from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.db.session import get_db_session

router = APIRouter()

class MusteriBase(BaseModel):
    firma_adi: str
    vergi_no: Optional[str] = None
    sehir: Optional[str] = None
    yetkili_kisi: Optional[str] = None
    telefon: Optional[str] = None
    email: Optional[str] = None
    adres: Optional[str] = None

class MusteriDurum(BaseModel):
    aktif_mi: bool

@router.get("")
def musterileri_getir():
    with get_db_session() as cur:
        cur.execute("SELECT * FROM musteriler ORDER BY id DESC")
        return [dict(row) for row in cur.fetchall()]

@router.post("")
def musteri_ekle(musteri: MusteriBase, islem_yapan: str = Header(default="Sistem")):
    with get_db_session() as cur:
        cur.execute("""
            INSERT INTO musteriler (firma_adi, vergi_no, sehir, yetkili_kisi, telefon, email, adres)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, (musteri.firma_adi, musteri.vergi_no, musteri.sehir, musteri.yetkili_kisi, musteri.telefon, musteri.email, musteri.adres))
        yeni_id = cur.fetchone()['id']
        # İsteğe bağlı: Log tablosuna kayıt atılabilir
        return {"mesaj": "Müşteri başarıyla eklendi", "id": yeni_id}

@router.put("/{musteri_id}")
def musteri_guncelle(musteri_id: int, musteri: MusteriBase, islem_yapan: str = Header(default="Sistem")):
    with get_db_session() as cur:
        cur.execute("""
            UPDATE musteriler SET firma_adi=%s, vergi_no=%s, sehir=%s, yetkili_kisi=%s, telefon=%s, email=%s, adres=%s
            WHERE id=%s
        """, (musteri.firma_adi, musteri.vergi_no, musteri.sehir, musteri.yetkili_kisi, musteri.telefon, musteri.email, musteri.adres, musteri_id))
        return {"mesaj": "Müşteri bilgileri güncellendi"}

@router.put("/{musteri_id}/durum")
def musteri_durum_guncelle(musteri_id: int, durum: MusteriDurum, islem_yapan: str = Header(default="Sistem")):
    with get_db_session() as cur:
        cur.execute("UPDATE musteriler SET aktif_mi = %s WHERE id = %s", (durum.aktif_mi, musteri_id))
        return {"mesaj": "Müşteri durumu güncellendi"}

@router.get("/{musteri_id}/detay")
def musteri_detayi_getir(musteri_id: int):
    with get_db_session() as cur:
        cur.execute("SELECT * FROM musteriler WHERE id = %s", (musteri_id,))
        musteri = dict(cur.fetchone())
        if not musteri:
            raise HTTPException(status_code=404, detail="Müşteri bulunamadı")
        
        # Müşteriye ait projeleri bul
        cur.execute("SELECT id, proje_adi as ad, durum FROM projeler WHERE musteri = %s", (musteri['firma_adi'],))
        musteri['projeler'] = [dict(row) for row in cur.fetchall()]
        
        # Müşterinin projelerine ait revizyonları bul
        cur.execute("""
            SELECT r.* FROM revizyonlar r
            JOIN projeler p ON r.is_emri_id = p.id
            WHERE p.musteri = %s ORDER BY r.tarih DESC
        """, (musteri['firma_adi'],))
        musteri['revizyonlar'] = [dict(row) for row in cur.fetchall()]
        
        return musteri