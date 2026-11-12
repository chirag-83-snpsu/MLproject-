from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.user import User, UserRole
from ..models.audit import AuditLog
from ..schemas.analytics import AuditLogResponse
from ..core.dependencies import get_current_user, require_role

router = APIRouter(prefix="/audit", tags=["Audit & Governance"])

@router.get("/logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.COMPLIANCE_OFFICER, UserRole.ADMIN, UserRole.RISK_ANALYST))
):
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
    return logs

