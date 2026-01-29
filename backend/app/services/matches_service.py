from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from datetime import date, timedelta
from typing import Optional, List, Tuple
from fastapi import HTTPException
from datetime import date, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import joinedload
from sqlalchemy import or_, and_


from app.models.models import Match, Event, Team, Player, User
from app.schemas.matches import MatchUpdate

class MatchService:
    def __init__(self, db: Session):
        self.db = db
    
    def liste_matches(
        self,
        current_user: User,
        upcoming: bool = False,
        team_id: Optional[int] = None,
        status_filter: Optional[str] = None,
        my_matches: bool = False
    ):
        '''Récupère la liste des matchs (Tuple: matches, total)'''
        
        query = self.db.query(Match).join(Event).options(
            joinedload(Match.event),
            joinedload(Match.team1).joinedload(Team.player1),
            joinedload(Match.team1).joinedload(Team.player2),
            joinedload(Match.team2).joinedload(Team.player1),
            joinedload(Match.team2).joinedload(Team.player2)
        )

        # Filtre "Mes matchs"
        if my_matches:
            player = self.db.query(Player).filter(Player.user_id == current_user.id).first()
            if not player:
                return [], 0
            
            query = query.filter(
                or_(
                    Match.team1.has(or_(Team.player1_id == player.id, Team.player2_id == player.id)),
                    Match.team2.has(or_(Team.player1_id == player.id, Team.player2_id == player.id))
                )
            )

        # Gestion des dates et du tri
        if upcoming:
            today = date.today()
            limit_date = today + timedelta(days=30)
            query = query.filter(Event.event_date >= today, Event.event_date <= limit_date)
            query = query.order_by(Event.event_date.asc(), Event.event_time.asc())
        else:
            query = query.order_by(Event.event_date.desc(), Event.event_time.desc())

       
        if team_id:
            query = query.filter(or_(Match.team1_id == team_id, Match.team2_id == team_id))
        
        if status_filter:
            query = query.filter(Match.status == status_filter)

        # Exécution
        matches = query.all()
        
        # Retourne un tuple de 2 éléments
        return matches, len(matches)
   
    # UPDATE
    def update_match(self, match_id: int, data: MatchUpdate) -> Match:
        match = self.db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise HTTPException(status_code=404, detail="Match non trouvé")

        update_data = data.model_dump(exclude_unset=True)
        
        if "status" in update_data: match.status = data.status
        if "score_team1" in update_data: match.score_team1 = data.score_team1
        if "score_team2" in update_data: match.score_team2 = data.score_team2
        if "court_number" in update_data: match.court_number = data.court_number

        if data.event_date or data.event_time:
            if match.status != "A_VENIR" and data.status != "ANNULE":
                 raise HTTPException(status_code=400, detail="Modification impossible")
            
            if data.event_date:
                match.event.event_date = data.event_date
            if data.event_time:
                match.event.event_time = data.event_time

        self.db.commit()
        self.db.refresh(match)
        return match

    # DELETE
    def delete_match(self, match_id: int) -> bool:
        match = self.db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise HTTPException(status_code=404, detail="Match non trouvé")
        
        if match.status != "A_VENIR":
            raise HTTPException(status_code=400, detail="Suppression impossible")

        event = match.event
        if len(event.matches) <= 1:
            self.db.delete(event)
        else:
            self.db.delete(match)
        
        self.db.commit()
        return True