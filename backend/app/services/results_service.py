'''from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from typing import List, Dict, Any
from app.models.models import Match, Player, Team, User

class ResultService:
    def __init__(self, db: Session):
        self.db = db

    def parse_score(self, score_str: str) -> tuple:
        Parse un score de type '6-4, 2-6, 6-3'
        Retourne (sets_gagnes, sets_perdus)
        
        if not score_str:
            return 0, 0
        
        sets_won = 0
        sets_lost = 0
        
        try:
            # Séparer les sets (virgule ou espace)
            sets = score_str.replace(',', ' ').split()
            for s in sets:
                if '-' in s:
                    games_1, games_2 = map(int, s.split('-'))
                    if games_1 > games_2:
                        sets_won += 1
                    elif games_2 > games_1:
                        sets_lost += 1
        except:
            pass # Ignorer les formats malformés pour éviter de crasher
            
        return sets_won, sets_lost
    def determine_winner(self, match: Match) -> int:
        
        Retourne 1 si équipe 1 gagne, 2 si équipe 2 gagne, 0 sinon
        
        if not match.score_team1 or not match.score_team2:
            return 0
            
        # On suppose que le score est du point de vue de l'équipe 1 pour score_team1 ?
        # Le CDC dit format "X-Y". Généralement score_team1="6-4, 6-3" veut dire team 1 gagne.
        # Mais le modèle a deux champs score.
        # Hypothèse: score_team1 est le score global vu par team1 (ex: "6-4, 6-3")
        # OU ALORS: score_team1 = "6, 6" et score_team2 = "4, 3".
        # Le modèle actuel a score_team1 et score_team2 en String.
        # Regardons le mock du frontend match: score_team1="6-4, 6-3".
        # On va utiliser score_team1 comme référence principale.
        
        s1_won, s1_lost = self.parse_score(match.score_team1)
        
        if s1_won > s1_lost:
            return 1
        elif s1_lost > s1_won:
            return 2
        return 0
    
    def get_player_results(self, user_id: int)-> Dict[str, Any]:
            
        Historique des matchs TERMINÉS du joueur connecté + Stats
        
        # 1. Trouver le joueur
        player = self.db.query(Player).filter(Player.user_id == user_id).first()
        if not player:
            return {"results": [], "statistics": {"total": 0, "wins": 0, "losses": 0}}

        # 2. Trouver les matchs terminés
        # On cherche les équipes où le joueur est présent
        matchs = self.db.query(Match).join(Team, or_(Match.team1_id == Team.id, Match.team2_id == Team.id)).filter(
            or_(Team.player1_id == player.id, Team.player2_id == player.id),
            Match.status == "TERMINE"
        ).order_by(Match.updated_at.desc()).all()

        results = []
        stats = {"total": 0, "wins": 0, "losses": 0}

        for m in matchs:
            # Identifier si le joueur est dans l'équipe 1 ou 2
            is_team1 = (m.team1.player1_id == player.id or m.team1.player2_id == player.id)
            
            # Déterminer vainqueur
            winner = self.determine_winner(m)
            
            is_victory = False
            if (is_team1 and winner == 1) or (not is_team1 and winner == 2):
                is_victory = True
                stats["wins"] += 1
            else:
                stats["losses"] += 1
                
            stats["total"] += 1

            results.append({
                "id": m.id,
                "date": m.event.event_date,
                "opponent": m.team2.company if is_team1 else m.team1.company,
                "score": m.score_team1 if is_team1 else m.score_team2, # Affiche le score du point de vue de l'équipe (ou brut)
                "result": "VICTOIRE" if is_victory else "DÉFAITE",
                "court": m.court_number
            })

        return {"results": results, "statistics": stats}'''


from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from typing import List, Dict, Any
from app.models.models import Match, Player, Team, User

class ResultService:
    def __init__(self, db: Session):
        self.db = db

    def parse_score(self, score_str: str) -> tuple:
        """Parse un score et retourne (sets_gagnes, sets_perdus)"""
        if not score_str:
            return 0, 0
        
        sets_won, sets_lost = 0, 0
        try:
            # Nettoyage et découpage des sets
            sets = score_str.replace(',', ' ').split()
            for s in sets:
                if '-' in s:
                    games_1, games_2 = map(int, s.split('-'))
                    if games_1 > games_2:
                        sets_won += 1
                    elif games_2 > games_1:
                        sets_lost += 1
        except Exception:
            pass 
        return sets_won, sets_lost

    def determine_winner(self, match: Match) -> int:
        """Retourne 1 (Team 1), 2 (Team 2) ou 0"""
        if not match.score_team1:
            return 0
        
        s1_won, s1_lost = self.parse_score(match.score_team1)
        if s1_won > s1_lost:
            return 1
        elif s1_lost > s1_won:
            return 2
        return 0

    def get_player_results(self, user_id: int) -> Dict[str, Any]:
        """Récupère les résultats et statistiques d'un joueur"""
        player = self.db.query(Player).filter(Player.user_id == user_id).first()
        if not player:
            return {"results": [], "statistics": {"total": 0, "wins": 0, "losses": 0}}

        # Chargement optimisé avec joinedload pour éviter les requêtes N+1
        matches = (
            self.db.query(Match)
            .join(Team, or_(Match.team1_id == Team.id, Match.team2_id == Team.id))
            .options(
                joinedload(Match.event),
                joinedload(Match.team1),
                joinedload(Match.team2)
            )
            .filter(
                or_(Team.player1_id == player.id, Team.player2_id == player.id),
                Match.status == "TERMINE"
            )
            .order_by(Match.updated_at.desc())
            .all()
        )

        results = []
        stats = {"total": 0, "wins": 0, "losses": 0}

        for m in matches:
            is_team1 = (m.team1.player1_id == player.id or m.team1.player2_id == player.id)
            winner = self.determine_winner(m)
            
            is_victory = (is_team1 and winner == 1) or (not is_team1 and winner == 2)
            
            if is_victory:
                stats["wins"] += 1
            else:
                stats["losses"] += 1
            stats["total"] += 1

            results.append({
                "id": m.id,
                "date": m.event.event_date,
                "opponent": m.team2.company if is_team1 else m.team1.company,
                "score": m.score_team1 if is_team1 else m.score_team2,
                "result": "VICTOIRE" if is_victory else "DÉFAITE",
                "court": m.court_number
            })

        return {"results": results, "statistics": stats}

    def get_rankings(self) -> Dict[str, List[Dict[str, Any]]]:
        """Calcule le classement général des entreprises"""
        matches = (
            self.db.query(Match)
            .options(joinedload(Match.team1), joinedload(Match.team2))
            .filter(Match.status == "TERMINE")
            .all()
        )
        
        ranking_data = {}

        for m in matches:
            for team in [m.team1, m.team2]:
                if team.company not in ranking_data:
                    ranking_data[team.company] = {
                        "company": team.company, 
                        "points": 0, "played": 0, "wins": 0, "losses": 0, 
                        "sets_won": 0, "sets_lost": 0
                    }

            c1, c2 = m.team1.company, m.team2.company
            t1_sw, t1_sl = self.parse_score(m.score_team1)
            
            # Mise à jour Sets
            ranking_data[c1]["sets_won"] += t1_sw
            ranking_data[c1]["sets_lost"] += t1_sl
            ranking_data[c2]["sets_won"] += t1_sl
            ranking_data[c2]["sets_lost"] += t1_sw
            
            ranking_data[c1]["played"] += 1
            ranking_data[c2]["played"] += 1
            
            winner = self.determine_winner(m)
            if winner == 1:
                ranking_data[c1]["points"] += 3
                ranking_data[c1]["wins"] += 1
                ranking_data[c2]["losses"] += 1
            elif winner == 2:
                ranking_data[c2]["points"] += 3
                ranking_data[c2]["wins"] += 1
                ranking_data[c1]["losses"] += 1
                
        rankings_list = list(ranking_data.values())
        
        # Tri : Points > Victoires > Diff sets > Nom
        rankings_list.sort(key=lambda x: (
            -x["points"], 
            -x["wins"], 
            -(x["sets_won"] - x["sets_lost"]), 
            x["company"]
        ))
        
        for i, row in enumerate(rankings_list):
            row["position"] = i + 1
            
        return {"rankings": rankings_list}