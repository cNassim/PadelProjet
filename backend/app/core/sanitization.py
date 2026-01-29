# ============================================
# FICHIER : backend/app/core/sanitization.py
# Protection contre les attaques XSS
# ============================================

import bleach

def sanitize_input(text: str) -> str:
    """
    Sanitize les entrées textuelles pour prévenir les attaques XSS.
    
    Supprime tous les tags HTML et échappe les caractères spéciaux.
    
    Args:
        text: Le texte à nettoyer
        
    Returns:
        Le texte nettoyé sans aucun tag HTML
    """
    if text is None:
        return None
    return bleach.clean(text, tags=[], strip=True)


def sanitize_dict(data: dict, fields: list) -> dict:
    """
    Sanitize plusieurs champs d'un dictionnaire.
    
    Args:
        data: Dictionnaire contenant les données
        fields: Liste des champs à sanitizer
        
    Returns:
        Le dictionnaire avec les champs nettoyés
    """
    for field in fields:
        if field in data and data[field] is not None:
            data[field] = sanitize_input(str(data[field]))
    return data
