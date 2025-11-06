from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth
from app.database import engine
from app.models import models

# Créer les tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Corpo Padel API",
    description="API pour la gestion de tournois corporatifs de padel",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,  # ← Changé de ALLOWED_ORIGINS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de sécurité
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

# Routes
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API Corpo Padel", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}