from sqlalchemy import Column, Integer, String, Enum, DateTime, Date, Text, DECIMAL, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base
import enum

class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    birth_date = Column(Date, nullable=True)
    id_card = Column(String(18), unique=True, nullable=True)
    address = Column(String(255), nullable=True)
    blood_type = Column(String(5), nullable=True)
    height = Column(DECIMAL(5, 2), nullable=True)
    weight = Column(DECIMAL(5, 2), nullable=True)
    allergies = Column(Text, nullable=True, comment="过敏史")
    medical_history = Column(Text, nullable=True, comment="既往病史")
    emergency_contact = Column(String(50), nullable=True)
    emergency_phone = Column(String(20), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", backref="patient_profile")
