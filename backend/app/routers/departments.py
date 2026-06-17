from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.department import Department
from ..schemas.department import DepartmentResponse

router = APIRouter(prefix="/api/departments", tags=["科室管理"])

@router.get("/list")
def list_departments(db: Session = Depends(get_db)):
    depts = db.query(Department).filter(Department.is_active == True).all()
    result = []
    for d in depts:
        child_count = db.query(Department).filter(Department.parent_id == d.id).count()
        result.append({
            "id": d.id, "name": d.name, "description": d.description,
            "location": d.location, "parent_id": d.parent_id,
            "child_count": child_count
        })
    return {"items": result}

@router.get("/{dept_id}", response_model=DepartmentResponse)
def get_department(dept_id: int, db: Session = Depends(get_db)):
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="科室不存在")
    return dept
