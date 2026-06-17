from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models.user import User
from ..models.doctor import Doctor
from ..models.patient import Patient
from ..models.appointment import Appointment
from ..utils.security import check_role

router = APIRouter(prefix="/api/admin", tags=["管理功能"])

@router.get("/stats")
def get_admin_stats(
    _=Depends(check_role("admin")),
    db: Session = Depends(get_db)
):
    user_count = db.query(func.count(User.id)).scalar() or 0
    doctor_count = db.query(func.count(Doctor.id)).scalar() or 0
    patient_count = db.query(func.count(Patient.id)).scalar() or 0
    appt_count = db.query(func.count(Appointment.id)).scalar() or 0
    pending_doctor = db.query(func.count(Doctor.id)).filter(Doctor.is_approved == False).scalar() or 0
    today_appts = db.query(func.count(Appointment.id)).filter(
        func.date(Appointment.appointment_date) == func.current_date()
    ).scalar() or 0
    return {
        "user_count": user_count, "doctor_count": doctor_count,
        "patient_count": patient_count, "appointment_count": appt_count,
        "pending_doctor_count": pending_doctor, "today_appointment_count": today_appts
    }

@router.get("/recent-activities")
def get_recent_activities(
    _=Depends(check_role("admin")),
    db: Session = Depends(get_db)
):
    recent_users = db.query(User).order_by(User.created_at.desc()).limit(10).all()
    return {
        "recent_users": [{"id": u.id, "username": u.username, "real_name": u.real_name,
                          "role": u.role.value if hasattr(u.role, "value") else u.role,
                          "created_at": str(u.created_at)} for u in recent_users]
    }
