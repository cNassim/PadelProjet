# 🎾 Corpo Padel - Kit de Démarrage

Application de gestion de tournois corporatifs de padel.

## 📦 Contenu

- **Backend** : FastAPI avec authentification JWT
- **Frontend** : VueJS 3 avec Vue Router et Pinia
- **Base de données** : SQLite
- **Tests** : Pytest (backend) + Cypress (frontend)

## 💻 Kit de démarrage fonctionnel

### Backend (FASTAPI)
```
backend/
├── app/
│   ├── api/
│   │   ├── auth.py          ✅ Routes d'authentification
│   │   └── deps.py          ✅ Dépendances (get_current_user)
│   ├── core/
│   │   ├── config.py        ✅ Configuration
│   │   └── security.py      ✅ JWT + hashing
│   ├── models/
│   │   └── models.py        ✅ User + LoginAttempt
│   ├── schemas/
│   │   └── auth.py          ✅ Schémas Pydantic
│   ├── database.py          ✅ Configuration SQLAlchemy
│   └── main.py              ✅ Application FastAPI
├── tests/
│   ├── conftest.py          ✅ Fixtures
│   ├── test_auth.py         ✅ Tests authentification
│   ├── test_security.py     ✅ Tests sécurité
│   └── test_validation.py   ✅ Tests validation
├── .env.example
├── requirements.txt
└── README.md
```

### Frontend (VueJS)
```
frontend/
├── src/
│   ├── components/
│   │   └── NavBar.vue       ✅ Barre de navigation
│   ├── router/
│   │   └── index.js         ✅ Routing avec guards
│   ├── services/
│   │   └── api.js           ✅ Client Axios + intercepteurs
│   ├── stores/
│   │   └── auth.js          ✅ Store Pinia authentification
│   ├── views/
│   │   ├── HomePage.vue     ✅ Page d'accueil
│   │   └── LoginPage.vue    ✅ Page de connexion
│   ├── App.vue
│   └── main.js
├── cypress/
│   ├── e2e/
│   │   ├── auth.cy.js       ✅ Tests E2E auth
│   │   └── navigation.cy.js ✅ Tests navigation
│   └── support/
│       └── commands.js      ✅ Commandes custom
├── .env.example
├── package.json
└── README.md
```

## 🚀 Démarrage rapide

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate sur Windows
pip install -r requirements.txt
cp .env.example .env
# Générer une SECRET_KEY : python -c "import secrets; print(secrets.token_urlsafe(32))"
python -c "from app.database import init_db; init_db()"
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## 🔐 Compte de test

- **Email** : admin@padel.com
- **Mot de passe** : Admin@2025!

## 📚 Documentation

Consultez le cahier des charges complet pour les spécifications détaillées.

## ✅ Fonctionnalités implémentées

- ✅ Authentification JWT
- ✅ Anti-brute force (5 tentatives, blocage 30min)
- ✅ Page d'accueil
- ✅ Page de login
- ✅ Navigation avec guards

## 🎯 À développer

Toutes les autres fonctionnalités selon le cahier des charges :
- Gestion des joueurs, équipes, poules
- Planning et événements
- Matchs et résultats
- Administration
- Profil utilisateur

## 📞 Support

Consultez le README détaillé dans backend/ et frontend/
