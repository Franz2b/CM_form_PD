# Analyse IA avec Structured Outputs

## 🎯 Principe

Le système utilise **OpenAI Structured Outputs** avec **Pydantic** pour garantir :
- ✅ Structure JSON **toujours identique**
- ✅ Catégories **strictement prédéfinies** (Enums)
- ✅ Validation automatique
- ✅ Robustesse 100%

---

## 📊 Structure JSON garantie

```json
{
  "user_story": {
    "html": "<p>En tant que...",
    "word_count": 85
  },
  "execution_schema": {
    "ascii_diagram": "┌────┐\n│ 1  │\n└─┬──┘\n  ▼",
    "steps": [
      {"step": 1, "description": "..."},
      {"step": 2, "description": "..."}
    ]
  },
  "elements_sources": {
    "types": [
      {"category": "Excel", "description": "..."},
      {"category": "PDF", "description": "..."}
    ],
    "count": 2,
    "complexity_level": "Semi-structuré"
  },
  "analysis": {
    "pain_points": ["Répétitivité", "Erreurs fréquentes"],
    "benefits": ["Gain de temps", "Amélioration qualité"],
    "feasibility_score": 75,
    "priority": "Quick win"
  }
}
```

---

## 🔒 Catégories STRICTES (Enums)

### ElementCategory
- `Excel`, `PDF`, `Email`, `Papier`, `BDD`, `Image`, `Word`, `Formulaire`, `ERP_CRM`, `Audio`, `Autre`

### ComplexityLevel
- `Structuré`, `Semi-structuré`, `Non-structuré`

### PainPoint
- `Répétitivité`, `Erreurs fréquentes`, `Lenteur`, `Complexité`, `Coordination difficile`, `Risque conformité`, `Manque visibilité`, `Volume élevé`

### Benefit
- `Gain de temps`, `Amélioration qualité`, `Réduction coûts`, `Satisfaction utilisateurs`, `Conformité`, `Traçabilité`, `Meilleure collaboration`

### Priority
- `Quick win`, `À challenger`, `Long shot`

**L'IA ne peut PAS sortir d'autres valeurs !**

---

## 🚀 Utilisation

### Backend
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 5050 --reload
```

### Frontend
1. Remplir le formulaire
2. Aller sur "👀 5. SumUp"
3. Cliquer sur "🤖 Analyser le formulaire"
4. Résultats affichés en temps réel

---

## 🧪 Test manuel de l'API

```bash
curl -X POST http://localhost:5050/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "form_data": {
      "q1": "Dupont",
      "q2": "Marie",
      "q3": "Comptable",
      "q4": "Finance",
      "q5": "Je reçois 50 factures par jour. Je dois les saisir manuellement dans SAP. C'\''est long et source d'\''erreurs.",
      "q6": "1. Réception e-mail\n2. Ouverture PDF\n3. Saisie SAP\n4. Archivage",
      "q7": "Quotidien",
      "q8": "51-200",
      "q9": "10-30 min",
      "q10": "2-5",
      "q11": "4",
      "q11a": "Tâche répétitive sans valeur ajoutée",
      "q11b": "Risque d'\''erreurs de facturation",
      "q12": "Factures PDF, Excel de suivi, SAP",
      "q13": "Oui",
      "q13a": "Copier-coller entre PDF et SAP",
      "q14": "Oui",
      "q14a": "",
      "q15": "Simple",
      "q16": "Outlook + SAP + Excel"
    }
  }'
```

---

## ✅ Garanties

1. **Structure fixe** : OpenAI ne peut pas changer la structure du JSON
2. **Enums stricts** : Impossible de créer de nouvelles catégories
3. **Validation Pydantic** : Double vérification côté serveur
4. **Comparabilité** : Tous les use cases ont exactement les mêmes champs

---

## 📈 Scoring de faisabilité

**Algorithme** (0-100 pts) :
- Règles simples et stables (Q14 = "Oui") : +30 pts
- Données structurées (Q12 = Excel/BDD/Formulaire) : +30 pts
- Complexité orga simple (Q15 = "Simple") : +20 pts
- Peu/pas d'actions manuelles (Q13 = "Non" ou basiques) : +20 pts

**Priorité** :
- \>70 pts → Quick win (vert)
- 45-70 pts → À challenger (orange)
- <45 pts → Long shot (rouge)

