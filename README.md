# Formulaire Diagnostic Process

Formulaire en ligne, autonome (HTML/CSS/JS), pour qualifier un processus et faciliter la priorisation des cas d'usage.

## Utilisation

1. Ouvrez le fichier `index.html` dans votre navigateur (double-clic).
2. Remplissez le formulaire (autosauvegarde activée – vous pouvez revenir plus tard).
3. Cliquez sur « Exporter en JSON » pour télécharger les réponses.
4. « Réinitialiser » efface le formulaire et les données locales.

## Structure

- `index.html` – Structure du formulaire (21 questions, 4 blocs)
- `styles.css` – Styles modernes, accessibles, responsive
- `script.js` – Autosauvegarde (`localStorage`), export JSON, réinitialisation
  et navigation par chapitres, scoring automatique, récap, IA (synthèse & delivery)

## Personnalisation

- Lien Coach IA: dans `script.js`, modifiez l'adresse e‑mail `coach-ia@exemple.com`.
- Thème: adaptez les variables CSS dans `styles.css` (`:root`).

## Données

Les données sont stockées localement dans votre navigateur (`localStorage`) sous la clé `cm_form_pd_v1`. Aucun envoi réseau n'est effectué.

## IA (optionnelle)

Deux options:

1. Recommandé — Backend FastAPI (sécurisé)
   - Prérequis: Python 3.10+
   - Installation:
     ```bash
     cd /Users/francoisvivarelli/Documents/Dev/CM/CM_form_PD/backend
     python3 -m venv .venv && source .venv/bin/activate
     pip install -r requirements.txt
     # Option A: .env → copiez ENV_EXAMPLE.txt en .env et remplissez OPENAI_API_KEY
     # Option B: variable d'env
     export OPENAI_API_KEY="VOTRE_CLE_OPENAI"
     uvicorn main:app --host 0.0.0.0 --port 5050
     ```
   - Dans la page (⚙️ Paramètres IA), mettez `http://localhost:5050/ai`.

2. Non recommandé — Clé OpenAI dans le navigateur
   - Renseignez la clé dans le champ Clé OpenAI. Risque d’exposition dans les DevTools.

Le formulaire n’envoie rien sans votre action sur « Générer ». Les prompts incluent un récap des réponses et des scores.


