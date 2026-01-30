from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.models import User, Player
from app.core.security import verify_password, get_password_hash
from app.core.sanitization import sanitize_input
from app.core.upload import save_upload_file, delete_upload_file

class ProfileService:
    @staticmethod
    def get_full_profile(db: Session, user: User):
        """Récupère l'utilisateur et son profil joueur associé"""
        player = db.query(Player).filter(Player.user_id == user.id).first()
        return user, player

    @staticmethod
    def update_user_profile(db: Session, user: User, data):
        """Met à jour les infos de compte et de joueur"""
        player = db.query(Player).filter(Player.user_id == user.id).first()
        
        # Validation de l'email unique
        if data.email and data.email != user.email:
            existing = db.query(User).filter(User.email == data.email, User.id != user.id).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="Cet email est déjà utilisé par un autre compte"
                )
            user.email = data.email

        # Mise à jour des champs joueur
        if player:
            if data.first_name is not None: 
                player.first_name = sanitize_input(data.first_name)
            if data.last_name is not None: 
                player.last_name = sanitize_input(data.last_name)
            if data.birth_date is not None: 
                player.birth_date = data.birth_date
            # On enregistre la chaîne Base64 telle quelle
            if hasattr(data, 'photo_url') and data.photo_url is not None:
                player.photo_url = data.photo_url

        db.commit()
        db.refresh(user)
        if player: 
            db.refresh(player)
        return user, player

    @staticmethod
    def update_password(db: Session, user: User, data):
        """Logique de changement de mot de passe avec vérifications de sécurité"""
        if not verify_password(data.current_password, user.password_hash):
            raise HTTPException(status_code=400, detail="Le mot de passe actuel est incorrect")
        
        if data.new_password != data.confirm_password:
            raise HTTPException(status_code=400, detail="Les nouveaux mots de passe ne correspondent pas")
            
        if verify_password(data.new_password, user.password_hash):
            raise HTTPException(status_code=400, detail="Le nouveau mot de passe doit être différent de l'ancien")

        user.password_hash = get_password_hash(data.new_password)
        # On désactive le flag si l'utilisateur devait obligatoirement changer son pass
        user.must_change_password = False
        db.commit()

    @staticmethod
    async def handle_photo_upload(db: Session, user: User, photo_data: str):
        player = db.query(Player).filter(Player.user_id == user.id).first()
        
        if not player:
            raise HTTPException(status_code=403, detail="Fonctionnalité réservée aux joueurs")
        
        player.photo_url = photo_data
        db.commit()
        db.refresh(player)
        
        # On retourne un dictionnaire qui match exactement PhotoUploadResponse
        return {
            "message": "Photo mise à jour avec succès",
            "photo_url": player.photo_url
        }

    @staticmethod
    def handle_photo_delete(db: Session, user: User):
        player = db.query(Player).filter(Player.user_id == user.id).first()
        
        if not player or not player.photo_url:
            raise HTTPException(status_code=404, detail="Aucune photo à supprimer")
        
        player.photo_url = None
        db.commit()
        
        # On retourne un dictionnaire qui match PhotoDeleteResponse
        return {"message": "Photo supprimée avec succès"}