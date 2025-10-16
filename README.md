# Formulaire Diagnostic Process

Formulaire en ligne pour qualifier un processus et faciliter la priorisation des cas d'usage avec scoring automatique, synthèses IA et chatbot d'assistance.

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
- Formulaire 21 questions → scoring automatique → récapitulatif
- Autosave dans `localStorage` (aucune donnée envoyée au serveur)
- Export JSON pour archivage

**Backend IA** (`backend/main.py`)
- Proxy FastAPI sécurisé vers OpenAI
- Génère synthèse + recommandations delivery
- Clé API reste côté serveur (jamais exposée au navigateur)

**Flux :** Remplir → Auto-save → Générer synthèse IA → Exporter JSON

---

## 🆕 Nouvelles fonctionnalités

### ✨ Améliorations récentes

1. **Q3 - Exemples d'étapes** : Exemples concrets pour aider à la saisie des étapes clés
2. **Q4 - Enjeux simplifiés** : Réduction de 7 à 5 catégories (regroupement Conformité/Risques, Satisfaction GO/clients)
3. **Q13 - Faisabilité technique** : Recentrage sur les critères techniques d'automatisation (API, règles claires, données structurées)
4. **Q14 - Impacts clarifiés** : Regroupement Qualité/Fiabilité en une seule option
5. **Q15 - Gains économiques** : Distinction claire entre gain de temps ET gain de coût (champs séparés)
6. **Q16 - Impact direct** : Clarification de la notion d'impact direct (première personne impactée)
7. **Q20 - Département** : Liste déroulante avec départements prédéfinis
8. **User Story éditable** : Section dédiée avec génération automatique et champs de validation
9. **Chatbot IA** : Widget flottant en bas à droite pour poser des questions pendant le remplissage
10. **Scoring amélioré** : Séparation claire entre opportunité métier (Q4) et faisabilité technique (Q13)

### 🤖 Assistance IA

- **Chatbot contextuel** : Cliquez sur le bouton 💬 en bas à droite pour poser vos questions
- **Génération User Story** : Bouton dédié dans la section "Scoring & Synthèse"
- **Synthèse intelligente** : Analyse automatique avec recommandations Go/No-Go
- **Delivery automatique** : Génération de roadmap et staffing

---

## 📁 Structure

```
/
├── index.html       # Formulaire (21 questions, 4 blocs)
├── styles.css       # Styles modernes, responsive
├── script.js        # Autosave, scoring, navigation, IA
└── backend/
    ├── main.py          # API FastAPI (proxy OpenAI)
    ├── requirements.txt # Dépendances Python
    └── .env            # Clé OpenAI (à créer, ignoré par git)
```

---

## 🛠️ Personnalisation

- **Lien Coach IA** : dans `script.js`, modifiez `coach-ia@exemple.com`
- **Thème** : adaptez les variables CSS dans `styles.css` (`:root`)
- **Modèle OpenAI** : dans `backend/.env`, ajoutez `OPENAI_MODEL=gpt-4o`

---

## 📊 Données

Les données sont stockées localement (`localStorage`, clé `cm_form_pd_v1`). Aucun envoi réseau sans action explicite sur "Générer".


