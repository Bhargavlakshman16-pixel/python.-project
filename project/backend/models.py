from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date

class BookCreate(BaseModel):
    isbn: str = Field(..., min_length=3, max_length=20, description="International Standard Book Number")
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=100)
    total_copies: int = Field(default=1, ge=1)
    copies_available: Optional[int] = Field(default=None, ge=0)

    @field_validator("copies_available", mode="before")
    def default_copies_available(cls, v, values):
        return v

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None
    total_copies: Optional[int] = Field(default=None, ge=1)
    copies_available: Optional[int] = Field(default=None, ge=0)

class BorrowerCreate(BaseModel):
    borrower_name: str = Field(..., min_length=1, max_length=255)
    roll_no: str = Field(..., min_length=1, max_length=50)
    borrower_type: str = Field(default="Student", description="Student, Teacher, Business Man, or Admin")
    email: Optional[str] = None
    contact: Optional[str] = None
    password: Optional[str] = Field(default="123456")

class BorrowerUpdate(BaseModel):
    borrower_name: Optional[str] = None
    roll_no: Optional[str] = None
    borrower_type: Optional[str] = None
    email: Optional[str] = None
    contact: Optional[str] = None
    password: Optional[str] = None

class LoginRequest(BaseModel):
    borrower_name: Optional[str] = None
    roll_no: str = Field(..., min_length=1, max_length=50)
    borrower_type: Optional[str] = Field(default="Student", description="Student, Teacher, Business Man, or Admin")
    password: Optional[str] = None

class RegisterRequest(BaseModel):
    borrower_name: str = Field(..., min_length=1, max_length=255)
    roll_no: str = Field(..., min_length=1, max_length=50)
    borrower_type: str = Field(default="Student", description="Student, Teacher, or Business Man")
    password: str = Field(default="123456", min_length=1)
    email: Optional[str] = None
    contact: Optional[str] = None

class LoanIssueRequest(BaseModel):
    book_id: int = Field(..., ge=1)
    borrower_id: int = Field(..., ge=1)
    issue_date: Optional[str] = None
    due_date: Optional[str] = None
    loan_period_days: Optional[int] = Field(default=None, ge=1, le=180)

class LoanReturnRequest(BaseModel):
    return_date: Optional[str] = None

class SystemSettings(BaseModel):
    default_loan_days: int = Field(default=14, ge=1, le=365)
    daily_overdue_fine: float = Field(default=1.50, ge=0.0)
