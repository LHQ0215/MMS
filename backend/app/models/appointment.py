from sqlalchemy import Column, Integer, String, Enum, DateTime, Date, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base
import enum

class TimeSlot(str, enum.Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"

class AppointmentStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    MISSED = "missed"

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    appointment_date = Column(Date, nullable=False, index=True)
    time_slot = Column(Enum(TimeSlot), nullable=False)
    queue_number = Column(Integer, nullable=False)
    status = Column(Enum(AppointmentStatus), nullable=False, default=AppointmentStatus.PENDING)
    symptoms = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    cancel_reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    patient = relationship("Patient", backref="appointments")
    doctor = relationship("Doctor", backref="appointments")
    department = relationship("Department", backref="appointments")
