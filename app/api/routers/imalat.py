from fastapi import APIRouter
from app.db.session import get_db_session

router = APIRouter()

@router.get("/is-emirleri")
def is_emirleri_getir():
    with get_db_session() as cur:
        cur.execute("SELECT id, proje_adi, durum, musteri FROM projeler ORDER BY id DESC")
        return [dict(r) for r in cur.fetchall()]

@router.get("/is-emirleri/aktif")
def aktif_is_emirleri():
    with get_db_session() as cur:
        # Sahada revizyon başlatabilmek için sadece bitmemiş projeleri çekiyoruz
        cur.execute("SELECT id, proje_adi, 'Genel Pano' as pano_turu FROM projeler WHERE durum != 'TAMAMLANDI'")
        return [dict(r) for r in cur.fetchall()]