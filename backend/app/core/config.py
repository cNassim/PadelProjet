from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    database_url: str = "sqlite:///./padel_corpo.db"
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    allowed_origins: str = "http://localhost:5173"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,  # Important pour accepter DATABASE_URL ou database_url
        extra='ignore'  # Ignore les champs supplémentaires
    )

settings = Settings()

# Convertir allowed_origins en liste si c'est une string
if isinstance(settings.allowed_origins, str):
    settings.allowed_origins = [settings.allowed_origins]