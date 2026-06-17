from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AIConsultationCreate(BaseModel):
    symptoms: str
    symptom_duration: Optional[str] = None
    severity: str = "mild"

class AIConsultationResponse(BaseModel):
    id: int
    patient_id: int
    symptoms: str
    symptom_duration: Optional[str] = None
    severity: str
    ai_diagnosis: Optional[str] = None
    confidence: Optional[float] = None
    suggested_department: Optional[str] = None
    risk_level: str
    advice: Optional[str] = None
    is_referred: bool
    created_at: datetime

    class Config:
        orm_mode = True
