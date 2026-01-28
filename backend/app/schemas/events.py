# ============================================
# FICHIER : backend/app/schemas/events.py
# ============================================

from pydantic import BaseModel, field_validator, model_validator
from datetime import date
from typing import List, Optional 
from app.schemas.matches import *

# --- SCHEMAS EVENT ---
class EventBase(BaseModel):
    event_date: date
    event_time: str  # HH:MM

    @field_validator('event_date')
    @classmethod
    def validate_date(cls, v):
        return v

class EventCreate(EventBase):
    matches: List[MatchCreate]

    @field_validator('matches')
    @classmethod
    def validate_matches_count(cls, v):
        if not (1 <= len(v) <= 3):
            raise ValueError("Un événement doit contenir entre 1 et 3 matchs")
        return v

    @model_validator(mode='after')
    def validate_uniqueness(self):
        #matches = self.matches
        courts = [m.court_number for m in self.matches]
        if len(courts) != len(set(courts)):
            raise ValueError("Impossible d'utiliser la même piste deux fois")
        
        teams_seen = set()
        for m in self.matches:
            if m.team1_id == m.team2_id:
                raise ValueError("Une équipe ne peut pas jouer contre elle-même")
            if m.team1_id in teams_seen or m.team2_id in teams_seen:
                 raise ValueError(f"Une équipe joue déjà dans cet événement")
            teams_seen.add(m.team1_id)
            teams_seen.add(m.team2_id)
        return self

class EventUpdate(BaseModel):
    event_date: Optional[date] = None
    event_time: Optional[str] = None

class EventResponse(EventBase):
    id: int
    matches: List[MatchResponse] = []

    class Config:
        from_attributes = True

class EventListResponse(BaseModel):
    events: List[EventResponse]
