from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import extract
from typing import Optional
from datetime import date

from app.database import get_db
from app.api import deps
from app.models.models import Event, Match, Team, User
from app.schemas.events import EventCreate, EventResponse, EventListResponse

router = APIRouter()

# GET /events
@router.get("/events", response_model=EventListResponse)
def read_events(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    month: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}$"), # Regex pour YYYY-MM
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user) # Authentification requise
):
    query = db.query(Event)

    # --- FILTRES ---
    if start_date:
        query = query.filter(Event.event_date >= start_date)
    if end_date:
        query = query.filter(Event.event_date <= end_date)
    if month:
        # sqlite gère l'extraction un peu différemment parfois, mais via SQLAlchemy:
        year_str, month_str = month.split("-")
        query = query.filter(
            extract('year', Event.event_date) == int(year_str),
            extract('month', Event.event_date) == int(month_str)
        )

    # Tri et exécution
    events = query.order_by(Event.event_date.asc()).all()
    
    # On retourne un dict pour matcher le schema EventListResponse
    return {"events": events}

# POST /events (ADMIN ONLY)
@router.post("/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event_in: EventCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    if current_user.role != "ADMINISTRATEUR":
        raise HTTPException(status_code=403, detail="Droits administrateur requis")

    # 1. Créer l'événement
    db_event = Event(event_date=event_in.event_date, event_time=event_in.event_time)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    # 2. Créer les matchs
    for match_data in event_in.matches:
        # Vérif existence équipes
        t1 = db.query(Team).filter(Team.id == match_data.team1_id).first()
        t2 = db.query(Team).filter(Team.id == match_data.team2_id).first()
        
        if not t1 or not t2:
            # Nettoyage si erreur : on supprime l'événement créé juste avant
            db.delete(db_event)
            db.commit()
            raise HTTPException(status_code=404, detail=f"Équipe introuvable (ID {match_data.team1_id} ou {match_data.team2_id})")

        db_match = Match(
            event_id=db_event.id,
            team1_id=match_data.team1_id,
            team2_id=match_data.team2_id,
            court_number=match_data.court_number,
            status="A_VENIR"
        )
        db.add(db_match)
    
    db.commit()
    db.refresh(db_event)
    return db_event

# PUT /events/{id} (ADMIN ONLY)
@router.put("/events/{id}", response_model=EventResponse)
def update_event(
    id: int,
    event_in: EventCreate, # Simplification: on réutilise le schema de création
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    if current_user.role != "ADMINISTRATEUR":
        raise HTTPException(status_code=403, detail="Droits administrateur requis")

    event = db.query(Event).filter(Event.id == id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Événement non trouvé")

    # Mise à jour simple (Date/Heure)
    # Pour modifier les matchs, c'est plus complexe (suppression/recréation), 
    # pour ce projet de 12h, on met souvent à jour juste l'entête de l'événement ici.
    event.event_date = event_in.event_date
    event.event_time = event_in.event_time
    
    db.commit()
    db.refresh(event)
    return event

# DELETE /events/{id} (ADMIN ONLY - Conditionnel)
@router.delete("/events/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    if current_user.role != "ADMINISTRATEUR":
        raise HTTPException(status_code=403, detail="Droits administrateur requis")

    event = db.query(Event).filter(Event.id == id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Événement non trouvé")

    # RÈGLE MÉTIER : Tous les matchs doivent être "A_VENIR"
    for match in event.matches:
        if match.status != "A_VENIR":
            raise HTTPException(
                status_code=400, 
                detail="Impossible de supprimer : certains matchs sont terminés ou annulés."
            )

    db.delete(event)
    db.commit()
    return None