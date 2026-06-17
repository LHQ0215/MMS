from ..models.user import User
from ..models.operation_log import OperationLog, LogStatus
from ..utils.security import get_password_hash
from sqlalchemy.orm import Session

def create_user(db: Session, username: str, password: str, real_name: str, role: str = "patient"):
    user = User(
        username=username,
        password_hash=get_password_hash(password),
        real_name=real_name,
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def log_operation(db: Session, user_id: int, username: str, action: str,
                  target_type: str = None, target_id: int = None,
                  detail: str = None, ip: str = None, status: str = "success"):
    log = OperationLog(
        user_id=user_id, username=username, action=action,
        target_type=target_type, target_id=target_id,
        detail=detail, ip_address=ip,
        status=LogStatus.SUCCESS if status == "success" else LogStatus.FAILURE
    )
    db.add(log)
    db.commit()
