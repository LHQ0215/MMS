from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, datetime
from ..database import get_db
from ..models.appointment import Appointment, AppointmentStatus, TimeSlot
from ..models.patient import Patient
from ..models.doctor import Doctor
from ..models.department import Department
from ..models.user import User
from ..schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentResponse, AppointmentDetailResponse
from ..utils.security import get_current_user_id, get_current_role

router = APIRouter(prefix="/api/appointments", tags=["挂号预约"])

@router.post("/create")
def create_appointment(req: AppointmentCreate, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.user_id == user_id).first()
    if not patient:
        patient = Patient(user_id=user_id, gender="other")
        db.add(patient)
        db.commit()
        db.refresh(patient)
    doctor = db.query(Doctor).filter(Doctor.id == req.doctor_id).first()
    if not doctor or not doctor.is_approved:
        raise HTTPException(status_code=404, detail="医生不存在或未审核")
    existing = db.query(Appointment).filter(
        Appointment.doctor_id == req.doctor_id,
        Appointment.appointment_date == req.appointment_date,
        Appointment.time_slot == req.time_slot,
        Appointment.status.in_(["pending", "confirmed"])
    ).count()
    if existing >= doctor.max_daily_patients:
        raise HTTPException(status_code=400, detail="该时段号源已满")
    queue_num = existing + 1
    appt = Appointment(
        patient_id=patient.id, doctor_id=req.doctor_id,
        department_id=req.department_id, appointment_date=req.appointment_date,
        time_slot=req.time_slot, queue_number=queue_num,
        symptoms=req.symptoms
    )
    db.add(appt)
    db.commit()
    db.refresh(appt)
    return {"message": "挂号成功", "appointment_id": appt.id, "queue_number": queue_num}

@router.get("/my")
def get_my_appointments(
    status_filter: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(Patient.user_id == user_id).first()
    if not patient:
        return {"total": 0, "items": []}
    query = db.query(Appointment).filter(Appointment.patient_id == patient.id)
    if status_filter:
        query = query.filter(Appointment.status == status_filter)
    total = query.count()
    appts = query.order_by(Appointment.created_at.desc()).offset((page-1)*size).limit(size).all()
    result = []
    for a in appts:
        doc = db.query(Doctor).filter(Doctor.id == a.doctor_id).first()
        dept = db.query(Department).filter(Department.id == a.department_id).first()
        result.append({
            "id": a.id, "doctor_id": a.doctor_id,
            "doctor_name": doc.user.real_name if doc else "",
            "doctor_title": doc.title if doc else "",
            "department_name": dept.name if dept else "",
            "appointment_date": str(a.appointment_date),
            "time_slot": a.time_slot.value if hasattr(a.time_slot, "value") else a.time_slot,
            "queue_number": a.queue_number, "status": a.status.value if hasattr(a.status, "value") else a.status,
            "symptoms": a.symptoms, "created_at": a.created_at
        })
    return {"total": total, "items": result}

@router.get("/doctor")
def get_doctor_appointments(
    date_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    doctor = db.query(Doctor).filter(Doctor.user_id == user_id).first()
    if not doctor:
        raise HTTPException(status_code=400, detail="无医生权限")
    query = db.query(Appointment).filter(Appointment.doctor_id == doctor.id)
    if date_filter:
        query = query.filter(Appointment.appointment_date == date.fromisoformat(date_filter))
    if status_filter:
        query = query.filter(Appointment.status == status_filter)
    total = query.count()
    appts = query.order_by(Appointment.appointment_date, Appointment.time_slot, Appointment.queue_number).offset((page-1)*size).limit(size).all()
    result = []
    for a in appts:
        pat = db.query(Patient).filter(Patient.id == a.patient_id).first()
        result.append({
            "id": a.id, "patient_id": a.patient_id,
            "patient_name": pat.user.real_name if pat else "",
            "appointment_date": str(a.appointment_date),
            "time_slot": a.time_slot.value if hasattr(a.time_slot, "value") else a.time_slot,
            "queue_number": a.queue_number, "status": a.status.value if hasattr(a.status, "value") else a.status,
            "symptoms": a.symptoms, "created_at": a.created_at
        })
    return {"total": total, "items": result}

@router.put("/{appointment_id}/cancel")
def cancel_appointment(appointment_id: int, reason: str = "", user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="挂号记录不存在")
    if appt.status in ["completed", "cancelled", "missed"]:
        raise HTTPException(status_code=400, detail="当前状态不允许取消")
    appt.status = AppointmentStatus.CANCELLED
    appt.cancel_reason = reason
    db.commit()
    return {"message": "已取消挂号"}

@router.put("/{appointment_id}/status")
def update_appointment_status(appointment_id: int, req: AppointmentUpdate, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="挂号记录不存在")
    if req.status:
        appt.status = req.status
    if req.notes:
        appt.notes = req.notes
    db.commit()
    return {"message": "状态已更新"}

