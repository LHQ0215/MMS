from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..models.patient import Patient
from ..models.user import User
from ..schemas.patient import PatientCreate, PatientUpdate, PatientResponse
from ..utils.security import get_current_user_id, get_current_role

router = APIRouter(prefix="/api/patients", tags=["患者管理"])

@router.get("/profile", response_model=PatientResponse)
def get_my_profile(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.user_id == user_id).first()
    if not patient:
        patient = Patient(user_id=user_id, gender="other")
        db.add(patient)
        db.commit()
        db.refresh(patient)
    return patient

@router.put("/profile")
def update_my_profile(req: PatientUpdate, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.user_id == user_id).first()
    if not patient:
        patient = Patient(user_id=user_id, gender="other")
        db.add(patient)
        db.commit()
        db.refresh(patient)
    for key, value in req.dict(exclude_unset=True).items():
        setattr(patient, key, value)
    db.commit()
    return {"message": "更新成功"}

@router.get("/list")
def list_patients(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Patient)
    if keyword:
        query = query.join(User).filter(
            User.real_name.contains(keyword) | User.username.contains(keyword)
        )
    total = query.count()
    patients = query.offset((page - 1) * size).limit(size).all()
    result = []
    for p in patients:
        result.append({
            "id": p.id, "user_id": p.user_id, "gender": p.gender,
            "real_name": p.user.real_name, "phone": p.user.phone,
            "birth_date": p.birth_date, "allergies": p.allergies,
            "created_at": p.created_at
        })
    return {"total": total, "items": result}

@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="患者不存在")
    return patient

@router.put("/{patient_id}")
def update_patient(
    patient_id: int,
    req: PatientUpdate,
    db: Session = Depends(get_db)
):
    """Update patient info by patient ID (admin/doctor)."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="患者不存在")
    for key, value in req.dict(exclude_unset=True).items():
        setattr(patient, key, value)
    db.commit()
    return {"message": "更新成功"}

@router.get("/stats/summary")
def get_patient_stats(db: Session = Depends(get_db)):
    """Get patient statistics."""
    from sqlalchemy import func
    total = db.query(func.count(Patient.id)).scalar() or 0
    male = db.query(func.count(Patient.id)).filter(Patient.gender == "male").scalar() or 0
    female = db.query(func.count(Patient.id)).filter(Patient.gender == "female").scalar() or 0
    return {"total": total, "male": male, "female": female, "other": total - male - female}
