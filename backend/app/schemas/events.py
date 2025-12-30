# ============================================
# FICHIER : backend/app/schemas/events.py
# ============================================

from pydantic import BaseModel, field_validator, model_validator
from datetime import date
from typing import List, Optional
from app.schemas.team import TeamResponse  # ✅ Import nécessaire pour afficher les équipes

# --- SCHEMAS MATCH ---
class MatchBase(BaseModel):
    court_number: int

    @field_validator('court_number')
    def validate_court(cls, v):
        if not (1 <= v <= 10):
            raise ValueError('Le numéro de piste doit être entre 1 et 10')
        return v

class MatchCreate(MatchBase):
    team1_id: int
    team2_id: int

    @field_validator('team2_id')
    def validate_teams_diff(cls, v, values):
        return v

class MatchResponse(MatchBase):
    id: int
    event_id: int
    team1_id: int
    team2_id: int
    status: str
    score_team1: Optional[str] = None
    score_team2: Optional[str] = None
    
    # ✅ AJOUT : Objets complets pour l'affichage (Entreprise, Joueurs...)
    team1: Optional[TeamResponse] = None
    team2: Optional[TeamResponse] = None

    class Config:
        from_attributes = True

# --- SCHEMAS EVENT ---
class EventBase(BaseModel):
    event_date: date
    event_time: str  # HH:MM

    @field_validator('event_date')
    def validate_date(cls, v):
        # On autorise les dates passées pour l'historique, 
        # mais pour la création on pourrait restreindre.
        return v

class EventCreate(EventBase):
    matches: List[MatchCreate]

    @field_validator('matches')
    def validate_matches_count(cls, v):
        if not (1 <= len(v) <= 3):
            raise ValueError("Un événement doit contenir entre 1 et 3 matchs")
        return v

    @model_validator(mode='after')
    def validate_uniqueness(self):
        matches = self.matches
        courts = [m.court_number for m in matches]
        if len(courts) != len(set(courts)):
            raise ValueError("Impossible d'utiliser la même piste deux fois")
        
        teams_seen = set()
        for m in matches:
            if m.team1_id == m.team2_id:
                raise ValueError("Une équipe ne peut pas jouer contre elle-même")
            if m.team1_id in teams_seen or m.team2_id in teams_seen:
                 raise ValueError(f"Une équipe joue déjà dans cet événement")
            teams_seen.add(m.team1_id)
            teams_seen.add(m.team2_id)
        return self

# ✅ AJOUT : Schéma spécifique pour la modification (partielle)
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