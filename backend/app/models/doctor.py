from sqlalchemy import Column, Integer, String, Enum, DateTime, Text, DECIMAL, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    title = Column(String(50), nullable=False, comment="职称")
    specialization = Column(String(200), nullable=True, comment="专业特长")
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    license_number = Column(String(50), unique=True, nullable=False, comment="执业证号")
    consultation_fee = Column(DECIMAL(10, 2), nullable=False, default=0)
    max_daily_patients = Column(Integer, nullable=False, default=30)
    introduction = Column(Text, nullable=True)
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", backref="doctor_profile")
    department = relationship("Department", backref="doctors")
