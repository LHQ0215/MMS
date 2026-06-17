from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..models.user import User
from ..schemas.user import UserResponse, UserUpdate, UserListResponse
from ..utils.security import get_current_user_id, check_role

router = APIRouter(prefix="/api/users", tags=["用户管理"])

@router.get("/me", response_model=UserResponse)
def get_current_user(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return user

@router.put("/me")
def update_current_user(req: UserUpdate, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    for key, value in req.dict(exclude_unset=True).items():
        setattr(user, key, value)
    db.commit()
    return {"message": "更新成功"}

@router.get("/list", response_model=UserListResponse)
def list_users(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    role: Optional[str] = None,
    keyword: Optional[str] = None,
    _: str = Depends(check_role("admin")),
    db: Session = Depends(get_db)
):
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    if keyword:
        query = query.filter(
            User.username.contains(keyword) | User.real_name.contains(keyword)
        )
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    return UserListResponse(total=total, items=items)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return user

@router.put("/{user_id}/toggle-status")
def toggle_user_status(user_id: int, _: str = Depends(check_role("admin")), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    user.is_active = not user.is_active
    db.commit()
    return {"message": "状态已更新", "is_active": user.is_active}

@router.get("/search")
def search_users(
    keyword: str,
    role: str = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    _: str = Depends(check_role("admin")),
    db: Session = Depends(get_db)
):
    """Search users by keyword with pagination."""
    from sqlalchemy import or_
    query = db.query(User)
    if keyword:
        query = query.filter(
            or_(User.username.contains(keyword), User.real_name.contains(keyword), User.phone.contains(keyword))
        )
    if role:
        query = query.filter(User.role == role)
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    return UserListResponse(total=total, items=items)

@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    _: str = Depends(check_role("admin")),
    db: Session = Depends(get_db)
):
    """Delete a user (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    if user.role == "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="不能删除管理员账户")
    db.delete(user)
    db.commit()
    return {"message": "用户已删除"}
