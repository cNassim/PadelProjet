from pydantic import BaseModel, field_validator, model_validator, ConfigDict
from typing import List, Optional
from datetime import date
import re

from app.schemas.team import TeamResponse 

# --- SCHÉMAS INTERMÉDIAIRES ---

class EventSimple(BaseModel):
    """Version légère pour éviter l'import circulaire"""
    id: int
    event_date: date
    event_time: str
    model_config = ConfigDict(from_attributes=True)

# --- SCHÉMAS MATCH ---

class MatchBase(BaseModel):
    court_number: int
    @field_validator('court_number')
    @classmethod
    def validate_court(cls, v):
        if not (1 <= v <= 10):
            raise ValueError('Le numéro de piste doit être entre 1 et 10')
        return v

class MatchCreate(MatchBase):
    team1_id: int
    team2_id: int
    @model_validator(mode='after')
    def validate_teams_diff(self):
        if self.team1_id == self.team2_id:
            raise ValueError("Une équipe ne peut pas jouer contre elle-même")
        return self

class MatchResponse(MatchBase):
    id: int
    event_id: int
    status: str
    score_team1: Optional[str] = None
    score_team2: Optional[str] = None
    team1: Optional[TeamResponse] = None
    team2: Optional[TeamResponse] = None
    event: Optional[EventSimple] = None  

    model_config = ConfigDict(from_attributes=True)

class MatchListResponse(BaseModel):
    matches: List[MatchResponse]
    total: int

class MatchUpdate(BaseModel):
    status: Optional[str] = None
    score_team1: Optional[str] = None
    score_team2: Optional[str] = None
    event_date: Optional[date] = None
    event_time: Optional[str] = None
    court_number: Optional[int] = None

    @field_validator('score_team1', 'score_team2')
    @classmethod
    def validate_score(cls, v):
        if v is None: return v
        if not re.match(r'^(\d+-\d+)(,\s*\d+-\d+){0,2}$', v):
            raise ValueError("Format de score invalide (ex: 6-4, 6-3)")
        return v