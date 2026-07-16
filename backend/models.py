from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    media_files = relationship("MediaFile", back_populates="owner")
    operations = relationship("StegoOperation", back_populates="user")
    credentials = relationship("Credential", back_populates="owner")
    secure_notes = relationship("SecureNote", back_populates="owner")

class MediaFile(Base):
    __tablename__ = "media_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    file_type = Column(String)  # png, jpg, etc.
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="media_files")
    operations = relationship("StegoOperation", back_populates="media_file")

class StegoOperation(Base):
    __tablename__ = "stego_operations"

    id = Column(Integer, primary_key=True, index=True)
    operation_type = Column(String)  # 'hide' or 'extract'
    description = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    media_file_id = Column(Integer, ForeignKey("media_files.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="operations")
    media_file = relationship("MediaFile", back_populates="operations")

class Credential(Base):
    __tablename__ = "credentials"
    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String, nullable=False) # Encrypted
    username = Column(String, nullable=False)     # Encrypted
    password = Column(String, nullable=False)     # Encrypted
    url = Column(String, nullable=True)           # Encrypted
    totp_secret = Column(String, nullable=True)    # Encrypted
    notes = Column(String, nullable=True)          # Encrypted
    
    health_score = Column(Integer, default=100)
    is_reused = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="credentials")

class SecureNote(Base):
    __tablename__ = "secure_notes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)   # Encrypted
    content = Column(String, nullable=False) # Encrypted
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="secure_notes")
