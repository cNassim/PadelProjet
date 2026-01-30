# ============================================
# FICHIER : backend/app/api/results.py
# ============================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.api import deps
from app.models.models import Match, User
from app.services.results_service import ResultService

router = APIRouter()


@router.get("/my-results")
def get_my_results(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Historique des matchs TERMINÉS du joueur connecté + Stats"""
    service = ResultService(db)
    return service.get_player_results(current_user.id)

@router.get("/rankings")
def get_rankings(db: Session = Depends(get_db)):
    """Classement général des entreprises"""
    service = ResultService(db)
    return service.get_rankings()






