# ============================================
# FICHIER : backend/app/models/models.py
# ============================================

from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, TIMESTAMP, CheckConstraint
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # JOUEUR ou ADMINISTRATEUR
    is_active = Column(Boolean, default=True)
    must_change_password = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    player = relationship("Player", back_populates="user", uselist=False)

class LoginAttempt(Base):
    __tablename__ = "login_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True, nullable=False)
    attempts_count = Column(Integer, default=0)
    last_attempt = Column(DateTime(timezone=True))
    locked_until = Column(DateTime(timezone=True), nullable=True)

class Player(Base):
    __tablename__="players"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True, nullable=False)
    last_name = Column(String, index=True, nullable=False)
    company = Column(String, index=True, nullable=False)
    license_number = Column(String, index=True, unique=True)
    birth_date = Column(DateTime)
    photo_url = Column(String)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)

    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    # contraintes
    __table_args__ = (
        CheckConstraint("license_number GLOB 'L[0-9][0-9][0-9][0-9][0-9][0-9]'", name="chk_license_format"),
    )

    user = relationship("User", back_populates="player", passive_deletes=True)

