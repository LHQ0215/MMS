from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..models.medicine import Medicine
from ..schemas.medicine import MedicineResponse

router = APIRouter(prefix="/api/medicines", tags=["药品管理"])

@router.get("/list")
def list_medicines(
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Medicine).filter(Medicine.is_active == True)
    if category:
        query = query.filter(Medicine.category == category)
    if keyword:
        query = query.filter(Medicine.name.contains(keyword) | Medicine.generic_name.contains(keyword))
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    return {"total": total, "items": items}
