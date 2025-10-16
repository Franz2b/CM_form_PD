# 🎯 Grille de Scoring - Documentation complète

## 📊 Vue d'ensemble

Le scoring permet de comparer objectivement tous les use cases sur une base de **100 points**.

**Formule générale :**
```
SCORE TOTAL = Impact Business (40 pts) + Faisabilité Technique (30 pts) + Urgence (30 pts)
```

---

## 1️⃣ IMPACT BUSINESS (/40 points)

Mesure l'impact métier potentiel de l'automatisation.

### Composants (4 critères)

| Critère | Source | Barème | Poids max |
|---------|--------|--------|-----------|
| **Fréquence du besoin** | Q7 | Quotidien=10, Hebdo=7, Mensuel=4, Occasionnel=2 | 10 pts |
| **Nb exécutions/occurrence** | Q8 | 200+=10, 51-200=7, 11-50=5, 2-10=3, 1=1 | 10 pts |
| **Temps d'exécution unitaire** | Q9 | >2h=10, 1-2h=7, 30min-1h=5, 10-30min=3, <10min=1 | 10 pts |
| **Nb personnes exécutantes** | Q10 | 50+=10, 21-50=7, 6-20=5, 2-5=3, 1=1 | 10 pts |

### Exemple de calcul

**Cas : Factures quotidiennes**
- Q7 : Quotidien → 10 points
- Q8 : 51-200 fois → 7 points
- Q9 : 10-30 min → 3 points
- Q10 : 2-5 personnes → 3 points

**Score Impact = 10 + 7 + 3 + 3 = 23/40**

---

## 2️⃣ FAISABILITÉ TECHNIQUE (/30 points)

Mesure la facilité/difficulté d'automatiser la tâche.

### Composants (4 critères)

| Critère | Source | Barème | Points |
|---------|--------|--------|--------|
| **Règles simples et stables** | Q17 | Oui=10, Partiellement=6, Non=2 | 10 pts |
| **Types de sources** | **count (IA)** | 1-2 types=10, 3-4 types=6, 5+ types=2 | 10 pts |
| **Complexité organisationnelle** | Q19 | Simple=7, Moyenne=4, Complexe=1 | 7 pts |
| **Action manuelle** | Q15 | Non=3, Oui=0 | 3 pts |

### Exemple de calcul

**Cas : Règles claires, 3 types de données, complexité moyenne**
- Q17 : Oui (règles claires) → 10 points
- **count** : 3 types (Excel, PDF, SAP) → **6 points** ⚠️ RÉSULTAT IA depuis Q14
- Q19 : Moyenne (validation nécessaire) → 4 points
- Q15 : Oui (action manuelle) → 0 point

**Score Faisabilité = 10 + 6 + 4 + 0 = 20/30**

---

## 3️⃣ URGENCE (/30 points)

Mesure le niveau d'urgence et l'irritant ressenti.

### Formule simple

| Critère | Source | Formule | Max |
|---------|--------|---------|-----|
| **Niveau d'irritant** | Q11 | Irritant × 6 | 30 pts |

### Barème

- Irritant 5/5 (Bloquant) → 5 × 6 = **30 points**
- Irritant 4/5 (Critique) → 4 × 6 = **24 points**
- Irritant 3/5 (Important) → 3 × 6 = **18 points**
- Irritant 2/5 (Modéré) → 2 × 6 = **12 points**
- Irritant 1/5 (Faible) → 1 × 6 = **6 points**

### Exemple de calcul

**Cas : Irritant niveau 4**
- Q11 : 4/5 → 4 × 6 = **24/30**

---

## 📐 EXEMPLE COMPLET DE CALCUL

### Contexte
- Q7 : Tâche quotidienne
- Q8 : 51-200 factures par occurrence
- Q9 : 10-30 min par facture
- Q10 : 2-5 personnes concernées
- Q17 : Règles claires (Oui)
- count (IA) : 3 types de données (PDF, Excel, SAP)
- Q19 : Complexité orga moyenne
- Q15 : Action manuelle (Oui)
- Q11 : Irritant niveau 4/5

### Calcul détaillé

```
IMPACT BUSINESS (/40)
  Fréquence(Quotidien=10) + 
  NbExec(51-200=7) + 
  Temps(10-30min=3) + 
  Personnes(2-5=3) 
  = 23/40

FAISABILITÉ TECHNIQUE (/30)
  Règles(Oui=10) + 
  TypesSources(3 types=6) ← RÉSULTAT IA
  ComplexitéOrga(Moyenne=4) + 
  ActionManuelle(Oui=0) 
  = 20/30

URGENCE (/30)
  Irritant(4×6) = 24/30

SCORE TOTAL = 23 + 20 + 24 = 67/100
```

---

## 🎯 Interprétation des scores

| Score | Catégorie | Signification |
|-------|-----------|---------------|
| **70-100** | 🟢 Quick win | Priorité maximale - Impact fort, faisable, urgent |
| **45-69** | 🟡 À challenger | À étudier - Bon potentiel mais contraintes |
| **0-44** | 🔴 Long shot | Faible priorité - Impact faible ou complexité élevée |

---

## 🔑 Points clés

✅ **Standardisé** : Même formule pour tous les use cases → comparable
✅ **Transparent** : Tous les poids et barèmes documentés
✅ **Hybride** : Combine données formulaire + résultats IA (count)
✅ **Simple** : 3 dimensions faciles à comprendre

---

## 💡 Variables IA utilisées dans le scoring

| Variable | Source | Usage |
|----------|--------|-------|
| **count** | Nb de types de sources uniques (IA) | Faisabilité Technique (×8 pts) |

**Important** : Plus il y a de types de sources différents, plus c'est complexe à automatiser → score de faisabilité réduit.

Exemple :
- 1-2 types (Excel, PDF) → 10 points → **Simple**
- 3-4 types (Excel, PDF, SAP, Email) → 6 points → **Moyen**
- 5+ types → 2 points → **Complexe**

---

## 📖 Utilisation

1. **Remplir le formulaire** (Q1-Q16)
2. **Analyser avec l'IA** → L'IA calcule automatiquement le score
3. **Comparer les use cases** grâce au score standardisé
4. **Prioriser** : Quick wins en premier !

