# ============================================
# FICHIER : backend/app/api/events.py
# ============================================

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import extract, cast, String, func  # ✅ IMPORT String AJOUTÉ
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

    events = query.order_by(Event.event_date.asc(), Event.event_time.asc()).all()
    return {"events": events}

# POST /events (ADMIN ONLY) - ✅ SÉCURITÉ RENFORCÉE (FIX SQLITE)
@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event_in: EventCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_admin)
):
    print(f"\n🚀 DÉBUT CRÉATION : {event_in.event_date} à {event_in.event_time}")

    # --- 1. VALIDATION INTERNE ---
    requested_courts = [m.court_number for m in event_in.matches]
    if len(requested_courts) != len(set(requested_courts)):
        raise HTTPException(status_code=400, detail="Doublon de piste dans votre demande.")

    requested_teams = []
    for m in event_in.matches:
        if m.team1_id == m.team2_id:
            raise HTTPException(status_code=400, detail="Une équipe ne peut pas jouer contre elle-même.")
        requested_teams.append(m.team1_id)
        requested_teams.append(m.team2_id)
    
    if len(requested_teams) != len(set(requested_teams)):
        raise HTTPException(status_code=400, detail="Une équipe est présente plusieurs fois dans votre demande.")

    # --- 2. VALIDATION EXTERNE (Vérification Inter-Événements) ---
    
    # ✅ FIX CRITIQUE : Conversion explicite en String pour la comparaison
    # Cela permet de matcher "2026-01-06" avec "2026-01-06 00:00:00"
    date_str = str(event_in.event_date)
    
    day_events = db.query(Event).filter(
        cast(Event.event_date, String).like(f"{date_str}%")
    ).all()
    
    print(f"📅 Analyse de {len(day_events)} événements existants pour la date {date_str}...")

    # On normalise l'heure demandée (HH:MM)
    new_time = event_in.event_time[:5] 

    for existing_event in day_events:
        # On normalise l'heure existante
        existing_time = existing_event.event_time[:5]

        # Si ce n'est pas la même heure, pas de conflit direct
        if existing_time != new_time:
            continue

        print(f"⚠️ Analyse conflit avec événement ID {existing_event.id} à {existing_time}")

        # On vérifie les matchs de cet événement existant
        for match in existing_event.matches:
            if match.status == "ANNULE":
                continue 

            # TEST A : PISTE DÉJÀ PRISE ?
            if match.court_number in requested_courts:
                print(f"❌ BLOCAGE : Piste {match.court_number} déjà prise.")
                raise HTTPException(
                    status_code=400, 
                    detail=f"CONFLIT : La piste {match.court_number} est déjà réservée à {existing_time}."
                )

            # TEST B : ÉQUIPE DÉJÀ PRISE ?
            if match.team1_id in requested_teams or match.team2_id in requested_teams:
                # Récupération de l'ID qui pose problème pour le log
                team_conflict = match.team1_id if match.team1_id in requested_teams else match.team2_id
                print(f"❌ BLOCAGE : Équipe ID {team_conflict} joue déjà.")
                raise HTTPException(
                    status_code=400, 
                    detail=f"CONFLIT : L'équipe ID {team_conflict} joue déjà un autre match à {existing_time}."
                )

    print("✅ Aucun conflit détecté.")

    # --- 3. CRÉATION ---
    db_event = Event(event_date=event_in.event_date, event_time=event_in.event_time)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    for match_data in event_in.matches:
        t1 = db.query(Team).filter(Team.id == match_data.team1_id).first()
        t2 = db.query(Team).filter(Team.id == match_data.team2_id).first()
        
        if not t1 or not t2:
            db.delete(db_event)
            db.commit()
            raise HTTPException(status_code=404, detail="Équipe introuvable.")

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

    # TODO: Ajouter ici aussi la vérification de conflit si on change la date/heure
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