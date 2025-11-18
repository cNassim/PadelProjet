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

    teams_as_player1 = relationship("Team", back_populates="player1", foreign_keys="Team.player1_id")
    teams_as_player2 = relationship("Team", back_populates="player2", foreign_keys="Team.player2_id")
    user = relationship("User", back_populates="player", passive_deletes=True)

class Pool(Base):
    __tablename__ = "pools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    # Relations
    teams = relationship("Team", back_populates="pool")




class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    company = Column(String, nullable=False)
    player1_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    player2_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    pool_id = Column(Integer, ForeignKey("pools.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Contraintes
    __table_args__ = (
        CheckConstraint("player1_id != player2_id", name="chk_different_players"),
    )

    # Relations
    player1 = relationship("Player", foreign_keys=[player1_id], back_populates="teams_as_player1")
    player2 = relationship("Player", foreign_keys=[player2_id], back_populates="teams_as_player2")
    pool = relationship("Pool", back_populates="teams")
    matches_as_team1 = relationship("Match", back_populates="team1", foreign_keys="[Match.team1_id]")
    matches_as_team2 = relationship("Match", back_populates="team2", foreign_keys="[Match.team2_id]")



class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    event_date = Column(DateTime, nullable=False)
    event_time = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relations
    matches = relationship("Match", back_populates="event", cascade="all, delete")



class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    team1_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    team2_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    court_number = Column(Integer, CheckConstraint("court_number BETWEEN 1 AND 10"), nullable=False)
    status = Column(
        String,
        nullable=False,
        server_default="A_VENIR"
    )
    score_team1 = Column(String, nullable=True)
    score_team2 = Column(String, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    __table_args__ = (
        CheckConstraint("team1_id != team2_id", name="chk_different_teams"),
        CheckConstraint("status IN ('A_VENIR', 'TERMINE', 'ANNULE')", name="chk_status_valid"),
    )

    # Relations
    event = relationship("Event", back_populates="matches")
    team1 = relationship("Team", foreign_keys=[team1_id], back_populates="matches_as_team1")
    team2 = relationship("Team", foreign_keys=[team2_id], back_populates="matches_as_team2")
