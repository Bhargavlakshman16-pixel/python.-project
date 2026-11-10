import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
load_dotenv(BASE_DIR / ".env")

class Config:
    # Database Settings
    DB_TYPE = os.getenv("DB_TYPE", "mysql").lower()  # 'mysql' or 'sqlite'
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "library_db")
    SQLITE_PATH = os.getenv("SQLITE_PATH", str(BASE_DIR / "database" / "library.db"))

    # Persona Due Times (Student < Teacher < Business Man)
    STUDENT_LOAN_DAYS = int(os.getenv("STUDENT_LOAN_DAYS", "7"))        # Less due time
    TEACHER_LOAN_DAYS = int(os.getenv("TEACHER_LOAN_DAYS", "14"))      # More than student
    BUSINESS_MAN_LOAN_DAYS = int(os.getenv("BUSINESS_MAN_LOAN_DAYS", "30")) # Maximum due time

    DEFAULT_LOAN_DAYS = int(os.getenv("DEFAULT_LOAN_DAYS", "14"))
    DAILY_OVERDUE_FINE = float(os.getenv("DAILY_OVERDUE_FINE", "1.50"))

    # Server Settings
    APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
    APP_PORT = int(os.getenv("APP_PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

    @classmethod
    def get_days_for_role(cls, role: str) -> int:
        role_clean = (role or "").strip().lower()
        if "admin" in role_clean:
            return 365
        elif "student" in role_clean:
            return cls.STUDENT_LOAN_DAYS
        elif "teacher" in role_clean or "faculty" in role_clean:
            return cls.TEACHER_LOAN_DAYS
        elif "business" in role_clean:
            return cls.BUSINESS_MAN_LOAN_DAYS
        return cls.DEFAULT_LOAN_DAYS

config = Config()
