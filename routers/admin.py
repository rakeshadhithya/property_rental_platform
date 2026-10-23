from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from dependencies import require_role
from models import User, UserRole
from schemas import UserOut

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), admin: User = Depends(require_role(UserRole.admin))):
    return db.query(User).order_by(User.id).all()

@router.patch("/users/{user_id}/active", response_model=UserOut)
def set_user_active(user_id: int, active: bool, db: Session = Depends(get_db), admin: User = Depends(require_role(UserRole.admin))):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    if user.id == admin.id and not active:
        raise HTTPException(400, "You cannot deactivate your own admin account")
    user.is_active = active
    db.commit()
    db.refresh(user)
    return user
