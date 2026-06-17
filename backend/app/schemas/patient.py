from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

class PatientBase(BaseModel):
    gender: str = Field(..., pattern="^(male|female|other)$")
    birth_date: Optional[date] = None
    id_card: Optional[str] = None
    address: Optional[str] = None
    blood_type: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    allergies: Optional[str] = None
    medical_history: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    address: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    allergies: Optional[str] = None
    medical_history: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None

class PatientResponse(PatientBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
