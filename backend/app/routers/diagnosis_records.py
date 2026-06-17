from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..models.diagnosis_record import DiagnosisRecord
from ..models.appointment import Appointment, AppointmentStatus
from ..models.patient import Patient
from ..models.doctor import Doctor
from ..schemas.diagnosis_record import DiagnosisRecordCreate, DiagnosisRecordUpdate, DiagnosisRecordResponse
from ..utils.security import get_current_user_id

router = APIRouter(prefix="/api/diagnosis", tags=["诊疗记录"])

@router.post("/create")
def create_diagnosis(req: DiagnosisRecordCreate, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.user_id == user_id).first()
    if not doctor:
        raise HTTPException(status_code=403, detail="仅医生可创建诊疗记录")
    appt = db.query(Appointment).filter(Appointment.id == req.appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="挂号记录不存在")
    record = DiagnosisRecord(
        appointment_id=req.appointment_id, patient_id=appt.patient_id,
        doctor_id=doctor.id, chief_complaint=req.chief_complaint,
        present_illness=req.present_illness, physical_examination=req.physical_examination,
        diagnosis=req.diagnosis, treatment_plan=req.treatment_plan,
        notes=req.notes, follow_up_date=req.follow_up_date
    )
    db.add(record)
    appt.status = AppointmentStatus.COMPLETED
    db.commit()
    db.refresh(record)
    return {"message": "诊疗记录已创建", "record_id": record.id}

@router.get("/my")
def get_my_records(page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100),
                   user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.user_id == user_id).first()
    if not patient:
        return {"total": 0, "items": []}
    query = db.query(DiagnosisRecord).filter(DiagnosisRecord.patient_id == patient.id)
    total = query.count()
    records = query.order_by(DiagnosisRecord.created_at.desc()).offset((page-1)*size).limit(size).all()
    result = []
    for r in records:
        doc = db.query(Doctor).filter(Doctor.id == r.doctor_id).first()
        result.append({
            "id": r.id, "diagnosis": r.diagnosis,
            "doctor_name": doc.user.real_name if doc else "",
            "treatment_plan": r.treatment_plan,
            "follow_up_date": str(r.follow_up_date) if r.follow_up_date else None,
            "created_at": r.created_at
        })
    return {"total": total, "items": result}



@router.get("/doctor")
def get_doctor_records(page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=200),
                       user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.user_id == user_id).first()
    if not doctor:
        raise HTTPException(status_code=403, detail="无医生权限")
    query = db.query(DiagnosisRecord).filter(DiagnosisRecord.doctor_id == doctor.id)
    total = query.count()
    records = query.order_by(DiagnosisRecord.created_at.desc()).offset((page-1)*size).limit(size).all()
    result = []
    for r in records:
        pat = db.query(Patient).filter(Patient.id == r.patient_id).first()
        result.append({
            "id": r.id, "diagnosis": r.diagnosis,
            "patient_name": pat.user.real_name if pat else "",
            "chief_complaint": r.chief_complaint,
            "treatment_plan": r.treatment_plan,
            "follow_up_date": str(r.follow_up_date) if r.follow_up_date else None,
            "created_at": r.created_at
        })
    return {"total": total, "items": result}


@router.get("/{record_id}")
def get_record(record_id: int, db: Session = Depends(get_db)):
    record = db.query(DiagnosisRecord).filter(DiagnosisRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    doc = db.query(Doctor).filter(Doctor.id == record.doctor_id).first()
    pat = db.query(Patient).filter(Patient.id == record.patient_id).first()
    return {
        "id": record.id, "diagnosis": record.diagnosis,
        "chief_complaint": record.chief_complaint,
        "present_illness": record.present_illness,
        "physical_examination": record.physical_examination,
        "treatment_plan": record.treatment_plan,
        "notes": record.notes, "follow_up_date": str(record.follow_up_date) if record.follow_up_date else None,
        "doctor_name": doc.user.real_name if doc else "",
        "doctor_title": doc.title if doc else "",
        "patient_name": pat.user.real_name if pat else "",
        "created_at": record.created_at
    }
