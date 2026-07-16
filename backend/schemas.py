from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)

class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class StegoHistoryOut(BaseModel):
    id: int
    operation_type: str
    description: str
    created_at: datetime
    media_file_id: Optional[int] = None

    class Config:
        from_attributes = True

class ExtractionResult(BaseModel):
    message: str

# --- Vault Schemas ---

class CredentialBase(BaseModel):
    service_name: str = Field(..., min_length=1, max_length=100)
    username: str = Field(..., min_length=1, max_length=150)
    password: str = Field(..., min_length=1, max_length=128)
    url: Optional[str] = Field(None, max_length=500)
    totp_secret: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=1000)

class CredentialCreate(CredentialBase):
    master_password: str = Field(..., min_length=8)

class VaultListRequest(BaseModel):
    master_password: str

class CredentialUpdate(BaseModel):
    service_name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    url: Optional[str] = None
    totp_secret: Optional[str] = None
    notes: Optional[str] = None

class CredentialOut(CredentialBase):
    id: int
    health_score: int
    is_reused: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Secure Notes Schemas ---

class SecureNoteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1, max_length=5000)

class SecureNoteCreate(SecureNoteBase):
    master_password: str = Field(..., min_length=8)

class NotesListRequest(BaseModel):
    master_password: str

class SecureNoteOut(SecureNoteBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
