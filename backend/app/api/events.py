# ============================================
# FICHIER : backend/app/api/events.py
# ============================================

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import extract, cast, String, func  
from typing import Optional
from datetime import date

from app.database import get_db
from app.api import deps
from app.models.models import Event, Match, Team, User
from app.schemas.events import *
from app.services.events_service import *

router = APIRouter()

# GET /events
'''@router.get("/", response_model=EventListResponse)
def read_events(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    month: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    service = EventService(db)
    events = service.get_events(start_date= start_date, end_date=end_date, month=month)
    return {"events": events} '''
@router.get("/", response_model=EventListResponse)
def read_events(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    month: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}$"),
    show_all: bool = Query(False), # Ajout du paramètre pour basculer l'affichage
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    service = EventService(db)
    # On passe current_user et show_all au service
    events = service.get_events(
        start_date=start_date, 
        end_date=end_date, 
        month=month, 
        current_user=current_user, 
        show_all=show_all
    )
    return {"events": events}

# POST /events (ADMIN ONLY)
@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event_in: EventCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_admin)
):
    service = EventService(db)
    return service.create_event(event_in=event_in)

# PUT /events/{id} (ADMIN ONLY)
@router.put("/{id}", response_model=EventResponse)
def update_event(
    id: int,
    event_in: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_admin)
):
    service = EventService(db)
    return service.update_event(id=id,event_in=event_in)
    

# DELETE /events/{id} (ADMIN ONLY)
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_admin)
):
    service = EventService(db)
    return service.delete_event(id=id)