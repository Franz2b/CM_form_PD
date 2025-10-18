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

**📊 3. Impact (7 questions)**
- Fréquence du besoin
- Nombre d'exécutions par occurrence
- Temps d'exécution unitaire  
- Nombre de personnes exécutantes
- Niveau d'irritant/urgence (+ pourquoi irritant/urgent)
- *Permet de calculer l'impact total*

**🔧 4. Faisabilité (5 questions)**
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
1. **Nom du projet** - Généré par l'IA (3-6 mots)
2. **User Story** (HTML, max 100 mots avec contexte) - "En tant que..., j'ai besoin de..., afin de..."
3. **Schéma d'exécution** (Diagramme ASCII uniquement)
4. **Éléments sources** (catégorisés, nb types uniques, complexité)
5. **Scoring sur 100** (Low/Mid/High par critère + score total)
6. **Pro/Con** (Arguments pour et contre avec poids)
7. **Plan de delivery** (Phases avec features + risques)
8. **Quick wins** (Actions utilisateur "En attendant...")

---

## 🎯 Grille de Scoring sur 100 points

### Formule générale

```
SCORE TOTAL = Impact Business (40) + Faisabilité Technique (30) + Urgence (30)
```

---

### 1️⃣ IMPACT BUSINESS (/40 points max)

Mesure l'impact métier de l'automatisation.

#### Q7 - Fréquence du besoin (max 10 pts)

| Réponse | Points |
|---------|--------|
| Plusieurs fois par jour | 10 |
| Quotidien | 10 |
| Hebdomadaire | 7 |
| Mensuel | 4 |
| Occasionnel | 2 |

#### Q8 - Nb d'exécutions par occurrence (max 10 pts)

| Réponse | Points |
|---------|--------|
| 200+ | 10 |
| 51-200 | 7 |
| 11-50 | 5 |
| 2-10 | 3 |
| 1 | 1 |

#### Q9 - Temps d'exécution unitaire (max 10 pts)

| Réponse | Points |
|---------|--------|
| > 2h | 10 |
| 1-2h | 7 |
| 30 min - 1h | 5 |
| 10-30 min | 3 |
| < 10 min | 1 |

#### Q10 - Nb de personnes exécutantes (max 10 pts)

| Réponse | Points |
|---------|--------|
| 50+ | 10 |
| 21-50 | 7 |
| 6-20 | 5 |
| 2-5 | 3 |
| 1 | 1 |

**Total Impact Business = Fréquence + NbExec + Temps + Personnes** (max 40 pts)

---

### 2️⃣ FAISABILITÉ TECHNIQUE (/30 points max)

Mesure la facilité d'automatiser.

#### Q17 - Règles simples et stables (max 10 pts)

| Réponse | Points |
|---------|--------|
| Oui — Règles claires et stables | 10 |
| Partiellement — Quelques cas particuliers | 6 |
| Non — Beaucoup d'exceptions | 2 |

#### Types de sources (IA) - count (max 10 pts)

| Nb de types différents | Points |
|------------------------|--------|
| 1-2 types | 10 |
| 3-4 types | 6 |
| 5+ types | 2 |

**⚠️ Variable calculée par l'IA** : Analyse de Q14. Plus il y a de types différents (Excel, PDF, SAP...), plus c'est complexe.

#### Q19 - Complexité organisationnelle (max 7 pts)

| Réponse | Points |
|---------|--------|
| Simple — Une personne seule | 7 |
| Moyenne — Validation d'une autre personne | 4 |
| Complexe — Coordination multi-personnes | 1 |

#### Q15 - Action manuelle (max 3 pts)

| Réponse | Points |
|---------|--------|
| Non | 3 |
| Oui | 0 |

**Total Faisabilité = Q17 + count(IA) + Q19 + Q15** (max 30 pts)

---

### 3️⃣ URGENCE (/30 points max)

Mesure le niveau d'urgence ressenti.

#### Q11 - Niveau d'irritant/urgence (max 30 pts)

| Réponse | Calcul | Points |
|---------|--------|--------|
| 5 — Bloquant | 5 × 6 | 30 |
| 4 — Critique | 4 × 6 | 24 |
| 3 — Important | 3 × 6 | 18 |
| 2 — Modéré | 2 × 6 | 12 |
| 1 — Faible gêne | 1 × 6 | 6 |

**Total Urgence = Irritant × 6** (max 30 pts)

---

### 📊 Exemple de calcul complet

**Contexte :**
- Q7 : Tâche quotidienne
- Q8 : 51-200 factures par occurrence
- Q9 : 10-30 min par facture
- Q10 : 2-5 personnes
- Q17 : Règles claires (Oui)
- count (IA) : 3 types de sources (PDF, Excel, SAP)
- Q19 : Complexité orga moyenne
- Q15 : Action manuelle (Oui)
- Q11 : Irritant 4/5

**Calcul :**
```
IMPACT BUSINESS
  Q7 Fréquence (Quotidien) = 10
  Q8 NbExec (51-200) = 7
  Q9 Temps (10-30min) = 3
  Q10 Personnes (2-5) = 3
  → Sous-total = 23/40

FAISABILITÉ TECHNIQUE
  Q17 Règles (Oui) = 10
  count TypesSources (3 types) = 6  ← Calculé par IA depuis Q14
  Q19 ComplexitéOrga (Moyenne) = 4
  Q15 ActionManuelle (Oui) = 0
  → Sous-total = 20/30

URGENCE
  Q11 Irritant (4 × 6) = 24/30

SCORE TOTAL = 23 + 20 + 24 = 67/100 → 🟡 À challenger
```

---

### 🎯 Interprétation des scores

| Score | Catégorie | Action recommandée |
|-------|-----------|-------------------|
| **70-100** | 🟢 Quick win | Priorité maximale - À lancer rapidement |
| **45-69** | 🟡 À challenger | À étudier - Bon potentiel avec contraintes |
| **0-44** | 🔴 Long shot | Faible priorité - Impact faible ou trop complexe |

---

### ✅ Vérification cohérence

- Impact Business : 10 + 10 + 10 + 10 = **40 pts max** ✓
- Faisabilité Technique : 10 + 10 + 7 + 3 = **30 pts max** ✓
- Urgence : 5 × 6 = **30 pts max** ✓
- **TOTAL : 100 pts max** ✓

**📖 Voir aussi [SCORING.md](SCORING.md) pour plus de détails**

---

## 📁 Structure

```
/
├── index.html       # Formulaire (16+4 questions, 6 pages)
├── styles.css       # Styles modernes, fond blanc
├── script.js        # Autosave, navigation, appel IA
├── SCORING.md       # 📊 GRILLE DE SCORING COMPLÈTE
└── backend/
    ├── main.py              # API FastAPI
    ├── models.py            # Modèles Pydantic + Enums stricts
    ├── requirements.txt     # Dépendances Python
    ├── .env                 # Clé OpenAI (à créer, ignoré par git)
    ├── use_cases/           # Use cases sauvegardés (auto)
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


