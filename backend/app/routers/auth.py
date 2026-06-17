from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from ..database import get_db
from ..models.user import User
from ..schemas.auth import LoginRequest, RegisterRequest, TokenResponse, PasswordChangeRequest
from ..utils.security import verify_password, get_password_hash, create_access_token, get_current_user_id, get_current_username, get_current_role
from ..config import settings

router = APIRouter(prefix="/api/auth", tags=["认证管理"])

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账户已被禁用")
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "role": user.role}
    )
    user.last_login = __import__("datetime").datetime.utcnow()
    db.commit()
    return TokenResponse(
        access_token=access_token,
        user_id=user.id,
        username=user.username,
        role=user.role,
        real_name=user.real_name
    )

@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == req.username).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")
    user = User(
        username=req.username,
        password_hash=get_password_hash(req.password),
        real_name=req.real_name,
        role=req.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "role": user.role}
    )
    return TokenResponse(
        access_token=access_token,
        user_id=user.id,
        username=user.username,
        role=user.role,
        real_name=user.real_name
    )

@router.put("/password")
def change_password(req: PasswordChangeRequest, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not verify_password(req.old_password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="原密码错误")
    user.password_hash = get_password_hash(req.new_password)
    db.commit()
    return {"message": "密码修改成功"}

@router.get("/check")
def check_token_valid(user_id: int = Depends(get_current_user_id)):
    """Check if the current token is still valid."""
    return {"valid": True, "user_id": user_id}

@router.post("/refresh")
def refresh_token(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Refresh the access token."""
    from ..utils.security import create_access_token
    from ..models.user import User
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账户已被禁用")
    new_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "role": user.role}
    )
    return {"access_token": new_token, "token_type": "bearer"}

@router.get("/users/count")
def count_users(db: Session = Depends(get_db)):
    """Get user counts by role (admin only)."""
    from ..models.user import User
    from sqlalchemy import func
    total = db.query(func.count(User.id)).scalar()
    admin_count = db.query(func.count(User.id)).filter(User.role == "admin").scalar()
    doctor_count = db.query(func.count(User.id)).filter(User.role == "doctor").scalar()
    patient_count = db.query(func.count(User.id)).filter(User.role == "patient").scalar()
    return {
        "total": total or 0, "admin": admin_count or 0,
        "doctor": doctor_count or 0, "patient": patient_count or 0
    }
