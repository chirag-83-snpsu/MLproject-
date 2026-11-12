from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta

from ..database import get_db
from ..models.user import User, UserRole
from ..schemas.user import UserCreate, UserResponse, Token, LoginRequest
from ..core.security import verify_password, get_password_hash, create_access_token
from ..core.dependencies import get_current_user, log_audit_event
from ..config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, request: Request, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists."
        )
        
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    log_audit_event(
        db,
        action="USER_REGISTERED",
        entity_type="User",
        entity_id=str(user.id),
        user=user,
        details={"email": user.email, "role": user.role.value},
        request=request
    )
    return user

@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user account")
        
    access_token = create_access_token(
        subject=user.email,
        user_id=user.id,
        role=user.role.value
    )
    
    log_audit_event(
        db,
        action="USER_LOGIN",
        entity_type="User",
        entity_id=str(user.id),
        user=user,
        details={"email": user.email},
        request=request
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

