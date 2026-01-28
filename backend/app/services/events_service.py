from sqlalchemy.orm import Session, joinedload
from sqlalchemy import extract, cast, String
from app.models.models import Pool , Team , Match, Event
from app.api.deps import get_current_admin
from app.schemas.events import EventCreate, EventUpdate
from fastapi import HTTPException, Query
from typing import Optional
from datetime import date

class EventService:
    def __init__(self, db: Session):
        self.db = db

    def get_events(self, start_date=None, end_date=None, month=None, current_user=None, show_all=False):
        query = self.db.query(Event).options(
            joinedload(Event.matches).joinedload(Match.team1).joinedload(Team.player1),
            joinedload(Event.matches).joinedload(Match.team1).joinedload(Team.player2),
            joinedload(Event.matches).joinedload(Match.team2).joinedload(Team.player1),
            joinedload(Event.matches).joinedload(Match.team2).joinedload(Team.player2)
        )

        # Filtres temporels existants
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

        # Logique de filtrage par utilisateur
        # Si l'utilisateur n'est pas Admin et qu'il ne demande pas 'show_all'
        if current_user and current_user.role != "ADMINISTRATEUR" and not show_all:
            player_id = current_user.player.id if current_user.player else None
            
            if player_id:
                # On filtre les événements qui possèdent au moins un match où le joueur participe
                query = query.join(Event.matches).filter(
                    (Match.team1_id.in_(self.db.query(Team.id).filter((Team.player1_id == player_id) | (Team.player2_id == player_id)))) |
                    (Match.team2_id.in_(self.db.query(Team.id).filter((Team.player1_id == player_id) | (Team.player2_id == player_id))))
                ).distinct()
            else:
                # Si le compte n'est lié à aucun joueur, on renvoie une liste vide par défaut
                return []

        return query.order_by(Event.event_date.asc(), Event.event_time.asc()).all()
    
    
    def create_event(self, event_in: EventCreate): 
        print(f"\n🚀 DÉBUT CRÉATION : {event_in.event_date} à {event_in.event_time}")

        # Les listes pour la vérification DB (Pydantic a déjà vérifié l'interne)
        requested_courts = [m.court_number for m in event_in.matches]
        requested_teams = []
        for m in event_in.matches:
            requested_teams.extend([m.team1_id, m.team2_id])

        date_str = str(event_in.event_date)
        day_events = self.db.query(Event).filter(cast(Event.event_date, String).like(f"{date_str}%")).all()
        new_time = event_in.event_time[:5] 

        for existing_event in day_events:
            if existing_event.event_time[:5] != new_time:
                continue

            for match in existing_event.matches:
                if match.status == "ANNULE": continue 

                if match.court_number in requested_courts:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"CONFLIT : La piste {match.court_number} est déjà réservée à {new_time}."
                    )
                if match.team1_id in requested_teams or match.team2_id in requested_teams:
                    raise HTTPException(
                        status_code=400, 
                        detail="CONFLIT : Une équipe joue déjà un autre match sur ce créneau."
                    )

        # --- CRÉATION ---
        try:
            db_event = Event(event_date=event_in.event_date, event_time=event_in.event_time)
            self.db.add(db_event)
            self.db.flush() 

            for m_data in event_in.matches:
                # Vérification de l'existence des équipes (Sécurité DB)
                if not self.db.query(Team).filter(Team.id.in_([m_data.team1_id, m_data.team2_id])).count() == 2:
                    raise HTTPException(status_code=404, detail="Une ou plusieurs équipes sont introuvables.")

                db_match = Match(
                    event_id=db_event.id,
                    team1_id=m_data.team1_id,
                    team2_id=m_data.team2_id,
                    court_number=m_data.court_number,
                    status="A_VENIR"
                )
                self.db.add(db_match)
            
            self.db.commit()
            self.db.refresh(db_event)
            return db_event 

        except Exception as e:
            self.db.rollback()
            if isinstance(e, HTTPException): raise e
            raise HTTPException(status_code=500, detail=str(e))
        
    def update_event(self, id:id, event_in: EventUpdate):
        event = self.db.query(Event).filter(Event.id == id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Événement non trouvé")

        # TODO: Ajouter ici aussi la vérification de conflit si on change la date/heure
        if event_in.event_date:
            event.event_date = event_in.event_date
        if event_in.event_time:
            event.event_time = event_in.event_time
        
        self.db.commit()
        self.db.refresh(event)
        return event
    
    def delete_event(self, id):
        event = self.db.query(Event).filter(Event.id == id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Événement non trouvé")

        for match in event.matches:
            if match.status != "A_VENIR":
                raise HTTPException(
                    status_code=400, 
                    detail="Impossible de supprimer : certains matchs sont terminés ou annulés."
                )

        self.db.delete(event)
        self.db.commit()
        return None