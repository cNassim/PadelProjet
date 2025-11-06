# 🌈 **Welcome to the PadelProject Repository!**

---

> <img src="https://img.shields.io/badge/rules-important-red?style=flat-square"/>  
> <img src="https://img.shields.io/badge/branches-structure-blue?style=flat-square"/>  
> <img src="https://img.shields.io/badge/commits-gitemoji-yellow?style=flat-square"/>  
> <img src="https://img.shields.io/badge/code%20style-conventions-green?style=flat-square"/>

---

## 📄 **Introduction**

> _This ReadMe is made for you, to show you how to use this git repo._  
> **You are obliged to follow these rules!** Otherwise, you are responsible for any issues.  
> These rules keep our project clear and understandable for us and our supervisor.

---

## 🌳 **Branch Rules**

| Branch      | Color | Description |
|-------------|:-----:|-------------|
| ![#e74c3c](https://placehold.co/15x15/e74c3c/e74c3c.png) `Master`      | 🔴 | La version stable du projet. No direct commits allowed! |
| ![#2980b9](https://placehold.co/15x15/2980b9/2980b9.png) `Development` | 🔵 | Branche active pour modifications et tests.             |
| ![#f1c40f](https://placehold.co/15x15/f1c40f/f1c40f.png) `Features`    | 🟡 | Une branche par fonctionnalité, créée depuis `Development`. |
| ![#8e44ad](https://placehold.co/15x15/8e44ad/8e44ad.png) `Release`     | 🟣 | Branche pour merger `Development` vers `Master` (résolution de conflits). |


---

## 🎨 **How to Use Branches?**

- **Master branch:**  
  **No one is allowed** to commit without prior approval. Only stable versions live here.

- **Development branch:**  
  Merge your features here for testing before merging to master.

- **Feature branches:**  
  Each new feature goes in its own branch, branched from `Development`.  
  When complete, merge back into `Development`.  
  🚫 **Never merge a feature directly into master!**

- **Release branch:**  
  Use this branch to resolve conflicts before merging to master.

---

## 📝 **Commit Rules**

> <img src="https://img.shields.io/badge/commit%20title-gitemoji-orange?style=flat-square"/>
> <img src="https://img.shields.io/badge/commit%20tags-required-magenta?style=flat-square"/>

All commits/merges **must be approved by me** before being published or confirmed.

### 🏷️ **Commit Title Format**

```
✨ [fonc] Ajouter la fonctionnalité de login
🐛 [corr] Corriger le bug d’affichage
♻️ [reus] Refactoriser la gestion des utilisateurs
```

#### **Available Tags**

| Tag      | Color | Usage                                         |
|----------|:-----:|-----------------------------------------------|
| [fonc]   | 🟩    | Ajout d’une fonctionnalité                    |
| [modif]  | 🟦    | Modification d’une fonctionnalité             |
| [supp]   | 🟥    | Suppression d’une fonctionnalité ou fichier   |
| [corr]   | 🟨    | Correction d’un bug                           |
| [reus]   | 🟪    | Refactor (réunisage) du code                  |
| [autr]   | ⬜    | Autre (si aucun tag ne correspond)            |

---

## 🗒️ **Commit Description**

In your commit description, **always explain**:

- **What you did:**  
  _Describe the changes you made._
- **Why you did it:**  
  _Justify the reason behind the modification._
- **How files were modified:**  
  _List and explain changes to files._

---

## 🧑‍💻 **Code Style**

All code **must follow the naming conventions** that will be provided to you.  
Please ask for the latest conventions if you are unsure.

---

## 💡 **Summary**

By following these rules, we keep our project organized, clear, and ready for review by our supervisor.  
**Thank you for your collaboration!**

---

> _“Great code is not just written, it is well managed.”_ 💎
