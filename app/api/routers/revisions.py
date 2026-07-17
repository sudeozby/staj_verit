from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from app.db.session import get_db_session

router = APIRouter()

# YENİ: Backend artık sadece id'yi değil, hangi pano olduğunu da (pano_turu) bekliyor!
class RevizyonTalep(BaseModel):
    is_emri_id: int
    pano_turu: str 
    revizyon_notu: str
    dosya_adi: str

@router.get("")
def revizyonlari_getir():
    with get_db_session() as cur:
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
        # Hangi pano olduğunu veritabanı tablosuna şık bir şekilde not olarak ekliyoruz
        zengin_not = f"[{talep.pano_turu}] - {talep.revizyon_notu}"
        
        cur.execute("""
            INSERT INTO revizyonlar (is_emri_id, dosya_adi, talep_eden, revizyon_notu, durum)
            VALUES (%s, %s, %s, %s, 'ONAY_BEKLIYOR')
        """, (talep.is_emri_id, talep.dosya_adi, islem_yapan, zengin_not))
        
        # İŞTE KİLİT NOKTA: Bütün projeyi değil, SADECE seçilen panoyu (Örn: MCC) kilitliyoruz!
        cur.execute("""
            UPDATE proje_pano_listesi 
            SET durum = 'REVIZYONDA' 
            WHERE proje_id = %s AND pano_turu = %s AND (durum != 'TAMAMLANDI' OR durum IS NULL)
        """, (talep.is_emri_id, talep.pano_turu))
        
        return {"mesaj": "Revizyon talebi oluşturuldu ve ilgili pano kilitlendi"}

@router.put("/{revizyon_id}/onayla")
def revizyon_onayla(revizyon_id: int, islem_yapan: str = Header(default="Sistem")):
    with get_db_session() as cur:
        cur.execute("UPDATE revizyonlar SET durum = 'ONAYLANDI' WHERE id = %s RETURNING is_emri_id", (revizyon_id,))
        is_emri_id = cur.fetchone()['is_emri_id']
        
        # Sadece REVIZYONDA olan (yani kilitlenmiş olan o tekil) panonun kilidini aç
        cur.execute("UPDATE proje_pano_listesi SET durum = 'YENİ' WHERE proje_id = %s AND durum = 'REVIZYONDA'", (is_emri_id,))
        return {"mesaj": "Revizyon onaylandı"}

@router.put("/{revizyon_id}/reddet")
def revizyon_reddet(revizyon_id: int, islem_yapan: str = Header(default="Sistem")):
    with get_db_session() as cur:
        cur.execute("UPDATE revizyonlar SET durum = 'REDDEDILDI' WHERE id = %s RETURNING is_emri_id", (revizyon_id,))
        is_emri_id = cur.fetchone()['is_emri_id']
        
        # Sadece REVIZYONDA olan panonun kilidini aç
        cur.execute("UPDATE proje_pano_listesi SET durum = 'YENİ' WHERE proje_id = %s AND durum = 'REVIZYONDA'", (is_emri_id,))
        return {"mesaj": "Revizyon reddedildi"}