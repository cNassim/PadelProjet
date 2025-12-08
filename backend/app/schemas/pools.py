from pydantic import BaseModel
from typing import List, Optional
from app.schemas.team import TeamResponse


class PoolCreate(BaseModel):
    name: str
    team_ids: List[int]


class PoolResponse(BaseModel):
    id: int
    name: str
    teams_count: int
    teams: List[TeamResponse]

    class Config:
        orm_mode = True

