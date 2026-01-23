from pydantic import BaseModel , computed_field
from typing import List, Optional
from app.schemas.player import PlayersListResponse
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
        from_attributes = True

class PoolSchema(BaseModel):
    id: int
    name: str
    teams: List[TeamResponse]

    @computed_field
    @property
    def teams_count(self)->int:
        return len(self.teams)
    
class PoolListResponse(BaseModel):
    pools: List[PoolSchema]