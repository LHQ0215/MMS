from sqlalchemy import Column, Integer, String, DateTime, Date, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class DiagnosisRecord(Base):
    __tablename__ = "diagnosis_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), unique=True, nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    chief_complaint = Column(Text, nullable=True, comment="主诉")
    present_illness = Column(Text, nullable=True, comment="现病史")
    physical_examination = Column(Text, nullable=True, comment="体格检查")
    diagnosis = Column(Text, nullable=False, comment="诊断结果")
    treatment_plan = Column(Text, nullable=True, comment="治疗方案")
    notes = Column(Text, nullable=True, comment="医生备注")
    follow_up_date = Column(Date, nullable=True, comment="复诊日期")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    appointment = relationship("Appointment", backref="diagnosis_record")
    patient = relationship("Patient", backref="diagnosis_records")
    doctor = relationship("Doctor", backref="diagnosis_records")
