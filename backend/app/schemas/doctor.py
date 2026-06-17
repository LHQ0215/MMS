from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DoctorBase(BaseModel):
    title: str
    specialization: Optional[str] = None
    department_id: int
    license_number: str
    consultation_fee: float = 0
    max_daily_patients: int = 30
    introduction: Optional[str] = None

class DoctorCreate(DoctorBase):
    pass

class DoctorUpdate(BaseModel):
    title: Optional[str] = None
    specialization: Optional[str] = None
    department_id: Optional[int] = None
    consultation_fee: Optional[float] = None
    max_daily_patients: Optional[int] = None
    introduction: Optional[str] = None

class DoctorResponse(DoctorBase):
    id: int
    user_id: int
    is_approved: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class DoctorWithUserResponse(DoctorResponse):
    username: str = ""
    real_name: str = ""
    phone: str = ""
    email: str = ""
    department_name: str = ""
