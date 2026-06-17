from sqlalchemy import Column, Integer, String, Enum, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base
import enum

class NotifType(str, enum.Enum):
    APPOINTMENT = "appointment"
    DIAGNOSIS = "diagnosis"
    PRESCRIPTION = "prescription"
    SYSTEM = "system"
    REMINDER = "reminder"

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    type = Column(Enum(NotifType), nullable=False, default=NotifType.SYSTEM)
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    user = relationship("User", backref="notifications")
