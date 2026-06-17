from sqlalchemy import Column, Integer, String, DateTime, Text, DECIMAL, Boolean
from sqlalchemy.sql import func
from ..database import Base

class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    generic_name = Column(String(100), nullable=True)
    category = Column(String(50), nullable=True)
    specification = Column(String(100), nullable=True)
    manufacturer = Column(String(100), nullable=True)
    unit = Column(String(10), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    requires_prescription = Column(Boolean, default=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
