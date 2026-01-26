from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.api import auth, teams, pools, admin, profile, events, matches, results, players
from app.database import engine
from app.models import models
from pathlib import Path

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
    #allow_origins=settings.allowed_origins,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
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

# --- ROUTES ---

# Authentification
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])

# Administration 
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Administration"])
app.include_router(profile.router, prefix="/api/v1/profile", tags=["Profile"])


# Événements
app.include_router(events.router, prefix="/api/v1/events", tags=["Events & Matches"])
app.include_router(matches.router, prefix="/api/v1/matches", tags=["Matches"])
# Pools et Teams 
app.include_router(players.router)
app.include_router(pools.router, prefix="/api/v1/pools", tags=["Pools"])
app.include_router(teams.router, prefix="/api/v1/teams", tags=["Teams"])

# Résultats
app.include_router(results.router, prefix="/api/v1/results", tags=["Results"])

# Servir les fichiers statiques (photos de profil)
uploads_path = Path("uploads")
if uploads_path.exists():
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API Corpo Padel", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
