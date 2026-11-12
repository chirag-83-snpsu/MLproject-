import os

class Settings:
    PROJECT_NAME: str = "CredX AI Credit Risk Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "credx-enterprise-risk-secret-key-super-secure-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'credx.db')}")
    
    # Model artifact directory
    ML_ARTIFACTS_DIR: str = os.path.join(os.path.dirname(BASE_DIR), "ml", "models", "model_artifacts")

settings = Settings()
