from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MedicineBase(BaseModel):
    name: str
    generic_name: Optional[str] = None
    category: Optional[str] = None
    specification: Optional[str] = None
    manufacturer: Optional[str] = None
    unit: str
    price: float
    stock: int = 0
    requires_prescription: bool = True
    description: Optional[str] = None

class MedicineCreate(MedicineBase):
    pass

class MedicineUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class MedicineResponse(MedicineBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
