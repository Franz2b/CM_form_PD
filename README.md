# Formulaire Process Designer

Formulaire d'interview utilisateur pour capturer les besoins d'automatisation et générer des user stories avec analyse IA structurée (Structured Outputs OpenAI).

## 🚀 Lancer l'application

### 1️⃣ Terminal 1 — Backend IA
```bash
cd /Users/francoisvivarelli/Documents/Dev/CM/CM_form_PD/backend
pip install -r requirements.txt  # Première fois seulement
uvicorn main:app --host 0.0.0.0 --port 5050
```

### 2️⃣ Terminal 2 — Ouvrir l'app
```bash
open /Users/francoisvivarelli/Documents/Dev/CM/CM_form_PD/index.html
```

### 3️⃣ Dans l'interface web
- Cliquez sur **⚙️ Paramètres IA**
- URL backend : `http://localhost:5050/ai`
- Cliquez **Sauvegarder**

---

## 🔑 Configuration clé OpenAI (première fois)

La clé API OpenAI doit être dans `/backend/.env` :

```bash
cd /Users/francoisvivarelli/Documents/Dev/CM/CM_form_PD/backend
echo "OPENAI_API_KEY=sk-votre-clé-ici" > .env
```

✅ Le fichier `.env` est protégé par `.gitignore` (jamais versionné)

---

## 💡 Comment ça fonctionne

**Frontend** (`index.html` + `script.js` + `styles.css`)
- Formulaire 16 questions (+ 4 conditionnelles) → Interview utilisateur guidée
- Autosave dans `localStorage` (aucune donnée envoyée sans action)
- Récapitulatif complet en temps réel

**Backend IA** (`backend/main.py` + `backend/models.py`)
- FastAPI avec **OpenAI Structured Outputs**
- Endpoint `/analyze` : Analyse structurée avec JSON **strictement validé**
- Modèles Pydantic avec **Enums** pour garantir catégories fixes
- Clé API côté serveur uniquement

**Architecture Structured Outputs :**
1. Schéma Pydantic définit structure JSON exacte
2. OpenAI **ne peut pas** dévier du schéma (mode `strict: True`)
3. Catégories **forcées** par Enums (impossible d'inventer)
4. Validation double : OpenAI + Pydantic

**Flux :** Remplir → Auto-save → Analyser (IA) → User story + Schéma + Analyse

---

## 🆕 Structure du formulaire

### 📋 16 questions principales (+ 4 conditionnelles)

**👤 1. Persona (4 questions)**
- Nom, Prénom, Rôle/Fonction, Département
- *Capture l'utilisateur final qui bénéficiera de l'automatisation*

**💡 2. Contexte & Besoin (2 questions)**
- Brief utilisateur (texte libre avec guide)
- Exécution actuelle de la tâche (texte libre)
- *L'IA analysera automatiquement les pain points et bénéfices*

**📊 3. Volumétrie & Impact (7 questions)**
- Fréquence du besoin
- Nombre d'exécutions par occurrence
- Temps d'exécution unitaire  
- Nombre de personnes exécutantes
- Niveau d'irritant/urgence (+ pourquoi irritant/urgent)
- *Permet de calculer l'impact total*

**🔧 4. Nature de la tâche (5 questions)**
- Éléments sources (Excel, PDF, papier...)
- Action manuelle ? (+ exemple)
- Règles simples ? (+ exemple complexité)
- Complexité organisationnelle
- Outils nécessaires
- *Permet d'évaluer la faisabilité technique*

**👀 5. Synthèse**
- Analyse IA structurée
- Récapitulatif complet

---

## 🤖 Analyse IA avec Structured Outputs

### Garanties
✅ **Structure JSON fixe** - Toujours les mêmes champs
✅ **Catégories strictes** - Enums Python (impossible d'inventer)
✅ **Validation automatique** - Pydantic + OpenAI
✅ **Comparabilité** - Tous les use cases analysés de la même façon

### Résultats de l'analyse
1. **User Story** (HTML, max 100 mots) - "En tant que..., j'ai besoin de..., afin de..."
2. **Schéma d'exécution** (ASCII diagram + liste d'étapes)
3. **Éléments sources** (catégorisés, comptés, niveau de complexité)
4. **Analyse** (pain points, bénéfices, score de faisabilité 0-100, priorité)

---

## 📁 Structure

```
/
├── index.html       # Formulaire (16+4 questions, 5 pages)
├── styles.css       # Styles modernes, fond blanc
├── script.js        # Autosave, navigation, appel IA
└── backend/
    ├── main.py              # API FastAPI
    ├── models.py            # Modèles Pydantic + Enums stricts
    ├── requirements.txt     # Dépendances Python
    ├── .env                 # Clé OpenAI (à créer, ignoré par git)
    └── README_ANALYSIS.md   # Documentation analyse IA
```

---

## 🛠️ Personnalisation

- **Lien Coach IA** : dans `script.js`, modifiez `coach-ia@exemple.com`
- **Thème** : adaptez les variables CSS dans `styles.css` (`:root`)
- **Modèle OpenAI** : dans `backend/.env`, ajoutez `OPENAI_MODEL=gpt-4o`

---

## 📊 Données

Les données sont stockées localement (`localStorage`, clé `cm_form_pd_v1`). Aucun envoi réseau sans action explicite sur "Générer".


