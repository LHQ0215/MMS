from sqlalchemy import Column, Integer, String, Enum, DateTime, Text
from sqlalchemy.sql import func
from ..database import Base
import enum

class LogStatus(str, enum.Enum):
    SUCCESS = "success"
    FAILURE = "failure"

class OperationLog(Base):
    __tablename__ = "operation_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=True)
    username = Column(String(50), nullable=True)
    action = Column(String(50), nullable=False)
    target_type = Column(String(50), nullable=True)
    target_id = Column(Integer, nullable=True)
    detail = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    status = Column(Enum(LogStatus), nullable=False, default=LogStatus.SUCCESS)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
