import os
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None  # will error at runtime if missing

from models import (
    FormAnalysisResponse, FormAnalysisResponseWithoutScoring, AnalyzeRequest, FormData,
    ElementCategory, ComplexityLevel, PainPoint, Benefit, Priority, DevTime, Scoring
)

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()
MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")


# ==================== CALCUL DU SCORING ====================
def calculate_scoring(form_data: FormData, elements_count: int) -> Scoring:
    """
    Calcule le scoring de manière déterministe côté backend.
    Basé sur les réponses du formulaire uniquement.
    """
    # IMPACT BUSINESS (0-40 points)
    impact_score = 0
    
    # Q7 - Fréquence du besoin
    freq_map = {"Quotidien": 10, "Hebdomadaire": 7, "Mensuel": 4, "Occasionnel": 2}
    impact_score += freq_map.get(form_data.q7, 0)
    
    # Q8 - Nombre d'exécutions
    exec_map = {"1": 1, "2-10": 3, "11-50": 5, "51-200": 7, "200+": 10}
    impact_score += exec_map.get(form_data.q8, 0)
    
    # Q9 - Temps unitaire (avec et sans espaces pour compatibilité formulaire)
    time_map = {
        "<10min": 1, "< 10 min": 1,
        "10-30min": 3, "10-30 min": 3,
        "30min-1h": 5, "30 min - 1h": 5,
        "1-2h": 7,
        ">2h": 10, "> 2h": 10
    }
    impact_score += time_map.get(form_data.q9, 0)
    
    # Q10 - Nombre de personnes
    people_map = {"1": 1, "2-5": 3, "6-20": 5, "21-50": 7, "50+": 10}
    impact_score += people_map.get(form_data.q10, 0)
    
    # FAISABILITÉ TECHNIQUE (0-30 points)
    faisabilite_score = 0
    
    # Q17 - Règles claires
    rules_map = {"Oui": 10, "Partiellement": 6, "Non": 2}
    faisabilite_score += rules_map.get(form_data.q17, 0)
    
    # Nombre de types de sources (calculé par l'IA)
    if elements_count <= 2:
        faisabilite_score += 10
    elif elements_count <= 4:
        faisabilite_score += 6
    else:
        faisabilite_score += 2
    
    # Q19 - Complexité organisationnelle
    complexity_map = {"Simple": 7, "Moyenne": 4, "Complexe": 1}
    faisabilite_score += complexity_map.get(form_data.q19, 0)
    
    # Q15 - Action manuelle requise
    manual_map = {"Non": 3, "Oui": 0}
    faisabilite_score += manual_map.get(form_data.q15, 0)
    
    # URGENCE (0-30 points)
    urgence_score = 0
    try:
        irritant = int(form_data.q11 or 0)
        urgence_score = irritant * 6  # 1-5 × 6 = 6-30
    except ValueError:
        urgence_score = 0
    
    # TOTAL
    total = impact_score + faisabilite_score + urgence_score
    
    # Convertir en base 100 pour l'affichage
    impact_normalized = round((impact_score / 40) * 100)
    faisabilite_normalized = round((faisabilite_score / 30) * 100)
    urgence_normalized = round((urgence_score / 30) * 100)
    
    # GAIN TEMPS MENSUEL (heures)
    # Fréquence = nombre d'occurrences par mois (sur 20 jours ouvrés)
    freq_factor = {"Quotidien": 20, "Hebdomadaire": 5, "Mensuel": 1, "Occasionnel": 0.5}
    # Nombre d'exécutions par occurrence (valeur médiane de chaque fourchette)
    exec_factor = {"1": 1, "2-10": 6, "11-50": 30, "51-200": 125, "200+": 200}
    # Temps par exécution en heures (avec et sans espaces pour compatibilité)
    time_factor = {
        "<10min": 0.1, "< 10 min": 0.1,
        "10-30min": 0.33, "10-30 min": 0.33,
        "30min-1h": 0.75, "30 min - 1h": 0.75,
        "1-2h": 1.5,
        ">2h": 3, "> 2h": 3
    }
    # Nombre de personnes (valeur médiane)
    people_factor = {"1": 1, "2-5": 3, "6-20": 10, "21-50": 30, "50+": 50}
    
    freq_val = freq_factor.get(form_data.q7, 0)
    exec_val = exec_factor.get(form_data.q8, 0)
    time_val = time_factor.get(form_data.q9, 0)
    people_val = people_factor.get(form_data.q10, 1)
    
    # FORMULE : (Fréquence × Nb exec × Temps par exec) = heures totales par mois pour l'équipe
    # Note: On ne multiplie PAS par le nombre de personnes car elles se partagent le travail
    # Mais on utilise le nombre de personnes pour ajuster le calcul si nécessaire
    gain_temps = int(freq_val * exec_val * time_val)
    
    # Formule lisible
    formula = (
        f"Impact[Fréquence({form_data.q7}={freq_map.get(form_data.q7, 0)}) + "
        f"NbExec({form_data.q8}={exec_map.get(form_data.q8, 0)}) + "
        f"Temps({form_data.q9}={time_map.get(form_data.q9, 0)}) + "
        f"Personnes({form_data.q10}={people_map.get(form_data.q10, 0)}) = {impact_score}/40 = {impact_normalized}/100] + "
        f"Faisabilité[Règles({form_data.q17}={rules_map.get(form_data.q17, 0)}) + "
        f"TypesSources({elements_count} types) + "
        f"ComplexitéOrga({form_data.q19}={complexity_map.get(form_data.q19, 0)}) + "
        f"ActionManuelle({form_data.q15}={manual_map.get(form_data.q15, 0)}) = {faisabilite_score}/30 = {faisabilite_normalized}/100] + "
        f"Urgence[Irritant({form_data.q11}×6) = {urgence_score}/30 = {urgence_normalized}/100] = "
        f"Total {total}/100"
    )
    
    justification = (
        f"Score de {total}/100 basé sur : Impact Business {impact_normalized}/100 "
        f"(fréquence {form_data.q7}, {form_data.q8} exécutions, {form_data.q9} par exécution, "
        f"{form_data.q10} personnes), Faisabilité Technique {faisabilite_normalized}/100 "
        f"({elements_count} types de sources, règles {form_data.q17 or 'non spécifié'}, "
        f"complexité {form_data.q19 or 'non spécifié'}), Urgence {urgence_normalized}/100 "
        f"(irritant {form_data.q11}/5)."
    )
    
    return Scoring(
        impact_business_score=f"{impact_normalized}/100",
        faisabilite_technique_score=f"{faisabilite_normalized}/100",
        urgence_score=f"{urgence_normalized}/100",
        total=total,
        formula=formula,
        justification=justification,
        gain_temps_mensuel_heures=gain_temps
    )

app = FastAPI(title="CM Form PD – AI Proxy", version="1.0.0")

# Log au démarrage
@app.on_event("startup")
async def startup_event():
    logger.info("=" * 80)
    logger.info("🚀 BACKEND DÉMARRÉ")
    logger.info("=" * 80)
    logger.info(f"Modèle OpenAI: {MODEL}")
    logger.info(f"API Key présente: {'✅' if os.environ.get('OPENAI_API_KEY') else '❌'}")
    logger.info("Endpoints disponibles:")
    logger.info("  - GET  /health")
    logger.info("  - POST /ai")
    logger.info("  - POST /analyze (Structured Outputs)")
    logger.info("  - POST /save (Sauvegarde use case)")
    logger.info("=" * 80 + "\n")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AiRequest(BaseModel):
    prompt: str


class AiResponse(BaseModel):
    text: str


@app.get("/health")
def health():
    return {"ok": True, "model": MODEL}


@app.post("/ai", response_model=AiResponse)
async def ai(req: AiRequest):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY manquant dans l'environnement")
    if OpenAI is None:
        raise HTTPException(status_code=500, detail="Package openai manquant. Installez-le via requirements.txt")

    try:
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Tu es un assistant expert en design de processus et delivery produit."},
                {"role": "user", "content": req.prompt},
            ],
            temperature=0.2,
            max_tokens=900,
        )
        text = (resp.choices[0].message.content or "").strip()
        return AiResponse(text=text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/analyze", response_model=FormAnalysisResponse)
async def analyze_form(req: AnalyzeRequest):
    """
    Analyse structurée du formulaire avec Structured Outputs.
    Garantit une structure JSON fixe et des catégories strictes.
    """
    logger.info("=" * 80)
    logger.info("📥 NOUVELLE REQUÊTE D'ANALYSE")
    logger.info("=" * 80)
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY manquant")
    if OpenAI is None:
        raise HTTPException(status_code=500, detail="Package openai manquant")

    # Construire le prompt contextuel
    d = req.form_data
    logger.info(f"📋 Données formulaire reçues:")
    logger.info(f"   - Persona: {d.q1} {d.q2} ({d.q3} - {d.q4})")
    logger.info(f"   - Brief: {(d.q5 or '')[:100]}...")
    logger.info(f"   - Volumétrie: {d.q7} / {d.q8} exec / {d.q9} unitaire")
    
    # Construire le contexte (éviter les {} dans f-string)
    context = """
CONTEXTE FORMULAIRE - ANALYSE PROCESS DESIGNER

=== PERSONA ===
Nom: """ + (d.q1 or '-') + " " + (d.q2 or '-') + """
Rôle: """ + (d.q3 or '-') + """
Département: """ + (d.q4 or '-') + """

=== BESOIN ===
Brief utilisateur:
""" + (d.q5 or '-') + """

Exécution actuelle:
""" + (d.q6 or '-') + """

=== VOLUMÉTRIE ===
Fréquence: """ + (d.q7 or '-') + """
Nb exécutions/occurrence: """ + (d.q8 or '-') + """
Temps unitaire: """ + (d.q9 or '-') + """
Nb personnes: """ + (d.q10 or '-') + """
Irritant: """ + (d.q11 or '3') + """/5
Pourquoi irritant: """ + (d.q12 or '-') + """
Pourquoi urgent: """ + (d.q13 or '-') + """

=== NATURE TÂCHE ===
Éléments sources: """ + (d.q14 or '-') + """
Action manuelle: """ + (d.q15 or '-') + """
Exemple action: """ + (d.q16 or '-') + """
Règles simples: """ + (d.q17 or '-') + """
Points complexes: """ + (d.q18 or '-') + """
Complexité orga: """ + (d.q19 or '-') + """
Outils: """ + (d.q20 or '-') + """

=== INSTRUCTIONS ===
1. USER STORY:
   - project_name: Génère un NOM DE PROJET court et impactant (3-6 mots max)
     Exemple: "Automatisation Saisie Factures SAP" ou "Robot Rapprochement Comptable"
   - html: User story HTML (max 100 mots) AVEC CONTEXTE
     Format: <p><strong>En tant que</strong> [rôle + contexte département/volumétrie],</p>
             <p><strong>j'ai besoin de</strong> [besoin détaillé]</p>
             <p><strong>afin de</strong> [bénéfice concret et mesurable].</p>

2. EXECUTION SCHEMA: Diagramme ASCII vertical UNIQUEMENT (pas de liste étapes)

3. ELEMENTS SOURCES (Q14):
   - types: Catégorise STRICTEMENT
   - count: Nombre de TYPES UNIQUES (Excel GL + Excel OSB = 1 seul type)
   - complexity_level: Structuré/Semi-structuré/Non-structuré

4. ANALYSIS: Pain points, bénéfices, score faisabilité, priorité

5. PRO/CON:
   - pros: 3-5 arguments POUR. Chaque: argument + weight (Faible/Moyen/Fort)
   - cons: 2-4 arguments CONTRE. Chaque: argument + weight (Faible/Moyen/Fort)

6. DELIVERY:
   - dev_time: Temps total
   - phases (2-3): Phases simples
     * name: POC / MVP / Production
     * feature_principale: LA feature principale exploitable
     * risque_principal: LE risque principal
     * duration: Durée
   - quick_wins (3-5): "En attendant, essaye de..."
"""

    try:
        client = OpenAI(api_key=api_key)
        
        # Vérifier que le modèle supporte Structured Outputs
        if MODEL not in ["gpt-4o", "gpt-4o-mini", "gpt-4o-2024-08-06"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Modèle {MODEL} ne supporte pas Structured Outputs. Utilisez gpt-4o ou gpt-4o-mini"
            )
        
        # Générer le schéma JSON (sans scoring, calculé côté backend)
        schema = FormAnalysisResponseWithoutScoring.model_json_schema()
        
        logger.info("\n" + "=" * 80)
        logger.info("🤖 APPEL OPENAI")
        logger.info("=" * 80)
        logger.info(f"Modèle: {MODEL}")
        system_prompt = "Tu es un expert en analyse de processus métier et automatisation. Tu dois analyser un formulaire et produire une réponse JSON STRICTEMENT conforme au schéma fourni. Utilise UNIQUEMENT les catégories prédéfinies dans les enums."
        
        logger.info(f"\n📤 MESSAGES ENVOYÉS À OPENAI:")
        logger.info("-" * 80)
        logger.info(f"SYSTEM: {system_prompt}")
        logger.info("")
        logger.info(f"USER:\n{context}")
        logger.info("-" * 80)
        logger.info("\n⏳ Appel OpenAI en cours...")
        
        # Chronomètre
        start_time = time.time()
        
        # Appel avec Structured Outputs
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": context
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "form_analysis_response",
                    "strict": True,
                    "schema": schema
                }
            },
            temperature=0.3,
            max_tokens=2000
        )
        
        # Temps écoulé
        elapsed = time.time() - start_time
        logger.info(f"✅ Réponse OpenAI reçue en {elapsed:.2f}s")
        
        # Tokens utilisés
        if hasattr(response, 'usage') and response.usage:
            logger.info(f"📊 Tokens utilisés:")
            logger.info(f"   - Prompt: {response.usage.prompt_tokens}")
            logger.info(f"   - Completion: {response.usage.completion_tokens}")
            logger.info(f"   - Total: {response.usage.total_tokens}")
        
        # Parse et valide avec Pydantic
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Réponse OpenAI vide")
        
        logger.info("\n📥 RÉPONSE OPENAI (JSON):")
        logger.info("-" * 80)
        # Pretty print du JSON
        try:
            formatted_json = json.dumps(json.loads(content), indent=2, ensure_ascii=False)
            logger.info(formatted_json)
        except:
            logger.info(content)
        logger.info("-" * 80)
        
        # Parse JSON
        result_json = json.loads(content)
        logger.info("\n✅ JSON parsé avec succès")
        logger.info(f"📊 Aperçu:")
        logger.info(f"   - User story: {result_json.get('user_story', {}).get('word_count', 0)} mots")
        logger.info(f"   - Étapes: {len(result_json.get('execution_schema', {}).get('steps', []))}")
        logger.info(f"   - Éléments sources: {result_json.get('elements_sources', {}).get('count', 0)} types")
        logger.info(f"   - Complexité: {result_json.get('elements_sources', {}).get('complexity_level', '?')}")
        logger.info(f"   - Faisabilité: {result_json.get('analysis', {}).get('feasibility_score', 0)}/100")
        logger.info(f"   - Priorité: {result_json.get('analysis', {}).get('priority', '?')}")
        logger.info(f"   - Pro/Con: {len(result_json.get('pro_con', {}).get('pros', []))} pros / {len(result_json.get('pro_con', {}).get('cons', []))} cons")
        logger.info(f"   - Temps dev: {result_json.get('delivery', {}).get('dev_time', '?')}")
        logger.info(f"   - Phases: {len(result_json.get('delivery', {}).get('phases', []))}")
        logger.info(f"   - Quick wins: {len(result_json.get('delivery', {}).get('quick_wins', []))}")
        
        # CALCUL DU SCORING CÔTÉ BACKEND (déterministe)
        logger.info("\n🧮 Calcul du scoring côté backend...")
        elements_count = result_json.get('elements_sources', {}).get('count', 0)
        calculated_scoring = calculate_scoring(req.form_data, elements_count)
        
        # Remplacer le scoring par notre calcul
        result_json['scoring'] = {
            'impact_business_score': calculated_scoring.impact_business_score,
            'faisabilite_technique_score': calculated_scoring.faisabilite_technique_score,
            'urgence_score': calculated_scoring.urgence_score,
            'total': calculated_scoring.total,
            'formula': calculated_scoring.formula,
            'justification': calculated_scoring.justification,
            'gain_temps_mensuel_heures': calculated_scoring.gain_temps_mensuel_heures
        }
        logger.info(f"   ✅ Scoring calculé: {calculated_scoring.total}/100")
        logger.info(f"      - Impact Business: {calculated_scoring.impact_business_score}")
        logger.info(f"      - Faisabilité: {calculated_scoring.faisabilite_technique_score}")
        logger.info(f"      - Urgence: {calculated_scoring.urgence_score}")
        logger.info(f"      - Gain temps: {calculated_scoring.gain_temps_mensuel_heures}h/mois")
        
        # Validation Pydantic
        validated_result = FormAnalysisResponse(**result_json)
        logger.info("\n✅ Validation Pydantic OK")
        logger.info("=" * 80 + "\n")
        
        return validated_result
        
    except HTTPException:
        raise
    except json.JSONDecodeError as e:
        logger.error(f"❌ Erreur parsing JSON: {str(e)}")
        raise HTTPException(status_code=502, detail=f"Erreur parsing JSON: {str(e)}")
    except Exception as e:
        # Log détaillé de l'erreur
        import traceback
        logger.error("❌ ERREUR OPENAI:")
        logger.error(traceback.format_exc())
        error_detail = f"Erreur OpenAI: {str(e)}"
        raise HTTPException(status_code=502, detail=error_detail)


class SaveRequest(BaseModel):
    """Requête de sauvegarde"""
    form_data: FormData
    ai_analysis: FormAnalysisResponse


@app.post("/save")
async def save_use_case(req: SaveRequest):
    """
    Sauvegarde le use case complet (formulaire + résultats IA) dans un fichier JSON.
    Format: YYYYMMDD_HHMMSS_[persona].json
    """
    try:
        # Créer le dossier use_cases
        use_cases_dir = Path(__file__).parent / "use_cases"
        use_cases_dir.mkdir(exist_ok=True)
        
        # Générer nom de fichier avec datetime
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        
        # Nom basé sur persona
        persona = f"{req.form_data.q1 or 'user'}_{req.form_data.q2 or 'unknown'}"
        clean_name = "".join(c if c.isalnum() or c in ('_',) else '_' for c in persona)[:30]
        
        filename = f"{timestamp}_{clean_name}.json"
        filepath = use_cases_dir / filename
        
        # Transformer les clés du formulaire en noms parlants
        d = req.form_data
        form_data_readable = {
            "persona": {
                "nom": d.q1,
                "prenom": d.q2,
                "role": d.q3,
                "departement": d.q4
            },
            "contexte_besoin": {
                "brief_utilisateur": d.q5,
                "execution_actuelle": d.q6
            },
            "volumetrie": {
                "frequence_besoin": d.q7,
                "nb_executions_par_occurrence": d.q8,
                "temps_execution_unitaire": d.q9,
                "nb_personnes_executantes": d.q10,
                "niveau_irritant": d.q11,
                "pourquoi_irritant": d.q12,
                "pourquoi_urgent": d.q13
            },
            "nature_tache": {
                "elements_sources": d.q14,
                "action_manuelle": d.q15,
                "exemple_action_manuelle": d.q16,
                "regles_simples_stables": d.q17,
                "points_complexes_detailles": d.q18,
                "complexite_organisationnelle": d.q19,
                "outils_necessaires": d.q20
            }
        }
        
        # Construire JSON complet
        complete_data = {
            "metadata": {
                "saved_at": now.isoformat(),
                "project_name": req.ai_analysis.user_story.project_name,
                "persona": f"{d.q1} {d.q2}",
                "role": d.q3,
                "department": d.q4,
                "score": req.ai_analysis.scoring.total,
                "priority": req.ai_analysis.analysis.priority
            },
            "form_data": form_data_readable,
            "ai_analysis": req.ai_analysis.model_dump()
        }
        
        # Sauvegarder
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(complete_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Use case sauvegardé: {filename}")
        logger.info(f"   Persona: {req.form_data.q1} {req.form_data.q2}")
        logger.info(f"   Score: {req.ai_analysis.scoring.total}/100")
        logger.info(f"   Fichier: {filepath}")
        
        return {
            "success": True,
            "filename": filename,
            "path": str(filepath)
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur sauvegarde: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur sauvegarde: {str(e)}")


