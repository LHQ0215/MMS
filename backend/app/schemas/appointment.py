from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class AppointmentBase(BaseModel):
    doctor_id: int
    department_id: int
    appointment_date: date
    time_slot: str  # morning, afternoon, evening
    symptoms: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    cancel_reason: Optional[str] = None

class AppointmentResponse(AppointmentBase):
    id: int
    patient_id: int
    queue_number: int
    status: str
    notes: Optional[str] = None
    cancel_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class AppointmentDetailResponse(AppointmentResponse):
    patient_name: str = ""
    doctor_name: str = ""
    doctor_title: str = ""
    department_name: str = ""
