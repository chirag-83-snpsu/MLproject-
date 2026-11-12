from fastapi import APIRouter

from .auth import router as auth_router
from .applications import router as applications_router
from .assessment import router as assessment_router
from .underwriting import router as underwriting_router
from .analytics import router as analytics_router
from .fairness import router as fairness_router
from .model_ops import router as model_ops_router
from .audit import router as audit_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(applications_router)
api_router.include_router(assessment_router)
api_router.include_router(underwriting_router)
api_router.include_router(analytics_router)
api_router.include_router(fairness_router)
api_router.include_router(model_ops_router)
api_router.include_router(audit_router)

