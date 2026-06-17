from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.notification import Notification
from ..schemas.notification import NotificationResponse, NotificationListResponse
from ..utils.security import get_current_user_id
from ..services.notification_service import get_unread_count

router = APIRouter(prefix="/api/notifications", tags=["通知管理"])

@router.get("/list")
def list_notifications(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    query = db.query(Notification).filter(Notification.user_id == user_id)
    total = query.count()
    unread = get_unread_count(db, user_id)
    items = query.order_by(Notification.created_at.desc()).offset((page-1)*size).limit(size).all()
    result = []
    for n in items:
        result.append({
            "id": n.id, "user_id": n.user_id, "title": n.title,
            "content": n.content, "type": n.type.value if hasattr(n.type, "value") else n.type,
            "is_read": n.is_read, "read_at": n.read_at, "created_at": n.created_at
        })
    return {"total": total, "unread_count": unread, "items": result}

@router.put("/{notification_id}/read")
def mark_as_read(
    notification_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    n = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == user_id).first()
    if not n:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="通知不存在")
    n.is_read = True
    n.read_at = __import__("datetime").datetime.utcnow()
    db.commit()
    return {"message": "已标记为已读"}

@router.put("/read-all")
def mark_all_as_read(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    db.query(Notification).filter(Notification.user_id == user_id, Notification.is_read == False).update(
        {"is_read": True, "read_at": __import__("datetime").datetime.utcnow()}
    )
    db.commit()
    return {"message": "全部标记为已读"}
