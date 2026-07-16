from fastapi import APIRouter, Header
from pydantic import BaseModel
from typing import Optional
from app.db.session import get_db_session

router = APIRouter()

class IskontoGrup(BaseModel):
    grup_adi: str
    maliyet_iskonto: float = 0.0
    proje_iskonto: float = 0.0
    satis_iskonto: float = 0.0
    notlar: Optional[str] = None

@router.get("")
def iskonto_gruplari_getir():
    with get_db_session() as cur:
        cur.execute("SELECT * FROM iskonto_gruplari ORDER BY id ASC")
        return [dict(r) for r in cur.fetchall()]

@router.post("")
def iskonto_grubu_ekle(veri: IskontoGrup, islem_yapan: str = Header(default="Sistem")):
    with get_db_session() as cur:
        cur.execute("""
            INSERT INTO iskonto_gruplari (grup_adi, maliyet_iskonto, proje_iskonto, satis_iskonto, notlar)
            VALUES (%s, %s, %s, %s, %s)
        """, (veri.grup_adi, veri.maliyet_iskonto, veri.proje_iskonto, veri.satis_iskonto, veri.notlar))
        return {"mesaj": "İskonto kuralı başarıyla tanımlandı"}