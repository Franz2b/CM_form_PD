# 🚀 Guide de Déploiement

## Avant de commencer

✅ **Checklist pré-déploiement :**
- [ ] Clé OpenAI API valide et fonctionnelle
- [ ] Backend testé en local (port 5050)
- [ ] Frontend testé avec le backend
- [ ] Variables d'environnement configurées

---

## Option 1 : Déploiement Backend (Heroku)

### 1. Créer un Procfile
```bash
# À la racine du projet
echo "web: cd backend && uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile
```

### 2. Configurer Heroku
```bash
heroku create votre-app-name
heroku config:set OPENAI_API_KEY=sk-votre-clé-ici
git push heroku main
```

### 3. Vérifier le déploiement
```bash
heroku logs --tail
heroku open
```

L'URL du backend sera : `https://votre-app-name.herokuapp.com`

---

## Option 2 : Déploiement Backend (Railway)

### 1. Créer un nouveau projet sur Railway
- Connecter votre repo GitHub
- Railway détecte automatiquement Python

### 2. Configurer les variables d'environnement
Dans Railway Dashboard :
```
OPENAI_API_KEY=sk-votre-clé-ici
```

### 3. Railway génère automatiquement l'URL
Format : `https://votre-app.railway.app`

---

## Option 3 : Déploiement Backend (Render)

### 1. Créer un nouveau Web Service
- Connecter votre repo GitHub
- Runtime : Python 3
- Build Command : `cd backend && pip install -r requirements.txt`
- Start Command : `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

### 2. Variables d'environnement
```
OPENAI_API_KEY=sk-votre-clé-ici
```

---

## Déploiement Frontend

### Option 1 : GitHub Pages
```bash
# Le frontend est statique, pas besoin de build
# Juste pousser sur GitHub et activer Pages dans Settings
```

**Important** : Configurer l'URL du backend dans l'interface :
- Ouvrir l'app → ⚙️ Paramètres IA
- URL backend : `https://votre-backend.herokuapp.com/analyze`
- Sauvegarder

### Option 2 : Netlify
```bash
# Drag & drop de tout le dossier racine (sauf backend/)
# Ou connecter le repo GitHub
```

**Configuration automatique** : Netlify détecte les fichiers HTML statiques

### Option 3 : Vercel
```bash
vercel --prod
```

**Note** : Le frontend est 100% statique (HTML/CSS/JS), donc déployable n'importe où

---

## Configuration Post-Déploiement

### 1. Tester le backend
```bash
curl https://votre-backend.herokuapp.com/health
# Devrait retourner: {"status": "ok"}
```

### 2. Configurer le frontend
Ouvrir l'application web et :
1. Cliquer sur **⚙️ Paramètres IA**
2. Saisir l'URL backend : `https://votre-backend.herokuapp.com/analyze`
3. Cliquer sur **Sauvegarder**

### 3. Tester l'analyse IA
1. Remplir le formulaire
2. Aller sur "👀 SumUp"
3. Cliquer sur **"Lancer l'analyse IA"**
4. Vérifier que l'analyse s'affiche correctement

---

## Variables d'Environnement

### Backend obligatoire
```bash
OPENAI_API_KEY=sk-...
```

### Backend optionnel
```bash
OPENAI_MODEL=gpt-4o-mini  # Par défaut
# Ou pour plus de puissance :
OPENAI_MODEL=gpt-4o
```

---

## Monitoring & Logs

### Heroku
```bash
heroku logs --tail
heroku ps
```

### Railway
- Dashboard → Logs (temps réel)

### Render
- Dashboard → Logs (temps réel)

---

## Troubleshooting

### ❌ Backend ne démarre pas
```bash
# Vérifier les logs
heroku logs --tail

# Vérifier les variables d'env
heroku config

# Redémarrer
heroku restart
```

### ❌ Frontend ne peut pas contacter le backend
1. Vérifier que l'URL backend est correcte dans Paramètres IA
2. Vérifier les CORS (déjà configuré dans main.py)
3. Vérifier que le backend est bien démarré

### ❌ Analyse IA échoue
1. Vérifier que `OPENAI_API_KEY` est bien configurée
2. Vérifier les crédits OpenAI
3. Consulter les logs du backend

---

## Coûts Estimés

### Backend
- **Heroku** : Gratuit (avec dynos éco) ou ~7$/mois (hobby)
- **Railway** : 5$ de crédit gratuit/mois puis pay-as-you-go
- **Render** : Gratuit (avec limitations) ou 7$/mois (starter)

### Frontend
- **GitHub Pages** : Gratuit
- **Netlify** : Gratuit (100GB bande passante)
- **Vercel** : Gratuit (hobby)

### API OpenAI
- **gpt-4o-mini** : ~0.15$/1M tokens input, ~0.60$/1M tokens output
- Coût moyen par analyse : ~0.01-0.02$ (environ 1000-2000 tokens)
- **Budget mensuel estimé** (100 analyses/mois) : ~1-2$

---

## Sécurité

✅ **Bonnes pratiques implémentées :**
- Clé API OpenAI côté serveur uniquement (jamais exposée au frontend)
- `.env` ignoré par git
- CORS configuré (modifiable dans `backend/main.py`)
- Validation stricte des données (Pydantic)

⚠️ **À faire en production :**
- Activer HTTPS (automatique sur Heroku/Railway/Render)
- Limiter les origins CORS à votre domaine frontend
- Ajouter un rate limiting si nécessaire
- Monitorer les coûts OpenAI

---

## Backup des Use Cases

Les use cases sauvegardés sont dans `backend/use_cases/`

**Pour sauvegarder régulièrement :**
```bash
# Heroku
heroku run "tar -czf use_cases.tar.gz backend/use_cases/ && cat use_cases.tar.gz" > backup.tar.gz

# Ou configurer un stockage externe (S3, Google Cloud Storage)
```

---

## Mise à jour de l'application

```bash
# Modifier le code
git add .
git commit -m "Description des changements"

# Déployer
git push heroku main  # ou main selon votre config
# Railway/Render se déploient automatiquement depuis GitHub
```

---

🎉 **Votre application est prête pour le déploiement !**

