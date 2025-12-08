# ============================================
# FICHIER : backend/app/api/results.py
# ============================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.api import deps
from app.models.models import Match, Player, Team, User

router = APIRouter()

def parse_score(score_str: str):
    """
    Parse un score de type '6-4, 2-6, 6-3'
    Retourne (sets_gagnes, sets_perdus)
    """
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

def determine_winner(match):
    """
    Retourne 1 si équipe 1 gagne, 2 si équipe 2 gagne, 0 sinon
    """
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
    
    s1_won, s1_lost = parse_score(match.score_team1)
    
    if s1_won > s1_lost:
        return 1
    elif s1_lost > s1_won:
        return 2
    return 0

@router.get("/my-results")
def get_my_results(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Historique des matchs TERMINÉS du joueur connecté + Stats
    """
    # 1. Trouver le joueur
    player = db.query(Player).filter(Player.user_id == current_user.id).first()
    if not player:
        return {"results": [], "statistics": {"total": 0, "wins": 0, "losses": 0}}

    # 2. Trouver les matchs terminés
    # On cherche les équipes où le joueur est présent
    matchs = db.query(Match).join(Team, or_(Match.team1_id == Team.id, Match.team2_id == Team.id)).filter(
        or_(Team.player1_id == player.id, Team.player2_id == player.id),
        Match.status == "TERMINE"
    ).order_by(Match.updated_at.desc()).all()

    results = []
    stats = {"total": 0, "wins": 0, "losses": 0}

    for m in matchs:
        # Identifier si le joueur est dans l'équipe 1 ou 2
        is_team1 = (m.team1.player1_id == player.id or m.team1.player2_id == player.id)
        
        # Déterminer vainqueur
        winner = determine_winner(m)
        
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

    return {"results": results, "statistics": stats}


@router.get("/rankings")
def get_rankings(db: Session = Depends(get_db)):
    """
    Classement général des entreprises
    Règles: Victoire 3pts, Défaite 0pt.
    Tri: Points > Victoires > Diff sets > Alphabétique
    """
    # Récupérer tous les matchs terminés
    matches = db.query(Match).filter(Match.status == "TERMINE").all()
    
    # Structure: { "NomEntreprise": { points, played, wins, losses, sets_won, sets_lost } }
    ranking_data = {}

    def init_company(name):
        if name not in ranking_data:
            ranking_data[name] = {
                "company": name, 
                "points": 0, "played": 0, "wins": 0, "losses": 0, 
                "sets_won": 0, "sets_lost": 0
            }

    for m in matches:
        c1 = m.team1.company
        c2 = m.team2.company
        init_company(c1)
        init_company(c2)
        
        # Stats sets (basé sur score_team1 qui est ex: "6-4, 6-3")
        # team1 sets
        t1_sw, t1_sl = parse_score(m.score_team1)
        # team2 sets (inverse)
        t2_sw, t2_sl = t1_sl, t1_sw 

        # Mise à jour Sets
        ranking_data[c1]["sets_won"] += t1_sw
        ranking_data[c1]["sets_lost"] += t1_sl
        ranking_data[c2]["sets_won"] += t2_sw
        ranking_data[c2]["sets_lost"] += t2_sl
        
        # Points & Victoires
        winner = determine_winner(m)
        
        ranking_data[c1]["played"] += 1
        ranking_data[c2]["played"] += 1
        
        if winner == 1:
            ranking_data[c1]["points"] += 3
            ranking_data[c1]["wins"] += 1
            ranking_data[c2]["losses"] += 1
        elif winner == 2:
            ranking_data[c2]["points"] += 3
            ranking_data[c2]["wins"] += 1
            ranking_data[c1]["losses"] += 1
            
    # Transformation en liste et tri
    rankings_list = list(ranking_data.values())
    
    # Tri multi-critères (Python sort est stable, on trie du moins prioritaire au plus prioritaire ou avec tuple)
    # Tuple (-points, -wins, -(sets_won - sets_lost), company_name)
    rankings_list.sort(key=lambda x: (
        -x["points"], 
        -x["wins"], 
        -(x["sets_won"] - x["sets_lost"]), 
        x["company"]
    ))
    
    # Ajouter la position
    for i, row in enumerate(rankings_list):
        row["position"] = i + 1
        
    return {"rankings": rankings_list}