from ..models.notification import Notification, NotifType
from sqlalchemy.orm import Session

def send_notification(db: Session, user_id: int, title: str, content: str,
                      notif_type: str = "system"):
    n = Notification(
        user_id=user_id, title=title, content=content,
        type=notif_type
    )
    db.add(n)
    db.commit()
    return n

def get_unread_count(db: Session, user_id: int) -> int:
    return db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).count()
