from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
import json

from ..config import settings
from ..database import get_db
from ..models.user import User, UserRole
from ..models.audit import AuditLog

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        user_id: int = payload.get("id")
        if email is None or user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if user is None:
        raise credentials_exception
    return user

def require_role(*allowed_roles: UserRole):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires one of roles: {[r.value for r in allowed_roles]}"
            )
        return current_user
    return role_checker

def log_audit_event(
    db: Session,
    action: str,
    entity_type: str,
    entity_id: str = None,
    user: User = None,
    details: dict = None,
    request: Request = None
):
    ip = request.client.host if request and request.client else "127.0.0.1"
    audit_entry = AuditLog(
        user_id=user.id if user else None,
        user_email=user.email if user else "system",
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id else None,
        details_json=json.dumps(details) if details else None,
        ip_address=ip
    )
    db.add(audit_entry)
    db.commit()

