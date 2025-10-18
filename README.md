# 🎯 Formulaire Process Designer - Analyse IA de Use Cases

Application web d'interview utilisateur pour capturer les besoins d'automatisation et générer automatiquement des analyses structurées avec IA (OpenAI Structured Outputs).

## 🚀 Démarrage Rapide

### Prérequis
- Python 3.8+
- Clé API OpenAI

### Installation

1. **Cloner le repository**
```bash
git clone <votre-repo>
cd CM_form_PD
```

2. **Configurer le backend**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Sur Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configurer la clé OpenAI**
```bash
# Créer le fichier .env dans backend/
echo "OPENAI_API_KEY=sk-votre-clé-ici" > .env
```

4. **Lancer le backend**
```bash
uvicorn main:app --host 0.0.0.0 --port 5050
```

5. **Ouvrir l'application**
```bash
# Dans un nouveau terminal, depuis la racine du projet
open index.html  # ou double-cliquer sur index.html
```

Le backend doit être accessible sur `http://localhost:5050`

## 💡 Fonctionnalités

### Formulaire Intelligent
- **20 questions structurées** (Persona, Contexte, Impact, Faisabilité)
- **Auto-save** dans le navigateur (localStorage)
- **Navigation guidée** avec validation
- **Récapitulatif temps réel**

### Analyse IA Automatique
✨ **Génération automatique :**
- 📝 **Nom du projet** et **User Story** (format Product Owner)
- 📊 **Schéma d'exécution** (diagramme ASCII)
- 🔧 **Classification des sources** (Standard, Intermédiaire, Complexe, Non standardisée)
- 💰 **Gain de temps estimé** (heures/mois + ETP)
- 💵 **Calcul du coût annuel** (avec saisie coût horaire)
- 🎯 **Scoring algorithmique** (Impact Business, Faisabilité, Urgence)
- 📈 **Graphique 2D** (Faisabilité × ETP avec zones colorées)
- 🚀 **Plan de delivery** (POC, MVP, MVP+, Production)

### Scoring Déterministe
- **Impact Business** (40 pts) : Calculé sur le gain de temps mensuel (fréquence × exécutions × durée × personnes)
- **Faisabilité Technique** (30 pts) : Basé sur les règles métier, nombre de sources, complexité organisationnelle
- **Urgence** (30 pts) : Niveau d'irritant ressenti

📖 [**Guide complet du scoring**](scoring_guide.html) — Documentation détaillée avec exemples

## 🏗️ Architecture

### Frontend
- **HTML/CSS/JS** pur (aucune dépendance)
- Interface responsive et moderne
- Graphique canvas pour visualisation

### Backend (FastAPI)
- **OpenAI Structured Outputs** : JSON strictement validé
- **Pydantic Models** : Validation de schéma avec Enums
- **Auto-sauvegarde** : Use cases sauvegardés automatiquement
- **Scoring algorithmique** : Calculs déterministes côté serveur

## 📁 Structure du Projet

```
/
├── index.html              # Interface principale
├── scoring_guide.html      # Documentation scoring
├── script.js              # Logique frontend
├── styles.css             # Styles
├── media/
│   └── trident.png        # Favicon
└── backend/
    ├── main.py            # API FastAPI + logique scoring
    ├── models.py          # Modèles Pydantic (schémas stricts)
    ├── requirements.txt   # Dépendances Python
    ├── ENV_EXAMPLE.txt    # Template configuration
    └── use_cases/         # Use cases sauvegardés (JSON)
        └── example_use_case.json
```

## 🔧 Configuration Avancée

### Variables d'environnement (backend/.env)
```bash
# Obligatoire
OPENAI_API_KEY=sk-...

# Optionnel (défaut: gpt-4o-mini)
OPENAI_MODEL=gpt-4o-mini
```

### Modèles OpenAI supportés
- `gpt-4o-mini` (recommandé, rapide et économique)
- `gpt-4o` (plus puissant, plus coûteux)

## 📊 Données et Sécurité

### Stockage Local
- Les données du formulaire sont sauvegardées dans le navigateur (`localStorage`)
- Aucune donnée envoyée au serveur tant que l'utilisateur ne clique pas sur "Lancer l'analyse IA"

### Sauvegarde Serveur
- Les use cases analysés sont automatiquement sauvegardés dans `backend/use_cases/`
- Format: `YYYYMMDD_HHMMSS_NomPrenom.json`
- Clés descriptives dans le JSON (ex: `persona.nom` au lieu de `q1`)

### Confidentialité
- La clé OpenAI est stockée côté serveur uniquement (jamais exposée au frontend)
- Le fichier `.env` est ignoré par git (`.gitignore`)

## 🚢 Déploiement

### Backend (FastAPI)
Déployable sur :
- **Heroku** : `Procfile` avec `web: uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- **Railway/Render** : Configuration auto-détectée
- **AWS/GCP/Azure** : Container Docker recommandé

### Frontend
Déployable sur :
- **GitHub Pages** : HTML/CSS/JS statique
- **Netlify/Vercel** : Déploiement automatique depuis git
- **Serveur web** : Nginx, Apache, ou simple HTTP server

**Note** : Configurer l'URL du backend dans l'interface (⚙️ Paramètres IA)

## 🛠️ Développement

### Tests en local
```bash
# Backend
cd backend
pytest  # Si des tests sont ajoutés

# Frontend
# Ouvrir index.html dans un navigateur
```

### Structure du code
- `backend/models.py` : Définit le schéma JSON strict avec Pydantic
- `backend/main.py` : API + logique métier + scoring
- `script.js` : Gestion formulaire + appels API + rendu
- `styles.css` : Design moderne et responsive

## 📚 Documentation

- [**Guide complet du scoring**](scoring_guide.html) : Barèmes détaillés et exemples
- [**Exemple de use case**](backend/use_cases/example_use_case.json) : Structure JSON complète

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amelioration`)
3. Commit (`git commit -m 'Ajout fonctionnalité'`)
4. Push (`git push origin feature/amelioration`)
5. Ouvrir une Pull Request

## 📝 Licence

Propriétaire - Tous droits réservés

## 🆘 Support

Pour toute question ou problème :
- Consulter la [documentation du scoring](scoring_guide.html)
- Vérifier que le backend est bien lancé sur le port 5050
- Vérifier que la clé OpenAI est correctement configurée dans `.env`

---

**Version** : 2.0 - Optimisé avec scoring algorithmique et graphique ETP
