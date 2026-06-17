from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.prescription import Prescription
from ..models.doctor import Doctor
from ..models.medicine import Medicine
from ..schemas.prescription import PrescriptionCreate, PrescriptionResponse, PrescriptionDetailResponse
from ..utils.security import get_current_user_id

router = APIRouter(prefix="/api/prescriptions", tags=["处方管理"])

@router.post("/create")
def create_prescription(req: PrescriptionCreate, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.user_id == user_id).first()
    if not doctor:
        raise HTTPException(status_code=403, detail="仅医生可开处方")
    med = db.query(Medicine).filter(Medicine.id == req.medicine_id).first()
    if not med or med.stock < req.quantity:
        raise HTTPException(status_code=400, detail="药品库存不足")
    presc = Prescription(
        record_id=req.record_id, medicine_id=req.medicine_id,
        doctor_id=doctor.id, patient_id=0,
        dosage=req.dosage, frequency=req.frequency,
        duration=req.duration, route=req.route,
        quantity=req.quantity, notes=req.notes
    )
    from ..models.diagnosis_record import DiagnosisRecord
    diag = db.query(DiagnosisRecord).filter(DiagnosisRecord.id == req.record_id).first()
    if diag:
        presc.patient_id = diag.patient_id
    med.stock -= req.quantity
    db.add(presc)
    db.commit()
    return {"message": "处方已创建", "prescription_id": presc.id}

@router.get("/record/{record_id}")
def get_record_prescriptions(record_id: int, db: Session = Depends(get_db)):
    prescs = db.query(Prescription).filter(Prescription.record_id == record_id).all()
    result = []
    for p in prescs:
        med = db.query(Medicine).filter(Medicine.id == p.medicine_id).first()
        result.append({
            "id": p.id, "medicine_name": med.name if med else "",
            "medicine_spec": med.specification if med else "",
            "dosage": p.dosage, "frequency": p.frequency,
            "duration": p.duration, "route": p.route,
            "quantity": p.quantity, "notes": p.notes,
            "created_at": p.created_at
        })
    return {"items": result}
