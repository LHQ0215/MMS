from typing import List
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    type: str
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        orm_mode = True

class NotificationListResponse(BaseModel):
    total: int
    unread_count: int
    items: List[NotificationResponse]

