from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class DiagnosisRecordBase(BaseModel):
    chief_complaint: Optional[str] = None
    present_illness: Optional[str] = None
    physical_examination: Optional[str] = None
    diagnosis: str
    treatment_plan: Optional[str] = None
    notes: Optional[str] = None
    follow_up_date: Optional[date] = None

class DiagnosisRecordCreate(DiagnosisRecordBase):
    appointment_id: int

class DiagnosisRecordUpdate(BaseModel):
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None
    notes: Optional[str] = None
    follow_up_date: Optional[date] = None

class DiagnosisRecordResponse(DiagnosisRecordBase):
    id: int
    appointment_id: int
    patient_id: int
    doctor_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
