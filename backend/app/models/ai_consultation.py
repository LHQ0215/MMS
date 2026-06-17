from sqlalchemy import Column, Integer, String, Enum, DateTime, Text, DECIMAL, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base
import enum

class Severity(str, enum.Enum):
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"

class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EMERGENCY = "emergency"

class AIConsultation(Base):
    __tablename__ = "ai_consultations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    symptoms = Column(Text, nullable=False)
    symptom_duration = Column(String(100), nullable=True)
    severity = Column(Enum(Severity), nullable=False, default=Severity.MILD)
    ai_diagnosis = Column(Text, nullable=True)
    confidence = Column(DECIMAL(5, 2), nullable=True)
    suggested_department = Column(String(100), nullable=True)
    suggested_doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=True)
    risk_level = Column(Enum(RiskLevel), nullable=False, default=RiskLevel.LOW)
    advice = Column(Text, nullable=True)
    is_referred = Column(Boolean, default=False)
    referred_appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    patient = relationship("Patient", backref="ai_consultations")
    suggested_doctor = relationship("Doctor", backref="ai_referrals")
