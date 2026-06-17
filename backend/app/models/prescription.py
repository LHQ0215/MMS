from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    record_id = Column(Integer, ForeignKey("diagnosis_records.id"), nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicines.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    dosage = Column(String(100), nullable=False, comment="用量")
    frequency = Column(String(100), nullable=False, comment="频次")
    duration = Column(String(100), nullable=False, comment="疗程")
    route = Column(String(50), nullable=False, default="口服")
    quantity = Column(Integer, nullable=False, comment="数量")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    record = relationship("DiagnosisRecord", backref="prescriptions")
    medicine = relationship("Medicine", backref="prescriptions")
    doctor = relationship("Doctor", backref="prescriptions")
    patient = relationship("Patient", backref="prescriptions")
