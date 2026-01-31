# 🏸 **PadelProject - Application de Gestion de Tournois de Padel**

---

> <img src="https://img.shields.io/badge/Vue.js-Frontend-42b883?style=flat-square"/>  
> <img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=flat-square"/>  
> <img src="https://img.shields.io/badge/SQLite-Database-003B57?style=flat-square"/>  
> <img src="https://img.shields.io/badge/TailwindCSS-Styling-38B2AC?style=flat-square"/>

---

## 📄 **Introduction**

PadelProject est une application web complète de gestion de tournois de padel d'entreprise. Elle permet de gérer les joueurs, les équipes, les poules, le planning des matchs et les résultats.

---

## 🏗️ **Architecture du Projet**

```
PadelProjet/
├── backend/                    # API REST FastAPI
│   ├── app/
│   │   ├── api/               # Routes/Endpoints de l'API
│   │   ├── core/              # Configuration & Sécurité (JWT, hashing)
│   │   ├── models/            # Modèles SQLAlchemy (ORM)
│   │   ├── schemas/           # Schémas Pydantic (validation)
│   │   ├── services/          # Logique métier
│   │   ├── database.py        # Configuration base de données
│   │   └── main.py            # Point d'entrée FastAPI
│   ├── tests/                 # Tests unitaires PyTest
│   └── requirements.txt       # Dépendances Python
│
├── frontend/                   # Application Vue.js
│   ├── src/
│   │   ├── views/             # Pages de l'application
│   │   ├── components/        # Composants réutilisables
│   │   ├── services/          # Appels API (Axios)
│   │   ├── stores/            # Gestion d'état (Pinia)
│   │   ├── router/            # Configuration des routes
│   │   └── assets/            # Ressources statiques
│   ├── cypress/               # Tests E2E Cypress
│   └── package.json           # Dépendances Node.js
│
└── README.md
```

### 🔧 **Stack Technique**

| Couche | Technologie |
|--------|-------------|
| **Frontend** | Vue.js 3 + Vite + TailwindCSS + Pinia |
| **Backend** | FastAPI + SQLAlchemy + Pydantic |
| **Base de données** | SQLite |
| **Authentification** | JWT (JSON Web Tokens) |
| **Tests** | PyTest (backend) + Cypress (E2E) |

---

## 🔐 **Comptes par Défaut**

| Rôle | Email | Mot de passe |
|------|-------|--------------|
| 🔴 **Administrateur** | `admin@padel.com` | `Admin@2025!` |
| 🟢 **Joueur** | `joueur1@test.com` | `User@2025!` |

> **Note** : Ces comptes sont créés automatiquement lors de l'initialisation de la base de données via `seed_data.py`.

---

## 🌳 **Structure des Branches**

| Branch      | Color | Description |
|-------------|:-----:|-------------|
| ![#e74c3c](https://placehold.co/15x15/e74c3c/e74c3c.png) `Master`      | 🔴 | La version stable du projet. No direct commits allowed! |
| ![#2980b9](https://placehold.co/15x15/2980b9/2980b9.png) `Development` | 🔵 | Branche active pour modifications et tests.             |
| ![#f1c40f](https://placehold.co/15x15/f1c40f/f1c40f.png) `Features`    | 🟡 | Une branche par fonctionnalité, créée depuis `Development`. |
| ![#8e44ad](https://placehold.co/15x15/8e44ad/8e44ad.png) `Release`     | 🟣 | Branche pour merger `Development` vers `Master` (résolution de conflits). |

---

## 🚀 **Lancement du Projet**

### Backend
```bash
cd backend
pip install -r requirements.txt
python seed_data.py          # Initialisation de la BDD
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 💡 **Fonctionnalités**

- ✅ Gestion des joueurs (CRUD)
- ✅ Gestion des équipes (2 joueurs par équipe)
- ✅ Système de poules
- ✅ Planning des matchs
- ✅ Saisie des scores
- ✅ Classement automatique
- ✅ Authentification JWT (Admin / Joueur)
- ✅ Protection des routes par rôle

---

> _"Great code is not just written, it is well managed."_ 💎
