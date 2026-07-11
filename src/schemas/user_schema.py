from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# =========================
# SIGNUP SCHEMA
# =========================


class UserCreate(BaseModel):
    """
    Naya user banane ke liye
    Frontend se yeh data aayega
    """

    name: str
    email: EmailStr  # Automatic email validation
    password: str


# =========================
# LOGIN SCHEMA
# =========================


class UserLogin(BaseModel):
    """
    Login ke liye
    """

    email: EmailStr
    password: str


# =========================
# TOKEN RESPONSE
# =========================


class TokenResponse(BaseModel):
    """
    Login successful hone ke baad
    Yeh response jayega
    """

    access_token: str
    token_type: str = "bearer"


# =========================
# USER RESPONSE
# =========================


class UserResponse(BaseModel):
    """
    User ka data return karne ke liye
    Password kabhi nahi jayega ✅
    """

    id: int
    name: str
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# =========================
# USER UPDATE
# =========================


class UserUpdate(BaseModel):
    """
    User apna profile update kare
    Sab optional hain —
    Jo chahein badlein
    """

    name: Optional[str] = None
    password: Optional[str] = None
