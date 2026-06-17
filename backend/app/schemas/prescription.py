from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PrescriptionCreate(BaseModel):
    record_id: int
    medicine_id: int
    dosage: str
    frequency: str
    duration: str
    route: str = "口服"
    quantity: int
    notes: Optional[str] = None

class PrescriptionResponse(BaseModel):
    id: int
    record_id: int
    medicine_id: int
    doctor_id: int
    patient_id: int
    dosage: str
    frequency: str
    duration: str
    route: str
    quantity: int
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True

class PrescriptionDetailResponse(PrescriptionResponse):
    medicine_name: str = ""
    medicine_spec: str = ""
    doctor_name: str = ""
