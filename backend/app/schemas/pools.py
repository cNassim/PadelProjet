from pydantic import BaseModel, EmailStr, Field, validator
import re

class Team(BaseModel):
    id:int #à importer de l'implementation des filles.

    
class Pool(BaseModel):
    id: int
    name: str
    teams_count: int
    teams: list[Team] = []
