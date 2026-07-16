from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from app.db.session import get_db_session

router = APIRouter()

class RevizyonTalep(BaseModel):
    is_emri_id: int
    revizyon_notu: str
    dosya_adi: str

@router.get("")
def revizyonlari_getir():
    with get_db_session() as cur:
        # Revizyon tablosu ile Projeler tablosunu birleştirip frontend'in beklediği formatı sunuyoruz
        cur.execute("""
            SELECT r.id, r.is_emri_id, r.dosya_adi, r.talep_eden, r.tarih, r.revizyon_notu, r.durum, 
                   p.proje_adi, 'Pano' as pano_turu 
            FROM revizyonlar r
            JOIN projeler p ON r.is_emri_id = p.id
            ORDER BY r.tarih DESC
        """)
        return [dict(row) for row in cur.fetchall()]

@router.post("/talep-et")
def revizyon_talep_et(talep: RevizyonTalep, islem_yapan: str = Header(default="Sistem")):
    with get_db_session() as cur:
        # 1. Revizyonu kaydet
        cur.execute("""
            INSERT INTO revizyonlar (is_emri_id, dosya_adi, talep_eden, revizyon_notu, durum)
            VALUES (%s, %s, %s, %s, 'ONAY_BEKLIYOR')
        """, (talep.is_emri_id, talep.dosya_adi, islem_yapan, talep.revizyon_notu))
        
        # 2. İş emrinin (Projenin) durumunu revizyona alarak sahada kilitle
        cur.execute("UPDATE projeler SET durum = 'REVIZYONDA' WHERE id = %s", (talep.is_emri_id,))
        return {"mesaj": "Revizyon talebi oluşturuldu ve saha kilitlendi"}

@router.put("/{revizyon_id}/onayla")
def revizyon_onayla(revizyon_id: int, islem_yapan: str = Header(default="Sistem")):
    with get_db_session() as cur:
        cur.execute("UPDATE revizyonlar SET durum = 'ONAYLANDI' WHERE id = %s RETURNING is_emri_id", (revizyon_id,))
        is_emri_id = cur.fetchone()['is_emri_id']
        # Projeyi tekrar montaja/imalata aç
        cur.execute("UPDATE projeler SET durum = 'MONTAJDA' WHERE id = %s", (is_emri_id,))
        return {"mesaj": "Revizyon onaylandı"}

@router.put("/{revizyon_id}/reddet")
def revizyon_reddet(revizyon_id: int, islem_yapan: str = Header(default="Sistem")):
    with get_db_session() as cur:
        cur.execute("UPDATE revizyonlar SET durum = 'REDDEDILDI' WHERE id = %s RETURNING is_emri_id", (revizyon_id,))
        is_emri_id = cur.fetchone()['is_emri_id']
        # Projeyi eski haline getir
        cur.execute("UPDATE projeler SET durum = 'MONTAJDA' WHERE id = %s", (is_emri_id,))
        return {"mesaj": "Revizyon reddedildi"}