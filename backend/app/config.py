import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))
from typing import List

class Settings:
    APP_NAME: str = "AI Medical Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    DB_TYPE: str = os.getenv("DB_TYPE", "sqlite")

    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "medical_system")

    @property
    def DATABASE_URL(self) -> str:
        if self.DB_TYPE == "mysql":
            return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        db_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return f"sqlite:///{os.path.join(db_dir, 'medical_system.db')}"

    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-change-in-production-2024")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    AI_API_KEY: str = os.getenv("AI_API_KEY", "")
    AI_API_URL: str = os.getenv("AI_API_URL", "https://api.openai.com/v1/chat/completions")
    AI_MODEL: str = os.getenv("AI_MODEL", "gpt-3.5-turbo")

    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]

settings = Settings()
