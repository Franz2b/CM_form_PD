# 🚀 Quick Start - Formulaire Process Designer

## ⚡ Démarrage rapide

### 1️⃣ Lancer le backend (Terminal 1)
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 5050 --reload
```

✅ Vérifier que ça fonctionne : http://localhost:5050/health

---

### 2️⃣ Ouvrir le formulaire
```bash
open index.html
```

---

### 3️⃣ Remplir le formulaire

**Navigation :**
- 👤 Persona → 💡 Besoin → 📊 Volumétrie → 🔧 Nature → 👀 Synthèse
- Boutons "Suivant →" et "← Précédent"
- Cliquer sur les onglets pour sauter

**Auto-save :**
- Sauvegarde automatique dans le navigateur
- Vous pouvez fermer et revenir plus tard

---

### 4️⃣ Analyser avec l'IA

Sur la page **👀 Synthèse** :
1. Cliquer sur "🤖 Analyser le formulaire"
2. Attendre 5-10 secondes
3. Résultats affichés :
   - User story générée
   - Schéma d'exécution (ASCII)
   - Éléments sources catégorisés
   - Pain points + Bénéfices
   - Score de faisabilité
   - Priorité (Quick win / À challenger / Long shot)

---

## 🧪 Tester le backend seul

```bash
cd backend
python test_analysis.py
```

Affiche un exemple complet d'analyse.

---

## 📋 Structure du formulaire

### Page 1 : Persona (4Q)
Nom, Prénom, Rôle, Département

### Page 2 : Besoin (2Q)
Brief utilisateur, Exécution actuelle

### Page 3 : Volumétrie (7Q)
Fréquence, Nb exécutions, Temps unitaire, Nb personnes, Irritant/Urgence

### Page 4 : Nature (5Q)
Éléments sources, Actions manuelles, Règles, Complexité orga, Outils

### Page 5 : Synthèse
Analyse IA + Récapitulatif

---

## 🔒 Catégories strictes garanties

**Types d'éléments :** Excel, PDF, Email, Papier, BDD, Image, Word, Formulaire, ERP_CRM, Audio, Autre

**Complexité :** Structuré, Semi-structuré, Non-structuré

**Pain points :** Répétitivité, Erreurs fréquentes, Lenteur, Complexité, Coordination difficile, Risque conformité, Manque visibilité, Volume élevé

**Bénéfices :** Gain de temps, Amélioration qualité, Réduction coûts, Satisfaction utilisateurs, Conformité, Traçabilité, Meilleure collaboration

**Priorité :** Quick win, À challenger, Long shot

➡️ **L'IA ne peut PAS sortir d'autres catégories !**

---

## ❌ Troubleshooting

**"Backend non accessible"**
→ Vérifier que uvicorn tourne sur port 5050

**"OPENAI_API_KEY manquant"**
→ Créer `backend/.env` avec `OPENAI_API_KEY=sk-...`

**"Model not found"**
→ Vérifier que vous utilisez `gpt-4o` ou `gpt-4o-mini` (Structured Outputs requis)

---

## 💡 Exemple de volumétrie

**Cas : Clôture comptable mensuelle**
- Q7 : Mensuel
- Q8 : 51-200 fois (150 factures à traiter)
- Q9 : 10-30 min (20 min par facture)

➡️ Impact total : 150 × 20 min = **50 heures par mois**

