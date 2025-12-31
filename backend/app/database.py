from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}  # Nécessaire pour SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Générateur de session de base de données"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialise la base de données avec un admin et un utilisateur par défaut"""
    from app.models.models import User
    from app.core.security import get_password_hash
    
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # ✅ FIX 1: Vérifier si un admin existe déjà
        admin = db.query(User).filter(User.email == "admin@padel.com").first()
        if not admin:
            admin = User(
                email="admin@padel.com",
                password_hash=get_password_hash("Admin@2025!"),
                role="ADMINISTRATEUR",
                is_active=True
            )
            db.add(admin)
            db.commit()
            print("✅ Admin créé : admin@padel.com / Admin@2025!")
        else:
            print("ℹ️  Admin existe déjà")
        
        # ✅ FIX 2: Vérifier si l'utilisateur de test existe déjà
        # NE PAS réutiliser la variable "User" (qui est la classe)
        user = db.query(User).filter(User.email == "pierre.dubois@datalab.com").first()
        if not user:
            user = User(
                email="pierre.dubois@datalab.com",
                password_hash=get_password_hash('I!H9"5"l}4R)m<^h'),  # ✅ FIX 3: Échapper les guillemets
                role="JOUEUR",
                is_active=True
            )
            db.add(user)
            db.commit()
            print('✅ Utilisateur créé : pierre.dubois@datalab.com / I!H9"5"l}4R)m<^h')
        else:
            print("ℹ️  Utilisateur existe déjà")
    finally:
        db.close()