# ============================================
# FICHIER : backend/app/core/upload.py
# ============================================

import os
import secrets
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException, status
from PIL import Image
import aiofiles

# Configuration
UPLOAD_DIR = Path("uploads/profiles")
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}
RECOMMENDED_SIZE = (400, 400)  # Dimensions recommandées


def get_file_extension(filename: str) -> str:
    """Extraire l'extension du fichier"""
    return Path(filename).suffix.lower()


def is_allowed_file(filename: str, content_type: str) -> bool:
    """
    Vérifier si le fichier est autorisé
    - Extension doit être .jpg, .jpeg ou .png
    - Type MIME doit être image/jpeg ou image/png
    """
    extension = get_file_extension(filename)
    return extension in ALLOWED_EXTENSIONS and content_type in ALLOWED_MIME_TYPES


def generate_unique_filename(original_filename: str) -> str:
    """
    Générer un nom de fichier unique et sécurisé
    Format : {random_token}_{timestamp}{extension}
    """
    extension = get_file_extension(original_filename)
    random_token = secrets.token_hex(16)
    import time
    timestamp = int(time.time())
    return f"{random_token}_{timestamp}{extension}"


async def validate_image_file(file: UploadFile) -> None:
    """
    Valider le fichier image
    - Vérifier l'extension et le type MIME
    - Vérifier la taille du fichier
    - Vérifier que c'est une vraie image (avec PIL)
    """
    
    # Vérifier l'extension et le type MIME
    if not is_allowed_file(file.filename, file.content_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Format de fichier non autorisé. Formats acceptés : {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Lire le contenu du fichier
    content = await file.read()
    file_size = len(content)
    
    # Vérifier la taille
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Fichier trop volumineux. Taille maximale : {MAX_FILE_SIZE // (1024 * 1024)} MB"
        )
    
    # Vérifier que c'est une vraie image (protection contre les faux fichiers)
    try:
        image = Image.open(file.file)
        image.verify()  # Vérifie l'intégrité de l'image
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le fichier n'est pas une image valide"
        )
    
    # Remettre le pointeur au début pour la sauvegarde
    await file.seek(0)


async def save_upload_file(file: UploadFile) -> str:
    """
    Sauvegarder le fichier uploadé
    
    Returns:
        str: Chemin relatif du fichier sauvegardé (ex: /uploads/profiles/xxx.jpg)
    """
    
    # Valider le fichier
    await validate_image_file(file)
    
    # Créer le dossier si nécessaire
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    # Générer un nom de fichier unique
    unique_filename = generate_unique_filename(file.filename)
    file_path = UPLOAD_DIR / unique_filename
    
    # Sauvegarder le fichier de manière asynchrone
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # Retourner le chemin relatif (URL)
    return f"/uploads/profiles/{unique_filename}"

