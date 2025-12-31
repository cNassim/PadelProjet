from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import extract
from typing import Optional
from datetime import date

from app.database import get_db
from app.api import deps
from app.models.models import Event, Match, Team, User
from app.schemas.events import EventCreate, EventUpdate, EventResponse, EventListResponse

router = APIRouter()

# GET /events
@router.get("/", response_model=EventListResponse)
def read_events(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    month: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    # FIX: We cannot join on 'Team.players' because it is a property, not a relationship.
    # We must explicitly join 'player1' and 'player2'.
    query = db.query(Event).options(
        joinedload(Event.matches).joinedload(Match.team1).joinedload(Team.player1),
        joinedload(Event.matches).joinedload(Match.team1).joinedload(Team.player2),
        joinedload(Event.matches).joinedload(Match.team2).joinedload(Team.player1),
        joinedload(Event.matches).joinedload(Match.team2).joinedload(Team.player2)
    )

    if start_date:
        query = query.filter(Event.event_date >= start_date)
    if end_date:
        query = query.filter(Event.event_date <= end_date)
    if month:
        year_str, month_str = month.split("-")
        query = query.filter(
            extract('year', Event.event_date) == int(year_str),
            extract('month', Event.event_date) == int(month_str)
        )

    # Sort by date and then time
    events = query.order_by(Event.event_date.asc(), Event.event_time.asc()).all()
    return {"events": events}

# POST /events (ADMIN ONLY)
@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event_in: EventCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_admin)
):
    # 1. Create Event
    db_event = Event(event_date=event_in.event_date, event_time=event_in.event_time)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    # 2. Create Matches
    if event_in.matches:
        for match_data in event_in.matches:
            # Verify teams exist
            t1 = db.query(Team).filter(Team.id == match_data.team1_id).first()
            t2 = db.query(Team).filter(Team.id == match_data.team2_id).first()
            
            if not t1 or not t2:
                db.delete(db_event)
                db.commit()
                raise HTTPException(status_code=404, detail="Équipe introuvable")

            db_match = Match(
                event_id=db_event.id,
                team1_id=match_data.team1_id,
                team2_id=match_data.team2_id,
                court_number=match_data.court_number,
                status="A_VENIR"
            )
            db.add(db_match)
    
    db.commit()
    # Refresh with relationships to ensure response model works
    db.refresh(db_event)
    return db_event

# PUT /events/{id} (ADMIN ONLY)
@router.put("/{id}", response_model=EventResponse)
def update_event(
    id: int,
    event_in: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_admin)
):
    event = db.query(Event).filter(Event.id == id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Événement non trouvé")

    if event_in.event_date:
        event.event_date = event_in.event_date
    if event_in.event_time:
        event.event_time = event_in.event_time
    
    db.commit()
    db.refresh(event)
    return event

# DELETE /events/{id} (ADMIN ONLY)
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_admin)
):
    event = db.query(Event).filter(Event.id == id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Événement non trouvé")

    for match in event.matches:
        if match.status != "A_VENIR":
            raise HTTPException(
                status_code=400, 
                detail="Impossible de supprimer : certains matchs sont terminés ou annulés."
            )

    db.delete(event)
    db.commit()
    return None