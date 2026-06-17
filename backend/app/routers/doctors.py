from fastapi import APIRouter, Depends, HTTPException, status, Query

from sqlalchemy.orm import Session

from typing import Optional

from ..database import get_db

from ..models.doctor import Doctor

from ..models.user import User

from ..models.department import Department

from ..schemas.doctor import DoctorCreate, DoctorUpdate, DoctorResponse, DoctorWithUserResponse

from ..utils.security import get_current_user_id, get_current_role, check_role



router = APIRouter(prefix="/api/doctors", tags=["医生管理"])



@router.get("/profile", response_model=DoctorWithUserResponse)

def get_my_doctor_profile(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):

    doctor = db.query(Doctor).filter(Doctor.user_id == user_id).first()

    if not doctor:

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="医生资料未找到，请先注册医师信息")

    dept = db.query(Department).filter(Department.id == doctor.department_id).first()

    return DoctorWithUserResponse(

        id=doctor.id, user_id=doctor.user_id,

        title=doctor.title, specialization=doctor.specialization,

        department_id=doctor.department_id, license_number=doctor.license_number,

        consultation_fee=doctor.consultation_fee, max_daily_patients=doctor.max_daily_patients,

        introduction=doctor.introduction, is_approved=doctor.is_approved,

        created_at=doctor.created_at, updated_at=doctor.updated_at,

        username=doctor.user.username, real_name=doctor.user.real_name,

        phone=doctor.user.phone or "", email=doctor.user.email or "",

        department_name=dept.name if dept else ""

    )



@router.put("/profile")

def update_doctor_profile(req: DoctorUpdate, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):

    doctor = db.query(Doctor).filter(Doctor.user_id == user_id).first()

    if not doctor:

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="医生资料不存在")

    for key, value in req.dict(exclude_unset=True).items():

        setattr(doctor, key, value)

    db.commit()

    return {"message": "更新成功"}



@router.get("/list")

def list_doctors(

    department_id: Optional[int] = None,

    page: int = Query(1, ge=1),

    size: int = Query(20, ge=1, le=100),

    db: Session = Depends(get_db)

):

    query = db.query(Doctor)

    if department_id:

        query = query.filter(Doctor.department_id == department_id)

    total = query.count()

    doctors = query.offset((page - 1) * size).limit(size).all()

    result = []

    for d in doctors:

        dept = db.query(Department).filter(Department.id == d.department_id).first()

        result.append({

            "id": d.id, "user_id": d.user_id, "title": d.title,

            "specialization": d.specialization, "department_id": d.department_id,

            "department_name": dept.name if dept else "",

            "consultation_fee": float(d.consultation_fee),

            "max_daily_patients": d.max_daily_patients,

            "introduction": d.introduction,
            "is_approved": d.is_approved,
            "email": d.user.email or "",

            "real_name": d.user.real_name, "phone": d.user.phone

        })

    return {"total": total, "items": result}



@router.get("/{doctor_id}", response_model=DoctorWithUserResponse)

def get_doctor(doctor_id: int, db: Session = Depends(get_db)):

    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()

    if not doctor:

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="医生不存在")

    dept = db.query(Department).filter(Department.id == doctor.department_id).first()

    return DoctorWithUserResponse(

        id=doctor.id, user_id=doctor.user_id,

        title=doctor.title, specialization=doctor.specialization,

        department_id=doctor.department_id, license_number=doctor.license_number,

        consultation_fee=doctor.consultation_fee, max_daily_patients=doctor.max_daily_patients,

        introduction=doctor.introduction, is_approved=doctor.is_approved,

        created_at=doctor.created_at, updated_at=doctor.updated_at,

        username=doctor.user.username, real_name=doctor.user.real_name,

        phone=doctor.user.phone or "", email=doctor.user.email or "",

        department_name=dept.name if dept else ""

    )



@router.post("/register")

def register_doctor(req: DoctorCreate, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):

    existing = db.query(Doctor).filter(Doctor.user_id == user_id).first()

    if existing:

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="已注册医师信息已存在")

    doctor = Doctor(user_id=user_id, is_approved=True, **req.dict())

    db.add(doctor)

    db.commit()

    return {"message": "医师注册成功，等待管理员审核"}



@router.put("/{doctor_id}/approve")

def approve_doctor(doctor_id: int, _=Depends(check_role("admin")), db: Session = Depends(get_db)):

    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()

    if not doctor:

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="医生不存在")

    doctor.is_approved = not doctor.is_approved

    db.commit()

    return {"message": "审核状态已更新", "is_approved": doctor.is_approved}

